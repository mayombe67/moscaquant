from __future__ import annotations
from config.paths import data_path

import numpy as np
from scipy import sparse

from oracle.d6_scar import (
    advance_scar,
    build_scar,
)
from oracle.d6_scar_effect import (
    apply_scar_effect,
)


CONNECTOME = str(
    data_path("processed", "connectome-baseline-v1.npz")
)

SOURCE = 43417
TARGET = 656


def test_scar_carryover_changes_real_downstream_drive():
    connectome = sparse.load_npz(
        CONNECTOME
    ).tocsr()

    original_data = connectome.data.copy()
    original_indices = connectome.indices.copy()
    original_indptr = connectome.indptr.copy()

    weight = float(
        connectome[TARGET, SOURCE]
    )

    assert weight != 0.0

    activity = np.zeros(
        connectome.shape[1],
        dtype=np.float32,
    )

    activity[SOURCE] = 1.0

    baseline = np.asarray(
        connectome @ activity,
        dtype=np.float32,
    ).ravel()

    scar_a = build_scar(
        session_id="session-A",
        current_generation=0,
    )

    scarred_a = apply_scar_effect(
        effective_activity=activity,
        scar_state=scar_a,
        target_model_index=SOURCE,
    )

    synaptic_a = np.asarray(
        connectome @ scarred_a,
        dtype=np.float32,
    ).ravel()

    expected_delta = (
        weight * -0.25
    )

    actual_delta_a = (
        synaptic_a[TARGET]
        - baseline[TARGET]
    )

    assert np.isclose(
        actual_delta_a,
        expected_delta,
        rtol=1e-6,
        atol=1e-7,
    )

    scar_b = advance_scar(
        state=scar_a,
        session_id="session-B",
    )

    scarred_b = apply_scar_effect(
        effective_activity=activity,
        scar_state=scar_b,
        target_model_index=SOURCE,
    )

    synaptic_b = np.asarray(
        connectome @ scarred_b,
        dtype=np.float32,
    ).ravel()

    actual_delta_b = (
        synaptic_b[TARGET]
        - baseline[TARGET]
    )

    assert np.isclose(
        actual_delta_b,
        expected_delta,
        rtol=1e-6,
        atol=1e-7,
    )

    scar_c = advance_scar(
        state=scar_b,
        session_id="session-C",
    )

    recovered = apply_scar_effect(
        effective_activity=activity,
        scar_state=scar_c,
        target_model_index=SOURCE,
    )

    synaptic_c = np.asarray(
        connectome @ recovered,
        dtype=np.float32,
    ).ravel()

    np.testing.assert_allclose(
        synaptic_c,
        baseline,
    )

    np.testing.assert_array_equal(
        activity[SOURCE],
        1.0,
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
