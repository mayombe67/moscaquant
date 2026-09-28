from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy import sparse

from brain.sq11_dark_forest_replay_v2 import (
    replay_csr_rows_float32,
)


ROOT = Path(__file__).resolve().parents[2]

CONTRACT = (
    ROOT
    / "config/experiments/"
    "sq11-dark-forest-replay-qualification-contract-v2.json"
)


def test_structural_skip_matches_csr():
    full = np.asarray(
        [
            [0.25, 0.5, 0.75, 1.0],
            [1.0, 0.5, 0.25, 0.125],
        ],
        dtype=np.float32,
    )

    #
    # Row 0: cols 0,1,2
    # BODY flat entry = 1
    #
    # Row 1: cols 1,3
    # BODY flat entry = 4
    #
    row_offsets = np.asarray(
        [0, 3, 5],
        dtype=np.int64,
    )

    row_indices = np.asarray(
        [0, 1, 2, 1, 3],
        dtype=np.int64,
    )

    row_weights = np.asarray(
        [0.25, 0.5, 0.75, 1.5, 0.125],
        dtype=np.float32,
    )

    union = np.unique(
        row_indices
    )

    mapping = np.searchsorted(
        union,
        row_indices,
    ).astype(np.int64)

    body = np.asarray(
        [1, 4],
        dtype=np.int64,
    )

    zeroed = np.asarray(
        [
            [1, 0],
            [0, 1],
        ],
        dtype=np.uint8,
    )

    observed = (
        replay_csr_rows_float32(
            local_activity=
                full[:, union],
            row_offsets=
                row_offsets,
            row_weights=
                row_weights,
            row_union_positions=
                mapping,
            body_flat_positions=
                body,
            condition_edge_zeroed=
                zeroed,
        )
    )

    expected = []

    for case in range(2):
        rows = []

        for row in range(2):
            start = row_offsets[row]
            stop = row_offsets[row + 1]

            cols = row_indices[
                start:stop
            ].copy()

            data = row_weights[
                start:stop
            ].copy()

            if zeroed[case, row]:
                local = (
                    body[row]
                    - start
                )

                cols = np.delete(
                    cols,
                    local,
                )

                data = np.delete(
                    data,
                    local,
                )

            csr = sparse.csr_matrix(
                (
                    data,
                    cols,
                    np.asarray(
                        [0, len(cols)],
                        dtype=np.int32,
                    ),
                ),
                shape=(1, 4),
                dtype=np.float32,
            )

            rows.append(
                np.asarray(
                    csr
                    @ full[case],
                    dtype=np.float32,
                ).ravel()[0]
            )

        expected.append(rows)

    expected = np.asarray(
        expected,
        dtype=np.float32,
    )

    np.testing.assert_array_equal(
        observed,
        expected,
    )


def test_contract_qualifies_all_masks():
    d = json.loads(
        CONTRACT.read_text()
    )

    q = d["qualification"]

    assert q["mask_count"] == 8

    assert q["masks"] == [
        "000",
        "001",
        "010",
        "011",
        "100",
        "101",
        "110",
        "111",
    ]

    assert (
        q[
            "row_case_mask_comparisons"
        ]
        == 2304
    )


def test_contract_requires_zero_tolerance():
    q = json.loads(
        CONTRACT.read_text()
    )["qualification"]

    assert (
        q["required_mismatch_count"]
        == 0
    )

    assert q["absolute_tolerance"] == 0.0
    assert q["relative_tolerance"] == 0.0


def test_contract_explicitly_covers_structural_lesions():
    d = json.loads(
        CONTRACT.read_text()
    )

    assert (
        "structurally lesioned"
        in d["reason"]
    )

    assert (
        "structurally omitted"
        in d["qualification"][
            "reference_operation"
        ]
    )
