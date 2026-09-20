from __future__ import annotations

from pathlib import Path
import hashlib
import json
import subprocess

import numpy as np

from brain.hybrid_runtime import HybridRuntimeConfig
from brain.sq03a_matched_runtime import build_matched_graph, run_single

ROOT = Path(__file__).resolve().parents[1]
CFG_PATH = ROOT / "config" / "experiments" / "sq03c_scalar_verification_v1.json"
PANEL_PATH = ROOT / "artifacts" / "sidequests" / "sq03c-verification-panel-v1.json"
SQ03A_PATH = ROOT / "artifacts" / "sidequests" / "sq03a-other-fly-result-v1.json"
SQ03B_LEDGER = ROOT / "artifacts" / "sidequests" / "sq03b-checkpoints-v1" / "results.ndjson"
FEATHER = Path.home() / "moscaquant-data" / "external" / "mq002" / "mcns_fw_edge_comp.feather"
OUTPUT = ROOT / "artifacts" / "sidequests" / "sq03c-scalar-verification-result-v1.json"


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


def require_clean_worktree():
    status = subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    )
    if status.strip():
        raise RuntimeError("Refusing SQ-03C scalar verification with dirty worktree")


def metric_delta(base: dict, cf: dict) -> dict:
    if base["first_positive_frame"] is None and cf["first_positive_frame"] is None:
        first_delta = None
    elif base["first_positive_frame"] is None or cf["first_positive_frame"] is None:
        first_delta = "one_only"
    else:
        first_delta = int(cf["first_positive_frame"]) - int(base["first_positive_frame"])

    return {
        "peak_voltage_delta": float(cf["peak_voltage"]) - float(base["peak_voltage"]),
        "integrated_positive_voltage_delta": (
            float(cf["integrated_positive_voltage"])
            - float(base["integrated_positive_voltage"])
        ),
        "first_positive_frame_delta": first_delta,
    }


def load_sq03b_index():
    idx = {}
    with SQ03B_LEDGER.open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            idx[(row["input"], row["subject"], int(row["edge_id"]))] = row
    return idx


def baseline_metrics(sq03a, subject, input_label):
    return sq03a["runs"][subject][input_label]["replicate_1"]["anchor_metrics"]


