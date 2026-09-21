from __future__ import annotations

import argparse
import gc
import hashlib
import json
import subprocess
import time
import tomllib
from dataclasses import asdict, is_dataclass
from pathlib import Path

import numpy as np
from scipy import sparse

from config.paths import data_path
from brain.mq5_ts_metrics import (
    compare_fingerprints,
    compare_onsets,
    compare_responder_identity,
)
from brain.mq5_ts_runtime import (
    CONNECTOME,
    RETINA,
    TRANSMITTER,
    build_arm_b_topology,
    build_arm_c_topology,
    build_condition_a_stimuli,
    evaluate_topology,
    frozen_edges,
    frozen_responders,
    lesion_frozen_edges,
    load_frozen_causal_artifact,
)
from brain.mq5_ts_strict_shuffle_verify import (
    verify_strict_matched_control_scalable,
)


CONFIG = Path("config/controls/mq5-ts-topology-specificity-v1.toml")
GATE = Path("artifacts/mq5-ts-a-d-duplicate-replay-gate-v1.json")
OUTPUT = data_path("experiments", "mq5-ts-topology-specificity-v1.json")

EXPECTED_GATE_SHA256 = "ef5cb45202327af4d82eb633db5c810ffb238a56c8e32875afb3960e0bb5674f"
EXPECTED_A_SHA256 = "03f0149a7c2bbd05869eda3cf799d2368eeab4dd493c4f0c44d8147d6ae51b9c"
EXPECTED_D_SHA256 = "d321ed9288404db49d41c45110c0b97b891869fec08212c3ed97c89f14548ed3"

EXPECTED_B_SEEDS = tuple(range(20262000, 20262020))
EXPECTED_C_SEEDS = tuple(range(20263000, 20263020))

