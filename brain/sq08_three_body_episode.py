from __future__ import annotations

import hashlib
import time
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path

import numpy as np
from scipy import sparse

from brain.physiology_constrained_visual_transduction import (
    PhysiologyConstrainedVisualTransductionRuntime,
)
from brain.sq05_stimulus import assert_frozen_stimulus
from brain.sq05_two_betrayals_runner import (
    ASSIGNED_DN_COUNT,
    CHANNELS,
    FRAME_COUNT,
    GRADED,
    RELAY,
    RELEASE_GAIN,
    build_stimuli,
)
from brain.sq07_the_maw_subset import (
    resolve_registry_edges,
    verify_exact_mask_subset,
)
from brain.mq3_2_causal_intervention import zero_edges
from brain.sq08_three_body_readout import (
    BODY_RESPONDERS,
    FRONTIER_INDICES,
    capture_mechanistic_state,
)
from brain.sq08_three_body_plan import (
    MASKS,
    REPLICATES,
    condition_id,
)
from brain.visual_transduction import VisualTransductionConfig


ROOT = Path(__file__).resolve().parents[1]

SQ05_RUNNER = ROOT / "brain/sq05_two_betrayals_runner.py"
SQ07_SUBSET = ROOT / "brain/sq07_the_maw_subset.py"
SQ08_READOUT = ROOT / "brain/sq08_three_body_readout.py"
SQ08_PLAN = ROOT / "brain/sq08_three_body_plan.py"

FRAME_SHAPE = (FRAME_COUNT, ASSIGNED_DN_COUNT)

BODY_EDGE_INDICES = (10, 11, 12)

