from __future__ import annotations

import numpy as np
from scipy import sparse


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

FLAT_ENTRY_COUNT = 4568
PRESYNAPTIC_UNION_COUNT = 4393

SOURCES = np.asarray(
    [65084, 128590, 135589],
    dtype=np.int64,
)

RESPONDERS = np.asarray(
    [137122, 317, 126002],
    dtype=np.int64,
)

EXPECTED_ROW_OFFSETS = np.asarray(
    [0, 2830, 3671, 4568],
    dtype=np.int64,
)

EXPECTED_BODY_POSITIONS = np.asarray(
    [1908, 671, 767],
    dtype=np.int64,
)

EXPECTED_BODY_FLAT_POSITIONS = np.asarray(
    [1908, 3501, 4438],
    dtype=np.int64,
)

EXPECTED_BODY_WEIGHTS = np.asarray(
    [
        0.0002288853283971548,
        0.0005941770505160093,
        0.0006234414177015424,
    ],
    dtype=np.float32,
)


DYNAMIC_KEYS = (
    "local_effective_activity_pre_synaptic",
    "source_voltage_pre_step",
    "source_spikes_pre_step",
    "source_effective_activity_pre_synaptic",
    "responder_synaptic_p3",
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
    "condition_edge_zeroed",
    "body_edge_weight",
    "row_offsets",
    "row_indices",
    "row_weights",
    "body_positions",
    "body_flat_positions",
    "presynaptic_union_indices",
    "row_union_positions",
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
                    f"sq11:{mask}:r{replicate}",
                    mask,
                    replicate,
                )
            )

    return rows


def verify_array_contract(
    arrays: dict[str, np.ndarray],
) -> None:
    if set(arrays) != EXPECTED_KEYS:
        refuse(
            "SQ-11 evidence key-set mismatch"
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

        "condition_edge_zeroed":
            (
                EPISODE_COUNT,
                BODY_PAIR_COUNT,
            ),

        "body_edge_weight":
            (BODY_PAIR_COUNT,),

        "row_offsets":
            (4,),

        "row_indices":
            (FLAT_ENTRY_COUNT,),

        "row_weights":
            (FLAT_ENTRY_COUNT,),

        "body_positions":
            (BODY_PAIR_COUNT,),

        "body_flat_positions":
            (BODY_PAIR_COUNT,),

        "presynaptic_union_indices":
            (
                PRESYNAPTIC_UNION_COUNT,
            ),

        "row_union_positions":
            (FLAT_ENTRY_COUNT,),

        "local_effective_activity_pre_synaptic":
            (
                EPISODE_COUNT,
                FRAME_COUNT,
                PRESYNAPTIC_UNION_COUNT,
            ),
    }

    for key in DYNAMIC_KEYS:
        if (
            key
            == "local_effective_activity_pre_synaptic"
        ):
            continue

        expected_shapes[key] = (
            EPISODE_COUNT,
            FRAME_COUNT,
            BODY_PAIR_COUNT,
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

        "condition_edge_zeroed":
            np.dtype(np.uint8),

        "body_edge_weight":
            np.dtype(np.float32),

        "row_offsets":
            np.dtype(np.int64),

        "row_indices":
            np.dtype(np.int64),

        "row_weights":
            np.dtype(np.float32),

        "body_positions":
            np.dtype(np.int64),

        "body_flat_positions":
            np.dtype(np.int64),

        "presynaptic_union_indices":
            np.dtype(np.int64),

        "row_union_positions":
            np.dtype(np.int64),

        "local_effective_activity_pre_synaptic":
            np.dtype(np.float32),

        "source_voltage_pre_step":
            np.dtype(np.float32),

        "source_spikes_pre_step":
            np.dtype(np.uint8),

        "source_effective_activity_pre_synaptic":
            np.dtype(np.float32),

        "responder_synaptic_p3":
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

    for key, shape in expected_shapes.items():
        value = arrays[key]

        if not isinstance(
            value,
            np.ndarray,
        ):
            refuse(
                f"SQ-11 evidence field "
                f"is not ndarray: {key}"
            )

        if value.shape != shape:
            refuse(
                f"SQ-11 shape mismatch "
                f"{key}: {value.shape} != {shape}"
            )

        if value.dtype != exact_dtypes[key]:
            refuse(
                f"SQ-11 dtype mismatch "
                f"{key}: {value.dtype} != "
                f"{exact_dtypes[key]}"
            )

    for key, value in arrays.items():
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
                f"SQ-11 non-finite evidence: {key}"
            )


