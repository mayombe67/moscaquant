from __future__ import annotations

import numpy as np
import pytest

from brain.sq11_dark_forest_episode import (
    BODY_FLAT_POSITIONS,
    BODY_SOURCES,
    FRAME_COUNT,
    PRESYNAPTIC_UNION_COUNT,
    RESULT_KEYS,
    ROW_OFFSETS,
    Refusal,
    condition_edge_zeroed,
    validate_result,
)

from brain.sq11_dark_forest_replay_v2 import (
    replay_csr_rows_float32,
)


BODY_WEIGHTS = np.asarray(
    [
        0.0002288853283971548,
        0.0005941770505160093,
        0.0006234414177015424,
    ],
    dtype=np.float32,
)


def make_result(
    mask: str = "000",
):
    #
    # Construct a strictly increasing union of
    # exactly 4,393 coordinates containing all
    # three BODY sources.
    #
    base = np.arange(
        PRESYNAPTIC_UNION_COUNT - 3,
        dtype=np.int64,
    )

    union = np.sort(
        np.concatenate(
            [
                base,
                BODY_SOURCES,
            ]
        )
    )

    assert (
        len(union)
        == PRESYNAPTIC_UNION_COUNT
    )

    assert (
        len(np.unique(union))
        == PRESYNAPTIC_UNION_COUNT
    )

    #
    # Build flat row coordinates with valid
    # row lengths and ensure the BODY positions
    # point at the real BODY sources.
    #
    row_indices = np.resize(
        union,
        ROW_OFFSETS[-1],
    ).astype(
        np.int64,
        copy=False,
    )

    row_indices = row_indices.copy()

    row_indices[
        BODY_FLAT_POSITIONS
    ] = BODY_SOURCES

    mapping = np.searchsorted(
        union,
        row_indices,
    ).astype(
        np.int64,
    )

    np.testing.assert_array_equal(
        union[mapping],
        row_indices,
    )

    row_weights = np.zeros(
        ROW_OFFSETS[-1],
        dtype=np.float32,
    )

    row_weights[
        BODY_FLAT_POSITIONS
    ] = BODY_WEIGHTS

    local = np.zeros(
        (
            FRAME_COUNT,
            PRESYNAPTIC_UNION_COUNT,
        ),
        dtype=np.float32,
    )

    #
    # Make the BODY source activities nonzero
    # so the replay isn't a trivial all-zero case.
    #
    for body, source in enumerate(
        BODY_SOURCES
    ):
        position = int(
            np.searchsorted(
                union,
                source,
            )
        )

        local[:, position] = np.float32(
            0.1 * (body + 1)
        )

    zeroed_vector = (
        condition_edge_zeroed(mask)
    )

    zeroed_frames = np.repeat(
        zeroed_vector[
            None,
            :
        ],
        FRAME_COUNT,
        axis=0,
    ).astype(
        np.uint8,
        copy=False,
    )

    p3 = replay_csr_rows_float32(
        local_activity=local,
        row_offsets=
            ROW_OFFSETS.copy(),
        row_weights=
            row_weights,
        row_union_positions=
            mapping,
        body_flat_positions=
            BODY_FLAT_POSITIONS.copy(),
        condition_edge_zeroed=
            zeroed_frames,
    )

    frame3_f32 = np.zeros(
        (
            FRAME_COUNT,
            3,
        ),
        dtype=np.float32,
    )

    frame3_u8 = np.zeros(
        (
            FRAME_COUNT,
            3,
        ),
        dtype=np.uint8,
    )

    result = {
        "local_effective_activity_pre_synaptic":
            local,

        "source_voltage_pre_step":
            frame3_f32.copy(),

        "source_spikes_pre_step":
            frame3_u8.copy(),

        "source_effective_activity_pre_synaptic":
            np.stack(
                [
                    local[
                        :,
                        int(
                            np.searchsorted(
                                union,
                                source,
                            )
                        ),
                    ]
                    for source in BODY_SOURCES
                ],
                axis=1,
            ).astype(
                np.float32,
                copy=False,
            ),

        "responder_synaptic_p3":
            p3,

        "responder_voltage_pre_threshold":
            frame3_f32.copy(),

        "responder_fired":
            frame3_u8.copy(),

        "responder_voltage_post_reset":
            frame3_f32.copy(),

        "responder_spikes_post_commit":
            frame3_u8.copy(),

        "row_offsets":
            ROW_OFFSETS.copy(),

        "row_indices":
            row_indices,

        "row_weights":
            row_weights,

        "body_positions":
            np.asarray(
                [1908, 671, 767],
                dtype=np.int64,
            ),

        "body_flat_positions":
            BODY_FLAT_POSITIONS.copy(),

        "presynaptic_union_indices":
            union,

        "row_union_positions":
            mapping,

        "body_edge_weight":
            BODY_WEIGHTS.copy(),

        "condition_edge_zeroed":
            zeroed_vector,
    }

    assert set(result) == set(
        RESULT_KEYS
    )

    return result


@pytest.mark.parametrize(
    "mask",
    (
        "000",
        "001",
        "010",
        "011",
        "100",
        "101",
        "110",
        "111",
    ),
)
def test_exact_replay_result_is_accepted(
    mask,
):
    result = make_result(mask)

    validate_result(
        result,
        mask=mask,
    )


def test_one_float32_p3_mutation_is_refused():
    result = make_result(
        "000"
    )

    original = result[
        "responder_synaptic_p3"
    ][0, 0]

    result[
        "responder_synaptic_p3"
    ][0, 0] = np.nextafter(
        original,
        np.float32(np.inf),
        dtype=np.float32,
    )

    with pytest.raises(
        Refusal,
        match="exact P3 replay mismatch",
    ):
        validate_result(
            result,
            mask="000",
        )
