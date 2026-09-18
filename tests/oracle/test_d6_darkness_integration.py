from __future__ import annotations

import numpy as np

from brain.market_sensory import MarketVisionSpatialEncoder
from oracle.d6_darkness import apply_darkness, build_darkness


def test_darkness_preserves_encoded_pattern_and_reduces_energy(
    tmp_path,
):
    population_size = 12

    artifact = tmp_path / "territories.npz"

    np.savez(
        artifact,
        neuron_index=np.arange(
            population_size,
            dtype=np.int32,
        ),
        eye=np.asarray(
            [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1],
            dtype=np.int8,
        ),
        h1=np.asarray(
            [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
            dtype=np.float32,
        ),
        h2=np.asarray(
            [0, 0, 1, 1, 2, 2, 0, 0, 1, 1, 2, 2],
            dtype=np.float32,
        ),
        territory=np.asarray(
            [1, 2, 3, 4, 5, 6, 1, 2, 3, 4, 5, 6],
            dtype=np.int8,
        ),
    )

    encoder = MarketVisionSpatialEncoder(
        territory_artifact=artifact,
        population_size=population_size,
        base_energy=1.0,
    )

    features = np.asarray(
        [
            [0.2, 0.1, 0.3, 0.0, 0.2, 0.1, 0.4],
            [-0.2, 0.0, 0.1, 0.3, -0.1, -0.2, 0.5],
            [0.1, -0.2, 0.2, 0.4, 0.0, 0.3, 0.6],
            [-0.1, 0.3, -0.2, 0.2, 0.1, -0.3, 0.7],
            [0.3, 0.2, 0.0, 0.1, -0.2, 0.2, 0.8],
            [0.0, -0.1, 0.3, 0.2, 0.2, -0.1, 0.9],
        ],
        dtype=np.float32,
    )

    original = encoder.encode(features)

    intervention = build_darkness(
        current_generation=0,
    )

    darkened = apply_darkness(
        stimulus=original,
        intervention=intervention,
        generation=0,
    )

    assert np.isclose(
        darkened.sum(),
        original.sum() * 0.25,
    )

    np.testing.assert_allclose(
        darkened / darkened.sum(),
        original / original.sum(),
    )

    np.testing.assert_array_equal(
        original,
        encoder.encode(features),
    )
