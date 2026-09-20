from __future__ import annotations

from pathlib import Path
import argparse
import hashlib
import json
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
SMOKE = ROOT / "config" / "experiments" / "sq03a_smoke_v1.json"
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--full",
        action="store_true",
        help="Refused by v1 smoke runner; result-bearing execution is not authorized.",
    )
    args = parser.parse_args()

    if args.full:
        raise SystemExit(
            "REFUSED: result-bearing SQ-03A execution is not authorized by the "
            "engineering smoke config. Freeze a separate result-execution config first."
        )

    protocol = load_protocol(PROTOCOL)
    smoke = json.loads(SMOKE.read_text())

    if smoke["authoritative_result"] is not False:
        raise RuntimeError("Smoke config must remain non-authoritative")
    if smoke["status"] != "ENGINEERING_SMOKE_ONLY":
        raise RuntimeError("Unexpected smoke status")

    inputs, anchors = frozen_labels(protocol)
    if smoke["input_label"] not in inputs:
        raise RuntimeError("Smoke input is not part of frozen SQ-03A input panel")

    graph = build_matched_graph(FEATHER)
    assert_frozen_labels_present(graph, inputs, anchors)

    runtime_cfg = runtime_config_from_dict(smoke["runtime"])
    frame_count = int(smoke["frames"])
    stim_frame = int(smoke["stimulus"]["frame"])
    stim_amp = float(smoke["stimulus"]["amplitude"])
    input_label = smoke["input_label"]

    runs = {}
    for subject, matrix in (("MORTY", graph.male), ("LILITH", graph.female)):
        r1 = run_single(
            matrix, graph, input_label, anchors,
            frame_count, stim_frame, stim_amp, runtime_cfg,
        )
        r2 = run_single(
            matrix, graph, input_label, anchors,
            frame_count, stim_frame, stim_amp, runtime_cfg,
        )
        if not exact_replay_equal(r1, r2):
            raise RuntimeError(f"{subject} A/A deterministic replay failed")
        runs[subject] = {
            "replicate_1": r1,
            "replicate_2": r2,
            "aa_exact": True,
        }

    output = {
        "schema": "moscaquant.sq03a_smoke_result/v1",
        "sidequest_id": "SQ-03A",
        "title": "THE OTHER FLY",
        "classification": "ENGINEERING_SMOKE_ONLY_NON_AUTHORITATIVE",
        "source_commit": git_head(),
        "protocol_sha256": sha256(PROTOCOL),
        "smoke_config_sha256": sha256(SMOKE),
        "aligned_edges_sha256": sha256(FEATHER),
        "graph": {
            "node_count": len(graph.labels),
            "edge_count": graph.edge_count,
            "common_normalization_scale": graph.scale,
            "male_nnz": int(graph.male.nnz),
            "female_nnz": int(graph.female.nnz),
            "same_sparsity_pattern": True,
        },
        "frozen_inputs_resolved": inputs,
        "frozen_anchors_resolved": anchors,
        "smoke_input": input_label,
        "runs": runs,
        "acceptance": {
            "all_frozen_inputs_present": True,
            "all_frozen_anchors_present": True,
            "same_sparsity_pattern": True,
            "morty_aa_exact": True,
            "lilith_aa_exact": True,
            "authoritative_result": False,
        },
        "claim_boundary": smoke["claim_boundary"],
    }

    out = ROOT / smoke["output"]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")

    print("SQ-03A ENGINEERING SMOKE")
    print("=" * 72)
    print("nodes:", len(graph.labels))
    print("edges:", graph.edge_count)
    print("common normalization scale:", graph.scale)
    print("frozen inputs resolved:", len(inputs), "/", len(inputs))
    print("frozen anchors resolved:", len(anchors), "/", len(anchors))
    print("smoke input:", input_label)
    print("MORTY A/A exact:", runs["MORTY"]["aa_exact"])
    print("LILITH A/A exact:", runs["LILITH"]["aa_exact"])
    print("artifact:", out)
    print()
    print("NON-AUTHORITATIVE ENGINEERING SMOKE ONLY.")
    print("No SQ-03A scientific result has been executed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
