from __future__ import annotations

from pathlib import Path
import json
import subprocess

from brain.sq03b_candidate_freezer import freeze_candidate_set, sha256

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "experiments" / "sq03b_mechanistic_localization_v1.json"
FEATHER = Path.home() / "moscaquant-data" / "external" / "mq002" / "mcns_fw_edge_comp.feather"
OUTPUT = ROOT / "artifacts" / "sidequests" / "sq03b-candidate-edges-v1.json"


def git_head():
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
    ).strip()


def require_clean_worktree():
    status = subprocess.check_output(
        ["git", "status", "--porcelain"],
        cwd=ROOT,
        text=True,
    )
    if status.strip():
        raise RuntimeError(
            "Refusing to freeze SQ-03B candidate set with a dirty git worktree."
        )


def main():
    require_clean_worktree()

    cfg = json.loads(CONFIG.read_text())

    if cfg["status"] != "FROZEN_BEFORE_LOCALIZATION_EXECUTION":
        raise RuntimeError("Unexpected SQ-03B protocol status")

    max_hops = int(cfg["candidate_edge_rule"]["max_hops"])
    if max_hops != 4:
        raise RuntimeError("SQ-03B v1 expected max_hops=4")

    if OUTPUT.exists():
        raise RuntimeError(f"Refusing to overwrite candidate artifact: {OUTPUT}")

    frozen = freeze_candidate_set(
        feather_path=FEATHER,
        inputs=list(cfg["frozen_inputs"]),
        anchors=list(cfg["frozen_anchors"]),
        max_hops=max_hops,
    )

    artifact = {
        "schema": "moscaquant.sq03b_candidate_edges/v1",
        "sidequest_id": "SQ-03B",
        "title": "FIND THE DIFFERENCE",
        "classification": "FROZEN_STRUCTURAL_CANDIDATE_SET",
        "source_commit": git_head(),
        "protocol_sha256": sha256(CONFIG),
        "aligned_edges_sha256": sha256(FEATHER),
        "selection_rule": {
            "simple_paths_only": True,
            "max_hops": max_hops,
            "requires_weight_difference": True,
            "uses_localization_outcomes": False,
        },
        "frozen_inputs": cfg["frozen_inputs"],
        "frozen_anchors": cfg["frozen_anchors"],
        **frozen,
        "claim_boundary": (
            "Structural candidate-set derivation only. No SQ-03B "
            "counterfactual neural execution was performed."
        ),
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n")

    print("SQ-03B — FROZEN CANDIDATE EDGE SET")
    print("=" * 72)
    print("source commit:", artifact["source_commit"])
    print("matched edges:", artifact["matched_edge_count"])
    print("candidate edges:", artifact["candidate_edge_count"])
    print()
    for pair in artifact["pair_records"]:
        print(
            f"{pair['input']} -> {pair['anchor']}: "
            f"path_edges={pair['simple_path_edge_count']} "
            f"differing_candidates={pair['weight_differing_candidate_edge_count']}"
        )
    print()
    print("artifact:", OUTPUT)
    print("No neural dynamics were executed.")


if __name__ == "__main__":
    main()
