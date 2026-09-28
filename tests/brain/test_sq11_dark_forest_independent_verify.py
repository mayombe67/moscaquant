from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from scipy import sparse

from brain.sq11_dark_forest_independent_verify import (
    VerificationRefusal,
    verify_evidence_arrays,
)


FRAME_COUNT = 192
EPISODE_COUNT = 16

SOURCES = np.asarray(
    [65084, 128590, 135589],
    dtype=np.int64,
)

RESPONDERS = np.asarray(
    [137122, 317, 126002],
    dtype=np.int64,
)

ROW_OFFSETS = np.asarray(
    [0, 2830, 3671, 4568],
    dtype=np.int64,
)

BODY_POSITIONS = np.asarray(
    [1908, 671, 767],
    dtype=np.int64,
)

BODY_FLAT_POSITIONS = np.asarray(
    [1908, 3501, 4438],
    dtype=np.int64,
)

BODY_WEIGHTS = np.asarray(
    [
        0.0002288853283971548,
        0.0005941770505160093,
        0.0006234414177015424,
    ],
    dtype=np.float32,
)

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


def build_geometry():
    union = np.sort(
        np.concatenate(
            [
                np.arange(
                    4390,
                    dtype=np.int64,
                ),
                SOURCES,
            ]
        )
    )

    assert union.shape == (4393,)

    row_indices = np.resize(
        union,
        4568,
    ).astype(
        np.int64,
        copy=False,
    ).copy()

    #
    # Replacing the three BODY locations can
    # remove otherwise unique union coordinates.
    # Preserve those displaced coordinates in
    # redundant tail slots so that:
    #
    #     unique(row_indices) == union
    #
    # exactly, as real DARK FOREST geometry
    # requires.
    #
    displaced = row_indices[
        BODY_FLAT_POSITIONS
    ].copy()

    row_indices[
        BODY_FLAT_POSITIONS
    ] = SOURCES

    repair_slots = np.asarray(
        [4393, 4394, 4395],
        dtype=np.int64,
    )

    row_indices[
        repair_slots
    ] = displaced

    np.testing.assert_array_equal(
        np.unique(row_indices),
        union,
    )

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
        4568,
        dtype=np.float32,
    )

    row_weights[
        BODY_FLAT_POSITIONS
    ] = BODY_WEIGHTS

    return (
        union,
        row_indices,
        mapping,
        row_weights,
    )


def build_arrays():
    (
        union,
        row_indices,
        mapping,
        row_weights,
    ) = build_geometry()

    local = np.zeros(
        (
            EPISODE_COUNT,
            FRAME_COUNT,
            4393,
        ),
        dtype=np.float32,
    )

    source_positions = np.searchsorted(
        union,
        SOURCES,
    )

    #
    # Deterministic nonzero P2 activity.
    # r1/r2 for each mask remain exact.
    #
    frame_values = (
        (
            np.arange(
                FRAME_COUNT,
                dtype=np.float32,
            )
            % np.float32(11.0)
        )
        + np.float32(1.0)
    ) * np.float32(0.03125)

    for episode in range(
        EPISODE_COUNT
    ):
        for body in range(3):
            local[
                episode,
                :,
                source_positions[body],
            ] = (
                frame_values
                * np.float32(body + 1)
            )

    source_p2 = local[
        :,
        :,
        source_positions,
    ].copy()

    p3 = np.zeros(
        (
            EPISODE_COUNT,
            FRAME_COUNT,
            3,
        ),
        dtype=np.float32,
    )

    condition_ids = []
    condition_masks = []
    condition_reps = []
    condition_zeroed = []

    ordinal = 0

    for mask in MASKS:
        for replicate in (1, 2):
            condition_ids.append(
                f"sq11:{mask}:r{replicate}"
            )

            condition_masks.append(
                mask
            )

            condition_reps.append(
                replicate
            )

            condition_zeroed.append(
                [
                    int(bit)
                    for bit in mask
                ]
            )

            for body in range(3):
                if mask[body] == "0":
                    p3[
                        ordinal,
                        :,
                        body,
                    ] = np.asarray(
                        source_p2[
                            ordinal,
                            :,
                            body,
                        ]
                        * BODY_WEIGHTS[body],
                        dtype=np.float32,
                    )

            ordinal += 1

    zeros_f32 = np.zeros(
        (
            EPISODE_COUNT,
            FRAME_COUNT,
            3,
        ),
        dtype=np.float32,
    )

    zeros_u8 = np.zeros(
        (
            EPISODE_COUNT,
            FRAME_COUNT,
            3,
        ),
        dtype=np.uint8,
    )

    return {
        "condition_ordinal":
            np.arange(
                EPISODE_COUNT,
                dtype=np.int32,
            ),

        "condition_id":
            np.asarray(
                condition_ids,
                dtype="<U11",
            ),

        "condition_mask":
            np.asarray(
                condition_masks,
                dtype="<U3",
            ),

        "condition_replicate":
            np.asarray(
                condition_reps,
                dtype=np.int8,
            ),

        "source_indices":
            SOURCES.copy(),

        "responder_indices":
            RESPONDERS.copy(),

        "condition_edge_zeroed":
            np.asarray(
                condition_zeroed,
                dtype=np.uint8,
            ),

        "body_edge_weight":
            BODY_WEIGHTS.copy(),

        "row_offsets":
            ROW_OFFSETS.copy(),

        "row_indices":
            row_indices,

        "row_weights":
            row_weights,

        "body_positions":
            BODY_POSITIONS.copy(),

        "body_flat_positions":
            BODY_FLAT_POSITIONS.copy(),

        "presynaptic_union_indices":
            union,

        "row_union_positions":
            mapping,

        "local_effective_activity_pre_synaptic":
            local,

        "source_voltage_pre_step":
            zeros_f32.copy(),

        "source_spikes_pre_step":
            zeros_u8.copy(),

        "source_effective_activity_pre_synaptic":
            source_p2,

        "responder_synaptic_p3":
            p3,

        "responder_voltage_pre_threshold":
            zeros_f32.copy(),

        "responder_fired":
            zeros_u8.copy(),

        "responder_voltage_post_reset":
            zeros_f32.copy(),

        "responder_spikes_post_commit":
            zeros_u8.copy(),
    }


