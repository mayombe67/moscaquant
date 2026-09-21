from __future__ import annotations

import numpy as np
from scipy import sparse

from brain.mq5_ts_metrics import (
    accepted_causal_edge_survival,
    compare_fingerprints,
    compare_onsets,
    compare_responder_identity,
    first_positive_onsets,
    lagged_mutual_information,
    positive_voltage_fingerprint,
    responder_identity,
)


def test_responder_identity_and_onsets():
    indices = np.asarray([10, 20, 30], dtype=np.int32)
    voltage = np.asarray(
        [
            [0.0, 0.0, 0.0],
            [0.1, 0.0, 0.0],
            [0.2, -0.1, 0.3],
        ],
        dtype=np.float64,
    )

    identity = responder_identity(voltage, indices)

    assert identity == {
        "responder_count": 2,
        "responder_indices": [10, 30],
    }

    assert first_positive_onsets(voltage, indices) == {
        10: 1,
        20: None,
        30: 2,
    }


def test_identity_onset_and_fingerprint_comparisons():
    assert compare_responder_identity(
        [1, 2, 3],
        [2, 3, 4],
    ) == {
        "exact_responder_set": False,
        "jaccard_vs_A": 0.5,
    }

    onset = compare_onsets(
        {1: 10, 2: 20, 3: None},
        {1: 10, 2: 23, 3: 40},
    )

    assert onset["common_present_responders"] == 2
    assert onset["exact_onset_agreement_count"] == 1
    assert onset["median_absolute_onset_shift"] == 1.5
    assert onset["maximum_absolute_onset_shift"] == 3

    a = positive_voltage_fingerprint(
        np.asarray(
            [
                [1.0, -2.0],
                [0.5, 0.0],
            ]
        )
    )

    b = positive_voltage_fingerprint(
        np.asarray(
            [
                [1.0, -4.0],
                [0.25, 0.0],
            ]
        )
    )

    result = compare_fingerprints(a, b)

    assert result["normalized_l2_distance"] > 0.0
    assert result["maximum_absolute_voltage_difference"] == 0.25


def test_lagged_mi_detects_shifted_dependency():
    stimulus = np.asarray(
        [0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0],
        dtype=np.float64,
    )

    dn = np.roll(stimulus, 1)
    dn[0] = 0.0

    result = lagged_mutual_information(stimulus, dn)

    assert result["bins"] == 8
    assert result["lags"] == [0, 1, 2, 3, 4]
    assert result["mi_by_lag"]["1"] >= result["mi_by_lag"]["0"]


def test_causal_edge_survival():
    rows = np.asarray([1, 2, 3], dtype=np.int32)
    cols = np.asarray([0, 1, 2], dtype=np.int32)
    data = np.ones(3, dtype=np.float32)

    matrix = sparse.csr_matrix(
        (data, (rows, cols)),
        shape=(4, 4),
    )
    matrix.sort_indices()

    result = accepted_causal_edge_survival(
        matrix,
        [(0, 1), (1, 2), (3, 0)],
    )

    assert result["frozen_causal_edge_count"] == 3
    assert result["surviving_causal_edge_count"] == 2
    assert result["causal_edge_survival_fraction"] == 2 / 3
    assert not result["complete_causal_route_set_survives"]
