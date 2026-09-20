from __future__ import annotations

from pathlib import Path
import hashlib
import json
import subprocess

import numpy as np

from brain.hybrid_runtime import HybridRuntimeConfig
from brain.sq03a_matched_runtime import build_matched_graph, run_single

ROOT = Path(__file__).resolve().parents[1]
CFG_PATH = ROOT / "config" / "experiments" / "sq03d1_scalar_verification_v1.json"
PANEL_PATH = ROOT / "artifacts" / "sidequests" / "sq03d1-verification-panel-v1.json"
SQ03A_PATH = ROOT / "artifacts" / "sidequests" / "sq03a-other-fly-result-v1.json"
SQ03B_LEDGER = ROOT / "artifacts" / "sidequests" / "sq03b-checkpoints-v1" / "results.ndjson"
SQ03D_RESULT = ROOT / "artifacts" / "sidequests" / "sq03d-reciprocity-result-v1.json"
FEATHER = Path.home() / "moscaquant-data" / "external" / "mq002" / "mcns_fw_edge_comp.feather"
OUTPUT = ROOT / "artifacts" / "sidequests" / "sq03d1-scalar-verification-result-v1.json"


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


def require_clean_worktree() -> None:
    status = subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    )
    if status.strip():
        raise RuntimeError("Refusing SQ-03D.1 scalar verification with dirty worktree")


def normalized_asymmetry(a: float, b: float) -> float:
    if a == 0.0 and b == 0.0:
        return 0.0
    return abs(a + b) / (abs(a) + abs(b))


def pair_metrics(dm: float, dl: float) -> dict:
    return {
        "delta_morty": dm,
        "delta_lilith": dl,
        "context_residual": abs(dm + dl),
        "total_effect_magnitude": abs(dm) + abs(dl),
        "normalized_asymmetry": normalized_asymmetry(dm, dl),
    }


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


def load_sq03b_index() -> dict:
    idx = {}
    with SQ03B_LEDGER.open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            idx[(row["input"], row["subject"], int(row["edge_id"]))] = row
    return idx


def baseline_metrics(sq03a: dict, subject: str, input_label: str) -> dict:
    return sq03a["runs"][subject][input_label]["replicate_1"]["anchor_metrics"]


def compare_metric(a: float, b: float, rtol: float, atol: float) -> bool:
    return bool(np.isclose(float(a), float(b), rtol=rtol, atol=atol))


