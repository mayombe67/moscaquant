from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest
from scipy import sparse

from brain.sq11_dark_forest_replay import (
    DarkForestReplayError,
    replay_csr_rows_float32,
)


ROOT = Path(__file__).resolve().parents[2]

CONTRACT = (
    ROOT
    / "config/experiments/"
    "sq11-dark-forest-replay-qualification-contract-v1.json"
)


def test_small_csr_replay_is_exact():
    matrix = sparse.csr_matrix(
        np.asarray(
            [
                [0.25, 0.0, -0.5, 1.0],
                [0.0, 0.125, 0.75, 0.0],
            ],
            dtype=np.float32,
        )
    )

    #
    # Flattened CSR rows already happen
    # to use every source index here.
    #
    row_offsets = (
        matrix.indptr.astype(
            np.int64
        )
    )

    row_weights = (
        matrix.data.astype(
            np.float32
        )
    )

    union = np.unique(
        matrix.indices
    ).astype(
        np.int64
    )

    row_union_positions = (
        np.searchsorted(
            union,
            matrix.indices,
        ).astype(
            np.int64
        )
    )

    full = np.asarray(
        [
            [0.1, 0.2, 0.3, 0.4],
            [1.0, 0.5, 0.25, 0.125],
            [0.0, 1.0, 0.0, 1.0],
        ],
        dtype=np.float32,
    )

    local = full[
        :,
        union,
    ]

    observed = (
        replay_csr_rows_float32(
            local_activity=local,
            row_offsets=row_offsets,
            row_weights=row_weights,
            row_union_positions=
                row_union_positions,
        )
    )

    expected = np.asarray(
        [
            matrix @ row
            for row in full
        ],
        dtype=np.float32,
    )

    np.testing.assert_array_equal(
        observed,
        expected,
    )


def test_replay_rejects_float64_activity():
    with pytest.raises(
        DarkForestReplayError
    ):
        replay_csr_rows_float32(
            local_activity=
                np.zeros(
                    (1, 1),
                    dtype=np.float64,
                ),
            row_offsets=
                np.asarray(
                    [0, 1],
                    dtype=np.int64,
                ),
            row_weights=
                np.asarray(
                    [1.0],
                    dtype=np.float32,
                ),
            row_union_positions=
                np.asarray(
                    [0],
                    dtype=np.int64,
                ),
        )


def test_qualification_contract_is_fail_closed():
    d = json.loads(
        CONTRACT.read_text()
    )

    assert (
        d["status"]
        == "FROZEN_PRE_QUALIFICATION"
    )

    assert (
        d["neural_evidence_allowed"]
        is False
    )

    q = d["qualification"]

    assert q["case_count"] == 96
    assert (
        q["row_case_comparisons"]
        == 288
    )

    assert (
        q["equality_rule"]
        == "exact float32 equality"
    )

    assert (
        q[
            "required_mismatch_count"
        ]
        == 0
    )

    assert (
        q["absolute_tolerance"]
        == 0.0
    )

    assert (
        q["relative_tolerance"]
        == 0.0
    )


def test_contract_binds_real_body_geometry():
    d = json.loads(
        CONTRACT.read_text()
    )

    assert (
        d["target"][
            "expected_row_nnz"
        ]
        == [2830, 841, 897]
    )

    assert (
        d["target"][
            "expected_body_positions"
        ]
        == [1908, 671, 767]
    )
