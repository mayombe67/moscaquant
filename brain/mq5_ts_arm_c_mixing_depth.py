from __future__ import annotations

import argparse
import gc
import hashlib
import json
import os
import subprocess
import tempfile
import time
import tomllib
from dataclasses import asdict
from pathlib import Path

import numpy as np
from scipy import sparse

from brain.mq5_ts_strict_shuffle_native import (
    build_strict_matched_control_native,
)
from brain.mq5_ts_strict_shuffle_verify import (
    verify_strict_matched_control_scalable,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config/controls/mq5-ts-arm-c-mixing-depth-v1.toml"
RESULT_NAME = "mq5-ts-arm-c-mixing-depth-v1.json"
AUTHORIZATION = (
    ROOT
    / "config/controls/"
    "mq5-ts-arm-c-mixing-depth-execution-authorization-v1.json"
)
VERIFIER = ROOT / "brain/mq5_ts_strict_shuffle_verify.py"

NARRATIVE_LABEL = "WARTHOG RUN"
NARRATIVE_BANNER = "THE MAW IS COLLAPSING. FLOOR IT."


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_config() -> dict:
    with CONFIG.open("rb") as f:
        return tomllib.load(f)


def resolve_input(data_root: Path, relative: str) -> Path:
    return (data_root / relative).resolve()


def verify_frozen_inputs(cfg: dict, data_root: Path) -> dict[str, Path]:
    inp = cfg["inputs"]
    paths = {
        "connectome": resolve_input(data_root, inp["connectome"]),
        "transmitter": resolve_input(data_root, inp["transmitter"]),
        "retina": resolve_input(data_root, inp["retina"]),
    }

    for name, path in paths.items():
        if not path.is_file():
            raise RuntimeError(f"missing frozen input {name}: {path}")
        expected = inp[f"{name}_sha256"]
        actual = sha256_file(path)
        if actual != expected:
            raise RuntimeError(
                f"frozen input hash mismatch for {name}: "
                f"{actual} != {expected}"
            )

    return paths


def protected_edge_count(
    matrix: sparse.csr_matrix,
    protected_indices: np.ndarray,
) -> int:
    protected_mask = np.zeros(matrix.shape[0], dtype=bool)
    protected_mask[np.asarray(protected_indices, dtype=np.int32)] = True
    return int(np.count_nonzero(protected_mask[matrix.indices]))


def structural_intersection_count(
    a: sparse.csr_matrix,
    b: sparse.csr_matrix,
) -> int:
    if a.shape != b.shape:
        raise ValueError("shape mismatch")
    if not np.array_equal(a.indptr, b.indptr):
        raise ValueError("row-degree structure mismatch")

    aa = sparse.csr_matrix(
        (np.ones(a.nnz, dtype=np.uint8), a.indices, a.indptr),
        shape=a.shape,
    )
    bb = sparse.csr_matrix(
        (np.ones(b.nnz, dtype=np.uint8), b.indices, b.indptr),
        shape=b.shape,
    )
    return int(aa.multiply(bb).nnz)


def eligible_overlap_fraction(
    a: sparse.csr_matrix,
    b: sparse.csr_matrix,
    *,
    protected_edges: int,
    eligible_edges: int,
) -> float:
    common_all = structural_intersection_count(a, b)
    common_eligible = common_all - int(protected_edges)

    if common_eligible < 0 or common_eligible > eligible_edges:
        raise RuntimeError(
            "eligible intersection outside valid range: "
            f"{common_eligible} / {eligible_edges}"
        )

    return float(common_eligible / eligible_edges)


def baseline_metrics(
    baseline: sparse.csr_matrix,
    candidate: sparse.csr_matrix,
    *,
    protected_edges: int,
    eligible_edges: int,
) -> dict[str, float]:
    retention = eligible_overlap_fraction(
        baseline,
        candidate,
        protected_edges=protected_edges,
        eligible_edges=eligible_edges,
    )
    changed = 1.0 - retention
    common = retention * eligible_edges
    union = (2.0 * eligible_edges) - common
    jaccard = (common / union) if union > 0 else 1.0

    return {
        "retention_fraction": float(retention),
        "changed_fraction": float(changed),
        "baseline_edge_jaccard": float(jaccard),
    }


def classify_seed_memory(
    memory_by_depth: dict[float, dict[int, float]],
    *,
    tolerance: float,
    required_seeds: list[int],
    complete: bool,
    invariants_ok: bool,
) -> str:
    if not complete or not invariants_ok:
        return "INCOMPLETE_OR_INVALID"

    one = memory_by_depth[1.0]
    two = memory_by_depth[2.0]

    if all(float(one[s]) <= tolerance for s in required_seeds):
        return "CURRENT_1X_ADEQUATE_FOR_SQ05"

    if all(float(two[s]) <= tolerance for s in required_seeds):
        return "SQ05_REQUIRES_2X_PROSPECTIVE_DEPTH"

    return "NO_ADEQUATE_DEPTH_WITHIN_TESTED_RANGE"


def assert_prefix_contract_source() -> dict[str, object]:
    import brain.mq5_ts_strict_shuffle_native as native

    source = native._NATIVE_SOURCE
    fn_source = source.split("int mq5_strict_shuffle(", 1)[-1]

    required = [
        "uint64_t rng_state = seed ^ 0xd1b54a32d192ed03ULL;",
        "while (accepted < target && attempted < max_attempts)",
        "rng_bounded(",
        "&rng_state,",
        "accepted += 1",
        "if (accepted != target) return 5;",
    ]
    missing = [x for x in required if x not in fn_source]
    if missing:
        raise RuntimeError(
            "native prefix-contract source audit failed; missing: "
            + repr(missing)
        )

    target_lines = [
        line.strip()
        for line in fn_source.splitlines()
        if "target" in line
    ]
    allowed_target_fragments = (
        "int64_t target,",
        "target < 0 || max_attempts < 0",
        "accepted < target && attempted < max_attempts",
        "accepted != target",
    )
    unexpected_target = [
        line
        for line in target_lines
        if not any(x in line for x in allowed_target_fragments)
    ]
    if unexpected_target:
        raise RuntimeError(
            "unexpected target-dependent native logic: "
            + repr(unexpected_target)
        )

    py_path = Path(native.__file__).resolve()
    return {
        "native_module": str(py_path),
        "native_module_sha256": sha256_file(py_path),
        "source_contract_checked": True,
        "target_use_restricted_to_termination": True,
    }


def assert_synthetic_determinism() -> dict[str, object]:
    rows = np.asarray(
        [0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5],
        dtype=np.int32,
    )
    cols = np.asarray(
        [1, 2, 0, 3, 1, 4, 0, 5, 2, 5, 3, 4],
        dtype=np.int32,
    )
    data = np.linspace(0.1, 1.2, len(rows), dtype=np.float32)
    graph = sparse.csr_matrix(
        (data, (rows, cols)),
        shape=(6, 6),
        dtype=np.float32,
    )
    graph.sort_indices()

    signs = np.ones(6, dtype=np.float32)
    protected = np.asarray([], dtype=np.int32)
    seed = 991337099

    a, da = build_strict_matched_control_native(
        graph,
        signs,
        protected,
        seed=seed,
        accepted_swaps_per_eligible_edge=0.5,
        max_attempt_multiplier=100,
    )
    b, db = build_strict_matched_control_native(
        graph,
        signs,
        protected,
        seed=seed,
        accepted_swaps_per_eligible_edge=0.5,
        max_attempt_multiplier=100,
    )

    if not (
        np.array_equal(a.indptr, b.indptr)
        and np.array_equal(a.indices, b.indices)
        and np.array_equal(a.data, b.data)
        and asdict(da) == asdict(db)
    ):
        raise RuntimeError("native same-seed deterministic replay failed")

    return {
        "synthetic_only": True,
        "seed_is_preregistered": False,
        "same_seed_exact_replay": True,
    }


def _load_baseline(paths: dict[str, Path]):
    baseline = sparse.load_npz(paths["connectome"]).tocsr()
    baseline.sum_duplicates()
    baseline.sort_indices()

    signs = np.load(paths["transmitter"])
    retina = np.load(paths["retina"])
    protected = np.asarray(retina["neuron_index"], dtype=np.int32)

    if baseline.shape[0] != baseline.shape[1]:
        raise RuntimeError("connectome must be square")
    if signs.shape != (baseline.shape[0],):
        raise RuntimeError("transmitter sign shape mismatch")

    return baseline, signs, protected


def _candidate_from_indices(
    baseline: sparse.csr_matrix,
    indices: np.ndarray,
) -> sparse.csr_matrix:
    result = sparse.csr_matrix(
        (
            baseline.data.copy(),
            np.asarray(indices, dtype=np.int32),
            baseline.indptr.copy(),
        ),
        shape=baseline.shape,
        dtype=baseline.dtype,
    )
    result.sort_indices()
    return result


def _save_indices(path: Path, candidate: sparse.csr_matrix) -> None:
    np.save(path, np.asarray(candidate.indices, dtype=np.int32))


def _load_indices(path: Path) -> np.ndarray:
    return np.load(path, mmap_mode="r")



def git_output(*args: str) -> str:
    p = subprocess.run(
        ["git", *args],
        cwd=str(ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if p.returncode != 0:
        raise RuntimeError(
            "git command failed: git "
            + " ".join(args)
            + "\n"
            + p.stdout
        )
    return p.stdout.strip()


def assert_execution_authorized() -> dict:
    if not AUTHORIZATION.is_file():
        raise RuntimeError(
            "result execution authorization is absent; "
            "WARTHOG RUN remains locked"
        )

    auth = json.loads(AUTHORIZATION.read_text(encoding="utf-8"))

    if auth.get("result_execution_enabled") is not True:
        raise RuntimeError("result execution is not enabled by authorization")

    mode = auth.get("execution_mode")
    if mode not in {"local", "rasputin"}:
        raise RuntimeError(f"invalid execution_mode in authorization: {mode!r}")

    if git_output("status", "--porcelain"):
        raise RuntimeError(
            "result execution requires a clean Git working tree"
        )

    import brain.mq5_ts_strict_shuffle_native as native
    native_path = Path(native.__file__).resolve()

    tracked = [
        str(Path(__file__).resolve().relative_to(ROOT)),
        str(CONFIG.relative_to(ROOT)),
        str(VERIFIER.relative_to(ROOT)),
        str(AUTHORIZATION.relative_to(ROOT)),
        str(native_path.relative_to(ROOT)),
    ]

    for rel in tracked:
        p = subprocess.run(
            ["git", "ls-files", "--error-unmatch", rel],
            cwd=str(ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )
        if p.returncode != 0:
            raise RuntimeError(
                f"result execution requires tracked file: {rel}"
            )

    current = {
        "runner_sha256": sha256_file(Path(__file__).resolve()),
        "config_sha256": sha256_file(CONFIG),
        "native_sha256": sha256_file(native_path),
        "verifier_sha256": sha256_file(VERIFIER),
    }

    for key, actual in current.items():
        expected = auth.get(key)
        if expected != actual:
            raise RuntimeError(
                f"execution authorization hash mismatch for {key}: "
                f"{actual} != {expected}"
            )

    implementation_commit = auth.get("implementation_commit")
    if not implementation_commit:
        raise RuntimeError("authorization missing implementation_commit")

    head = git_output("rev-parse", "HEAD")
    ancestry = subprocess.run(
        [
            "git",
            "merge-base",
            "--is-ancestor",
            implementation_commit,
            head,
        ],
        cwd=str(ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    if ancestry.returncode != 0:
        raise RuntimeError(
            "authorized implementation commit is not an ancestor of HEAD"
        )

    return {
        "authorization": str(AUTHORIZATION.relative_to(ROOT)),
        "authorization_sha256": sha256_file(AUTHORIZATION),
        "execution_mode": mode,
        "implementation_commit": implementation_commit,
        "execution_head": head,
        **current,
    }

def result_path() -> Path:
    data_root = Path(
        os.environ.get(
            "MOSCAQUANT_DATA_ROOT",
            str(Path.home() / "moscaquant-data"),
        )
    ).resolve()
    return data_root / "experiments" / RESULT_NAME


def preflight_only() -> dict:
    cfg = load_config()
    data_root = Path(
        os.environ.get(
            "MOSCAQUANT_DATA_ROOT",
            str(Path.home() / "moscaquant-data"),
        )
    ).resolve()
    paths = verify_frozen_inputs(cfg, data_root)
    prefix = assert_prefix_contract_source()
    synthetic = assert_synthetic_determinism()

    return {
        "status": "PREFLIGHT_PASS",
        "config_sha256": sha256_file(CONFIG),
        "input_sha256": {k: sha256_file(v) for k, v in paths.items()},
        "prefix_contract": prefix,
        "synthetic_determinism": synthetic,
        "execution_authorization_present": AUTHORIZATION.is_file(),
        "result_exists": result_path().exists(),
        "topology_build_executed": False,
        "neural_execution": False,
    }


def run_frozen() -> dict:
    authorization = assert_execution_authorized()

    if result_path().exists():
        raise RuntimeError(
            "refusing result execution because final artifact already exists: "
            f"{result_path()}"
        )

    cfg = load_config()
    data_root = Path(
        os.environ.get(
            "MOSCAQUANT_DATA_ROOT",
            str(Path.home() / "moscaquant-data"),
        )
    ).resolve()

    paths = verify_frozen_inputs(cfg, data_root)
    prefix_contract = assert_prefix_contract_source()
    baseline, signs, protected = _load_baseline(paths)

    protected_edges = protected_edge_count(baseline, protected)
    eligible_edges = int(baseline.nnz - protected_edges)
    baseline_self_edges = int(
        np.count_nonzero(np.asarray(baseline.diagonal()) != 0)
    )

    depths = [float(x) for x in cfg["design"]["depths"]]
    seeds = [int(x) for x in cfg["design"]["seeds"]]
    max_attempt_multiplier = int(cfg["backend"]["max_attempt_multiplier"])

    if depths != [0.5, 1.0, 2.0, 4.0]:
        raise RuntimeError("frozen depth grid mismatch")
    if seeds != [20264000, 20264001, 20264002]:
        raise RuntimeError("frozen seed set mismatch")

    builds = []
    failures = []
    deep_paths = {}

    print("=" * 88)
    print(NARRATIVE_LABEL)
    print(NARRATIVE_BANNER)
    print("=" * 88)
    print("STRUCTURAL ONLY:", True)
    print("NEURAL EXECUTION:", False)

    with tempfile.TemporaryDirectory(
        prefix="moscaquant-warthog-run-"
    ) as tmp:
        tmpdir = Path(tmp)

        # Build all deep references first so cross-seed comparisons remain
        # memory-conscious and deterministic.
        for seed in seeds:
            depth = 4.0
            try:
                start = time.perf_counter()
                candidate, diag = build_strict_matched_control_native(
                    baseline,
                    signs,
                    protected,
                    seed=seed,
                    accepted_swaps_per_eligible_edge=depth,
                    max_attempt_multiplier=max_attempt_multiplier,
                )
                seconds = time.perf_counter() - start

                report = verify_strict_matched_control_scalable(
                    baseline,
                    candidate,
                    signs,
                    protected,
                )
                if not all(report.values()):
                    raise RuntimeError(
                        "invariant failure: "
                        + ", ".join(k for k, v in report.items() if not v)
                    )

                item = {
                    "seed": seed,
                    "depth": depth,
                    "diagnostics": asdict(diag),
                    "invariants": report,
                    "baseline_metrics": baseline_metrics(
                        baseline,
                        candidate,
                        protected_edges=protected_edges,
                        eligible_edges=eligible_edges,
                    ),
                    "baseline_self_edge_count": baseline_self_edges,
                    "candidate_self_edge_count": int(
                        np.count_nonzero(
                            np.asarray(candidate.diagonal()) != 0
                        )
                    ),
                    "construction_wall_seconds_non_scientific": seconds,
                    "status": "COMPLETE",
                }
                builds.append(item)

                p = tmpdir / f"deep-{seed}.npy"
                _save_indices(p, candidate)
                deep_paths[seed] = p
                del candidate
                gc.collect()

            except Exception as exc:
                failures.append(
                    {"seed": seed, "depth": depth, "error": repr(exc)}
                )

        for seed in seeds:
            for depth in (0.5, 1.0, 2.0):
                try:
                    start = time.perf_counter()
                    candidate, diag = build_strict_matched_control_native(
                        baseline,
                        signs,
                        protected,
                        seed=seed,
                        accepted_swaps_per_eligible_edge=depth,
                        max_attempt_multiplier=max_attempt_multiplier,
                    )
                    seconds = time.perf_counter() - start

                    report = verify_strict_matched_control_scalable(
                        baseline,
                        candidate,
                        signs,
                        protected,
                    )
                    if not all(report.values()):
                        raise RuntimeError(
                            "invariant failure: "
                            + ", ".join(
                                k for k, v in report.items() if not v
                            )
                        )

                    item = {
                        "seed": seed,
                        "depth": depth,
                        "diagnostics": asdict(diag),
                        "invariants": report,
                        "baseline_metrics": baseline_metrics(
                            baseline,
                            candidate,
                            protected_edges=protected_edges,
                            eligible_edges=eligible_edges,
                        ),
                        "baseline_self_edge_count": baseline_self_edges,
                        "candidate_self_edge_count": int(
                            np.count_nonzero(
                                np.asarray(candidate.diagonal()) != 0
                            )
                        ),
                        "construction_wall_seconds_non_scientific": seconds,
                        "status": "COMPLETE",
                    }

                    if depth in (1.0, 2.0) and len(deep_paths) == len(seeds):
                        overlaps = {}
                        for deep_seed in seeds:
                            deep = _candidate_from_indices(
                                baseline,
                                _load_indices(deep_paths[deep_seed]),
                            )
                            overlaps[deep_seed] = eligible_overlap_fraction(
                                candidate,
                                deep,
                                protected_edges=protected_edges,
                                eligible_edges=eligible_edges,
                            )
                            del deep
                            gc.collect()

                        within = float(overlaps[seed])
                        cross = float(
                            np.mean(
                                [
                                    overlaps[s]
                                    for s in seeds
                                    if s != seed
                                ]
                            )
                        )
                        item["deep_overlap_by_seed"] = {
                            str(k): float(v)
                            for k, v in overlaps.items()
                        }
                        item["within_seed_overlap"] = within
                        item["cross_seed_overlap_mean"] = cross
                        item["seed_memory_excess"] = within - cross

                    builds.append(item)
                    del candidate
                    gc.collect()

                except Exception as exc:
                    failures.append(
                        {"seed": seed, "depth": depth, "error": repr(exc)}
                    )

        deep_pairwise = {}
        if len(deep_paths) == len(seeds):
            for i, a_seed in enumerate(seeds):
                for b_seed in seeds[i + 1:]:
                    a = _candidate_from_indices(
                        baseline,
                        _load_indices(deep_paths[a_seed]),
                    )
                    b = _candidate_from_indices(
                        baseline,
                        _load_indices(deep_paths[b_seed]),
                    )
                    deep_pairwise[f"{a_seed}:{b_seed}"] = (
                        eligible_overlap_fraction(
                            a,
                            b,
                            protected_edges=protected_edges,
                            eligible_edges=eligible_edges,
                        )
                    )
                    del a, b
                    gc.collect()

    complete = len(builds) == int(cfg["design"]["expected_build_count"])
    invariants_ok = (
        complete
        and all(all(item["invariants"].values()) for item in builds)
    )

    memory = {1.0: {}, 2.0: {}}
    for item in builds:
        d = float(item["depth"])
        if d in memory and "seed_memory_excess" in item:
            memory[d][int(item["seed"])] = float(
                item["seed_memory_excess"]
            )

    complete_for_classification = (
        complete
        and all(len(memory[d]) == len(seeds) for d in (1.0, 2.0))
    )

    classification = classify_seed_memory(
        memory,
        tolerance=float(cfg["decision"]["seed_memory_excess_tolerance"]),
        required_seeds=seeds,
        complete=complete_for_classification,
        invariants_ok=invariants_ok,
    )

    return {
        "artifact": "mq5-ts-arm-c-mixing-depth-v1",
        "narrative_label": NARRATIVE_LABEL,
        "narrative_label_scientific": False,
        "scope": "structural_null_characterization_only",
        "neural_execution": False,
        "financial_semantics": False,
        "parent_mq5_ts_result_reopened": False,
        "execution_authorization": authorization,
        "config": str(CONFIG.relative_to(ROOT)),
        "config_sha256": sha256_file(CONFIG),
        "input_sha256": {k: sha256_file(v) for k, v in paths.items()},
        "prefix_contract": prefix_contract,
        "eligible_edges": eligible_edges,
        "protected_edges": protected_edges,
        "builds": sorted(
            builds,
            key=lambda x: (int(x["seed"]), float(x["depth"])),
        ),
        "failures": failures,
        "deep_pairwise_overlap": deep_pairwise,
        "classification": classification,
    }


def write_result_atomic(payload: dict) -> Path:
    path = result_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    if path.exists():
        raise RuntimeError(
            f"refusing to overwrite existing result artifact: {path}"
        )

    raw = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode()
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_bytes(raw)
    os.replace(tmp, path)
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preflight-only", action="store_true")
    mode.add_argument("--run-frozen", action="store_true")
    args = parser.parse_args()

    if args.preflight_only:
        print(json.dumps(preflight_only(), indent=2, sort_keys=True))
        return

    payload = run_frozen()
    path = write_result_atomic(payload)

    print()
    print("=" * 88)
    print("WARTHOG RUN COMPLETE")
    print("=" * 88)
    print("classification:", payload["classification"])
    print("result:", path)
    print("result_sha256:", sha256_file(path))


if __name__ == "__main__":
    main()