def main() -> int:
    require_clean_worktree()

    if OUTPUT.exists():
        raise RuntimeError(f"Refusing to overwrite existing SQ-03D.1 result: {OUTPUT}")

    cfg = json.loads(CFG_PATH.read_text())
    panel = json.loads(PANEL_PATH.read_text())
    sq03a = json.loads(SQ03A_PATH.read_text())
    sq03d = json.loads(SQ03D_RESULT.read_text())

    if cfg["status"] != "FROZEN_BEFORE_PANEL_SELECTION":
        raise RuntimeError("Unexpected SQ-03D.1 protocol status")
    if panel["classification"] != "FROZEN_VERIFICATION_PANEL":
        raise RuntimeError("Unexpected SQ-03D.1 panel classification")

    if sha256(SQ03D_RESULT) != panel["sq03d_result_sha256"]:
        raise RuntimeError("SQ-03D result hash mismatch")
    if sha256(SQ03B_LEDGER) != panel["sq03b_ledger_sha256"]:
        raise RuntimeError("SQ-03B ledger hash mismatch")

    graph = build_matched_graph(FEATHER)
    sq03b = load_sq03b_index()

    # Reuse frozen runtime mechanics from SQ-03C/SQ-03A.
    runtime_cfg = HybridRuntimeConfig(
        dt_ms=1.0,
        tau_ms=20.0,
        threshold=1.0,
        reset_voltage=0.0,
    )
    frames = 64
    stimulus_frame = 0
    stimulus_amplitude = 0.5

    rtol = float(cfg["verification"]["batched_scalar_rtol"])
    atol = float(cfg["verification"]["batched_scalar_atol"])

    jobs = panel["upper_tail"] + panel["low_tail_controls"]

    # Baseline replay gate for every input/subject/anchor combination in panel.
    baseline_keys = sorted({
        (job["input"], subject, job["anchor"])
        for job in jobs
        for subject in ("MORTY", "LILITH")
    })

    baseline_cache = {}

    for input_label, subject, anchor in baseline_keys:
        matrix = graph.male if subject == "MORTY" else graph.female
        replay = run_single(
            matrix=matrix,
            graph=graph,
            input_label=input_label,
            anchor_labels=[anchor],
            frames=frames,
            stimulus_frame=stimulus_frame,
            stimulus_amplitude=stimulus_amplitude,
            runtime_cfg=runtime_cfg,
        )
        expected = baseline_metrics(sq03a, subject, input_label)[anchor]

        got_trace = np.asarray(replay["anchor_metrics"][anchor]["trace"], dtype=np.float32)
        exp_trace = np.asarray(expected["trace"], dtype=np.float32)
        if not np.array_equal(got_trace, exp_trace):
            raise RuntimeError(
                f"SQ-03A baseline replay mismatch: {input_label} {subject} {anchor}"
            )

        baseline_cache[(input_label, subject, anchor)] = expected

    results = []

    for n, job in enumerate(jobs, 1):
        input_label = job["input"]
        edge_id = int(job["edge_id"])
        anchor = job["anchor"]

        subject_results = {}

        for subject in ("MORTY", "LILITH"):
            key = (input_label, subject, edge_id)
            if key not in sq03b:
                raise RuntimeError(f"Frozen panel job missing from SQ-03B ledger: {key}")

            b_row = sq03b[key]

            matrix = (graph.male if subject == "MORTY" else graph.female).copy().tolil()

            pre_idx = graph.index[job["pre"]]
            post_idx = graph.index[job["post"]]

            # The authoritative SQ-03B row already contains the exact opposite-subject
            # counterfactual weight used in production.
            cf_weight = float(b_row["counterfactual_weight"])
            matrix[post_idx, pre_idx] = np.float32(cf_weight / graph.scale)
            matrix = matrix.tocsr()

            rep1 = run_single(
                matrix=matrix,
                graph=graph,
                input_label=input_label,
                anchor_labels=[anchor],
                frames=frames,
                stimulus_frame=stimulus_frame,
                stimulus_amplitude=stimulus_amplitude,
                runtime_cfg=runtime_cfg,
            )
            rep2 = run_single(
                matrix=matrix,
                graph=graph,
                input_label=input_label,
                anchor_labels=[anchor],
                frames=frames,
                stimulus_frame=stimulus_frame,
                stimulus_amplitude=stimulus_amplitude,
                runtime_cfg=runtime_cfg,
            )

            t1 = np.asarray(rep1["anchor_metrics"][anchor]["trace"], dtype=np.float32)
            t2 = np.asarray(rep2["anchor_metrics"][anchor]["trace"], dtype=np.float32)

            if not np.array_equal(t1, t2):
                raise RuntimeError(
                    f"SQ-03D.1 A/A mismatch: {input_label} {subject} "
                    f"edge={edge_id} anchor={anchor}"
                )

            base = baseline_cache[(input_label, subject, anchor)]
            scalar_delta = metric_delta(base, rep1["anchor_metrics"][anchor])
            batched_delta = b_row["anchor_results"][anchor]["delta"]

            peak_agree = compare_metric(
                scalar_delta["peak_voltage_delta"],
                batched_delta["peak_voltage_delta"],
                rtol, atol,
            )
            integrated_agree = compare_metric(
                scalar_delta["integrated_positive_voltage_delta"],
                batched_delta["integrated_positive_voltage_delta"],
                rtol, atol,
            )
            first_agree = (
                scalar_delta["first_positive_frame_delta"]
                == batched_delta["first_positive_frame_delta"]
            )

            subject_results[subject] = {
                "aa_exact": True,
                "scalar_delta": scalar_delta,
                "sq03b_batched_delta": batched_delta,
                "peak_agree_with_sq03b": peak_agree,
                "integrated_agree_with_sq03b": integrated_agree,
                "first_positive_agree_with_sq03b": first_agree,
                "all_metrics_agree_with_sq03b": (
                    peak_agree and integrated_agree and first_agree
                ),
            }

        dm_i = subject_results["MORTY"]["scalar_delta"]["integrated_positive_voltage_delta"]
        dl_i = subject_results["LILITH"]["scalar_delta"]["integrated_positive_voltage_delta"]
        dm_p = subject_results["MORTY"]["scalar_delta"]["peak_voltage_delta"]
        dl_p = subject_results["LILITH"]["scalar_delta"]["peak_voltage_delta"]

        reconstructed_integrated = pair_metrics(dm_i, dl_i)
        reconstructed_peak = pair_metrics(dm_p, dl_p)

        expected_integrated = job["integrated"]
        expected_peak = job["peak"]

        pair_agreement = {
            "integrated_context_residual": compare_metric(
                reconstructed_integrated["context_residual"],
                expected_integrated["context_residual"],
                rtol, atol,
            ),
            "integrated_total_effect_magnitude": compare_metric(
                reconstructed_integrated["total_effect_magnitude"],
                expected_integrated["total_effect_magnitude"],
                rtol, atol,
            ),
            "integrated_normalized_asymmetry": compare_metric(
                reconstructed_integrated["normalized_asymmetry"],
                expected_integrated["normalized_asymmetry"],
                rtol, atol,
            ),
            "peak_context_residual": compare_metric(
                reconstructed_peak["context_residual"],
                expected_peak["context_residual"],
                rtol, atol,
            ),
            "peak_total_effect_magnitude": compare_metric(
                reconstructed_peak["total_effect_magnitude"],
                expected_peak["total_effect_magnitude"],
                rtol, atol,
            ),
            "peak_normalized_asymmetry": compare_metric(
                reconstructed_peak["normalized_asymmetry"],
                expected_peak["normalized_asymmetry"],
                rtol, atol,
            ),
        }

        all_subject_metrics_agree = all(
            subject_results[s]["all_metrics_agree_with_sq03b"]
            for s in ("MORTY", "LILITH")
        )
        all_pair_metrics_agree = all(pair_agreement.values())
        verified = all_subject_metrics_agree and all_pair_metrics_agree

        results.append({
            "input": input_label,
            "edge_id": edge_id,
            "anchor": anchor,
            "pre": job["pre"],
            "post": job["post"],
            "panel_class": job["panel_class"],
            "subjects": subject_results,
            "scalar_reconstructed": {
                "integrated": reconstructed_integrated,
                "peak": reconstructed_peak,
            },
            "sq03d_expected": {
                "integrated": expected_integrated,
                "peak": expected_peak,
            },
            "pair_metric_agreement": pair_agreement,
            "verified": verified,
        })

        print(
            f"{n:2d}/{len(jobs)} {job['panel_class']:16s} "
            f"{input_label:10s} {anchor:5s} edge={edge_id:6d} "
            f"verified={verified}",
            flush=True,
        )

    upper = [r for r in results if r["panel_class"] == "UPPER_TAIL"]
    low = [r for r in results if r["panel_class"] == "LOW_TAIL_CONTROL"]

    artifact = {
        "schema": "moscaquant.sq03d1_result/v1",
        "sidequest_id": "SQ-03D.1",
        "title": "DOUBLE CHECK THE KNIFE",
        "classification": "AUTHORITATIVE_SCALAR_VERIFICATION_RESULT",
        "source_commit": git_head(),
        "protocol_sha256": sha256(CFG_PATH),
        "panel_sha256": sha256(PANEL_PATH),
        "sq03d_result_sha256": sha256(SQ03D_RESULT),
        "sq03b_ledger_sha256": sha256(SQ03B_LEDGER),
        "aligned_edges_sha256": sha256(FEATHER),
        "pair_count": len(results),
        "upper_tail_pair_count": len(upper),
        "low_tail_control_pair_count": len(low),
        "all_aa_exact": all(
            s["aa_exact"]
            for r in results
            for s in r["subjects"].values()
        ),
        "all_subject_metrics_agree_with_sq03b": all(
            s["all_metrics_agree_with_sq03b"]
            for r in results
            for s in r["subjects"].values()
        ),
        "all_pair_metrics_agree_with_sq03d": all(
            all(r["pair_metric_agreement"].values()) for r in results
        ),
        "all_pairs_verified": all(r["verified"] for r in results),
        "upper_tail_verified_count": sum(r["verified"] for r in upper),
        "low_tail_verified_count": sum(r["verified"] for r in low),
        "results": results,
        "claim_boundary": cfg["claim_boundary"],
    }

    OUTPUT.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n")

    print()
    print("=" * 72)
    print("SQ-03D.1 SCALAR VERIFICATION COMPLETE")
    print("pairs:", artifact["pair_count"])
    print("upper-tail pairs:", artifact["upper_tail_pair_count"])
    print("low-tail controls:", artifact["low_tail_control_pair_count"])
    print("all A/A exact:", artifact["all_aa_exact"])
    print(
        "all subject metrics agree with SQ-03B:",
        artifact["all_subject_metrics_agree_with_sq03b"],
    )
    print(
        "all reconstructed pair metrics agree with SQ-03D:",
        artifact["all_pair_metrics_agree_with_sq03d"],
    )
    print("all pairs verified:", artifact["all_pairs_verified"])
    print(
        "upper-tail verified:",
        f"{artifact['upper_tail_verified_count']}/{len(upper)}",
    )
    print(
        "low-tail verified:",
        f"{artifact['low_tail_verified_count']}/{len(low)}",
    )
    print("artifact:", OUTPUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
