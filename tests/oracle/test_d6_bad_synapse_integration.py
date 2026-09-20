from __future__ import annotations
from config.paths import data_path

import numpy as np
from scipy import sparse

from oracle.d6_bad_synapse import (
    apply_bad_synapse_overlay,
    build_bad_synapse_overlay,
)


CONNECTOME = str(
    data_path("processed", "connectome-baseline-v1.npz")
)

UPSTREAM = 56393
INTERMEDIATE = 68045
DOWNSTREAM = 1273


def test_bad_synapse_real_frozen_pathway_edges():
    connectome = sparse.load_npz(
        CONNECTOME
    ).tocsr()

    original_data = connectome.data.copy()
    original_indices = connectome.indices.copy()
    original_indptr = connectome.indptr.copy()

    upstream_weight = float(
        connectome[INTERMEDIATE, UPSTREAM]
    )

    intermediate_weight = float(
        connectome[DOWNSTREAM, INTERMEDIATE]
    )

    assert upstream_weight != 0.0
    assert intermediate_weight != 0.0

    #
    # Edge 1: 56393 -> 68045
    #

    activity = np.zeros(
        connectome.shape[1],
        dtype=np.float32,
    )

    activity[UPSTREAM] = 1.0

    baseline = np.asarray(
        connectome @ activity,
        dtype=np.float32,
    ).ravel()

    overlay = build_bad_synapse_overlay(
        presynaptic=UPSTREAM,
        postsynaptic=INTERMEDIATE,
    )

    result = apply_bad_synapse_overlay(
        connectome=connectome,
        effective_activity=activity,
        overlay=overlay,
    )

    expected = (
        upstream_weight * 0.95
    )

    assert np.isclose(
        result[INTERMEDIATE],
        expected,
        rtol=1e-6,
        atol=1e-7,
    )

    assert np.isclose(
        result[INTERMEDIATE] - baseline[INTERMEDIATE],
        upstream_weight * -0.05,
        rtol=1e-6,
        atol=1e-7,
    )

    #
    # Edge 2: 68045 -> 1273
    #

    activity = np.zeros(
        connectome.shape[1],
        dtype=np.float32,
    )

    activity[INTERMEDIATE] = 1.0

    baseline = np.asarray(
        connectome @ activity,
        dtype=np.float32,
    ).ravel()

    overlay = build_bad_synapse_overlay(
        presynaptic=INTERMEDIATE,
        postsynaptic=DOWNSTREAM,
    )

    result = apply_bad_synapse_overlay(
        connectome=connectome,
        effective_activity=activity,
        overlay=overlay,
    )

    expected = (
        intermediate_weight * 0.95
    )

    assert np.isclose(
        result[DOWNSTREAM],
        expected,
        rtol=1e-6,
        atol=1e-7,
    )

    assert np.isclose(
        result[DOWNSTREAM] - baseline[DOWNSTREAM],
        intermediate_weight * -0.05,
        rtol=1e-6,
        atol=1e-7,
    )

    #
    # Frozen artifact still untouched.
    #

    np.testing.assert_array_equal(
        connectome.data,
        original_data,
    )

    np.testing.assert_array_equal(
        connectome.indices,
        original_indices,
    )

    np.testing.assert_array_equal(
        connectome.indptr,
        original_indptr,
    )
