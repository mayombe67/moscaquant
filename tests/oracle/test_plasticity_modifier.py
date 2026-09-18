from __future__ import annotations

import numpy as np

from oracle.plasticity_modifier import (
    build_synaptic_modifier,
)
from oracle.plasticity_state import (
    apply_plasticity_update,
    build_empty_plasticity_state,
)


ARTIFACT = "connectome-baseline-v1.npz"


def build_state():
    state = build_empty_plasticity_state()

    return apply_plasticity_update(
        state,
        presynaptic=1,
        postsynaptic=2,
        baseline_artifact_id=ARTIFACT,
        baseline_weight=4.0,
        session_id="session-A",
        evidence_reference="credit-001",
    )


def test_empty_plasticity_is_identity():
    state = build_empty_plasticity_state()

    modifier = build_synaptic_modifier(
        state
    )

    activity = np.array(
        [0.0, 1.0, 0.0],
        dtype=np.float32,
    )

    synaptic = np.array(
        [1.0, 2.0, 4.0],
        dtype=np.float32,
    )

    result = modifier(
        activity,
        synaptic,
    )

    np.testing.assert_array_equal(
        result,
        synaptic,
    )


def test_modifier_applies_persisted_multiplier():
    modifier = build_synaptic_modifier(
        build_state()
    )

    activity = np.array(
        [0.0, 1.0, 0.0],
        dtype=np.float32,
    )

    #
    # Baseline target contribution is 4.0.
    #
    synaptic = np.array(
        [0.0, 0.0, 4.0],
        dtype=np.float32,
    )

    result = modifier(
        activity,
        synaptic,
    )

    assert np.isclose(
        result[2],
        3.8,
    )


def test_modifier_preserves_input_arrays():
    modifier = build_synaptic_modifier(
        build_state()
    )

    activity = np.array(
        [0.0, 1.0, 0.0],
        dtype=np.float32,
    )

    synaptic = np.array(
        [0.0, 0.0, 4.0],
        dtype=np.float32,
    )

    original_activity = activity.copy()
    original_synaptic = synaptic.copy()

    modifier(
        activity,
        synaptic,
    )

    np.testing.assert_array_equal(
        activity,
        original_activity,
    )

    np.testing.assert_array_equal(
        synaptic,
        original_synaptic,
    )


def test_multiple_edges_apply_independently():
    state = build_empty_plasticity_state()

    state = apply_plasticity_update(
        state,
        presynaptic=0,
        postsynaptic=2,
        baseline_artifact_id=ARTIFACT,
        baseline_weight=2.0,
        session_id="session-A",
        evidence_reference="credit-001",
    )

    state = apply_plasticity_update(
        state,
        presynaptic=1,
        postsynaptic=3,
        baseline_artifact_id=ARTIFACT,
        baseline_weight=4.0,
        session_id="session-B",
        evidence_reference="credit-002",
    )

    modifier = build_synaptic_modifier(
        state
    )

    activity = np.array(
        [1.0, 1.0, 0.0, 0.0],
        dtype=np.float32,
    )

    synaptic = np.array(
        [0.0, 0.0, 2.0, 4.0],
        dtype=np.float32,
    )

    result = modifier(
        activity,
        synaptic,
    )

    assert np.isclose(
        result[2],
        1.9,
    )

    assert np.isclose(
        result[3],
        3.8,
    )