def verify_coordinates(
    arrays: dict[str, np.ndarray],
) -> None:
    if not np.array_equal(
        arrays["source_indices"],
        SOURCES,
    ):
        refuse(
            "SQ-11 source coordinate mismatch"
        )

    if not np.array_equal(
        arrays["responder_indices"],
        RESPONDERS,
    ):
        refuse(
            "SQ-11 responder coordinate mismatch"
        )

    expected = expected_conditions()

    if not np.array_equal(
        arrays["condition_ordinal"],
        np.arange(
            EPISODE_COUNT,
            dtype=np.int32,
        ),
    ):
        refuse(
            "SQ-11 ordinal ordering mismatch"
        )

    if not np.array_equal(
        arrays["condition_id"],
        np.asarray(
            [
                row[0]
                for row in expected
            ],
            dtype="<U11",
        ),
    ):
        refuse(
            "SQ-11 condition-ID ordering mismatch"
        )

    if not np.array_equal(
        arrays["condition_mask"],
        np.asarray(
            [
                row[1]
                for row in expected
            ],
            dtype="<U3",
        ),
    ):
        refuse(
            "SQ-11 mask ordering mismatch"
        )

    if not np.array_equal(
        arrays["condition_replicate"],
        np.asarray(
            [
                row[2]
                for row in expected
            ],
            dtype=np.int8,
        ),
    ):
        refuse(
            "SQ-11 replicate ordering mismatch"
        )

    expected_zeroed = np.asarray(
        [
            [
                int(bit)
                for bit in row[1]
            ]
            for row in expected
        ],
        dtype=np.uint8,
    )

    if not np.array_equal(
        arrays[
            "condition_edge_zeroed"
        ],
        expected_zeroed,
    ):
        refuse(
            "SQ-11 lesion-coordinate mismatch"
        )

    for key in (
        "condition_edge_zeroed",
        "source_spikes_pre_step",
        "responder_fired",
        "responder_spikes_post_commit",
    ):
        value = arrays[key]

        if np.any(
            (value != 0)
            & (value != 1)
        ):
            refuse(
                f"SQ-11 non-binary field: {key}"
            )

    if not np.array_equal(
        arrays["row_offsets"],
        EXPECTED_ROW_OFFSETS,
    ):
        refuse(
            "SQ-11 row-offset mismatch"
        )

    if not np.array_equal(
        arrays["body_positions"],
        EXPECTED_BODY_POSITIONS,
    ):
        refuse(
            "SQ-11 BODY-position mismatch"
        )

    if not np.array_equal(
        arrays[
            "body_flat_positions"
        ],
        EXPECTED_BODY_FLAT_POSITIONS,
    ):
        refuse(
            "SQ-11 BODY-flat-position mismatch"
        )

    expected_flat = (
        arrays["row_offsets"][:-1]
        + arrays["body_positions"]
    )

    if not np.array_equal(
        arrays[
            "body_flat_positions"
        ],
        expected_flat,
    ):
        refuse(
            "SQ-11 BODY position arithmetic mismatch"
        )

    union = arrays[
        "presynaptic_union_indices"
    ]

    if np.any(
        union[1:] <= union[:-1]
    ):
        refuse(
            "SQ-11 presynaptic union "
            "is not strictly increasing"
        )

    mapping = arrays[
        "row_union_positions"
    ]

    if np.any(mapping < 0):
        refuse(
            "SQ-11 negative row-union position"
        )

    if np.any(
        mapping
        >= PRESYNAPTIC_UNION_COUNT
    ):
        refuse(
            "SQ-11 row-union position "
            "outside union"
        )

    if not np.array_equal(
        union[mapping],
        arrays["row_indices"],
    ):
        refuse(
            "SQ-11 row/union round-trip mismatch"
        )

    if not np.array_equal(
        arrays["row_indices"][
            EXPECTED_BODY_FLAT_POSITIONS
        ],
        SOURCES,
    ):
        refuse(
            "SQ-11 BODY source-location mismatch"
        )

    if not np.array_equal(
        arrays["row_weights"][
            EXPECTED_BODY_FLAT_POSITIONS
        ],
        arrays["body_edge_weight"],
    ):
        refuse(
            "SQ-11 BODY weight-location mismatch"
        )

    if not np.array_equal(
        arrays["body_edge_weight"],
        EXPECTED_BODY_WEIGHTS,
    ):
        refuse(
            "SQ-11 BODY weight mismatch"
        )


