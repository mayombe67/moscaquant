from __future__ import annotations

import numpy as np


class DarkForestReplayV2Error(RuntimeError):
    pass


def replay_csr_rows_float32(
    *,
    local_activity: np.ndarray,
    row_offsets: np.ndarray,
    row_weights: np.ndarray,
    row_union_positions: np.ndarray,
    body_flat_positions: np.ndarray,
    condition_edge_zeroed: np.ndarray,
) -> np.ndarray:
    """
    Explicit float32 CSR replay with structural
    BODY-edge omission.

    A lesioned BODY edge is SKIPPED entirely.
    It is not multiplied by zero.

    This models the actual CSR accumulation path
    after the BODY entry has been eliminated.
    """

    activity = np.asarray(local_activity)
    offsets = np.asarray(row_offsets)
    weights = np.asarray(row_weights)
    mapping = np.asarray(
        row_union_positions
    )
    body = np.asarray(
        body_flat_positions
    )
    zeroed = np.asarray(
        condition_edge_zeroed
    )

    if activity.dtype != np.dtype(np.float32):
        raise DarkForestReplayV2Error(
            "local_activity must be float32"
        )

    if weights.dtype != np.dtype(np.float32):
        raise DarkForestReplayV2Error(
            "row_weights must be float32"
        )

    for name, value in (
        ("row_offsets", offsets),
        ("row_union_positions", mapping),
        ("body_flat_positions", body),
    ):
        if value.dtype != np.dtype(np.int64):
            raise DarkForestReplayV2Error(
                f"{name} must be int64"
            )

    if zeroed.dtype != np.dtype(np.uint8):
        raise DarkForestReplayV2Error(
            "condition_edge_zeroed must be uint8"
        )

    if activity.ndim != 2:
        raise DarkForestReplayV2Error(
            "local_activity must be 2D"
        )

    if offsets.ndim != 1:
        raise DarkForestReplayV2Error(
            "row_offsets must be 1D"
        )

    row_count = len(offsets) - 1
    case_count = activity.shape[0]

    if row_count <= 0:
        raise DarkForestReplayV2Error(
            "no responder rows"
        )

    if body.shape != (row_count,):
        raise DarkForestReplayV2Error(
            "body_flat_positions shape mismatch"
        )

    if zeroed.shape != (
        case_count,
        row_count,
    ):
        raise DarkForestReplayV2Error(
            "condition_edge_zeroed shape mismatch"
        )

    if np.any(
        (zeroed != 0)
        & (zeroed != 1)
    ):
        raise DarkForestReplayV2Error(
            "condition_edge_zeroed is not binary"
        )

    if offsets[0] != 0:
        raise DarkForestReplayV2Error(
            "row_offsets must start at zero"
        )

    if np.any(
        offsets[1:]
        < offsets[:-1]
    ):
        raise DarkForestReplayV2Error(
            "row_offsets not monotonic"
        )

    if int(offsets[-1]) != len(weights):
        raise DarkForestReplayV2Error(
            "row weight length mismatch"
        )

    if len(mapping) != len(weights):
        raise DarkForestReplayV2Error(
            "row mapping length mismatch"
        )

    if np.any(mapping < 0):
        raise DarkForestReplayV2Error(
            "negative union position"
        )

    if np.any(
        mapping >= activity.shape[1]
    ):
        raise DarkForestReplayV2Error(
            "union position outside activity"
        )

    for row in range(row_count):
        start = int(offsets[row])
        stop = int(offsets[row + 1])
        position = int(body[row])

        if not (
            start
            <= position
            < stop
        ):
            raise DarkForestReplayV2Error(
                "BODY flat position outside row"
            )

    out = np.empty(
        (
            case_count,
            row_count,
        ),
        dtype=np.float32,
    )

    for case in range(case_count):
        for row in range(row_count):
            start = int(offsets[row])
            stop = int(offsets[row + 1])

            skip = (
                int(body[row])
                if zeroed[case, row]
                else -1
            )

            accumulator = np.float32(
                0.0
            )

            for flat in range(
                start,
                stop,
            ):
                #
                # Structural lesion:
                # do not perform multiplication
                # or addition for this CSR entry.
                #
                if flat == skip:
                    continue

                value = np.float32(
                    activity[
                        case,
                        mapping[flat],
                    ]
                )

                product = np.float32(
                    weights[flat]
                    * value
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
