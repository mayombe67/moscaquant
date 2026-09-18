from __future__ import annotations

import numpy as np
from scipy import sparse

from oracle.d6_shock import (
    apply_shock_activity,
    build_shock,
)


CONNECTOME = (
    "/home/wil/moscaquant-data/processed/"
    "connectome-baseline-v1.npz"
)

SOURCE = 43417
TARGET = 656


def find_seed_for_source() -> int:
    for seed in range(10000):
        intervention = build_shock(
            seed=seed,
            experiment_id="mq7-shock",
            session_id="integration-001",
            current_generation=0,
        )

        if intervention.target_model_index == SOURCE:
            return seed

    raise AssertionError(
        "could not select frozen source 43417"
    )


def test_shock_propagates_through_frozen_connectome():
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

    baseline_synaptic = np.asarray(
        connectome @ activity,
        dtype=np.float32,
    ).ravel()

    seed = find_seed_for_source()

    intervention = build_shock(
        seed=seed,
        experiment_id="mq7-shock",
        session_id="integration-001",
        current_generation=0,
    )

    assert (
        intervention.target_model_index
        == SOURCE
    )

    shocked_activity = apply_shock_activity(
        effective_activity=activity,
        intervention=intervention,
        generation=0,
    )

    assert np.isclose(
        shocked_activity[SOURCE],
        0.75,
    )

    shocked_synaptic = np.asarray(
        connectome @ shocked_activity,
        dtype=np.float32,
    ).ravel()

    expected_target_delta = (
        weight * 0.75
    )

    actual_target_delta = (
        shocked_synaptic[TARGET]
        - baseline_synaptic[TARGET]
    )

    assert np.isclose(
        actual_target_delta,
        expected_target_delta,
        rtol=1e-6,
        atol=1e-7,
    )

    assert not np.isclose(
        shocked_synaptic[TARGET],
        baseline_synaptic[TARGET],
    )

    np.testing.assert_array_equal(
        activity,
        np.zeros_like(activity),
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
