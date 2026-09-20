from __future__ import annotations

from pathlib import Path
import argparse
import hashlib
import json
import os
import subprocess
import time

import numpy as np

from brain.hybrid_runtime import HybridRuntimeConfig
from brain.sq03a_matched_runtime import build_matched_graph, run_single
from brain.sq03b_batched_engine import (
    EdgeSwap,
    run_batched_edge_swaps,
    summarize_anchor_traces,
)

ROOT = Path(__file__).resolve().parents[1]
CFG_PATH = ROOT / "config" / "experiments" / "sq03b_execution_v1.json"
PROTOCOL_PATH = ROOT / "config" / "experiments" / "sq03b_mechanistic_localization_v1.json"
CANDIDATES_PATH = ROOT / "artifacts" / "sidequests" / "sq03b-candidate-edges-v1.json"
SQ03A_PATH = ROOT / "artifacts" / "sidequests" / "sq03a-other-fly-result-v1.json"
FEATHER = Path.home() / "moscaquant-data" / "external" / "mq002" / "mcns_fw_edge_comp.feather"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git_head() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()


def git_clean() -> bool:
    status = subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    )
    return not status.strip()


def first_positive_delta(base, cf):
    if base is None and cf is None:
        return None
    if base is None or cf is None:
        return "one_only"
    return int(cf) - int(base)


def metric_delta(base: dict, cf: dict) -> dict:
    return {
        "peak_voltage_delta": float(cf["peak_voltage"]) - float(base["peak_voltage"]),
        "integrated_positive_voltage_delta": (
            float(cf["integrated_positive_voltage"])
            - float(base["integrated_positive_voltage"])
        ),
        "first_positive_frame_delta": first_positive_delta(
            base["first_positive_frame"], cf["first_positive_frame"]
        ),
    }


def fsync_append_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, sort_keys=True) + "\n")
        f.flush()
        os.fsync(f.fileno())


def atomic_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    os.replace(tmp, path)


def build_input_jobs(candidate: dict, input_label: str) -> list[dict]:
    rows = []
    for edge in candidate["candidate_edges"]:
        memberships = [
            m for m in edge["memberships"] if m["input"] == input_label
        ]
        if memberships:
            rows.append({
                "edge_id": edge["edge_id"],
                "pre": edge["pre"],
                "post": edge["post"],
                "weight_m": edge["weight_m"],
                "weight_f": edge["weight_f"],
                "anchors": sorted({m["anchor"] for m in memberships}),
            })
    rows.sort(key=lambda x: x["edge_id"])
    return rows


