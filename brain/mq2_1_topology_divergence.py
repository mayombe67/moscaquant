from __future__ import annotations
from config.paths import data_path


from pathlib import Path
import tomllib

import numpy as np
from scipy import sparse

from brain.market_replay import (
    ASSETS,
    FRAME_COUNT,
    OBSERVATIONS,
    SENSORY_GAIN,
    synthetic_series,
    market_window_at,
)
from brain.market_temporal import MarketVisionTemporalEncoder
from brain.visual_transduction import (
    VisualTransductionConfig,
    VisualTransductionRuntime,
)
from market.features import compute_features
from market.normalization import CausalNormalizer


BIOLOGICAL = data_path('processed', 'connectome-baseline-v1.npz')

SHUFFLED = data_path('processed', 'connectome-shuffled-mosca-v2.npz')

RETINA = data_path('processed', 'visual-r1-r6-map-v1.npz')

RELAY = data_path('processed', 'visual-relay-map-v1.npz')

TERRITORIES = data_path('processed', 'market-retinal-territories-v1.npz')

CONFIG = Path(
    "config/sensory/visual-transduction-v1.toml"
)


def build_frames(condition):
    normalizers = [
        CausalNormalizer(
            window_size=64,
            min_history=8,
        )
        for _ in ASSETS
    ]

    series = [
        synthetic_series(
            condition,
            asset_index,
        )
        for asset_index in range(6)
    ]

    encoder = MarketVisionTemporalEncoder(
        TERRITORIES
    )

    result = []

    for observation in range(
        OBSERVATIONS
    ):
        normalized = np.empty(
            (6, 7),
            dtype=np.float32,
        )

        for asset_index in range(6):
            window = market_window_at(
                series[asset_index],
                observation,
            )

            features = compute_features(
                window
            )

            normalized[
                asset_index
            ] = normalizers[
                asset_index
            ].transform(
                features
            )

        frames = encoder.encode_sequence(
            normalized,
            frame_count=FRAME_COUNT,
        )

        result.extend(frames)

    return result


def run(condition):
    with CONFIG.open("rb") as handle:
        config = tomllib.load(handle)

    release_gain = float(
        config["transduction"]["release_gain"]
    )

    bio_connectome = sparse.load_npz(
        BIOLOGICAL
    ).tocsr()

    shuf_connectome = sparse.load_npz(
        SHUFFLED
    ).tocsr()

    retina = np.load(RETINA)

    retinal_indices = np.asarray(
        retina["neuron_index"],
        dtype=np.int32,
    )

    relay = np.load(RELAY)

    relay_indices = np.asarray(
        relay["neuron_index"],
        dtype=np.int32,
    )

    n = bio_connectome.shape[0]

    retinal_mask = np.zeros(
        n,
        dtype=bool,
    )
    retinal_mask[
        retinal_indices
    ] = True

    relay_mask = np.zeros(
        n,
        dtype=bool,
    )
    relay_mask[
        relay_indices
    ] = True

    wider_mask = ~(
        retinal_mask
        | relay_mask
    )

    bio = VisualTransductionRuntime(
        connectome=bio_connectome,
        retinal_indices=retinal_indices,
        relay_artifact=RELAY,
        config=VisualTransductionConfig(
            release_gain=release_gain,
        ),
    )

    shuf = VisualTransductionRuntime(
        connectome=shuf_connectome,
        retinal_indices=retinal_indices,
        relay_artifact=RELAY,
        config=VisualTransductionConfig(
            release_gain=release_gain,
        ),
    )

    frames = build_frames(
        condition
    )

    first = {
        "whole_voltage": None,
        "retinal_voltage": None,
        "relay_voltage": None,
        "wider_voltage": None,
        "whole_spike": None,
        "retinal_spike": None,
        "relay_spike": None,
        "wider_spike": None,
    }

    first_relay_activity = None

    max_voltage_difference = 0.0
    max_voltage_difference_frame = None

    for frame_number, stimulus in enumerate(
        frames
    ):
        bio_spikes = (
            bio.step(
                stimulus
                * SENSORY_GAIN
            ) > 0
        )

        shuf_spikes = (
            shuf.step(
                stimulus
                * SENSORY_GAIN
            ) > 0
        )

        if (
            first_relay_activity is None
            and (
                np.any(
                    bio_spikes
                    & relay_mask
                )
                or np.any(
                    shuf_spikes
                    & relay_mask
                )
            )
        ):
            first_relay_activity = (
                frame_number
            )

        voltage_diff = np.abs(
            bio.voltage
            - shuf.voltage
        )

        frame_max = float(
            voltage_diff.max()
        )

        if (
            frame_max
            > max_voltage_difference
        ):
            max_voltage_difference = (
                frame_max
            )

            max_voltage_difference_frame = (
                frame_number
            )

        if (
            first["whole_voltage"]
            is None
            and np.any(
                voltage_diff > 0
            )
        ):
            first["whole_voltage"] = (
                frame_number
            )

        if (
            first["retinal_voltage"]
            is None
            and np.any(
                voltage_diff[
                    retinal_mask
                ] > 0
            )
        ):
            first["retinal_voltage"] = (
                frame_number
            )

        if (
            first["relay_voltage"]
            is None
            and np.any(
                voltage_diff[
                    relay_mask
                ] > 0
            )
        ):
            first["relay_voltage"] = (
                frame_number
            )

        if (
            first["wider_voltage"]
            is None
            and np.any(
                voltage_diff[
                    wider_mask
                ] > 0
            )
        ):
            first["wider_voltage"] = (
                frame_number
            )

        spike_diff = (
            bio_spikes
            != shuf_spikes
        )

        if (
            first["whole_spike"]
            is None
            and np.any(
                spike_diff
            )
        ):
            first["whole_spike"] = (
                frame_number
            )

        if (
            first["retinal_spike"]
            is None
            and np.any(
                spike_diff
                & retinal_mask
            )
        ):
            first["retinal_spike"] = (
                frame_number
            )

        if (
            first["relay_spike"]
            is None
            and np.any(
                spike_diff
                & relay_mask
            )
        ):
            first["relay_spike"] = (
                frame_number
            )

        if (
            first["wider_spike"]
            is None
            and np.any(
                spike_diff
                & wider_mask
            )
        ):
            first["wider_spike"] = (
                frame_number
            )

    print()
    print("=" * 72)
    print(
        f"TOPOLOGY DIVERGENCE — CONDITION {condition}"
    )
    print("=" * 72)

    print(
        "first relay activity:",
        first_relay_activity,
    )

    print()
    print("FIRST VOLTAGE DIVERGENCE")
    print(
        "  whole:",
        first["whole_voltage"],
    )
    print(
        "  retina:",
        first["retinal_voltage"],
    )
    print(
        "  relay:",
        first["relay_voltage"],
    )
    print(
        "  wider:",
        first["wider_voltage"],
    )

    print()
    print("FIRST SPIKE DIVERGENCE")
    print(
        "  whole:",
        first["whole_spike"],
    )
    print(
        "  retina:",
        first["retinal_spike"],
    )
    print(
        "  relay:",
        first["relay_spike"],
    )
    print(
        "  wider:",
        first["wider_spike"],
    )

    print()
    print(
        "maximum absolute voltage divergence:",
        max_voltage_difference,
    )

    print(
        "maximum divergence frame:",
        max_voltage_difference_frame,
    )


def main():
    run("A")
    run("B")

    print()
    print(
        "MQ-2.1 TOPOLOGY DIVERGENCE "
        "PROBE COMPLETE"
    )


if __name__ == "__main__":
    main()
