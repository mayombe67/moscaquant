from __future__ import annotations

from pathlib import Path
import hashlib
import json
import math
import subprocess

from brain.sq03a_matched_runtime import (
    assert_frozen_labels_present,
    build_matched_graph,
    exact_replay_equal,
    frozen_labels,
    load_protocol,
    run_single,
    runtime_config_from_dict,
)

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "config" / "experiments" / "sq03a_other_fly_v1.json"
EXECUTION = ROOT / "config" / "experiments" / "sq03a_result_execution_v1.json"
SMOKE_ARTIFACT = ROOT / "artifacts" / "sidequests" / "sq03a-other-fly-smoke-v1.json"
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


def require_clean_worktree() -> None:
    proc = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    if proc.stdout.strip():
        raise RuntimeError(
            "Refusing authoritative SQ-03A execution with a dirty git worktree. "
            "Commit the frozen protocol/config/runner/tests first."
        )


def require_smoke() -> dict:
    if not SMOKE_ARTIFACT.exists():
        raise RuntimeError("Required SQ-03A engineering smoke artifact is missing")

    smoke = json.loads(SMOKE_ARTIFACT.read_text())
    acc = smoke.get("acceptance", {})

    required = (
        acc.get("all_frozen_inputs_present") is True
        and acc.get("all_frozen_anchors_present") is True
        and acc.get("same_sparsity_pattern") is True
        and acc.get("morty_aa_exact") is True
        and acc.get("lilith_aa_exact") is True
        and acc.get("authoritative_result") is False
    )
    if not required:
        raise RuntimeError("SQ-03A engineering smoke acceptance did not pass")

    return smoke


def first_positive_delta(morty, lilith):
    if morty is None and lilith is None:
        return None
    if morty is None or lilith is None:
        return "one_subject_only"
    return int(morty) - int(lilith)


def rank_order(metrics: dict, anchors: list[str]) -> list[str]:
    return sorted(
        anchors,
        key=lambda label: (
            -float(metrics[label]["peak_voltage"]),
            label,
        ),
    )


def euclidean(xs, ys) -> float:
    return float(math.sqrt(sum((float(a) - float(b)) ** 2 for a, b in zip(xs, ys))))


