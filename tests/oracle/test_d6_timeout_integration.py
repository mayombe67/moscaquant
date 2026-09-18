from __future__ import annotations

import numpy as np

from brain.mq3_2_anonymous_market_readout import (
    CHANNELS,
    build_channel_indices,
    decide,
    frame_metrics,
)
from oracle.d6_timeout import (
    apply_timeout_readout,
    build_timeout,
)


CONSENSUS = (
    "/home/wil/moscaquant-data/processed/"
    "mq3-dn-consensus-v1.npz"
)


def test_timeout_blocks_frozen_mq3_readout_only():
    consensus = np.load(CONSENSUS)

    channels = build_channel_indices(
        consensus
    )

    assert len(channels["DN-C0"]) == 6
    assert len(channels["DN-C1"]) == 646
    assert len(channels["DN-C2"]) == 539

    all_indices = np.concatenate(
        [
            channels[name]
            for name in CHANNELS
        ]
    )

    assert len(all_indices) == 1191
    assert len(np.unique(all_indices)) == 1191

    population_size = (
        int(all_indices.max()) + 1
    )

    voltage = np.zeros(
        population_size,
        dtype=np.float32,
    )

    spikes = np.zeros(
        population_size,
        dtype=np.float32,
    )

    voltage[all_indices] = 0.5
    spikes[all_indices] = 1.0

    original_voltage = voltage.copy()
    original_spikes = spikes.copy()

    intervention = build_timeout(
        current_generation=0,
    )

    blocked = apply_timeout_readout(
        voltage=voltage,
        spikes=spikes,
        readout_indices=all_indices,
        intervention=intervention,
        generation=0,
    )

    scores = {}

    for channel in CHANNELS:
        metrics = frame_metrics(
            blocked.voltage,
            blocked.spikes,
            channels[channel],
        )

        scores[channel] = (
            metrics[
                "mean_positive_voltage"
            ]
        )

        assert metrics[
            "mean_positive_voltage"
        ] == 0.0

        assert metrics[
            "spike_count"
        ] == 0

    decision = decide(scores)

    assert (
        decision["outcome"]
        == "ABSTAIN"
    )

    assert decision["winner"] is None

    np.testing.assert_array_equal(
        voltage,
        original_voltage,
    )

    np.testing.assert_array_equal(
        spikes,
        original_spikes,
    )
