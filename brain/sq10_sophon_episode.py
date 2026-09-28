from __future__ import annotations

import numpy as np
from scipy import sparse

from brain.physiology_constrained_visual_transduction import (
    PhysiologyConstrainedVisualTransductionRuntime,
)
from brain.sq05_stimulus import (
    assert_frozen_stimulus,
)
from brain.sq05_two_betrayals_runner import (
    FRAME_COUNT,
    GRADED,
    RELAY,
    RELEASE_GAIN,
    build_stimuli,
)
from brain.sq08_three_body_episode import (
    build_body_lesion,
    resolve_body_edges,
)
from brain.sq10_sophon_instrumentation import (
    SophonPhaseRecorder,
)
from brain.sq10_sophon_plan import (
    MASKS,
    REPLICATES,
    condition_id,
)
from brain.visual_transduction import (
    VisualTransductionConfig,
)


BODY_SOURCES = np.asarray(
    [
        65084,
        128590,
        135589,
    ],
    dtype=np.int64,
)

BODY_RESPONDERS = np.asarray(
    [
        137122,
        317,
        126002,
    ],
    dtype=np.int64,
)

BODY_LABELS = (
    "A",
    "B",
    "C",
)


RESULT_KEYS = (
    "source_voltage_pre_step",
    "source_spikes_pre_step",
    "source_effective_activity_pre_synaptic",
    "responder_voltage_pre_threshold",
    "responder_fired",
    "responder_voltage_post_reset",
    "responder_spikes_post_commit",
    "body_edge_weight",
    "condition_edge_zeroed",
)


class Refusal(RuntimeError):
    pass


def refuse(message: str) -> None:
    raise Refusal(message)


def validate_condition(
    condition: dict,
) -> dict:
    required = {
        "ordinal",
        "condition_id",
        "mask",
        "replicate",
        "edge_zeroed",
    }

    if set(condition) != required:
        raise ValueError(
            "SQ-10 condition structure drift"
        )

    mask = condition["mask"]
    replicate = condition["replicate"]

    if mask not in MASKS:
        raise ValueError(
            f"invalid SQ-10 lesion mask: {mask!r}"
        )

    if replicate not in REPLICATES:
        raise ValueError(
            f"invalid SQ-10 replicate: {replicate}"
        )

    expected_id = condition_id(
        mask,
        replicate,
    )

    if (
        condition["condition_id"]
        != expected_id
    ):
        raise ValueError(
            "SQ-10 condition ID mismatch"
        )

    expected_zeroed = {
        "A": int(mask[0]),
        "B": int(mask[1]),
        "C": int(mask[2]),
    }

    if (
        condition["edge_zeroed"]
        != expected_zeroed
    ):
        raise ValueError(
            "SQ-10 lesion-coordinate drift"
        )

    return dict(condition)


def resolve_sophon_body_edges() -> tuple[
    tuple[int, int, float],
    tuple[int, int, float],
    tuple[int, int, float],
]:
    body = resolve_body_edges()

    observed_sources = np.asarray(
        [
            int(pre)
            for pre, _post, _weight
            in body
        ],
        dtype=np.int64,
    )

    observed_responders = np.asarray(
        [
            int(post)
            for _pre, post, _weight
            in body
        ],
        dtype=np.int64,
    )

    if not np.array_equal(
        observed_sources,
        BODY_SOURCES,
    ):
        refuse(
            "SQ-10 BODY source coordinate drift"
        )

    if not np.array_equal(
        observed_responders,
        BODY_RESPONDERS,
    ):
        refuse(
            "SQ-10 BODY responder coordinate drift"
        )

    return body


def condition_edge_zeroed(
    mask: str,
) -> np.ndarray:
    if mask not in MASKS:
        raise ValueError(
            f"invalid SQ-10 mask: {mask!r}"
        )

    return np.asarray(
        [int(bit) for bit in mask],
        dtype=np.uint8,
    )


def body_edge_weights() -> np.ndarray:
    body = resolve_sophon_body_edges()

    return np.asarray(
        [
            weight
            for _pre, _post, weight
            in body
        ],
        dtype=np.float32,
    )