def main() -> int:
    protocol = load_protocol(PROTOCOL)
    execution = json.loads(EXECUTION.read_text())

    if execution["status"] != "FROZEN_BEFORE_RESULT_EXECUTION":
        raise RuntimeError("Unexpected SQ-03A result-execution status")
    if execution["authoritative_result"] is not True:
        raise RuntimeError("Result config is not marked authoritative")

    if execution.get("requires_clean_git_worktree", True):
        require_clean_worktree()

    smoke = require_smoke()

    frozen_inputs, frozen_anchors = frozen_labels(protocol)

    if execution["input_labels"] != frozen_inputs:
        raise RuntimeError("Execution input panel differs from frozen protocol")
    if execution["anchor_labels"] != frozen_anchors:
        raise RuntimeError("Execution anchors differ from frozen protocol")

    graph = build_matched_graph(FEATHER)
    assert_frozen_labels_present(graph, frozen_inputs, frozen_anchors)

    if graph.edge_count != smoke["graph"]["edge_count"]:
        raise RuntimeError("Matched graph edge count differs from accepted smoke")
    if len(graph.labels) != smoke["graph"]["node_count"]:
        raise RuntimeError("Matched graph node count differs from accepted smoke")
    if graph.scale != smoke["graph"]["common_normalization_scale"]:
        raise RuntimeError("Common graph normalization differs from accepted smoke")

    runtime_cfg = runtime_config_from_dict(execution["runtime"])
    frames = int(execution["frames"])
    stim_frame = int(execution["stimulus"]["frame"])
    stim_amp = float(execution["stimulus"]["amplitude"])

    if int(execution["stimulus"]["duration_frames"]) != 1:
        raise RuntimeError("v1 runner supports the frozen one-frame pulse only")

    runs = {"MORTY": {}, "LILITH": {}}

    for subject, matrix in (("MORTY", graph.male), ("LILITH", graph.female)):
        for input_label in frozen_inputs:
            rep1 = run_single(
                matrix=matrix,
                graph=graph,
                input_label=input_label,
                anchor_labels=frozen_anchors,
                frames=frames,
                stimulus_frame=stim_frame,
                stimulus_amplitude=stim_amp,
                runtime_cfg=runtime_cfg,
            )
            rep2 = run_single(
                matrix=matrix,
                graph=graph,
                input_label=input_label,
                anchor_labels=frozen_anchors,
                frames=frames,
                stimulus_frame=stim_frame,
                stimulus_amplitude=stim_amp,
                runtime_cfg=runtime_cfg,
            )

            if not exact_replay_equal(rep1, rep2):
                raise RuntimeError(
                    f"{subject} A/A deterministic replay failed for {input_label}"
                )

            runs[subject][input_label] = {
                "replicate_1": rep1,
                "replicate_2": rep2,
                "aa_exact": True,
            }

    comparisons = {}

    for input_label in frozen_inputs:
        morty_metrics = runs["MORTY"][input_label]["replicate_1"]["anchor_metrics"]
        lilith_metrics = runs["LILITH"][input_label]["replicate_1"]["anchor_metrics"]

        per_anchor = {}
        morty_vector = []
        lilith_vector = []

        for anchor in frozen_anchors:
            m = morty_metrics[anchor]
            l = lilith_metrics[anchor]

            m_peak = float(m["peak_voltage"])
            l_peak = float(l["peak_voltage"])
            m_int = float(m["integrated_positive_voltage"])
            l_int = float(l["integrated_positive_voltage"])

            morty_vector.extend([m_peak, m_int])
            lilith_vector.extend([l_peak, l_int])

            per_anchor[anchor] = {
                "morty_peak_voltage": m_peak,
                "lilith_peak_voltage": l_peak,
                "morty_minus_lilith_peak_voltage": m_peak - l_peak,
                "morty_integrated_positive_voltage": m_int,
                "lilith_integrated_positive_voltage": l_int,
                "morty_minus_lilith_integrated_positive_voltage": m_int - l_int,
                "morty_first_positive_frame": m["first_positive_frame"],
                "lilith_first_positive_frame": l["first_positive_frame"],
                "morty_minus_lilith_first_positive_frame": first_positive_delta(
                    m["first_positive_frame"], l["first_positive_frame"]
                ),
            }

        m_rank = rank_order(morty_metrics, frozen_anchors)
        l_rank = rank_order(lilith_metrics, frozen_anchors)

        comparisons[input_label] = {
            "per_anchor": per_anchor,
            "response_vector_euclidean_distance": euclidean(
                morty_vector, lilith_vector
            ),
            "morty_peak_rank_order": m_rank,
            "lilith_peak_rank_order": l_rank,
            "peak_rank_order_identical": m_rank == l_rank,
        }

    artifact = {
        "schema": "moscaquant.sq03a_result/v1",
        "sidequest_id": "SQ-03A",
        "title": "THE OTHER FLY",
        "classification": "AUTHORITATIVE_RESULT_BEARING_EXECUTION",
        "source_commit": git_head(),
        "protocol_sha256": sha256(PROTOCOL),
        "execution_config_sha256": sha256(EXECUTION),
        "aligned_edges_sha256": sha256(FEATHER),
        "accepted_smoke_artifact_sha256": sha256(SMOKE_ARTIFACT),
        "graph": {
            "node_count": len(graph.labels),
            "edge_count": graph.edge_count,
            "common_normalization_scale": graph.scale,
            "male_nnz": int(graph.male.nnz),
            "female_nnz": int(graph.female.nnz),
            "same_sparsity_pattern": True,
        },
        "runtime": execution["runtime"],
        "stimulus": execution["stimulus"],
        "input_labels": frozen_inputs,
        "anchor_labels": frozen_anchors,
        "runs": runs,
        "comparisons": comparisons,
        "controls": {
            "morty_all_aa_exact": all(
                row["aa_exact"] for row in runs["MORTY"].values()
            ),
            "lilith_all_aa_exact": all(
                row["aa_exact"] for row in runs["LILITH"].values()
            ),
            "identical_runtime_parameters": True,
            "identical_stimulus_parameters": True,
            "identical_sparsity_pattern": True,
        },
        "claim_boundary": execution["claim_boundary"],
    }

    out = ROOT / execution["outputs"]["artifact"]
    if out.exists():
        raise RuntimeError(
            f"Refusing to overwrite existing authoritative result artifact: {out}"
        )

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n")

    print("SQ-03A — THE OTHER FLY")
    print("=" * 72)
    print("AUTHORITATIVE RESULT-BEARING EXECUTION COMPLETE")
    print("source commit:", artifact["source_commit"])
    print("nodes:", artifact["graph"]["node_count"])
    print("edges:", artifact["graph"]["edge_count"])
    print("inputs:", len(frozen_inputs))
    print("anchors:", len(frozen_anchors))
    print("MORTY A/A all exact:", artifact["controls"]["morty_all_aa_exact"])
    print("LILITH A/A all exact:", artifact["controls"]["lilith_all_aa_exact"])
    print()
    print("Per-input comparison summary:")
    for label in frozen_inputs:
        c = comparisons[label]
        print(
            f"  {label}: distance={c['response_vector_euclidean_distance']:.12g} "
            f"rank_same={c['peak_rank_order_identical']}"
        )
    print()
    print("artifact:", out)
    print("Interpret only under the frozen SQ-03A claim boundary.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