def verify_baseline_binding(
    arrays: dict[str, np.ndarray],
    baseline: sparse.csr_matrix,
) -> None:
    if not sparse.isspmatrix_csr(
        baseline
    ):
        refuse(
            "SQ-11 verifier baseline is not CSR"
        )

    if baseline.dtype != np.dtype(
        np.float32
    ):
        refuse(
            "SQ-11 verifier baseline "
            "is not float32"
        )

    expected_indices = []
    expected_weights = []
    expected_offsets = [0]

    for responder in RESPONDERS:
        start = int(
            baseline.indptr[
                int(responder)
            ]
        )

        stop = int(
            baseline.indptr[
                int(responder) + 1
            ]
        )

        indices = np.asarray(
            baseline.indices[
                start:stop
            ],
            dtype=np.int64,
        )

        weights = np.asarray(
            baseline.data[
                start:stop
            ],
            dtype=np.float32,
        )

        expected_indices.append(
            indices
        )

        expected_weights.append(
            weights
        )

        expected_offsets.append(
            expected_offsets[-1]
            + len(indices)
        )

    expected_indices = (
        np.concatenate(
            expected_indices
        )
    )

    expected_weights = (
        np.concatenate(
            expected_weights
        )
    )

    expected_offsets = np.asarray(
        expected_offsets,
        dtype=np.int64,
    )

    if not np.array_equal(
        arrays["row_offsets"],
        expected_offsets,
    ):
        refuse(
            "SQ-11 stored row offsets "
            "do not match baseline"
        )

    if not np.array_equal(
        arrays["row_indices"],
        expected_indices,
    ):
        refuse(
            "SQ-11 stored row indices "
            "do not match baseline"
        )

    if not np.array_equal(
        arrays["row_weights"],
        expected_weights,
    ):
        refuse(
            "SQ-11 stored row weights "
            "do not match baseline"
        )

    expected_union = np.unique(
        expected_indices
    ).astype(
        np.int64,
        copy=False,
    )

    if not np.array_equal(
        arrays[
            "presynaptic_union_indices"
        ],
        expected_union,
    ):
        refuse(
            "SQ-11 stored presynaptic union "
            "does not match baseline"
        )


def _rows_for_mask(
    arrays: dict[str, np.ndarray],
    mask: str,
) -> sparse.csr_matrix:
    data_parts = []
    index_parts = []
    indptr = [0]

    offsets = arrays[
        "row_offsets"
    ]

    weights = arrays[
        "row_weights"
    ]

    mapping = arrays[
        "row_union_positions"
    ]

    body_positions = arrays[
        "body_positions"
    ]

    for row in range(
        BODY_PAIR_COUNT
    ):
        start = int(
            offsets[row]
        )

        stop = int(
            offsets[row + 1]
        )

        row_data = weights[
            start:stop
        ]

        row_indices = mapping[
            start:stop
        ]

        if mask[row] == "1":
            body_position = int(
                body_positions[row]
            )

            keep = np.ones(
                len(row_data),
                dtype=bool,
            )

            keep[
                body_position
            ] = False

            row_data = (
                row_data[keep]
            )

            row_indices = (
                row_indices[keep]
            )

        data_parts.append(
            row_data.astype(
                np.float32,
                copy=False,
            )
        )

        index_parts.append(
            row_indices.astype(
                np.int32,
                copy=False,
            )
        )

        indptr.append(
            indptr[-1]
            + len(row_data)
        )

    return sparse.csr_matrix(
        (
            np.concatenate(
                data_parts
            ),
            np.concatenate(
                index_parts
            ),
            np.asarray(
                indptr,
                dtype=np.int32,
            ),
        ),
        shape=(
            BODY_PAIR_COUNT,
            PRESYNAPTIC_UNION_COUNT,
        ),
        dtype=np.float32,
    )


