from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from brain.market_temporal import MarketVisionTemporalEncoder
from brain.mq5_er_encoder import (
    ARM_A,
    ARM_B,
    ARM_C,
    ARM_D,
    ARM_E,
    FIXED_CYCLES_B,
    EncodingVariant,
    MQ5EREncodingVariantEncoder,
    balanced_asset_territory_mappings,
)


@dataclass
class _Geometry:
    neuron_index: np.ndarray
    x: np.ndarray


class _FakeSpatial:
    def __init__(self):
        self.geometries = {}

        for territory in range(1, 7):
            start = (territory - 1) * 4
            indices = np.arange(start, start + 4, dtype=np.int32)
            self.geometries[territory] = _Geometry(
                neuron_index=indices,
                x=np.array([-1.0, -0.3, 0.3, 1.0], dtype=np.float32),
            )

    @staticmethod
    def _validate_features(features):
        values = np.asarray(features, dtype=np.float32)
        if values.shape != (6, 7):
            raise ValueError
        return values

    def encode(self, features):
        values = self._validate_features(features)
        stimulus = np.zeros(24, dtype=np.float32)

        for row_index, territory in enumerate(range(1, 7)):
            geometry = self.geometries[territory]

            # Deterministic energy-normalized row-specific base pattern.
            raw = np.array(
                [
                    1.0 + 0.10 * row_index,
                    2.0 + 0.05 * float(values[row_index, 0]),
                    3.0 + 0.05 * float(values[row_index, 2]),
                    4.0 + 0.05 * float(values[row_index, 5]),
                ],
                dtype=np.float32,
            )
            raw /= raw.sum()

            stimulus[geometry.neuron_index] = raw

        return stimulus


def _features():
    values = np.array(
        [
            [-0.80, -0.75, -0.60, -0.50, -0.40, -0.25, -0.10],
            [-0.55, -0.45, -0.35, -0.25, -0.15, -0.05,  0.05],
            [-0.30, -0.20, -0.10,  0.00,  0.10,  0.20,  0.30],
            [-0.05,  0.10,  0.20,  0.30,  0.40,  0.50,  0.60],
            [ 0.20,  0.35,  0.45,  0.55,  0.65,  0.75,  0.85],
            [ 0.45,  0.60,  0.70,  0.80,  0.90,  0.95,  1.00],
        ],
        dtype=np.float32,
    )
    return values


def _reference_encoder():
    encoder = MarketVisionTemporalEncoder.__new__(MarketVisionTemporalEncoder)
    encoder.spatial = _FakeSpatial()
    encoder.population_size = 24
    encoder.base_energy = 1.0
    return encoder


def _variant_encoder(variant):
    encoder = MQ5EREncodingVariantEncoder.__new__(MQ5EREncodingVariantEncoder)
    encoder.spatial = _FakeSpatial()
    encoder.population_size = 24
    encoder.base_energy = 1.0
    encoder.variant = variant
    return encoder


def _territory_mean_energy(sequence, geometry):
    return float(
        sequence[:, geometry.neuron_index]
        .sum(axis=1)
        .mean()
    )


def test_arm_a_is_byte_identical_to_frozen_encoder():
    features = _features()

    expected = _reference_encoder().encode_sequence(
        features,
        frame_count=16,
    )
    actual = _variant_encoder(
        EncodingVariant(ARM_A)
    ).encode_sequence(
        features,
        frame_count=16,
    )

    assert expected.dtype == actual.dtype
    assert expected.shape == actual.shape
    assert expected.tobytes() == actual.tobytes()


def test_balanced_asset_mapping_family_is_exactly_12_and_balanced():
    mappings = balanced_asset_territory_mappings()

    assert len(mappings) == 12
    assert mappings[0] == ("rotation-0", (0, 1, 2, 3, 4, 5))

    counts = np.zeros((6, 6), dtype=np.int32)

    for _, mapping in mappings:
        assert sorted(mapping) == list(range(6))
        for territory_index, asset_index in enumerate(mapping):
            counts[asset_index, territory_index] += 1

    assert np.array_equal(counts, np.full((6, 6), 2, dtype=np.int32))


