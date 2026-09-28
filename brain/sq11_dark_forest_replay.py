from __future__ import annotations

import numpy as np


class DarkForestReplayError(RuntimeError):
    pass


def replay_csr_rows_float32(
    *,
    local_activity: np.ndarray,
    row_offsets: np.ndarray,
    row_weights: np.ndarray,
    row_union_positions: np.ndarray,
) -> np.ndarray:
    """
    Explicit float32 CSR-row accumulation.

    No scipy sparse operation is used here.

    local_activity:
        [frame_or_case, presynaptic_union]

    row_offsets:
        CSR-style boundaries for the three
        flattened responder rows.

    row_weights:
        flattened float32 CSR data in original
        row order.

    row_union_positions:
        for every flattened CSR entry, index
        into the local presynaptic union.

    Returns:
        float32 [frame_or_case, responder_row]
    """

    activity = np.asarray(
        local_activity
    )

    offsets = np.asarray(
        row_offsets
    )

    weights = np.asarray(
        row_weights
    )

    union_positions = np.asarray(
        row_union_positions
    )

    if activity.dtype != np.dtype(np.float32):
        raise DarkForestReplayError(
            "local_activity must be float32"
        )

    if weights.dtype != np.dtype(np.float32):
        raise DarkForestReplayError(
            "row_weights must be float32"
        )

    if offsets.dtype != np.dtype(np.int64):
        raise DarkForestReplayError(
            "row_offsets must be int64"
        )

    if (
        union_positions.dtype
        != np.dtype(np.int64)
    ):
        raise DarkForestReplayError(
            "row_union_positions must be int64"
        )

    if activity.ndim != 2:
        raise DarkForestReplayError(
            "local_activity must be 2D"
        )

    if offsets.ndim != 1:
        raise DarkForestReplayError(
            "row_offsets must be 1D"
        )

    if weights.ndim != 1:
        raise DarkForestReplayError(
            "row_weights must be 1D"
        )

    if union_positions.ndim != 1:
        raise DarkForestReplayError(
            "row_union_positions must be 1D"
        )

    if len(offsets) < 2:
        raise DarkForestReplayError(
            "row_offsets must define rows"
        )

    if offsets[0] != 0:
        raise DarkForestReplayError(
            "row_offsets must begin at zero"
        )

    if np.any(
        offsets[1:]
        < offsets[:-1]
    ):
        raise DarkForestReplayError(
            "row_offsets are not monotonic"
        )

    if int(offsets[-1]) != len(weights):
        raise DarkForestReplayError(
            "row_offsets/weights length mismatch"
        )

    if (
        len(union_positions)
        != len(weights)
    ):
        raise DarkForestReplayError(
            "row mapping/weights length mismatch"
        )

    if np.any(
        union_positions < 0
    ):
        raise DarkForestReplayError(
            "negative union position"
        )

    if np.any(
        union_positions
        >= activity.shape[1]
    ):
        raise DarkForestReplayError(
            "union position outside activity"
        )

    case_count = activity.shape[0]
    row_count = len(offsets) - 1

    out = np.empty(
        (
            case_count,
            row_count,
        ),
        dtype=np.float32,
    )

    for case in range(case_count):
        for row in range(row_count):
            start = int(
                offsets[row]
            )

            stop = int(
                offsets[row + 1]
            )

            accumulator = np.float32(
                0.0
            )

            for flat in range(
                start,
                stop,
            ):
                value = np.float32(
                    activity[
                        case,
                        union_positions[
                            flat
                        ],
                    ]
                )

                weight = np.float32(
                    weights[flat]
                )

                product = np.float32(
                    weight * value
                )

                accumulator = np.float32(
                    accumulator
                    + product
                )

            out[
                case,
                row,
            ] = accumulator

    return out
