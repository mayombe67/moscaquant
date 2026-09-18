from __future__ import annotations

import numpy as np

from oracle.d6_timeout import (
    DEFAULT_DURATION_TRANSITIONS,
    TIMEOUT_VERSION,
    apply_timeout_readout,
    build_timeout,
    is_timeout_active,
)
from oracle.reinforcement import ReinforcementCondition


def test_timeout_defaults_are_frozen():
    intervention = build_timeout(
        current_generation=5,
    )

    assert intervention.schema_version == TIMEOUT_VERSION
    assert (
        intervention.condition
        is ReinforcementCondition.SC_04_TIME_OUT
    )
    assert intervention.duration_transitions == 10
    assert (
        DEFAULT_DURATION_TRANSITIONS
        == 10
    )


def test_timeout_window_is_exact():
    intervention = build_timeout(
        current_generation=5,
    )

    assert not is_timeout_active(
        intervention,
        generation=4,
    )

    assert is_timeout_active(
        intervention,
        generation=5,
    )

    assert is_timeout_active(
        intervention,
        generation=14,
    )

    assert not is_timeout_active(
        intervention,
        generation=15,
    )


def test_timeout_zeros_readout_copy():
    voltage = np.asarray(
        [0.1, 0.8, 0.3, 0.9],
        dtype=np.float32,
    )

    spikes = np.asarray(
        [0, 1, 0, 1],
        dtype=np.float32,
    )

    intervention = build_timeout(
        current_generation=0,
    )

    result = apply_timeout_readout(
        voltage=voltage,
        spikes=spikes,
        readout_indices=np.asarray(
            [1, 3],
            dtype=np.int64,
        ),
        intervention=intervention,
        generation=0,
    )

    np.testing.assert_allclose(
        result.voltage,
        [0.1, 0.0, 0.3, 0.0],
    )

    np.testing.assert_array_equal(
        result.spikes,
        [0, 0, 0, 0],
    )

    assert result.active is True


def test_timeout_preserves_live_state():
    voltage = np.asarray(
        [0.1, 0.8, 0.3, 0.9],
        dtype=np.float32,
    )

    spikes = np.asarray(
        [0, 1, 0, 1],
        dtype=np.float32,
    )

    original_voltage = voltage.copy()
    original_spikes = spikes.copy()

    intervention = build_timeout(
        current_generation=0,
    )

    apply_timeout_readout(
        voltage=voltage,
        spikes=spikes,
        readout_indices=np.asarray(
            [1, 3],
            dtype=np.int64,
        ),
        intervention=intervention,
        generation=0,
    )

    np.testing.assert_array_equal(
        voltage,
        original_voltage,
    )

    np.testing.assert_array_equal(
        spikes,
        original_spikes,
    )


def test_timeout_preserves_non_readout_values():
    voltage = np.asarray(
        [0.1, 0.8, 0.3, 0.9],
        dtype=np.float32,
    )

    spikes = np.asarray(
        [1, 1, 1, 1],
        dtype=np.float32,
    )

    intervention = build_timeout(
        current_generation=0,
    )

    result = apply_timeout_readout(
        voltage=voltage,
        spikes=spikes,
        readout_indices=np.asarray(
            [1, 3],
            dtype=np.int64,
        ),
        intervention=intervention,
        generation=0,
    )

    assert result.voltage[0] == voltage[0]
    assert result.voltage[2] == voltage[2]

    assert result.spikes[0] == spikes[0]
    assert result.spikes[2] == spikes[2]


def test_timeout_recovers_immediately():
    voltage = np.asarray(
        [0.1, 0.8],
        dtype=np.float32,
    )

    spikes = np.asarray(
        [0, 1],
        dtype=np.float32,
    )

    intervention = build_timeout(
        current_generation=0,
    )

    result = apply_timeout_readout(
        voltage=voltage,
        spikes=spikes,
        readout_indices=np.asarray(
            [1],
            dtype=np.int64,
        ),
        intervention=intervention,
        generation=10,
    )

    np.testing.assert_array_equal(
        result.voltage,
        voltage,
    )

    np.testing.assert_array_equal(
        result.spikes,
        spikes,
    )

    assert result.active is False
