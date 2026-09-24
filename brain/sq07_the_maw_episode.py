from __future__ import annotations

import hashlib
import time
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path

import numpy as np
from scipy import sparse

from brain.sq05_two_betrayals_runner import (
    build_stimuli,
    duplicate_exact,
    run_episode,
    verify_frozen_dependencies as verify_sq05_frozen_dependencies,
)
from brain.sq07_the_maw_subset import build_mask_subset


ROOT = Path(__file__).resolve().parents[1]

PREREG = ROOT / "config/controls/sq07-the-maw-v1.toml"
PLAN_SOURCE = ROOT / "brain/sq07_the_maw_plan.py"
SUBSET_SOURCE = ROOT / "brain/sq07_the_maw_subset.py"
SQ05_RUNNER_SOURCE = ROOT / "brain/sq05_two_betrayals_runner.py"
SQ05_STIMULUS_SOURCE = ROOT / "brain/sq05_stimulus.py"
PHYSIOLOGY_SOURCE = ROOT / "brain/physiology_constrained_visual_transduction.py"
VISUAL_SOURCE = ROOT / "brain/visual_transduction.py"

EXPECTED_SHA256 = {
    "prereg": "0ff34f0f4c2c1315b766ecc1acf66e2e6c24650aba87ae033e5a71a2b707a84a",
    "condition_planner": "38b8e628492a475f63c40c332232b36c929512dfae8341f5b64afd1597f5411f",
    "subset_operator": "693ae8c2455361351802d0ac0c9cee4ada3bb8a25a60043264de5da14da00a5e",
    "sq05_runner": "06f640dd6c829d917bb537298f8e54048066455b92f6932dc09fe5abdef4867e",
    "sq05_stimulus": "90bf95fc7bf1baab5f8a77ba4dce9182a5ad5909ca6a3ca37a0cf10c946f623a",
    "physiology": "bf754a29155ade789349fbdfc3c579f1b2c8dbea3c63804f2cf3d858d0a2f605",
    "visual": "015cc699f49e16bb59f6e7e5f04f92cca7bfc1a3c7057e73fe54398c755831f6",
}

FRAME_COUNT = 192
DN_COUNT = 1191
LAYOUTS = ("LR", "RL")
REPLICATES = (1, 2)

RESULT_KEYS = (
    "positive_voltage",
    "spikes",
    "channel_mean_positive_voltage",
    "channel_positive_fraction",
    "channel_spike_count",
    "channel_spike_rate",
)


class Refusal(RuntimeError):
    pass


def refuse(message: str) -> None:
    raise Refusal(message)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            h.update(chunk)

    return h.hexdigest()


@lru_cache(maxsize=1)
def verify_frozen_dependencies() -> dict:
    paths = {
        "prereg": PREREG,
        "condition_planner": PLAN_SOURCE,
        "subset_operator": SUBSET_SOURCE,
        "sq05_runner": SQ05_RUNNER_SOURCE,
        "sq05_stimulus": SQ05_STIMULUS_SOURCE,
        "physiology": PHYSIOLOGY_SOURCE,
        "visual": VISUAL_SOURCE,
    }

    observed = {}

    for name, path in paths.items():
        if not path.is_file():
            refuse(f"missing frozen Tooth Four dependency {name}: {path}")

        actual = sha256_file(path)
        expected = EXPECTED_SHA256[name]

        if actual != expected:
            refuse(
                f"Tooth Four dependency SHA mismatch for {name}: "
                f"{actual} != {expected}"
            )

        observed[name] = actual

    sq05_runtime = verify_sq05_frozen_dependencies()

    return {
        "dependencies": observed,
        "sq05_runtime_dependencies": sq05_runtime,
        "fresh_runtime_each_episode": True,
        "primary_shape": [FRAME_COUNT, DN_COUNT],
    }


def expected_ordinal(mask13: str, layout: str, replicate: int) -> int:
    if not isinstance(mask13, str):
        raise ValueError("mask13 must be a string")

    if len(mask13) != 13 or set(mask13) - {"0", "1"}:
        raise ValueError("mask13 must be exactly 13 binary characters")

    if layout not in LAYOUTS:
        raise ValueError(f"unknown SQ-07 layout: {layout}")

    if replicate not in REPLICATES:
        raise ValueError(f"unknown SQ-07 replicate: {replicate}")

    layout_offset = 0 if layout == "LR" else 2

    return (
        int(mask13, 2) * 4
        + layout_offset
        + (replicate - 1)
    )


