from __future__ import annotations

import numpy as np
import pytest
from scipy import sparse

from oracle.d6_bad_synapse import (
    BAD_SYNAPSE_VERSION,
    DEFAULT_MULTIPLIER,
    BadSynapseError,
    apply_bad_synapse_overlay,
    build_bad_synapse_overlay,
)
from oracle.reinforcement import ReinforcementCondition


def make_connectome():
    return sparse.csr_matrix(
        np.array(
            [
                [0.0, 0.0, 0.0],
                [2.0, 0.0, 0.0],
                [0.0, 3.0, 0.0],
            ],
            dtype=np.float32,
        )
    )


def test_bad_synapse_defaults_are_frozen():
    overlay = build_bad_synapse_overlay(
        presynaptic=0,
        postsynaptic=1,
    )

    assert overlay.schema_version == BAD_SYNAPSE_VERSION
    assert (
        overlay.condition
        is ReinforcementCondition.SC_03_BAD_SYNAPSE
    )
    assert overlay.multiplier == DEFAULT_MULTIPLIER == 0.95


def test_bad_synapse_reduces_selected_edge_by_five_percent():
    connectome = make_connectome()

    activity = np.array(
        [1.0, 0.0, 0.0],
        dtype=np.float32,
    )

    overlay = build_bad_synapse_overlay(
        presynaptic=0,
        postsynaptic=1,
    )

    result = apply_bad_synapse_overlay(
        connectome=connectome,
        effective_activity=activity,
        overlay=overlay,
    )

    assert np.isclose(
        result[1],
        1.9,
    )


def test_bad_synapse_does_not_change_unrelated_target():
    connectome = make_connectome()

    activity = np.array(
        [1.0, 1.0, 0.0],
        dtype=np.float32,
    )

    overlay = build_bad_synapse_overlay(
        presynaptic=0,
        postsynaptic=1,
    )

    result = apply_bad_synapse_overlay(
        connectome=connectome,
        effective_activity=activity,
        overlay=overlay,
    )

    assert np.isclose(
        result[2],
        3.0,
    )


def test_bad_synapse_zero_activity_produces_zero_adjustment():
    connectome = make_connectome()

    activity = np.zeros(
        3,
        dtype=np.float32,
    )

    overlay = build_bad_synapse_overlay(
        presynaptic=0,
        postsynaptic=1,
    )

    result = apply_bad_synapse_overlay(
        connectome=connectome,
        effective_activity=activity,
        overlay=overlay,
    )

    np.testing.assert_array_equal(
        result,
        np.zeros(3, dtype=np.float32),
    )


def test_bad_synapse_preserves_connectome():
    connectome = make_connectome()

    original_data = connectome.data.copy()
    original_indices = connectome.indices.copy()
    original_indptr = connectome.indptr.copy()

    activity = np.array(
        [1.0, 0.0, 0.0],
        dtype=np.float32,
    )

    overlay = build_bad_synapse_overlay(
        presynaptic=0,
        postsynaptic=1,
    )

    apply_bad_synapse_overlay(
        connectome=connectome,
        effective_activity=activity,
        overlay=overlay,
    )

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


def test_bad_synapse_preserves_activity():
    connectome = make_connectome()

    activity = np.array(
        [1.0, 0.0, 0.0],
        dtype=np.float32,
    )

    original = activity.copy()

    overlay = build_bad_synapse_overlay(
        presynaptic=0,
        postsynaptic=1,
    )

    apply_bad_synapse_overlay(
        connectome=connectome,
        effective_activity=activity,
        overlay=overlay,
    )

    np.testing.assert_array_equal(
        activity,
        original,
    )


def test_bad_synapse_rejects_nonexistent_edge():
    connectome = make_connectome()

    activity = np.ones(
        3,
        dtype=np.float32,
    )

    overlay = build_bad_synapse_overlay(
        presynaptic=2,
        postsynaptic=0,
    )

    with pytest.raises(
        BadSynapseError,
        match="does not exist",
    ):
        apply_bad_synapse_overlay(
            connectome=connectome,
            effective_activity=activity,
            overlay=overlay,
        )
