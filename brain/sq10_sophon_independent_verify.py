from __future__ import annotations

import numpy as np


MASKS = (
    "000",
    "001",
    "010",
    "011",
    "100",
    "101",
    "110",
    "111",
)

REPLICATES = (1, 2)

FRAME_COUNT = 192
EPISODE_COUNT = 16
BODY_PAIR_COUNT = 3

SOURCES = np.asarray(
    [65084, 128590, 135589],
    dtype=np.int64,
)

RESPONDERS = np.asarray(
    [137122, 317, 126002],
    dtype=np.int64,
)


DYNAMIC_KEYS = (
    "source_voltage_pre_step",
    "source_spikes_pre_step",
    "source_effective_activity_pre_synaptic",
    "responder_voltage_pre_threshold",
    "responder_fired",
    "responder_voltage_post_reset",
    "responder_spikes_post_commit",
)

EXPECTED_KEYS = {
    "condition_ordinal",
    "condition_id",
    "condition_mask",
    "condition_replicate",
    "source_indices",
    "responder_indices",
    "body_edge_weight",
    "condition_edge_zeroed",
    *DYNAMIC_KEYS,
}


class VerificationRefusal(RuntimeError):
    pass


def refuse(message: str) -> None:
    raise VerificationRefusal(message)


def expected_conditions():
    rows = []

    for mask in MASKS:
        for replicate in REPLICATES:
            rows.append(
                (
                    f"sq10:{mask}:r{replicate}",
                    mask,
                    replicate,
                )
            )

    return rows


