from __future__ import annotations

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


BIOLOGICAL = Path(
    "/home/wil/moscaquant-data/processed/"
    "connectome-baseline-v1.npz"
)

SHUFFLED = Path(
    "/home/wil/moscaquant-data/processed/"
    "connectome-shuffled-mosca-v1.npz"
)

TERRITORIES = Path(
    "/home/wil/moscaquant-data/processed/"
    "market-retinal-territories-v1.npz"
)


def build_normalized_stream(condition: str):
    normalizers = [
        CausalNormalizer(
            window_size=64,
            min_history=8,
        )
        for _ in ASSETS
    ]

    series = [
        synthetic_series(condition, i)
        for i in range(6)
    ]

    for observation in range(OBSERVATIONS):
        normalized = np.empty(
            (6, 7),
            dtype=np.float32,
        )

        for asset_index in range(6):
            window = market_window_at(
                series[asset_index],
                observation,
            )

            normalized[asset_index] = (
                normalizers[
                    asset_index
                ].transform(
                    compute_features(window)
                )
            )

        yield normalized


def analyze(
    name: str,
    connectome,
    condition: str,
):
    territory_data = np.load(
        TERRITORIES
    )

    retinal_indices = territory_data[
        "neuron_index"
    ].astype(
        np.int32,
        copy=False,
    )

    retinal_mask = np.zeros(
        connectome.shape[0],
        dtype=bool,
    )

    retinal_mask[
        retinal_indices
    ] = True

    encoder = MarketVisionTemporalEncoder(
        TERRITORIES
    )

    runtime = LIFRuntime(
        connectome
    )

    retinal_spikes = 0
    downstream_spikes = 0

    retinal_unique = np.zeros(
        connectome.shape[0],
        dtype=bool,
    )

    downstream_unique = np.zeros(
        connectome.shape[0],
        dtype=bool,
    )

    downstream_frame_counts = []
    first_downstream_frame = None

    frame_number = 0

    for normalized in build_normalized_stream(
        condition
    ):
        retinal = encoder.encode_sequence(
            normalized,
            frame_count=FRAME_COUNT,
        )

        for frame in retinal:
            spikes = (
                runtime.step(
                    frame * SENSORY_GAIN
                )
                > 0
            )

            retinal_fired = (
                spikes
                & retinal_mask
            )

            downstream_fired = (
                spikes
                & ~retinal_mask
            )

            r_count = int(
                np.count_nonzero(
                    retinal_fired
                )
            )

            d_count = int(
                np.count_nonzero(
                    downstream_fired
                )
            )

            retinal_spikes += r_count
            downstream_spikes += d_count

            retinal_unique |= retinal_fired
            downstream_unique |= downstream_fired

            downstream_frame_counts.append(
                d_count
            )

            if (
                first_downstream_frame is None
                and d_count > 0
            ):
                first_downstream_frame = (
                    frame_number
                )

            frame_number += 1

    total = (
        retinal_spikes
        + downstream_spikes
    )

    print()
    print("=" * 72)
    print(
        f"{name} — CONDITION {condition}"
    )
    print("=" * 72)

    print(
        "total spikes:",
        total,
    )

    print(
        "retinal spikes:",
        retinal_spikes,
    )

    print(
        "downstream spikes:",
        downstream_spikes,
    )

    print(
        "downstream fraction:",
        (
            downstream_spikes / total
            if total
            else 0.0
        ),
    )

    print()
    print(
        "unique retinal spiking neurons:",
        int(
            np.count_nonzero(
                retinal_unique
            )
        ),
    )

    print(
        "unique downstream spiking neurons:",
        int(
            np.count_nonzero(
                downstream_unique
            )
        ),
    )

    print(
        "first downstream spike frame:",
        first_downstream_frame,
    )

    print(
        "downstream-active frames:",
        int(
            np.count_nonzero(
                np.asarray(
                    downstream_frame_counts
                )
            )
        ),
    )

    print(
        "max downstream spikes/frame:",
        int(
            np.max(
                downstream_frame_counts
            )
        ),
    )

    return downstream_unique


def main():
    print("loading biological connectome...")
    biological = sparse.load_npz(
        BIOLOGICAL
    )

    print("loading shuffled connectome...")
    shuffled = sparse.load_npz(
        SHUFFLED
    )

    for condition in ("A", "B"):
        bio_downstream = analyze(
            "MQ-001 BIOLOGICAL",
            biological,
            condition,
        )

        shuffled_downstream = analyze(
            "SHUFFLED MOSCA",
            shuffled,
            condition,
        )

        intersection = int(
            np.count_nonzero(
                bio_downstream
                & shuffled_downstream
            )
        )

        union = int(
            np.count_nonzero(
                bio_downstream
                | shuffled_downstream
            )
        )

        jaccard = (
            intersection / union
            if union
            else 1.0
        )

        print()
        print(
            f"DOWNSTREAM TOPOLOGY OVERLAP — {condition}"
        )

        print(
            "intersection:",
            intersection,
        )

        print(
            "union:",
            union,
        )

        print(
            "Jaccard:",
            jaccard,
        )

    print()
    print(
        "DOWNSTREAM PROPAGATION ANALYSIS PASS"
    )


if __name__ == "__main__":
    main()