def main() -> int:
    require_clean_worktree()

    if OUTPUT.exists():
        raise RuntimeError(f"Refusing to overwrite existing SQ-03C result: {OUTPUT}")

    cfg = json.loads(CFG_PATH.read_text())
    panel = json.loads(PANEL_PATH.read_text())
    sq03a = json.loads(SQ03A_PATH.read_text())

    if cfg["status"] != "FROZEN_BEFORE_PANEL_SELECTION":
        raise RuntimeError("Unexpected SQ-03C protocol status")
    if panel["classification"] != "FROZEN_VERIFICATION_PANEL":
        raise RuntimeError("Unexpected SQ-03C panel classification")

    if sha256(SQ03B_LEDGER) != cfg["parents"]["sq03b_ledger_sha256"]:
        raise RuntimeError("SQ-03B ledger hash mismatch")

    graph = build_matched_graph(FEATHER)
    sq03b = load_sq03b_index()

    rt = cfg["runtime"]
    runtime_cfg = HybridRuntimeConfig(
        dt_ms=float(rt["dt_ms"]),
        tau_ms=float(rt["tau_ms"]),
        threshold=float(rt["threshold"]),
        reset_voltage=float(rt["reset_voltage"]),
    )
    frames = int(rt["frames"])
    stimulus_frame = int(rt["stimulus_frame"])
    stimulus_amplitude = float(rt["stimulus_amplitude"])
    rtol = float(cfg["verification"]["batched_vs_scalar_rtol"])
    atol = float(cfg["verification"]["batched_vs_scalar_atol"])

    # Baseline replay gate for all eight strata.
    strata = sorted({(r["input"], r["subject"]) for r in panel["selected_jobs"]})
    for input_label, subject in strata:
        matrix = graph.male if subject == "MORTY" else graph.female
        replay = run_single(
            matrix=matrix,
            graph=graph,
            input_label=input_label,
            anchor_labels=panel["selected_jobs"][0]["sq03b_anchor_results"].keys()
                if False else panel["selected_jobs"][0]["relevant_anchors"],
            frames=frames,
            stimulus_frame=stimulus_frame,
            stimulus_amplitude=stimulus_amplitude,
            runtime_cfg=runtime_cfg,
        )
        # Re-run baseline against all frozen anchors from SQ-03A instead.
        anchors = list(sq03a["runs"][subject][input_label]["replicate_1"]["anchor_metrics"].keys())
        replay = run_single(
            matrix=matrix,
            graph=graph,
            input_label=input_label,
            anchor_labels=anchors,
            frames=frames,
            stimulus_frame=stimulus_frame,
            stimulus_amplitude=stimulus_amplitude,
            runtime_cfg=runtime_cfg,
        )
        expected = baseline_metrics(sq03a, subject, input_label)
        for anchor in anchors:
            got = np.asarray(replay["anchor_metrics"][anchor]["trace"], dtype=np.float32)
            exp = np.asarray(expected[anchor]["trace"], dtype=np.float32)
            if not np.array_equal(got, exp):
                raise RuntimeError(
                    f"SQ-03A baseline replay mismatch: {input_label} {subject} {anchor}"
                )

    results = []

    for n, job in enumerate(panel["selected_jobs"], 1):
        input_label = job["input"]
        subject = job["subject"]
        edge_id = int(job["edge_id"])
        key = (input_label, subject, edge_id)

        if key not in sq03b:
            raise RuntimeError(f"Frozen panel job missing from SQ-03B ledger: {key}")

        b_row = sq03b[key]

        matrix = (graph.male if subject == "MORTY" else graph.female).copy().tolil()
        pre = graph.index[job["pre"]]
        post = graph.index[job["post"]]
        matrix[post, pre] = np.float32(float(job["counterfactual_weight"]) / graph.scale)
        matrix = matrix.tocsr()

        anchors = list(job["relevant_anchors"])

        rep1 = run_single(
            matrix=matrix,
            graph=graph,
            input_label=input_label,
            anchor_labels=anchors,
            frames=frames,
            stimulus_frame=stimulus_frame,
            stimulus_amplitude=stimulus_amplitude,
            runtime_cfg=runtime_cfg,
        )
        rep2 = run_single(
            matrix=matrix,
            graph=graph,
            input_label=input_label,
            anchor_labels=anchors,
            frames=frames,
            stimulus_frame=stimulus_frame,
            stimulus_amplitude=stimulus_amplitude,
            runtime_cfg=runtime_cfg,
        )

        for anchor in anchors:
            t1 = np.asarray(rep1["anchor_metrics"][anchor]["trace"], dtype=np.float32)
            t2 = np.asarray(rep2["anchor_metrics"][anchor]["trace"], dtype=np.float32)
            if not np.array_equal(t1, t2):
                raise RuntimeError(
                    f"SQ-03C scalar A/A mismatch: {input_label} {subject} {edge_id} {anchor}"
                )

        base = baseline_metrics(sq03a, subject, input_label)
        anchor_results = {}
        all_agree = True

        for anchor in anchors:
            scalar_delta = metric_delta(base[anchor], rep1["anchor_metrics"][anchor])
            batched_delta = b_row["anchor_results"][anchor]["delta"]

            peak_agree = np.isclose(
                float(scalar_delta["peak_voltage_delta"]),
                float(batched_delta["peak_voltage_delta"]),
                rtol=rtol,
                atol=atol,
            )
            int_agree = np.isclose(
                float(scalar_delta["integrated_positive_voltage_delta"]),
                float(batched_delta["integrated_positive_voltage_delta"]),
                rtol=rtol,
                atol=atol,
            )
            first_agree = (
                scalar_delta["first_positive_frame_delta"]
                == batched_delta["first_positive_frame_delta"]
            )

            all_agree = all_agree and peak_agree and int_agree and first_agree

            anchor_results[anchor] = {
                "scalar_delta": scalar_delta,
                "sq03b_batched_delta": batched_delta,
                "peak_agree": bool(peak_agree),
                "integrated_agree": bool(int_agree),
                "first_positive_agree": bool(first_agree),
                "peak_abs_difference": abs(
                    float(scalar_delta["peak_voltage_delta"])
                    - float(batched_delta["peak_voltage_delta"])
                ),
                "integrated_abs_difference": abs(
                    float(scalar_delta["integrated_positive_voltage_delta"])
                    - float(batched_delta["integrated_positive_voltage_delta"])
                ),
            }

        results.append({
            "input": input_label,
            "subject": subject,
            "edge_id": edge_id,
            "pre": job["pre"],
            "post": job["post"],
            "panel_class": job["panel_class"],
            "selection_roles": job["selection_roles"],
            "relevant_anchors": anchors,
            "aa_exact": True,
            "all_metrics_agree_with_sq03b": bool(all_agree),
            "anchor_results": anchor_results,
        })

        print(
            f"{n:3d}/{panel['selected_job_count']} "
            f"{input_label:10s} {subject:6s} edge={edge_id} "
            f"{job['panel_class']:16s} agree={all_agree}",
            flush=True,
        )

    upper = [r for r in results if r["panel_class"] == "UPPER_TAIL"]
    low = [r for r in results if r["panel_class"] == "LOW_TAIL_CONTROL"]

    artifact = {
        "schema": "moscaquant.sq03c_result/v1",
        "sidequest_id": "SQ-03C",
        "title": "CHECK THE RECEIPTS",
        "classification": "AUTHORITATIVE_SCALAR_VERIFICATION_RESULT",
        "source_commit": git_head(),
        "protocol_sha256": sha256(CFG_PATH),
        "panel_sha256": sha256(PANEL_PATH),
        "sq03b_ledger_sha256": sha256(SQ03B_LEDGER),
        "aligned_edges_sha256": sha256(FEATHER),
        "selected_job_count": len(results),
        "upper_tail_job_count": len(upper),
        "low_tail_control_job_count": len(low),
        "all_aa_exact": all(r["aa_exact"] for r in results),
        "all_metrics_agree_with_sq03b": all(
            r["all_metrics_agree_with_sq03b"] for r in results
        ),
        "upper_tail_agreement_count": sum(
            r["all_metrics_agree_with_sq03b"] for r in upper
        ),
        "low_tail_agreement_count": sum(
            r["all_metrics_agree_with_sq03b"] for r in low
        ),
        "results": results,
        "claim_boundary": cfg["claim_boundary"],
    }

    OUTPUT.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n")

    print()
    print("=" * 72)
    print("SQ-03C SCALAR VERIFICATION COMPLETE")
    print("selected jobs:", artifact["selected_job_count"])
    print("upper-tail jobs:", artifact["upper_tail_job_count"])
    print("low-tail controls:", artifact["low_tail_control_job_count"])
    print("all A/A exact:", artifact["all_aa_exact"])
    print("all metrics agree with SQ-03B:", artifact["all_metrics_agree_with_sq03b"])
    print("upper-tail agreement:", f"{artifact['upper_tail_agreement_count']}/{len(upper)}")
    print("low-tail agreement:", f"{artifact['low_tail_agreement_count']}/{len(low)}")
    print("artifact:", OUTPUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
