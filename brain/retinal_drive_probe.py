from pathlib import Path

import numpy as np
from scipy import sparse

from brain.market_replay import (
    ASSETS,
    FRAME_COUNT,
    OBSERVATIONS,
    SENSORY_GAIN,
    market_window_at,
    synthetic_series,
)
from brain.market_temporal import MarketVisionTemporalEncoder
from brain.runtime import LIFRuntime
from market.features import compute_features
from market.normalization import CausalNormalizer


CONNECTOME = Path(
    "/home/wil/moscaquant-data/processed/"
    "connectome-baseline-v1.npz"
)

TERRITORIES = Path(
    "/home/wil/moscaquant-data/processed/"
    "market-retinal-territories-v1.npz"
)


def main():
    connectome = sparse.load_npz(
        CONNECTOME
    )

    territory_data = np.load(
        TERRITORIES
    )

    retinal_indices = territory_data[
        "neuron_index"
    ]

    retinal_mask = np.zeros(
        connectome.shape[0],
        dtype=bool,
    )

    retinal_mask[
        retinal_indices
    ] = True

    normalizers = [
        CausalNormalizer(
            window_size=64,
            min_history=8,
        )
        for _ in ASSETS
    ]

    series = [
        synthetic_series("A", i)
        for i in range(6)
    ]

    encoder = MarketVisionTemporalEncoder(
        TERRITORIES
    )

    runtime = LIFRuntime(
        connectome
    )

    retinal_spike_frames = 0

    downstream_positive_events = 0
    downstream_negative_events = 0

    max_positive_drive = 0.0
    most_negative_drive = 0.0

    max_downstream_voltage = -np.inf
    min_downstream_voltage = np.inf

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

            normalized[
                asset_index
            ] = normalizers[
                asset_index
            ].transform(
                compute_features(window)
            )

        retinal = encoder.encode_sequence(
            normalized,
            frame_count=FRAME_COUNT,
        )

        for frame in retinal:
            previous_spikes = (
                runtime.spikes.copy()
            )

            retinal_previous = (
                previous_spikes
                * retinal_mask
            )

            if np.any(
                retinal_previous
            ):
                retinal_spike_frames += 1

                synaptic = (
                    connectome
                    @ retinal_previous
                )

                downstream = synaptic[
                    ~retinal_mask
                ]

                positive = downstream[
                    downstream > 0
                ]

                negative = downstream[
                    downstream < 0
                ]

                downstream_positive_events += len(
                    positive
                )

                downstream_negative_events += len(
                    negative
                )

                if len(positive):
                    max_positive_drive = max(
                        max_positive_drive,
                        float(
                            positive.max()
                        ),
                    )

                if len(negative):
                    most_negative_drive = min(
                        most_negative_drive,
                        float(
                            negative.min()
                        ),
                    )

            runtime.step(
                frame * SENSORY_GAIN
            )

            downstream_voltage = (
                runtime.voltage[
                    ~retinal_mask
                ]
            )

            max_downstream_voltage = max(
                max_downstream_voltage,
                float(
                    downstream_voltage.max()
                ),
            )

            min_downstream_voltage = min(
                min_downstream_voltage,
                float(
                    downstream_voltage.min()
                ),
            )

    print("RETINAL FIRST-HOP DRIVE")
    print(
        "  retinal spike source frames:",
        retinal_spike_frames,
    )

    print(
        "  downstream positive events:",
        downstream_positive_events,
    )

    print(
        "  downstream negative events:",
        downstream_negative_events,
    )

    print(
        "  strongest positive synaptic drive:",
        max_positive_drive,
    )

    print(
        "  strongest negative synaptic drive:",
        most_negative_drive,
    )

    print()
    print(
        "  maximum downstream voltage:",
        max_downstream_voltage,
    )

    print(
        "  minimum downstream voltage:",
        min_downstream_voltage,
    )

    print(
        "  firing threshold:",
        runtime.config.threshold,
    )

    print()
    print(
        "RETINAL DRIVE PROBE PASS"
    )


if __name__ == "__main__":
    main()
