from __future__ import annotations
from config.paths import data_path

import numpy as np
from scipy import sparse

from oracle.d6_mercy import (
    apply_mercy_activity,
    build_mercy,
)


CONNECTOME = str(
    data_path("processed", "connectome-baseline-v1.npz")
)

SOURCE = 43417
TARGET = 656


def find_seed_for_source() -> int:
    for seed in range(10000):
        intervention = build_mercy(
            seed=seed,
            experiment_id="mq7-mercy",
            session_id="integration-001",
            current_generation=0,
        )

        if intervention.target_model_index == SOURCE:
            return seed

    raise AssertionError(
        "could not select frozen source 43417"
    )


def test_mercy_increases_real_downstream_drive():
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

    activity[SOURCE] = 0.40

    baseline = np.asarray(
        connectome @ activity,
        dtype=np.float32,
    ).ravel()

    seed = find_seed_for_source()

    intervention = build_mercy(
        seed=seed,
        experiment_id="mq7-mercy",
        session_id="integration-001",
        current_generation=0,
    )

    assert intervention.target_model_index == SOURCE

    merciful = apply_mercy_activity(
        effective_activity=activity,
        intervention=intervention,
        generation=0,
    )

    assert np.isclose(
        merciful[SOURCE],
        0.50,
    )

    boosted = np.asarray(
        connectome @ merciful,
        dtype=np.float32,
    ).ravel()

    expected_delta = (
        weight * 0.10
    )

    actual_delta = (
        boosted[TARGET]
        - baseline[TARGET]
    )

    assert np.isclose(
        actual_delta,
        expected_delta,
        rtol=1e-6,
        atol=1e-7,
    )

    np.testing.assert_array_equal(
        activity[SOURCE],
        np.float32(0.40),
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