def build_baseline(
    arrays,
):
    n = int(
        max(
            SOURCES.max(),
            RESPONDERS.max(),
        )
        + 1
    )

    #
    # CSR stores rows globally in ascending
    # row order, while DARK FOREST geometry
    # stores them in A/B/C responder order.
    #
    per_row = {}

    for body, responder in enumerate(
        RESPONDERS
    ):
        start = int(
            ROW_OFFSETS[body]
        )

        stop = int(
            ROW_OFFSETS[body + 1]
        )

        per_row[int(responder)] = (
            arrays[
                "row_indices"
            ][start:stop].copy(),
            arrays[
                "row_weights"
            ][start:stop].copy(),
        )

    indptr = np.zeros(
        n + 1,
        dtype=np.int64,
    )

    for responder, (
        indices,
        _weights,
    ) in per_row.items():
        indptr[
            responder + 1
        ] = len(indices)

    np.cumsum(
        indptr,
        out=indptr,
    )

    index_parts = []
    weight_parts = []

    for responder in sorted(
        per_row
    ):
        indices, weights = (
            per_row[responder]
        )

        index_parts.append(
            indices.astype(
                np.int32,
                copy=False,
            )
        )

        weight_parts.append(
            weights
        )

    return sparse.csr_matrix(
        (
            np.concatenate(
                weight_parts
            ),
            np.concatenate(
                index_parts
            ),
            indptr,
        ),
        shape=(n, n),
        dtype=np.float32,
    )


def test_complete_cube_passes_independent_verifier():
    arrays = build_arrays()

    baseline = build_baseline(
        arrays
    )

    report = verify_evidence_arrays(
        arrays,
        baseline=baseline,
    )

    assert report == {
        "status":
            "PASS",

        "episode_count":
            16,

        "frame_count":
            192,

        "body_pair_count":
            3,

        "p3_values_verified":
            9216,

        "duplicate_pairs_verified":
            8,

        "baseline_binding_verified":
            True,

        "replay_semantics":
            "structural BODY-edge omission",

        "absolute_tolerance":
            0.0,

        "relative_tolerance":
            0.0,
    }


def test_one_float32_p3_corruption_is_refused():
    arrays = build_arrays()

    #
    # Corrupt both deterministic replicas
    # identically. This deliberately preserves
    # the duplicate gate so the independent
    # replay gate is the one that must refuse.
    #
    for episode in (0, 1):
        value = arrays[
            "responder_synaptic_p3"
        ][episode, 0, 0]

        arrays[
            "responder_synaptic_p3"
        ][episode, 0, 0] = np.nextafter(
            value,
            np.float32(np.inf),
            dtype=np.float32,
        )

    with pytest.raises(
        VerificationRefusal,
        match="independent P3 replay mismatch",
    ):
        verify_evidence_arrays(
            arrays
        )


def test_duplicate_dynamic_corruption_is_refused():
    arrays = build_arrays()

    arrays[
        "source_voltage_pre_step"
    ][1, 0, 0] = np.float32(
        1.0
    )

    with pytest.raises(
        VerificationRefusal,
        match="deterministic duplicate mismatch",
    ):
        verify_evidence_arrays(
            arrays
        )


def test_baseline_weight_drift_is_refused():
    arrays = build_arrays()

    baseline = build_baseline(
        arrays
    )

    start = int(
        baseline.indptr[
            int(RESPONDERS[0])
        ]
    )

    baseline.data[
        start
    ] = np.nextafter(
        baseline.data[start],
        np.float32(np.inf),
        dtype=np.float32,
    )

    with pytest.raises(
        VerificationRefusal,
        match="row weights.*baseline",
    ):
        verify_evidence_arrays(
            arrays,
            baseline=baseline,
        )


def test_verifier_has_no_sq11_runtime_dependency():
    path = Path(
        "brain/"
        "sq11_dark_forest_independent_verify.py"
    )

    source = path.read_text()

    forbidden = (
        "sq11_dark_forest_episode",
        "sq11_dark_forest_evidence",
        "sq11_dark_forest_replay_v2",
    )

    for name in forbidden:
        assert name not in source
