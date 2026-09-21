from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from dataclasses import asdict
from pathlib import Path

import numpy as np
from scipy import sparse

from brain.mq5_ts_runtime import (
    CONNECTOME,
    RETINA,
    TRANSMITTER,
    build_condition_a_stimuli,
    evaluate_topology,
    frozen_edges,
    frozen_responders,
    lesion_frozen_edges,
    load_frozen_causal_artifact,
)


REQUIRED_TRACKED_FILES = (
    "brain/mq5_ts_harness.py",
    "brain/mq5_ts_metrics.py",
    "brain/mq5_ts_runtime.py",
    "brain/mq5_ts_duplicate_replay.py",
    "tests/brain/test_mq5_ts_harness.py",
    "tests/brain/test_mq5_ts_metrics.py",
    "tests/brain/test_mq5_ts_runtime.py",
    "tests/brain/test_mq5_ts_duplicate_replay.py",
)


def canonical_payload(result) -> bytes:
    payload = (
        asdict(result)
        if hasattr(result, "__dataclass_fields__")
        else result
    )

    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def payload_sha256(result) -> str:
    return hashlib.sha256(
        canonical_payload(result)
    ).hexdigest()


def exact_duplicate_report(first, second) -> dict:
    first_bytes = canonical_payload(first)
    second_bytes = canonical_payload(second)

    return {
        "exact_payload_equal":
            first_bytes == second_bytes,
        "first_sha256":
            hashlib.sha256(first_bytes).hexdigest(),
        "second_sha256":
            hashlib.sha256(second_bytes).hexdigest(),
        "first_size_bytes":
            len(first_bytes),
        "second_size_bytes":
            len(second_bytes),
    }


def git_status_porcelain() -> str:
    completed = subprocess.run(
        ["git", "status", "--porcelain"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )

    if completed.returncode != 0:
        raise RuntimeError(
            "unable to inspect git status: "
            + completed.stdout
        )

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
        raise RuntimeError(
            "unable to determine git HEAD: "
            + completed.stdout
        )

    return completed.stdout.strip()


def ensure_frozen_execution_state() -> str:
    status = git_status_porcelain()

    if status.strip():
        raise RuntimeError(
            "REAL A/D DUPLICATE REPLAY REFUSED: "
            "working tree is not clean. Commit/freeze Step 33C first."
        )

    completed = subprocess.run(
        [
            "git",
            "ls-files",
            "--error-unmatch",
            *REQUIRED_TRACKED_FILES,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )

    if completed.returncode != 0:
        raise RuntimeError(
            "REAL A/D DUPLICATE REPLAY REFUSED: "
            "required Step 33 files are not all tracked by Git."
        )

    return git_head()


def _load_real_inputs():
    original = sparse.load_npz(
        CONNECTOME
    ).tocsr()

    retina = np.load(
        RETINA
    )

    retinal_indices = np.asarray(
        retina["neuron_index"],
        dtype=np.int32,
    )

    transmitter_sign = np.load(
        TRANSMITTER
    )

    causal = load_frozen_causal_artifact()

    responders = frozen_responders(
        causal
    )

    weighted_edges = frozen_edges(
        causal
    )

    edge_pairs = [
        (
            int(pre),
            int(post),
        )
        for pre, post, _
        in weighted_edges
    ]

    stimuli = build_condition_a_stimuli()

    return {
        "original":
            original,
        "retinal_indices":
            retinal_indices,
        "transmitter_sign":
            transmitter_sign,
        "responders":
            responders,
        "weighted_edges":
            weighted_edges,
        "edge_pairs":
            edge_pairs,
        "stimuli":
            stimuli,
    }


def run_real_duplicate_replays() -> dict:
    freeze_commit = ensure_frozen_execution_state()

    inputs = _load_real_inputs()

    original = inputs[
        "original"
    ]

    lesioned = lesion_frozen_edges(
        original,
        inputs[
            "weighted_edges"
        ],
    )

    kwargs = {
        "retinal_indices":
            inputs[
                "retinal_indices"
            ],
        "responder_indices":
            inputs[
                "responders"
            ],
        "causal_edges":
            inputs[
                "edge_pairs"
            ],
        "stimuli":
            inputs[
                "stimuli"
            ],
    }

    print("running Arm A duplicate replay 1/2...")
    a1 = evaluate_topology(
        original,
        **kwargs,
    )

    print("running Arm A duplicate replay 2/2...")
    a2 = evaluate_topology(
        original,
        **kwargs,
    )

    print("running Arm D duplicate replay 1/2...")
    d1 = evaluate_topology(
        lesioned,
        **kwargs,
    )

    print("running Arm D duplicate replay 2/2...")
    d2 = evaluate_topology(
        lesioned,
        **kwargs,
    )

    a_report = exact_duplicate_report(
        a1,
        a2,
    )

    d_report = exact_duplicate_report(
        d1,
        d2,
    )

    if not a_report[
        "exact_payload_equal"
    ]:
        raise RuntimeError(
            "Arm A duplicate replay mismatch"
        )

    if not d_report[
        "exact_payload_equal"
    ]:
        raise RuntimeError(
            "Arm D duplicate replay mismatch"
        )

    return {
        "status":
            "A_D_DUPLICATE_REPLAY_PASS",
        "freeze_commit":
            freeze_commit,
        "arm_A":
            a_report,
        "arm_D":
            d_report,
        "arm_A_responder_identity":
            a1.responder_identity,
        "arm_D_responder_identity":
            d1.responder_identity,
        "arm_A_first_positive_onsets":
            a1.first_positive_onsets,
        "arm_D_first_positive_onsets":
            d1.first_positive_onsets,
        "arm_A_causal_edge_survival":
            a1.causal_edge_survival,
        "arm_D_causal_edge_survival":
            d1.causal_edge_survival,
        "financial_semantics_used":
            False,
        "randomized_arm_executed":
            False,
        "result_bearing_B_seed_executed":
            False,
        "result_bearing_C_seed_executed":
            False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--run-real-after-freeze",
        action="store_true",
        help=(
            "run deterministic Arm A and Arm D duplicate replays; "
            "requires a clean Git working tree with all Step 33 files tracked"
        ),
    )

    args = parser.parse_args()

    if not args.run_real_after_freeze:
        parser.error(
            "only --run-real-after-freeze is supported"
        )

    result = run_real_duplicate_replays()

    print()
    print(
        json.dumps(
            result,
            indent=2,
            sort_keys=True,
        )
    )
    print()
    print("=" * 88)
    print("MQ-5.TS A/D DUPLICATE REPLAY PASSED")
    print("=" * 88)
    print("NO ARM B SEED EXECUTED")
    print("NO ARM C SEED EXECUTED")
    print("NO RANDOMIZED NULL RESULT EXECUTED")
    print("NO RESULT ARTIFACT WRITTEN")


if __name__ == "__main__":
    main()