def expected_condition_id(
    mask13: str,
    layout: str,
    replicate: int,
) -> str:
    expected_ordinal(mask13, layout, replicate)
    return f"sq07:{mask13}:{layout}:r{replicate}"


def validate_condition(condition: dict) -> dict:
    required = {
        "ordinal",
        "condition_id",
        "mask13",
        "layout",
        "replicate",
    }

    if set(condition) != required:
        raise ValueError(
            "SQ-07 condition must contain exactly: "
            + ", ".join(sorted(required))
        )

    mask13 = condition["mask13"]
    layout = condition["layout"]
    replicate = condition["replicate"]

    ordinal = expected_ordinal(
        mask13,
        layout,
        replicate,
    )

    condition_id = expected_condition_id(
        mask13,
        layout,
        replicate,
    )

    if condition["ordinal"] != ordinal:
        raise ValueError(
            f"SQ-07 condition ordinal mismatch: "
            f"{condition['ordinal']} != {ordinal}"
        )

    if condition["condition_id"] != condition_id:
        raise ValueError(
            f"SQ-07 condition ID mismatch: "
            f"{condition['condition_id']} != {condition_id}"
        )

    return dict(condition)


def validate_episode_result(result: dict) -> None:
    if set(result) != set(RESULT_KEYS):
        refuse("SQ-07 episode result key-set drift")

    expected = {
        "positive_voltage": ((FRAME_COUNT, DN_COUNT), np.dtype(np.float32)),
        "spikes": ((FRAME_COUNT, DN_COUNT), np.dtype(np.uint8)),
        "channel_mean_positive_voltage": (
            (3, FRAME_COUNT),
            np.dtype(np.float64),
        ),
        "channel_positive_fraction": (
            (3, FRAME_COUNT),
            np.dtype(np.float64),
        ),
        "channel_spike_count": (
            (3, FRAME_COUNT),
            np.dtype(np.int32),
        ),
        "channel_spike_rate": (
            (3, FRAME_COUNT),
            np.dtype(np.float64),
        ),
    }

    for key, (shape, dtype) in expected.items():
        value = result[key]

        if not isinstance(value, np.ndarray):
            refuse(f"SQ-07 evidence array is not ndarray: {key}")

        if value.shape != shape:
            refuse(
                f"SQ-07 evidence shape drift for {key}: "
                f"{value.shape} != {shape}"
            )

        if value.dtype != dtype:
            refuse(
                f"SQ-07 evidence dtype drift for {key}: "
                f"{value.dtype} != {dtype}"
            )


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def execute_condition(
    baseline: sparse.csr_matrix,
    retinal_indices: np.ndarray,
    dn_indices: np.ndarray,
    channel_positions: dict[str, np.ndarray],
    condition: dict,
) -> dict:
    verify_frozen_dependencies()

    canonical = validate_condition(condition)

    if not sparse.isspmatrix_csr(baseline):
        raise TypeError("SQ-07 baseline must be CSR")

    if np.asarray(dn_indices).shape != (DN_COUNT,):
        raise ValueError("SQ-07 DN population must contain exactly 1191 indices")

    if set(channel_positions) != {"DN-C0", "DN-C1", "DN-C2"}:
        raise ValueError("SQ-07 DN channel-position keys drift")

    candidate, topology_provenance = build_mask_subset(
        baseline,
        canonical["mask13"],
    )

    stimuli = build_stimuli(
        canonical["layout"],
    )

    started_at = _utc_now()
    started_clock = time.perf_counter()

    result = run_episode(
        candidate,
        retinal_indices,
        dn_indices,
        channel_positions,
        stimuli,
    )

    elapsed = time.perf_counter() - started_clock
    completed_at = _utc_now()

    validate_episode_result(result)

    return {
        "condition": canonical,
        "topology_provenance": topology_provenance,
        "result": result,
        "timing": {
            "started_at_utc": started_at,
            "completed_at_utc": completed_at,
            "elapsed_seconds": float(elapsed),
        },
    }


def duplicate_pair_exact(first: dict, second: dict) -> bool:
    a = validate_condition(first["condition"])
    b = validate_condition(second["condition"])

    if a["mask13"] != b["mask13"]:
        return False

    if a["layout"] != b["layout"]:
        return False

    if {a["replicate"], b["replicate"]} != {1, 2}:
        return False

    validate_episode_result(first["result"])
    validate_episode_result(second["result"])

    return duplicate_exact(
        first["result"],
        second["result"],
    )
