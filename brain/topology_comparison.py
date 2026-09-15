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

RETINA = Path(
    "/home/wil/moscaquant-data/processed/"
    "market-retinal-territories-v1.npz"
)


def compare_condition(condition: str):
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

    encoder = MarketVisionTemporalEncoder(
        RETINA
    )

    print(
        f"loading connectomes for condition {condition}..."
    )

    biological = sparse.load_npz(
        BIOLOGICAL
    )

    shuffled = sparse.load_npz(
        SHUFFLED
    )

    bio_runtime = LIFRuntime(
        biological
    )

    shuffled_runtime = LIFRuntime(
        shuffled
    )

    n = biological.shape[0]

    bio_neuron_counts = np.zeros(
        n,
        dtype=np.int32,
    )

    shuffled_neuron_counts = np.zeros(
        n,
        dtype=np.int32,
    )

    jaccards = []
    disagreements = []
    bio_counts = []
    shuffled_counts = []

    first_divergence = None
    frame_number = 0

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

        retinal = encoder.encode_sequence(
            normalized,
            frame_count=FRAME_COUNT,
        )

        for frame in retinal:
            stimulus = (
                frame * SENSORY_GAIN
            )

            bio = (
                bio_runtime.step(
                    stimulus
                )
                > 0
            )

            shuf = (
                shuffled_runtime.step(
                    stimulus
                )
                > 0
            )

            bio_neuron_counts += bio
            shuffled_neuron_counts += shuf

            bio_count = int(
                np.count_nonzero(bio)
            )

            shuffled_count = int(
                np.count_nonzero(shuf)
            )

            bio_counts.append(
                bio_count
            )

            shuffled_counts.append(
                shuffled_count
            )

            intersection = int(
                np.count_nonzero(
                    bio & shuf
                )
            )

            union = int(
                np.count_nonzero(
                    bio | shuf
                )
            )

            different = int(
                np.count_nonzero(
                    bio != shuf
                )
            )

            if union == 0:
                jaccard = 1.0
            else:
                jaccard = (
                    intersection / union
                )

            jaccards.append(
                jaccard
            )

            disagreements.append(
                different
            )

            if (
                first_divergence is None
                and different > 0
            ):
                first_divergence = (
                    frame_number
                )

            frame_number += 1

    bio_counts = np.asarray(
        bio_counts,
        dtype=np.int32,
    )

    shuffled_counts = np.asarray(
        shuffled_counts,
        dtype=np.int32,
    )

    jaccards = np.asarray(
        jaccards,
        dtype=np.float64,
    )

    disagreements = np.asarray(
        disagreements,
        dtype=np.int32,
    )

    active_union = (
        (bio_neuron_counts > 0)
        | (shuffled_neuron_counts > 0)
    )

    bio_active = (
        bio_neuron_counts > 0
    )

    shuffled_active = (
        shuffled_neuron_counts > 0
    )

    unique_intersection = int(
        np.count_nonzero(
            bio_active
            & shuffled_active
        )
    )

    unique_union = int(
        np.count_nonzero(
            bio_active
            | shuffled_active
        )
    )

    unique_jaccard = (
        unique_intersection
        / unique_union
        if unique_union
        else 1.0
    )

    # Compare per-neuron spike totals only over neurons active
    # in at least one topology.
    x = bio_neuron_counts[
        active_union
    ].astype(
        np.float64
    )

    y = shuffled_neuron_counts[
        active_union
    ].astype(
        np.float64
    )

    if len(x) > 1:
        correlation = float(
            np.corrcoef(
                x,
                y,
            )[0, 1]
        )
    else:
        correlation = float("nan")

    active_frames = (
        (bio_counts > 0)
        | (shuffled_counts > 0)
    )

    active_jaccards = jaccards[
        active_frames
    ]

    print()
    print("=" * 72)
    print(
        f"TOPOLOGY COMPARISON — CONDITION {condition}"
    )
    print("=" * 72)

    print(
        "frames:",
        len(bio_counts),
    )

    print(
        "first divergent frame:",
        first_divergence,
    )

    print()
    print(
        "biological total spikes:",
        int(bio_counts.sum()),
    )

    print(
        "shuffled total spikes:",
        int(shuffled_counts.sum()),
    )

    print(
        "frames with unequal spike counts:",
        int(
            np.count_nonzero(
                bio_counts
                != shuffled_counts
            )
        ),
    )

    print()
    print(
        "mean frame spike-set Jaccard:",
        float(jaccards.mean()),
    )

    if len(active_jaccards):
        print(
            "mean active-frame Jaccard:",
            float(
                active_jaccards.mean()
            ),
        )

    print(
        "minimum frame Jaccard:",
        float(jaccards.min()),
    )

    print(
        "max neurons disagreeing in one frame:",
        int(
            disagreements.max()
        ),
    )

    print()
    print(
        "biological unique spiking neurons:",
        int(
            np.count_nonzero(
                bio_active
            )
        ),
    )

    print(
        "shuffled unique spiking neurons:",
        int(
            np.count_nonzero(
                shuffled_active
            )
        ),
    )

    print(
        "unique-neuron intersection:",
        unique_intersection,
    )

    print(
        "unique-neuron Jaccard:",
        unique_jaccard,
    )

    print()
    print(
        "per-neuron spike-count correlation:",
        correlation,
    )

    print()
    print(
        "TOPOLOGY COMPARISON PASS"
    )


def main():
    compare_condition("A")
    print()
    compare_condition("B")


if __name__ == "__main__":
    main()