def load_completed_keys(results_path: Path) -> set[tuple[str, str, int]]:
    completed = set()
    if not results_path.exists():
        return completed
    with results_path.open(encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise RuntimeError(
                    f"Invalid checkpoint JSON at {results_path}:{lineno}"
                ) from exc
            completed.add((
                row["input"],
                row["subject"],
                int(row["edge_id"]),
            ))
    return completed


def baseline_metrics_from_sq03a(
    sq03a: dict, subject: str, input_label: str
) -> dict:
    return sq03a["runs"][subject][input_label]["replicate_1"]["anchor_metrics"]


def replay_baselines(cfg, candidate, sq03a, graph, runtime_cfg):
    anchors = candidate["frozen_anchors"]
    for subject, matrix in (("MORTY", graph.male), ("LILITH", graph.female)):
        for input_label in candidate["frozen_inputs"]:
            replay = run_single(
                matrix=matrix,
                graph=graph,
                input_label=input_label,
                anchor_labels=anchors,
                frames=int(cfg["frames"]),
                stimulus_frame=int(cfg["stimulus"]["frame"]),
                stimulus_amplitude=float(cfg["stimulus"]["amplitude"]),
                runtime_cfg=runtime_cfg,
            )
            expected = baseline_metrics_from_sq03a(sq03a, subject, input_label)
            for anchor in anchors:
                got_trace = np.asarray(
                    replay["anchor_metrics"][anchor]["trace"], dtype=np.float32
                )
                exp_trace = np.asarray(
                    expected[anchor]["trace"], dtype=np.float32
                )
                if not np.array_equal(got_trace, exp_trace):
                    raise RuntimeError(
                        f"SQ-03A baseline replay mismatch: "
                        f"{subject} {input_label} {anchor}"
                    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--resume",
        action="store_true",
        help="resume from the frozen checkpoint ledger",
    )
    ap.add_argument(
        "--max-batches",
        type=int,
        default=None,
        help="engineering/test escape hatch: stop cleanly after N new batches",
    )
    args = ap.parse_args()

    cfg = json.loads(CFG_PATH.read_text())
    protocol = json.loads(PROTOCOL_PATH.read_text())
    candidate = json.loads(CANDIDATES_PATH.read_text())
    sq03a = json.loads(SQ03A_PATH.read_text())

    if cfg["status"] != "FROZEN_BEFORE_COUNTERFACTUAL_EXECUTION":
        raise RuntimeError("Unexpected SQ-03B execution config status")
    if cfg["batch_size"] != 32:
        raise RuntimeError("SQ-03B v1 batch size must remain frozen at 32")
    if protocol["status"] != "FROZEN_BEFORE_LOCALIZATION_EXECUTION":
        raise RuntimeError("Unexpected SQ-03B protocol status")
    if candidate["classification"] != "FROZEN_STRUCTURAL_CANDIDATE_SET":
        raise RuntimeError("Unexpected SQ-03B candidate classification")

    checkpoint_dir = ROOT / cfg["checkpoint"]["directory"]
    manifest_path = checkpoint_dir / cfg["checkpoint"]["manifest"]
    results_path = checkpoint_dir / cfg["checkpoint"]["results_ndjson"]
    final_path = ROOT / cfg["output"]["artifact"]

    if final_path.exists():
        raise RuntimeError(
            f"Refusing to overwrite completed SQ-03B result: {final_path}"
        )

    identity = {
        "schema": "moscaquant.sq03b_checkpoint_manifest/v1",
        "source_commit": git_head(),
        "execution_config_sha256": sha256(CFG_PATH),
        "protocol_sha256": sha256(PROTOCOL_PATH),
        "candidate_artifact_sha256": sha256(CANDIDATES_PATH),
        "sq03a_artifact_sha256": sha256(SQ03A_PATH),
        "aligned_edges_sha256": sha256(FEATHER),
        "batch_size": cfg["batch_size"],
    }

    if args.resume:
        if not manifest_path.exists():
            raise RuntimeError("--resume requested but checkpoint manifest is missing")
        prior = json.loads(manifest_path.read_text())
        for key in (
            "execution_config_sha256",
            "protocol_sha256",
            "candidate_artifact_sha256",
            "sq03a_artifact_sha256",
            "aligned_edges_sha256",
            "batch_size",
        ):
            if prior.get(key) != identity.get(key):
                raise RuntimeError(
                    f"Checkpoint identity mismatch for {key}; refusing resume"
                )
        # Preserve original source commit provenance across resume.
        identity["source_commit"] = prior["source_commit"]
    else:
        if manifest_path.exists() or results_path.exists():
            raise RuntimeError(
                "Checkpoint state already exists. Use --resume or remove it "
                "only after deliberately abandoning the run."
            )
        if cfg["controls"]["require_clean_git_worktree_at_start"] and not git_clean():
            raise RuntimeError(
                "Refusing new SQ-03B run with dirty git worktree. "
                "Commit the frozen executor/config/tests first."
            )
        checkpoint_dir.mkdir(parents=True, exist_ok=True)
        atomic_json(manifest_path, {
            **identity,
            "status": "IN_PROGRESS",
            "started_unix": time.time(),
            "completed_records": 0,
            "completed_batches": 0,
        })

    graph = build_matched_graph(FEATHER)
    anchors = list(candidate["frozen_anchors"])
    anchor_indices = np.asarray([graph.index[a] for a in anchors], dtype=np.int64)

    runtime_cfg = HybridRuntimeConfig(
        dt_ms=float(cfg["runtime"]["dt_ms"]),
        tau_ms=float(cfg["runtime"]["tau_ms"]),
        threshold=float(cfg["runtime"]["threshold"]),
        reset_voltage=float(cfg["runtime"]["reset_voltage"]),
    )

    print("SQ-03B — FIND THE DIFFERENCE")
    print("=" * 72)
    print("mode:", "RESUME" if args.resume else "NEW")
    print("source commit:", identity["source_commit"])
    print("batch size:", cfg["batch_size"])
    print("candidate edges:", candidate["candidate_edge_count"])
    print("replaying SQ-03A baselines...")

    replay_baselines(cfg, candidate, sq03a, graph, runtime_cfg)
    print("SQ-03A baseline replay: PASS")

    completed = load_completed_keys(results_path)
    print("checkpoint records already complete:", len(completed))

    batch_size = int(cfg["batch_size"])
    new_batches = 0
    new_records = 0
    started = time.perf_counter()

    for input_label in candidate["frozen_inputs"]:
        jobs = build_input_jobs(candidate, input_label)

        for subject, matrix, baseline_col, cf_col in (
            ("MORTY", graph.male, "weight_m", "weight_f"),
            ("LILITH", graph.female, "weight_f", "weight_m"),
        ):
            pending = [
                j for j in jobs
                if (input_label, subject, int(j["edge_id"])) not in completed
            ]

            for start in range(0, len(pending), batch_size):
                chunk = pending[start:start + batch_size]

                swaps = [
                    EdgeSwap(
                        pre=graph.index[j["pre"]],
                        post=graph.index[j["post"]],
                        baseline_weight=float(j[baseline_col]) / graph.scale,
                        counterfactual_weight=float(j[cf_col]) / graph.scale,
                    )
                    for j in chunk
                ]

                kwargs = dict(
                    matrix=matrix,
                    swaps=swaps,
                    input_index=graph.index[input_label],
                    anchor_indices=anchor_indices,
                    frames=int(cfg["frames"]),
                    stimulus_frame=int(cfg["stimulus"]["frame"]),
                    stimulus_amplitude=float(cfg["stimulus"]["amplitude"]),
                    config=runtime_cfg,
                )

                traces_a, _ = run_batched_edge_swaps(**kwargs)
                traces_b, _ = run_batched_edge_swaps(**kwargs)

                if not np.array_equal(traces_a, traces_b):
                    raise RuntimeError(
                        f"A/A batch replay failed: "
                        f"{input_label} {subject} batch_start={start}"
                    )

                metrics = summarize_anchor_traces(traces_a, anchors)
                baseline = baseline_metrics_from_sq03a(
                    sq03a, subject, input_label
                )

                rows = []
                for job, cf_metrics in zip(chunk, metrics):
                    relevant = {}
                    any_effect = False

                    for anchor in job["anchors"]:
                        delta = metric_delta(
                            baseline[anchor],
                            cf_metrics[anchor],
                        )
                        relevant[anchor] = {
                            "baseline": {
                                "peak_voltage": float(
                                    baseline[anchor]["peak_voltage"]
                                ),
                                "integrated_positive_voltage": float(
                                    baseline[anchor]["integrated_positive_voltage"]
                                ),
                                "first_positive_frame": baseline[anchor][
                                    "first_positive_frame"
                                ],
                            },
                            "counterfactual": cf_metrics[anchor],
                            "delta": delta,
                        }

                        if (
                            delta["peak_voltage_delta"] != 0.0
                            or delta["integrated_positive_voltage_delta"] != 0.0
                            or delta["first_positive_frame_delta"] not in (0, None)
                        ):
                            any_effect = True

                    rows.append({
                        "schema": "moscaquant.sq03b_edge_counterfactual/v1",
                        "input": input_label,
                        "subject": subject,
                        "edge_id": int(job["edge_id"]),
                        "pre": job["pre"],
                        "post": job["post"],
                        "baseline_weight": float(job[baseline_col]),
                        "counterfactual_weight": float(job[cf_col]),
                        "relevant_anchors": list(job["anchors"]),
                        "anchor_results": relevant,
                        "model_level_effect_observed": any_effect,
                        "aa_exact": True,
                    })

                fsync_append_jsonl(results_path, rows)
                new_records += len(rows)
                new_batches += 1

                manifest = {
                    **identity,
                    "status": "IN_PROGRESS",
                    "completed_records": len(completed) + new_records,
                    "completed_batches_this_process": new_batches,
                    "updated_unix": time.time(),
                }
                atomic_json(manifest_path, manifest)

                elapsed = time.perf_counter() - started
                rate = new_records / elapsed if elapsed else 0.0
                print(
                    f"{input_label:10s} {subject:6s} "
                    f"+{len(rows):2d} records | "
                    f"new={new_records} | {rate:.2f} records/s",
                    flush=True,
                )

                if args.max_batches is not None and new_batches >= args.max_batches:
                    print()
                    print("Stopped cleanly at --max-batches limit.")
                    print("Resume with:")
                    print("  python -m brain.sq03b_run --resume")
                    return 0

    # Finalize by reading the durable ledger only after all jobs are present.
    rows = []
    with results_path.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))

    expected = 0
    for input_label in candidate["frozen_inputs"]:
        expected += len(build_input_jobs(candidate, input_label)) * 2

    keys = {
        (r["input"], r["subject"], int(r["edge_id"]))
        for r in rows
    }
    if len(keys) != expected or len(rows) != expected:
        raise RuntimeError(
            f"Final ledger incomplete/duplicated: "
            f"rows={len(rows)} unique={len(keys)} expected={expected}"
        )

    effect_rows = [r for r in rows if r["model_level_effect_observed"]]

    final = {
        "schema": "moscaquant.sq03b_result/v1",
        "sidequest_id": "SQ-03B",
        "title": "FIND THE DIFFERENCE",
        "classification": "AUTHORITATIVE_MODEL_LEVEL_LOCALIZATION_RESULT",
        "source_commit": identity["source_commit"],
        "execution_config_sha256": identity["execution_config_sha256"],
        "protocol_sha256": identity["protocol_sha256"],
        "candidate_artifact_sha256": identity["candidate_artifact_sha256"],
        "sq03a_artifact_sha256": identity["sq03a_artifact_sha256"],
        "aligned_edges_sha256": identity["aligned_edges_sha256"],
        "batch_size": batch_size,
        "frozen_inputs": candidate["frozen_inputs"],
        "frozen_anchors": anchors,
        "candidate_edge_count": candidate["candidate_edge_count"],
        "input_edge_subject_jobs": expected,
        "effect_observed_jobs": len(effect_rows),
        "all_aa_exact": all(r["aa_exact"] for r in rows),
        "checkpoint_ledger": str(results_path.relative_to(ROOT)),
        "claim_boundary": cfg["claim_boundary"],
    }

    atomic_json(final_path, final)
    atomic_json(manifest_path, {
        **identity,
        "status": "COMPLETE",
        "completed_records": len(rows),
        "effect_observed_jobs": len(effect_rows),
        "completed_unix": time.time(),
        "final_artifact": str(final_path.relative_to(ROOT)),
    })

    print()
    print("=" * 72)
    print("SQ-03B COUNTERFACTUAL EXECUTION COMPLETE")
    print("records:", len(rows))
    print("model-level effect rows:", len(effect_rows))
    print("all A/A exact:", final["all_aa_exact"])
    print("final artifact:", final_path)
    print("checkpoint ledger:", results_path)
    print("Interpret only under the frozen SQ-03B claim boundary.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
