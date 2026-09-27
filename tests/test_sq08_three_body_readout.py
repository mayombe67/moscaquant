from __future__ import annotations

import numpy as np
import pytest

from brain.sq08_three_body_readout import (
    BODY_RESPONDERS,
    FRONTIER_INDICES,
    ReadoutRefusal,
    capture_mechanistic_state,
    validate_readout_indices,
)


def test_frozen_readout_coordinates():
    assert BODY_RESPONDERS.tolist() == [
        137122,
        317,
        126002,
    ]

    assert FRONTIER_INDICES.tolist() == [
        7,
        72,
        129,
        411,
        470,
        1472,
        1574,
        1662,
        1919,
        2009,
        2327,
        3712,
        4068,
        14273,
        16349,
        18196,
        130134,
        131527,
    ]


def test_readout_coordinates_are_unique():
    validate_readout_indices(200000)

    combined = np.concatenate(
        (BODY_RESPONDERS, FRONTIER_INDICES)
    )

    assert len(np.unique(combined)) == 21


def test_capture_is_ordered_and_passive():
    size = 140000

    voltage = np.zeros(size, dtype=np.float32)
    spikes = np.zeros(size, dtype=np.float32)

    for ordinal, node in enumerate(BODY_RESPONDERS):
        voltage[node] = 100.0 + ordinal
        spikes[node] = ordinal % 2

    for ordinal, node in enumerate(FRONTIER_INDICES):
        voltage[node] = 200.0 + ordinal
        spikes[node] = (ordinal + 1) % 2

    voltage_before = voltage.copy()
    spikes_before = spikes.copy()

    result = capture_mechanistic_state(
        voltage=voltage,
        spikes=spikes,
    )

    assert result["body_responder_voltage"].tolist() == [
        100.0,
        101.0,
        102.0,
    ]

    assert result["frontier_voltage"].tolist() == [
        200.0 + i
        for i in range(18)
    ]

    assert np.array_equal(voltage, voltage_before)
    assert np.array_equal(spikes, spikes_before)


def test_capture_converts_spikes_to_binary_uint8():
    size = 140000

    voltage = np.zeros(size, dtype=np.float32)
    spikes = np.zeros(size, dtype=np.float32)

    spikes[137122] = 1.0
    spikes[7] = 1.0

    result = capture_mechanistic_state(
        voltage=voltage,
        spikes=spikes,
    )

    assert result["body_responder_spikes"].dtype == np.uint8
    assert result["frontier_spikes"].dtype == np.uint8

    assert result["body_responder_spikes"][0] == 1
    assert result["frontier_spikes"][0] == 1


def test_capture_refuses_population_too_small():
    voltage = np.zeros(1000, dtype=np.float32)
    spikes = np.zeros(1000, dtype=np.float32)

    with pytest.raises(ReadoutRefusal):
        capture_mechanistic_state(
            voltage=voltage,
            spikes=spikes,
        )


def test_capture_refuses_nonfinite_voltage():
    size = 140000

    voltage = np.zeros(size, dtype=np.float32)
    spikes = np.zeros(size, dtype=np.float32)

    voltage[7] = np.nan

    with pytest.raises(ReadoutRefusal):
        capture_mechanistic_state(
            voltage=voltage,
            spikes=spikes,
        )
