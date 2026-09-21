from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tomllib
from pathlib import Path

from config.paths import data_path

CONFIG = Path("config/controls/mq5-ts-topology-specificity-v1.toml")
CAUSAL = data_path("processed", "mq3-2-first-onset-causal-edges-v1.json")

EXPECTED_CAUSAL_SHA256 = (
    "23cc19a39c30e554671bdf92b904865311d2f7df4dd9ef82af1eaf66638c3a2b"
)
EXPECTED_ARM_C_FREEZE_COMMIT = "77daf9e"

EXPECTED_ARMS = {
    "A": "original_malecns",
    "B": "shuffled_mosca_v2",
    "C": "strict_degree_sign_matched_edge_swap",
    "D": "accepted_mq3_2_causal_route_lesion",
}

EXPECTED_B_SEEDS = tuple(range(20262000, 20262020))
EXPECTED_C_SEEDS = tuple(range(20263000, 20263020))
EXPECTED_FRAMES = 192
EXPECTED_RELEASE_GAIN = 0.9981738484618123
EXPECTED_RESPONDER_COUNT = 9
EXPECTED_CAUSAL_EDGE_COUNT = 13


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git_head():
    completed = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError("unable to determine git HEAD: " + completed.stdout)
    return completed.stdout.strip()


def load_protocol():
    with CONFIG.open("rb") as handle:
        return tomllib.load(handle)


def load_frozen_causal_artifact():
    actual_hash = sha256_file(CAUSAL)

    if actual_hash != EXPECTED_CAUSAL_SHA256:
        raise RuntimeError(
            "frozen causal artifact hash mismatch: "
            f"{actual_hash}"
        )

    artifact = json.loads(CAUSAL.read_text(encoding="utf-8"))

    if len(artifact.get("edges", [])) != EXPECTED_CAUSAL_EDGE_COUNT:
        raise RuntimeError("expected exactly 13 frozen causal edges")

    if len(artifact.get("targets", [])) != EXPECTED_RESPONDER_COUNT:
        raise RuntimeError("expected exactly nine frozen responders")

    return artifact


def expected_seed_plan():
    return {
        "A": [None],
        "B": list(EXPECTED_B_SEEDS),
        "C": list(EXPECTED_C_SEEDS),
        "D": [None],
    }


def preflight():
    protocol = load_protocol()
    experiment = protocol["experiment"]

    if experiment["id"] != "mq5-ts-topology-specificity-v1":
        raise RuntimeError("unexpected MQ-5.TS experiment id")

    if int(experiment["frames"]) != EXPECTED_FRAMES:
        raise RuntimeError("frozen frame count changed")

    if float(experiment["release_gain"]) != EXPECTED_RELEASE_GAIN:
        raise RuntimeError("frozen release gain changed")

    if protocol["arms"] != EXPECTED_ARMS:
        raise RuntimeError("frozen arm definitions changed")

    b = protocol["ensemble"]["B"]
    c = protocol["ensemble"]["C"]

    b_seeds = tuple(
        range(
            int(b["seed_start"]),
            int(b["seed_start"]) + int(b["seed_count"]),
        )
    )
    c_seeds = tuple(
        range(
            int(c["seed_start"]),
            int(c["seed_start"]) + int(c["seed_count"]),
        )
    )

    if b_seeds != EXPECTED_B_SEEDS:
        raise RuntimeError("Arm B frozen seed plan changed")
    if c_seeds != EXPECTED_C_SEEDS:
        raise RuntimeError("Arm C frozen seed plan changed")

    arm_c = protocol["arm_c"]
    required_arm_c = {
        "preserve_retinal_origin_edges_exactly": True,
        "preserve_exact_indegree_per_neuron": True,
        "preserve_exact_outdegree_per_neuron": True,
        "preserve_transmitter_sign": True,
        "preserve_incoming_sign_counts_per_target": True,
        "preserve_signed_row_weight_multiset": True,
        "preserve_incoming_absolute_normalization": True,
        "preserve_edge_count": True,
        "forbid_new_duplicate_edges": True,
        "forbid_new_self_edges": True,
        "accepted_swaps_per_eligible_edge": 1.0,
        "max_attempt_multiplier": 20,
        "stop_if_target_not_reached": True,
    }

    for key, expected in required_arm_c.items():
        if arm_c.get(key) != expected:
            raise RuntimeError(f"Arm C frozen field changed: {key}")

    causal = load_frozen_causal_artifact()

    responder_indices = sorted(
        int(target["model_index"])
        for target in causal["targets"]
    )

    frozen_edges = sorted(
        (
            int(edge["presynaptic"]),
            int(edge["postsynaptic"]),
        )
        for edge in causal["edges"]
    )

    return {
        "status": "PREFLIGHT_ONLY",
        "result_execution_enabled": False,
        "git_head": git_head(),
        "arm_c_freeze_commit": EXPECTED_ARM_C_FREEZE_COMMIT,
        "experiment": experiment["id"],
        "frames": EXPECTED_FRAMES,
        "release_gain": EXPECTED_RELEASE_GAIN,
        "arms": EXPECTED_ARMS,
        "seed_plan": expected_seed_plan(),
        "accepted_responder_indices": responder_indices,
        "accepted_responder_count": len(responder_indices),
        "frozen_causal_edges": [
            {"presynaptic": pre, "postsynaptic": post}
            for pre, post in frozen_edges
        ],
        "frozen_causal_edge_count": len(frozen_edges),
        "frozen_causal_artifact": str(CAUSAL),
        "frozen_causal_artifact_sha256": EXPECTED_CAUSAL_SHA256,
        "duplicate_replay_required_before_randomized_interpretation": {
            "A": True,
            "D": True,
        },
        "financial_semantics_used": False,
    }


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--preflight",
        action="store_true",
        help="validate frozen MQ-5.TS harness inputs without execution",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="reserved result-bearing mode; disabled until harness freeze",
    )

    args = parser.parse_args()

    if args.execute:
        raise RuntimeError(
            "RESULT-BEARING MQ-5.TS EXECUTION IS DISABLED. "
            "Freeze the tested execution harness before enabling it."
        )

    if not args.preflight:
        parser.error("only --preflight is currently authorized")

    report = preflight()

    print(json.dumps(report, indent=2, sort_keys=True))
    print()
    print("MQ-5.TS HARNESS PREFLIGHT PASSED")
    print("NO EXPERIMENT EXECUTED")
    print("NO RESULT-BEARING SEED EXECUTED")
    print("NO RESULT ARTIFACT WRITTEN")


if __name__ == "__main__":
    main()