REQUIRED_TRACKED_FILES = (
    "artifacts/mq5-ts-a-d-duplicate-replay-gate-v1.json",
    "brain/mq5_ts_harness.py",
    "brain/mq5_ts_metrics.py",
    "brain/mq5_ts_runtime.py",
    "brain/mq5_ts_duplicate_replay.py",
    "brain/mq5_ts_randomized_ensemble.py",
    "tests/brain/test_mq5_ts_harness.py",
    "tests/brain/test_mq5_ts_metrics.py",
    "tests/brain/test_mq5_ts_runtime.py",
    "tests/brain/test_mq5_ts_duplicate_replay.py",
    "tests/brain/test_mq5_ts_randomized_ensemble.py",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_payload_sha(result) -> str:
    payload = asdict(result) if is_dataclass(result) else result
    raw = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def logical_connectome_hash(matrix: sparse.csr_matrix) -> str:
    graph = matrix.tocsr(copy=True)
    graph.sum_duplicates()
    graph.sort_indices()

    digest = hashlib.sha256()
    digest.update(
        np.asarray(graph.shape, dtype=np.int64).tobytes()
    )
    digest.update(
        np.asarray(graph.indptr, dtype=np.int64).tobytes()
    )
    digest.update(
        np.asarray(graph.indices, dtype=np.int64).tobytes()
    )
    digest.update(
        np.asarray(graph.data, dtype=np.float32).tobytes()
    )
    return digest.hexdigest()


def git_status_porcelain() -> str:
    completed = subprocess.run(
        ["git", "status", "--porcelain"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError("unable to inspect git status: " + completed.stdout)
    return completed.stdout


def git_head() -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError("unable to determine git HEAD: " + completed.stdout)
    return completed.stdout.strip()


def ensure_frozen_execution_state() -> str:
    if git_status_porcelain().strip():
        raise RuntimeError(
            "RANDOMIZED MQ-5.TS EXECUTION REFUSED: working tree is not clean. "
            "Commit/freeze the randomized ensemble runner first."
        )

    completed = subprocess.run(
        ["git", "ls-files", "--error-unmatch", *REQUIRED_TRACKED_FILES],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            "RANDOMIZED MQ-5.TS EXECUTION REFUSED: "
            "required runner/gate files are not all tracked by Git."
        )

    if sha256_file(GATE) != EXPECTED_GATE_SHA256:
        raise RuntimeError("A/D duplicate replay gate hash mismatch")

    gate = json.loads(GATE.read_text(encoding="utf-8"))

    if gate.get("status") != "A_D_DUPLICATE_REPLAY_PASS":
        raise RuntimeError("A/D duplicate replay gate is not PASS")

    if not gate["arm_A"]["exact_payload_equal"]:
        raise RuntimeError("Arm A duplicate gate is not exact")
    if not gate["arm_D"]["exact_payload_equal"]:
        raise RuntimeError("Arm D duplicate gate is not exact")

    return git_head()


def load_protocol():
    with CONFIG.open("rb") as handle:
        return tomllib.load(handle)


def exact_reproduction_against_a(
    a_result,
    candidate_result,
    *,
    fingerprint_tolerance: float,
) -> dict:
    identity_cmp = compare_responder_identity(
        a_result.responder_identity["responder_indices"],
        candidate_result.responder_identity["responder_indices"],
    )

    onset_exact = (
        candidate_result.first_positive_onsets
        == a_result.first_positive_onsets
    )

    onset_cmp = compare_onsets(
        a_result.first_positive_onsets,
        candidate_result.first_positive_onsets,
    )

    fingerprint_cmp = compare_fingerprints(
        np.asarray(a_result.positive_voltage_fingerprint, dtype=np.float64),
        np.asarray(candidate_result.positive_voltage_fingerprint, dtype=np.float64),
    )

    fingerprint_match = (
        fingerprint_cmp["normalized_l2_distance"]
        <= float(fingerprint_tolerance)
    )

    exact = (
        identity_cmp["exact_responder_set"]
        and onset_exact
        and fingerprint_match
    )

    return {
        "exact_response_pattern_reproduction": bool(exact),
        "responder_set_match": bool(identity_cmp["exact_responder_set"]),
        "responder_jaccard_vs_A": float(identity_cmp["jaccard_vs_A"]),
        "onset_vector_match": bool(onset_exact),
        "onset_comparison": onset_cmp,
        "fingerprint_match": bool(fingerprint_match),
        "fingerprint_comparison": fingerprint_cmp,
    }


def classify_arm_c(
    exact_reproduction_count: int,
    completed_count: int,
    expected_count: int,
    *,
    max_for_supported: int,
    min_for_frequent: int,
) -> str:
    if completed_count != expected_count:
        return "INCOMPLETE_DUE_TO_FAILED_ARM_C_BUILDS"

    count = int(exact_reproduction_count)

    if count <= int(max_for_supported):
        return "TOPOLOGY-SPECIFIC RESPONSE PATTERN SUPPORTED"

    if count >= int(min_for_frequent):
        return "STRICT NULL FREQUENTLY REPRODUCES RESPONSE"

    return "MIXED TOPOLOGY SPECIFICITY"


def _diagnostics_dict(value):
    if value is None:
        return None
    if is_dataclass(value):
        return asdict(value)
    if hasattr(value, "__dict__"):
        return dict(value.__dict__)
    return value


def summarize_seed(
    arm: str,
    seed: int,
    candidate,
    original,
    result,
    a_result,
    *,
    fingerprint_tolerance: float,
    build_seconds: float,
    runtime_seconds: float,
    topology_report: dict,
    build_diagnostics=None,
) -> dict:
    comparison = exact_reproduction_against_a(
        a_result,
        result,
        fingerprint_tolerance=fingerprint_tolerance,
    )

    return {
        "arm": arm,
        "seed": int(seed),
        "status": "COMPLETE",
        "connectome_logical_hash": logical_connectome_hash(candidate),
        "edge_count": int(candidate.nnz),
        "build_seconds": float(build_seconds),
        "runtime_seconds": float(runtime_seconds),
        "comparison_vs_A": comparison,
        "responder_identity": result.responder_identity,
        "first_positive_onsets": result.first_positive_onsets,
        "mutual_information": result.mutual_information,
        "causal_edge_survival": result.causal_edge_survival,
        "topology_diagnostics_vs_A": topology_report,
        "build_diagnostics": _diagnostics_dict(build_diagnostics),
    }


def run_all() -> dict:
    freeze_commit = ensure_frozen_execution_state()

    if OUTPUT.exists():
        raise RuntimeError(f"refusing to overwrite existing result artifact: {OUTPUT}")

    protocol = load_protocol()
    classification = protocol["classification"]

    tolerance = float(
        classification["fingerprint_normalized_l2_match_tolerance"]
    )
    max_supported = int(
        classification["arm_c_exact_reproduction_max_for_supported"]
    )
    min_frequent = int(
        classification["arm_c_exact_reproduction_min_for_frequent"]
    )

    if not bool(
        classification["exact_reproduction_requires_all_three_matches"]
    ):
        raise RuntimeError("unexpected classification contract")

    b_cfg = protocol["ensemble"]["B"]
    c_cfg = protocol["ensemble"]["C"]

    b_seeds = tuple(
        range(
            int(b_cfg["seed_start"]),
            int(b_cfg["seed_start"]) + int(b_cfg["seed_count"]),
        )
    )
    c_seeds = tuple(
        range(
            int(c_cfg["seed_start"]),
            int(c_cfg["seed_start"]) + int(c_cfg["seed_count"]),
        )
    )

    if b_seeds != EXPECTED_B_SEEDS:
        raise RuntimeError("Arm B seed plan changed")
    if c_seeds != EXPECTED_C_SEEDS:
        raise RuntimeError("Arm C seed plan changed")

    original = sparse.load_npz(CONNECTOME).tocsr()
    original.sum_duplicates()
    original.sort_indices()

    retina = np.load(RETINA)
    retinal_indices = np.asarray(
        retina["neuron_index"],
        dtype=np.int32,
    )

    transmitter_sign = np.load(TRANSMITTER)

    causal = load_frozen_causal_artifact()
    responders = frozen_responders(causal)
    weighted_edges = frozen_edges(causal)
    edge_pairs = [
        (int(pre), int(post))
        for pre, post, _ in weighted_edges
    ]

    stimuli = build_condition_a_stimuli()

    common_kwargs = {
        "retinal_indices": retinal_indices,
        "responder_indices": responders,
        "causal_edges": edge_pairs,
        "stimuli": stimuli,
    }

    print("revalidating frozen Arm A reference...")
    a_result = evaluate_topology(
        original,
        **common_kwargs,
    )
    a_sha = canonical_payload_sha(a_result)
    if a_sha != EXPECTED_A_SHA256:
        raise RuntimeError(
            f"Arm A reference hash changed: {a_sha}"
        )

    print("revalidating frozen Arm D positive control...")
    d_topology = lesion_frozen_edges(
        original,
        weighted_edges,
    )
    d_result = evaluate_topology(
        d_topology,
        **common_kwargs,
    )
    d_sha = canonical_payload_sha(d_result)
    if d_sha != EXPECTED_D_SHA256:
        raise RuntimeError(
            f"Arm D reference hash changed: {d_sha}"
        )
    del d_topology
    gc.collect()

    results_b = []
    results_c = []

    for seed in b_seeds:
        print(f"Arm B seed {seed}...")
        started = time.perf_counter()

        try:
            candidate = build_arm_b_topology(
                original,
                transmitter_sign,
                retinal_indices,
                seed,
            )
            build_seconds = time.perf_counter() - started

            topology_report = verify_strict_matched_control_scalable(
                original,
                candidate,
                transmitter_sign,
                retinal_indices,
            )

            runtime_start = time.perf_counter()
            result = evaluate_topology(
                candidate,
                **common_kwargs,
            )
            runtime_seconds = time.perf_counter() - runtime_start

            item = summarize_seed(
                "B",
                seed,
                candidate,
                original,
                result,
                a_result,
                fingerprint_tolerance=tolerance,
                build_seconds=build_seconds,
                runtime_seconds=runtime_seconds,
                topology_report=topology_report,
            )
        except Exception as exc:
            item = {
                "arm": "B",
                "seed": int(seed),
                "status": "FAILED",
                "error_type": type(exc).__name__,
                "error": str(exc),
            }

        results_b.append(item)

        if "candidate" in locals():
            del candidate
        gc.collect()

    for seed in c_seeds:
        print(f"Arm C seed {seed}...")
        started = time.perf_counter()

        try:
            candidate, diagnostics, topology_report = build_arm_c_topology(
                original,
                transmitter_sign,
                retinal_indices,
                seed,
            )
            build_seconds = time.perf_counter() - started

            runtime_start = time.perf_counter()
            result = evaluate_topology(
                candidate,
                **common_kwargs,
            )
            runtime_seconds = time.perf_counter() - runtime_start

            item = summarize_seed(
                "C",
                seed,
                candidate,
                original,
                result,
                a_result,
                fingerprint_tolerance=tolerance,
                build_seconds=build_seconds,
                runtime_seconds=runtime_seconds,
                topology_report=topology_report,
                build_diagnostics=diagnostics,
            )
        except Exception as exc:
            item = {
                "arm": "C",
                "seed": int(seed),
                "status": "FAILED",
                "error_type": type(exc).__name__,
                "error": str(exc),
            }

        results_c.append(item)

        if "candidate" in locals():
            del candidate
        gc.collect()

    complete_b = [
        x for x in results_b
        if x["status"] == "COMPLETE"
    ]
    complete_c = [
        x for x in results_c
        if x["status"] == "COMPLETE"
    ]

    b_exact = sum(
        bool(
            x["comparison_vs_A"]["exact_response_pattern_reproduction"]
        )
        for x in complete_b
    )
    c_exact = sum(
        bool(
            x["comparison_vs_A"]["exact_response_pattern_reproduction"]
        )
        for x in complete_c
    )

    c_classification = classify_arm_c(
        c_exact,
        len(complete_c),
        len(c_seeds),
        max_for_supported=max_supported,
        min_for_frequent=min_frequent,
    )

    payload = {
        "artifact": "mq5-ts-topology-specificity-v1",
        "status": (
            "COMPLETE"
            if len(complete_b) == len(b_seeds)
            and len(complete_c) == len(c_seeds)
            else "COMPLETE_WITH_RECORDED_BUILD_FAILURES"
        ),
        "execution_commit": freeze_commit,
        "a_d_gate_sha256": EXPECTED_GATE_SHA256,
        "financial_semantics_used": False,
        "arm_A": {
            "payload_sha256": a_sha,
            "responder_identity": a_result.responder_identity,
            "first_positive_onsets": a_result.first_positive_onsets,
            "mutual_information": a_result.mutual_information,
            "causal_edge_survival": a_result.causal_edge_survival,
            "connectome_logical_hash": logical_connectome_hash(original),
        },
        "arm_D": {
            "payload_sha256": d_sha,
            "responder_identity": d_result.responder_identity,
            "first_positive_onsets": d_result.first_positive_onsets,
            "mutual_information": d_result.mutual_information,
            "causal_edge_survival": d_result.causal_edge_survival,
        },
        "arm_B": {
            "seed_count_expected": len(b_seeds),
            "seed_count_completed": len(complete_b),
            "exact_response_pattern_reproductions": int(b_exact),
            "results": results_b,
        },
        "arm_C": {
            "seed_count_expected": len(c_seeds),
            "seed_count_completed": len(complete_c),
            "exact_response_pattern_reproductions": int(c_exact),
            "classification": c_classification,
            "classification_contract": {
                "max_exact_reproductions_for_supported": max_supported,
                "min_exact_reproductions_for_frequent": min_frequent,
                "fingerprint_normalized_l2_match_tolerance": tolerance,
                "requires_all_three_matches": True,
            },
            "results": results_c,
        },
        "rules": {
            "no_seed_selection_after_results": True,
            "no_early_stopping": True,
            "failed_builds_recorded_not_replaced": True,
            "arm_b_and_c_seed_ranges_disjoint": True,
            "mutual_information_determines_classification": False,
            "causal_path_survival_determines_classification": False,
        },
    }

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT.write_text(
        json.dumps(
            payload,
            indent=2,
            sort_keys=True,
            allow_nan=False,
        ) + "\n",
        encoding="utf-8",
    )

    print()
    print("=" * 88)
    print("MQ-5.TS RANDOMIZED ENSEMBLE COMPLETE")
    print("=" * 88)
    print("Arm B completed:", len(complete_b), "/", len(b_seeds))
    print("Arm C completed:", len(complete_c), "/", len(c_seeds))
    print("Arm B exact reproductions:", b_exact)
    print("Arm C exact reproductions:", c_exact)
    print("Arm C classification:", c_classification)
    print("artifact:", OUTPUT)
    print("artifact sha256:", sha256_file(OUTPUT))

    return payload


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--run-frozen-ensemble",
        action="store_true",
        help=(
            "execute all 20 Arm B and all 20 Arm C frozen seeds; "
            "requires clean committed tree and valid A/D gate"
        ),
    )

    args = parser.parse_args()

    if not args.run_frozen_ensemble:
        parser.error("only --run-frozen-ensemble is supported")

    run_all()


if __name__ == "__main__":
    main()