RESULT_KEYS = (
    "positive_voltage",
    "spikes",
    "body_responder_voltage",
    "body_responder_spikes",
    "frontier_voltage",
    "frontier_spikes",
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
        for chunk in iter(
            lambda: handle.read(8 * 1024 * 1024),
            b"",
        ):
            h.update(chunk)

    return h.hexdigest()


def _utc_now() -> str:
    return (
        datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z")
    )


@lru_cache(maxsize=1)
def resolve_body_edges() -> tuple[
    tuple[int, int, float],
    tuple[int, int, float],
    tuple[int, int, float],
]:
    edges = resolve_registry_edges()

    if len(edges) != 13:
        refuse("SQ-08 inherited edge universe drift")

    body = tuple(
        edges[index]
        for index in BODY_EDGE_INDICES
    )

    expected_pairs = (
        (65084, 137122),
        (128590, 317),
        (135589, 126002),
    )

    observed_pairs = tuple(
        (int(pre), int(post))
        for pre, post, _weight in body
    )

    if observed_pairs != expected_pairs:
        refuse(
            "SQ-08 BODY edge identity drift: "
            f"{observed_pairs}"
        )

    return body


def validate_mask(mask: str) -> None:
    if mask not in MASKS:
        raise ValueError(
            f"invalid SQ-08 lesion mask: {mask!r}"
        )


def selected_body_edges(
    mask: str,
) -> tuple[tuple[int, int, float], ...]:
    """
    SQ-08 inherits SQ-07 lesion-mask semantics:

        0 = frozen BODY edge retained
        1 = frozen BODY edge zeroed
    """
    validate_mask(mask)

    body_edges = resolve_body_edges()

    return tuple(
        edge
        for bit, edge in zip(mask, body_edges)
        if bit == "1"
    )


def build_body_lesion(
    baseline: sparse.csr_matrix,
    mask: str,
) -> tuple[sparse.csr_matrix, dict]:
    validate_mask(mask)

    selected = selected_body_edges(mask)

    candidate = zero_edges(
        baseline,
        selected,
    )

    verify_exact_mask_subset(
        baseline=baseline,
        candidate=candidate,
        selected_edges=selected,
    )

    selected_indices = [
        BODY_EDGE_INDICES[i]
        for i, bit in enumerate(mask)
        if bit == "1"
    ]

    return candidate, {
        "artifact": (
            "sq08-three-body-lesion-subset-v1"
        ),
        "mask": mask,
        "mask_semantics": (
            "0=retained,1=zeroed"
        ),
        "selected_edge_count": len(selected),
        "selected_edge_indices": selected_indices,
        "selected_edge_ids": [
            f"E{i:02d}"
            for i in selected_indices
        ],
        "body_edge_order": [
            "E10",
            "E11",
            "E12",
        ],
        "neural_execution_authorized_here": False,
        "result_interpretation_authorized_here": False,
    }


def validate_condition(condition: dict) -> dict:
    required = {
        "ordinal",
        "condition_id",
        "mask",
        "replicate",
        "edge_zeroed",
    }

    if set(condition) != required:
        raise ValueError(
            "SQ-08 condition structure drift"
        )

    mask = condition["mask"]
    replicate = condition["replicate"]

    validate_mask(mask)

    if replicate not in REPLICATES:
        raise ValueError(
            f"invalid SQ-08 replicate: {replicate}"
        )

    expected_id = condition_id(
        mask,
        replicate,
    )

    if condition["condition_id"] != expected_id:
        raise ValueError(
            "SQ-08 condition ID mismatch"
        )

    expected_edge_zeroed = {
        "A": int(mask[0]),
        "B": int(mask[1]),
        "C": int(mask[2]),
    }

    if (
        condition["edge_zeroed"]
        != expected_edge_zeroed
    ):
        raise ValueError(
            "SQ-08 lesion-coordinate drift"
        )

    return dict(condition)


def validate_result(result: dict) -> None:
    if set(result) != set(RESULT_KEYS):
        refuse(
            "SQ-08 episode result key-set drift"
        )

    expected = {
        "positive_voltage": (
            (FRAME_COUNT, ASSIGNED_DN_COUNT),
            np.dtype(np.float32),
        ),
        "spikes": (
            (FRAME_COUNT, ASSIGNED_DN_COUNT),
            np.dtype(np.uint8),
        ),
        "body_responder_voltage": (
            (FRAME_COUNT, 3),
            np.dtype(np.float32),
        ),
        "body_responder_spikes": (
            (FRAME_COUNT, 3),
            np.dtype(np.uint8),
        ),
        "frontier_voltage": (
            (FRAME_COUNT, 18),
            np.dtype(np.float32),
        ),
        "frontier_spikes": (
            (FRAME_COUNT, 18),
            np.dtype(np.uint8),
        ),
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
            refuse(
                f"SQ-08 evidence is not ndarray: {key}"
            )

        if value.shape != shape:
            refuse(
                f"SQ-08 shape drift {key}: "
                f"{value.shape} != {shape}"
            )

        if value.dtype != dtype:
            refuse(
                f"SQ-08 dtype drift {key}: "
                f"{value.dtype} != {dtype}"
            )


def run_episode_with_mechanistic_readout(
    *,
    connectome: sparse.csr_matrix,
    retinal_indices: np.ndarray,
    dn_indices: np.ndarray,
    channel_positions: dict[str, np.ndarray],
    stimuli: tuple[np.ndarray, ...],
) -> dict[str, np.ndarray]:
    if len(stimuli) != FRAME_COUNT:
        raise ValueError(
            "SQ-08 episode must contain exactly 192 frames"
        )

    if np.asarray(dn_indices).shape != (
        ASSIGNED_DN_COUNT,
    ):
        raise ValueError(
            "SQ-08 DN population must contain "
            "exactly 1191 indices"
        )

    if set(channel_positions) != set(CHANNELS):
        raise ValueError(
            "SQ-08 DN channel-position keys drift"
        )

    runtime = (
        PhysiologyConstrainedVisualTransductionRuntime(
            connectome=connectome.tocsr(
                copy=False
            ),
            retinal_indices=np.asarray(
                retinal_indices,
                dtype=np.int32,
            ),
            relay_artifact=RELAY,
            graded_artifact=GRADED,
            config=VisualTransductionConfig(
                release_gain=RELEASE_GAIN
            ),
        )
    )

    positive = np.empty(
        (FRAME_COUNT, ASSIGNED_DN_COUNT),
        dtype=np.float32,
    )

    spikes = np.empty(
        (FRAME_COUNT, ASSIGNED_DN_COUNT),
        dtype=np.uint8,
    )

    body_voltage = np.empty(
        (FRAME_COUNT, 3),
        dtype=np.float32,
    )

    body_spikes = np.empty(
        (FRAME_COUNT, 3),
        dtype=np.uint8,
    )

    frontier_voltage = np.empty(
        (FRAME_COUNT, 18),
        dtype=np.float32,
    )

    frontier_spikes = np.empty(
        (FRAME_COUNT, 18),
        dtype=np.uint8,
    )

    channel_mean = np.empty(
        (3, FRAME_COUNT),
        dtype=np.float64,
    )

    channel_fraction = np.empty(
        (3, FRAME_COUNT),
        dtype=np.float64,
    )

    channel_spike_count = np.empty(
        (3, FRAME_COUNT),
        dtype=np.int32,
    )

    channel_spike_rate = np.empty(
        (3, FRAME_COUNT),
        dtype=np.float64,
    )

    for frame, stimulus in enumerate(stimuli):
        runtime.step(stimulus)

        dn_voltage = np.asarray(
            runtime.voltage[dn_indices],
            dtype=np.float32,
        )

        local_positive = np.maximum(
            dn_voltage,
            0.0,
        )

        local_spikes = np.asarray(
            runtime.spikes[dn_indices] > 0,
            dtype=np.uint8,
        )

        capture = capture_mechanistic_state(
            voltage=runtime.voltage,
            spikes=runtime.spikes,
        )

        positive[frame] = local_positive
        spikes[frame] = local_spikes

        body_voltage[frame] = capture[
            "body_responder_voltage"
        ]

        body_spikes[frame] = capture[
            "body_responder_spikes"
        ]

        frontier_voltage[frame] = capture[
            "frontier_voltage"
        ]

        frontier_spikes[frame] = capture[
            "frontier_spikes"
        ]

        for channel_index, channel in enumerate(
            CHANNELS
        ):
            pos = channel_positions[channel]

            pv = local_positive[pos]
            sp = local_spikes[pos]

            channel_mean[
                channel_index,
                frame,
            ] = float(pv.mean())

            channel_fraction[
                channel_index,
                frame,
            ] = float(
                np.mean(pv > 0.0)
            )

            channel_spike_count[
                channel_index,
                frame,
            ] = int(sp.sum())

            channel_spike_rate[
                channel_index,
                frame,
            ] = float(sp.mean())

    result = {
        "positive_voltage": positive,
        "spikes": spikes,
        "body_responder_voltage":
            body_voltage,
        "body_responder_spikes":
            body_spikes,
        "frontier_voltage":
            frontier_voltage,
        "frontier_spikes":
            frontier_spikes,
        "channel_mean_positive_voltage":
            channel_mean,
        "channel_positive_fraction":
            channel_fraction,
        "channel_spike_count":
            channel_spike_count,
        "channel_spike_rate":
            channel_spike_rate,
    }

    validate_result(result)

    return result


def execute_condition(
    *,
    baseline: sparse.csr_matrix,
    retinal_indices: np.ndarray,
    dn_indices: np.ndarray,
    channel_positions: dict[str, np.ndarray],
    condition: dict,
) -> dict:
    canonical = validate_condition(condition)

    if not sparse.isspmatrix_csr(baseline):
        raise TypeError(
            "SQ-08 baseline must be CSR"
        )

    candidate, topology_provenance = (
        build_body_lesion(
            baseline,
            canonical["mask"],
        )
    )

    # SQ-08 is specifically the frozen RL core.
    stimuli = build_stimuli("RL")

    assert_frozen_stimulus()

    started_at = _utc_now()
    started_clock = time.perf_counter()

    result = (
        run_episode_with_mechanistic_readout(
            connectome=candidate,
            retinal_indices=retinal_indices,
            dn_indices=dn_indices,
            channel_positions=channel_positions,
            stimuli=stimuli,
        )
    )

    elapsed = (
        time.perf_counter()
        - started_clock
    )

    completed_at = _utc_now()

    return {
        "condition": canonical,
        "topology_provenance":
            topology_provenance,
        "result": result,
        "timing": {
            "started_at_utc":
                started_at,
            "completed_at_utc":
                completed_at,
            "elapsed_seconds":
                float(elapsed),
        },
    }


def duplicate_pair_exact(
    first: dict,
    second: dict,
) -> bool:
    a = validate_condition(
        first["condition"]
    )

    b = validate_condition(
        second["condition"]
    )

    if a["mask"] != b["mask"]:
        return False

    if {
        a["replicate"],
        b["replicate"],
    } != {1, 2}:
        return False

    validate_result(first["result"])
    validate_result(second["result"])

    return all(
        np.array_equal(
            first["result"][key],
            second["result"][key],
        )
        for key in RESULT_KEYS
    )