def verify_exact_p3_replay(
    arrays: dict[str, np.ndarray],
) -> None:
    local = arrays[
        "local_effective_activity_pre_synaptic"
    ]

    observed = arrays[
        "responder_synaptic_p3"
    ]

    for episode in range(
        EPISODE_COUNT
    ):
        mask = str(
            arrays[
                "condition_mask"
            ][episode]
        )

        rows = _rows_for_mask(
            arrays,
            mask,
        )

        for frame in range(
            FRAME_COUNT
        ):
            replay = np.asarray(
                rows
                @ local[
                    episode,
                    frame,
                ],
                dtype=np.float32,
            ).ravel()

            if np.array_equal(
                replay,
                observed[
                    episode,
                    frame,
                ],
            ):
                continue

            mismatch = np.flatnonzero(
                replay
                != observed[
                    episode,
                    frame,
                ]
            )

            body = int(
                mismatch[0]
            )

            refuse(
                "SQ-11 independent P3 replay "
                "mismatch: "
                f"episode={episode}, "
                f"frame={frame}, "
                f"body={body}"
            )


def verify_duplicates(
    arrays: dict[str, np.ndarray],
) -> None:
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
                "SQ-11 duplicate mask mismatch"
            )

        for key in DYNAMIC_KEYS:
            if not np.array_equal(
                arrays[key][offset],
                arrays[key][
                    offset + 1
                ],
            ):
                refuse(
                    "SQ-11 deterministic "
                    "duplicate mismatch: "
                    f"{key}, mask="
                    f"{arrays['condition_mask'][offset]}"
                )


def verify_source_cross_readout(
    arrays: dict[str, np.ndarray],
) -> None:
    union = arrays[
        "presynaptic_union_indices"
    ]

    positions = np.searchsorted(
        union,
        SOURCES,
    )

    if not np.array_equal(
        union[positions],
        SOURCES,
    ):
        refuse(
            "SQ-11 BODY sources missing "
            "from local union"
        )

    local_sources = arrays[
        "local_effective_activity_pre_synaptic"
    ][
        :,
        :,
        positions,
    ]

    if not np.array_equal(
        local_sources,
        arrays[
            "source_effective_activity_pre_synaptic"
        ],
    ):
        refuse(
            "SQ-11 source/local P2 "
            "cross-readout mismatch"
        )


def verify_evidence_arrays(
    arrays: dict[str, np.ndarray],
    *,
    baseline: sparse.csr_matrix | None = None,
) -> dict:
    verify_array_contract(
        arrays
    )

    verify_coordinates(
        arrays
    )

    if baseline is not None:
        verify_baseline_binding(
            arrays,
            baseline,
        )

    verify_duplicates(
        arrays
    )

    verify_source_cross_readout(
        arrays
    )

    verify_exact_p3_replay(
        arrays
    )

    return {
        "status":
            "PASS",

        "episode_count":
            EPISODE_COUNT,

        "frame_count":
            FRAME_COUNT,

        "body_pair_count":
            BODY_PAIR_COUNT,

        "p3_values_verified":
            (
                EPISODE_COUNT
                * FRAME_COUNT
                * BODY_PAIR_COUNT
            ),

        "duplicate_pairs_verified":
            8,

        "baseline_binding_verified":
            baseline is not None,

        "replay_semantics":
            "structural BODY-edge omission",

        "absolute_tolerance":
            0.0,

        "relative_tolerance":
            0.0,
    }