def verify_evidence_arrays(
    arrays: dict[str, np.ndarray],
) -> dict:
    if set(arrays) != EXPECTED_KEYS:
        refuse(
            "SQ-10 evidence key-set mismatch"
        )

    expected_shapes = {
        "condition_ordinal":
            (EPISODE_COUNT,),
        "condition_id":
            (EPISODE_COUNT,),
        "condition_mask":
            (EPISODE_COUNT,),
        "condition_replicate":
            (EPISODE_COUNT,),
        "source_indices":
            (BODY_PAIR_COUNT,),
        "responder_indices":
            (BODY_PAIR_COUNT,),
        "body_edge_weight":
            (BODY_PAIR_COUNT,),
        "condition_edge_zeroed":
            (
                EPISODE_COUNT,
                BODY_PAIR_COUNT,
            ),
    }

    for key in DYNAMIC_KEYS:
        expected_shapes[key] = (
            EPISODE_COUNT,
            FRAME_COUNT,
            BODY_PAIR_COUNT,
        )

    for key, shape in expected_shapes.items():
        value = arrays[key]

        if not isinstance(
            value,
            np.ndarray,
        ):
            refuse(
                f"SQ-10 evidence field "
                f"is not ndarray: {key}"
            )

        if value.shape != shape:
            refuse(
                f"SQ-10 shape mismatch "
                f"{key}: {value.shape} != {shape}"
            )

    exact_dtypes = {
        "condition_ordinal":
            np.dtype(np.int32),
        "condition_id":
            np.dtype("<U11"),
        "condition_mask":
            np.dtype("<U3"),
        "condition_replicate":
            np.dtype(np.int8),
        "source_indices":
            np.dtype(np.int64),
        "responder_indices":
            np.dtype(np.int64),
        "body_edge_weight":
            np.dtype(np.float32),
        "condition_edge_zeroed":
            np.dtype(np.uint8),
        "source_voltage_pre_step":
            np.dtype(np.float32),
        "source_spikes_pre_step":
            np.dtype(np.uint8),
        "source_effective_activity_pre_synaptic":
            np.dtype(np.float32),
        "responder_voltage_pre_threshold":
            np.dtype(np.float32),
        "responder_fired":
            np.dtype(np.uint8),
        "responder_voltage_post_reset":
            np.dtype(np.float32),
        "responder_spikes_post_commit":
            np.dtype(np.uint8),
    }

    for key, dtype in exact_dtypes.items():
        if arrays[key].dtype != dtype:
            refuse(
                f"SQ-10 dtype mismatch "
                f"{key}: "
                f"{arrays[key].dtype} != {dtype}"
            )

    if not np.array_equal(
        arrays["source_indices"],
        SOURCES,
    ):
        refuse(
            "SQ-10 source coordinate mismatch"
        )

    if not np.array_equal(
        arrays["responder_indices"],
        RESPONDERS,
    ):
        refuse(
            "SQ-10 responder coordinate mismatch"
        )

    expected = expected_conditions()

    ids = np.asarray(
        [row[0] for row in expected],
        dtype="<U11",
    )
    masks = np.asarray(
        [row[1] for row in expected],
        dtype="<U3",
    )
    replicates = np.asarray(
        [row[2] for row in expected],
        dtype=np.int8,
    )

    if not np.array_equal(
        arrays["condition_ordinal"],
        np.arange(
            EPISODE_COUNT,
            dtype=np.int32,
        ),
    ):
        refuse(
            "SQ-10 ordinal ordering mismatch"
        )

    if not np.array_equal(
        arrays["condition_id"],
        ids,
    ):
        refuse(
            "SQ-10 condition ID mismatch"
        )

    if not np.array_equal(
        arrays["condition_mask"],
        masks,
    ):
        refuse(
            "SQ-10 mask ordering mismatch"
        )

    if not np.array_equal(
        arrays["condition_replicate"],
        replicates,
    ):
        refuse(
            "SQ-10 replicate ordering mismatch"
        )

    expected_zeroed = np.asarray(
        [
            [int(bit) for bit in mask]
            for mask in masks
        ],
        dtype=np.uint8,
    )

    if not np.array_equal(
        arrays["condition_edge_zeroed"],
        expected_zeroed,
    ):
        refuse(
            "SQ-10 lesion-coordinate mismatch"
        )

    binary_keys = (
        "condition_edge_zeroed",
        "source_spikes_pre_step",
        "responder_fired",
        "responder_spikes_post_commit",
    )

    for key in binary_keys:
        values = np.unique(
            arrays[key]
        )

        if not set(
            values.tolist()
        ) <= {0, 1}:
            refuse(
                f"SQ-10 non-binary "
                f"evidence: {key}"
            )

    float_keys = (
        "body_edge_weight",
        "source_voltage_pre_step",
        "source_effective_activity_pre_synaptic",
        "responder_voltage_pre_threshold",
        "responder_voltage_post_reset",
    )

    for key in float_keys:
        if not np.all(
            np.isfinite(arrays[key])
        ):
            refuse(
                f"SQ-10 non-finite "
                f"evidence: {key}"
            )

    if np.any(
        arrays["body_edge_weight"] == 0.0
    ):
        refuse(
            "SQ-10 frozen BODY edge "
            "weight unexpectedly zero"
        )

    duplicate_pairs = 0

    for offset in range(
        0,
        EPISODE_COUNT,
        2,
    ):
        if (
            arrays[
                "condition_mask"
            ][offset]
            != arrays[
                "condition_mask"
            ][offset + 1]
        ):
            refuse(
                "SQ-10 duplicate mask mismatch"
            )

        for key in DYNAMIC_KEYS:
            if not np.array_equal(
                arrays[key][offset],
                arrays[key][offset + 1],
            ):
                refuse(
                    "SQ-10 deterministic "
                    f"duplicate mismatch: "
                    f"{key}"
                )

        duplicate_pairs += 1

    return {
        "status":
            "VERIFIED",
        "episode_count":
            EPISODE_COUNT,
        "mask_count":
            len(MASKS),
        "duplicate_pair_count":
            duplicate_pairs,
        "frame_count":
            FRAME_COUNT,
        "body_pair_count":
            BODY_PAIR_COUNT,
    }