def test_arm_b_changes_gate_cadence_but_not_feature_matrix():
    features = _features()

    encoder_a = _variant_encoder(EncodingVariant(ARM_A))
    encoder_b = _variant_encoder(EncodingVariant(ARM_B))

    before = features.copy()

    gate_a = encoder_a._temporal_gate(
        volatility=float(features[0, 3]),
        entropy=float(features[0, 6]),
        frame_count=16,
    )
    gate_b = encoder_b._mq5_er_temporal_gate(
        volatility=float(features[0, 3]),
        entropy=float(features[0, 6]),
        frame_count=16,
    )

    assert FIXED_CYCLES_B == 2.5
    assert not np.array_equal(gate_a, gate_b)
    assert np.array_equal(features, before)


def test_arm_c_disables_entropy_jitter_without_mutating_feature_matrix():
    features = _features()
    before = features.copy()

    encoder_c = _variant_encoder(EncodingVariant(ARM_C))

    gate_entropy_low = encoder_c._mq5_er_temporal_gate(
        volatility=0.2,
        entropy=-1.0,
        frame_count=16,
    )
    gate_entropy_high = encoder_c._mq5_er_temporal_gate(
        volatility=0.2,
        entropy=1.0,
        frame_count=16,
    )

    assert np.array_equal(gate_entropy_low, gate_entropy_high)
    assert np.array_equal(features, before)


def test_arm_d_only_permutes_complete_asset_rows_before_encoding():
    features = _features()
    mapping = (1, 2, 3, 4, 5, 0)

    spatial = _FakeSpatial()
    expected_base = spatial.encode(features[np.asarray(mapping)])

    encoder_d = _variant_encoder(
        EncodingVariant(ARM_D, asset_mapping=mapping)
    )

    # Zero momentum and neutral timing make the first-frame spatial ownership
    # directly inspectable without invoking any neural model.
    controlled = features.copy()
    controlled[:, 1] = 0.0
    controlled[:, 3] = 0.0
    controlled[:, 6] = -1.0

    expected_base = spatial.encode(controlled[np.asarray(mapping)])
    actual = encoder_d.encode_sequence(controlled, frame_count=16)

    # With motion disabled by zero momentum, each frame is the mapped spatial
    # pattern scaled only by a territory-wide gate. Normalizing each territory
    # frame recovers the mapped base pattern.
    for territory in range(1, 7):
        geometry = spatial.geometries[territory]
        observed = actual[0, geometry.neuron_index]
        observed = observed / observed.sum()
        expected = expected_base[geometry.neuron_index]
        assert np.allclose(observed, expected, rtol=1e-6, atol=1e-7)


def test_arm_e_removes_momentum_motion_only():
    features = _features()

    encoder_e = _variant_encoder(EncodingVariant(ARM_E))

    plus = features.copy()
    minus = features.copy()
    plus[:, 1] = 0.9
    minus[:, 1] = -0.9

    seq_plus = encoder_e.encode_sequence(plus, frame_count=16)
    seq_minus = encoder_e.encode_sequence(minus, frame_count=16)

    assert np.array_equal(seq_plus, seq_minus)


def test_all_variants_preserve_mean_territory_energy():
    features = _features()

    variants = [
        EncodingVariant(ARM_A),
        EncodingVariant(ARM_B),
        EncodingVariant(ARM_C),
        EncodingVariant(ARM_D, asset_mapping=(1, 2, 3, 4, 5, 0)),
        EncodingVariant(ARM_E),
    ]

    for variant in variants:
        encoder = _variant_encoder(variant)
        sequence = encoder.encode_sequence(features, frame_count=16)

        for territory in range(1, 7):
            geometry = encoder.spatial.geometries[territory]
            assert np.isclose(
                _territory_mean_energy(sequence, geometry),
                1.0,
                rtol=1e-6,
                atol=1e-6,
            )