def validate_result(
    result: dict,
) -> None:
    if set(result) != set(RESULT_KEYS):
        refuse(
            "SQ-10 episode result key-set drift"
        )

    frame_shape = (
        FRAME_COUNT,
        3,
    )

    expected = {
        "source_voltage_pre_step": (
            frame_shape,
            np.dtype(np.float32),
        ),
        "source_spikes_pre_step": (
            frame_shape,
            np.dtype(np.uint8),
        ),
        "source_effective_activity_pre_synaptic": (
            frame_shape,
            np.dtype(np.float32),
        ),
        "responder_voltage_pre_threshold": (
            frame_shape,
            np.dtype(np.float32),
        ),
        "responder_fired": (
            frame_shape,
            np.dtype(np.uint8),
        ),
        "responder_voltage_post_reset": (
            frame_shape,
            np.dtype(np.float32),
        ),
        "responder_spikes_post_commit": (
            frame_shape,
            np.dtype(np.uint8),
        ),
        "body_edge_weight": (
            (3,),
            np.dtype(np.float32),
        ),
        "condition_edge_zeroed": (
            (3,),
            np.dtype(np.uint8),
        ),
    }

    for key, (
        expected_shape,
        expected_dtype,
    ) in expected.items():
        value = result[key]

        if not isinstance(
            value,
            np.ndarray,
        ):
            refuse(
                f"SQ-10 result is not "
                f"ndarray: {key}"
            )

        if (
            value.shape
            != expected_shape
        ):
            refuse(
                f"SQ-10 shape drift {key}: "
                f"{value.shape} != "
                f"{expected_shape}"
            )

        if (
            value.dtype
            != expected_dtype
        ):
            refuse(
                f"SQ-10 dtype drift {key}: "
                f"{value.dtype} != "
                f"{expected_dtype}"
            )

        if (
            np.issubdtype(
                value.dtype,
                np.floating,
            )
            and not np.all(
                np.isfinite(value)
            )
        ):
            refuse(
                f"SQ-10 non-finite "
                f"result: {key}"
            )


def run_sophon_episode(
    *,
    connectome: sparse.csr_matrix,
    retinal_indices: np.ndarray,
    stimuli: tuple[np.ndarray, ...],
    mask: str,
) -> dict[str, np.ndarray]:
    if len(stimuli) != FRAME_COUNT:
        raise ValueError(
            "SQ-10 episode must contain "
            "exactly 192 frames"
        )

    zeroed = condition_edge_zeroed(
        mask
    )

    weights = body_edge_weights()

    recorder = SophonPhaseRecorder(
        source_indices=BODY_SOURCES,
        responder_indices=BODY_RESPONDERS,
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
            synaptic_modifier=recorder,
        )
    )

    for stimulus in stimuli:
        recorder.before_step(
            runtime,
            stimulus,
        )

        runtime.step(
            stimulus
        )

        recorder.after_step(
            runtime
        )

    result = recorder.arrays()

    result["body_edge_weight"] = (
        weights.copy()
    )

    result["condition_edge_zeroed"] = (
        zeroed.copy()
    )

    validate_result(result)

    return result


def execute_condition(
    *,
    baseline: sparse.csr_matrix,
    retinal_indices: np.ndarray,
    condition: dict,
) -> dict:
    canonical = validate_condition(
        condition
    )

    if not sparse.isspmatrix_csr(
        baseline
    ):
        raise TypeError(
            "SQ-10 baseline must be CSR"
        )

    candidate, topology_provenance = (
        build_body_lesion(
            baseline,
            canonical["mask"],
        )
    )

    #
    # SOPHON inherits the frozen SQ-08 RL
    # stimulus exactly.
    #
    stimuli = build_stimuli("RL")

    assert_frozen_stimulus()

    result = run_sophon_episode(
        connectome=candidate,
        retinal_indices=retinal_indices,
        stimuli=stimuli,
        mask=canonical["mask"],
    )

    return {
        "condition": canonical,
        "topology_provenance":
            topology_provenance,
        "result": result,
        "execution_authorized_here": False,
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

    validate_result(
        first["result"]
    )

    validate_result(
        second["result"]
    )

    return all(
        np.array_equal(
            first["result"][key],
            second["result"][key],
        )
        for key in RESULT_KEYS
    )
