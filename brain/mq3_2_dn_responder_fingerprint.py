from __future__ import annotations
from config.paths import data_path


from pathlib import Path

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
from brain.visual_transduction import VisualTransductionConfig
from market.features import compute_features
from market.normalization import CausalNormalizer

from brain.mq3_2_graded_type_subsets import SubsetVisualRuntime


BASE = data_path('processed')

CONNECTOME = BASE / "connectome-baseline-v1.npz"
RETINA = BASE / "visual-r1-r6-map-v1.npz"
RELAY = BASE / "visual-relay-map-v1.npz"
TERRITORIES = BASE / "market-retinal-territories-v1.npz"
CONSENSUS = BASE / "mq3-dn-consensus-v1.npz"
GRADED = BASE / "mq3-2-graded-visual-types-v1.npz"
NEURON_IDS = BASE / "neuron_ids.npy"

RELEASE_GAIN = 0.9981738484618123

SUBSETS = (
    ("Tm2",),
    ("Tm4",),
    ("Tm2", "Tm4"),
    ("Tm2", "Tm3", "Tm4"),
)


def subset_name(subset):
    return "+".join(subset)


def run_subset(
    subset,
    connectome,
    retinal_indices,
    graded_indices,
    graded_types,
    c1_indices,
):
    selected = graded_indices[
        np.isin(
            graded_types,
            subset,
        )
    ]

    runtime = SubsetVisualRuntime(
        connectome=connectome,
        retinal_indices=retinal_indices,
        relay_artifact=RELAY,
        graded_indices=selected,
        config=VisualTransductionConfig(
            release_gain=RELEASE_GAIN,
        ),
    )

    normalizers = [
        CausalNormalizer(
            window_size=64,
            min_history=8,
        )
        for _ in ASSETS
    ]

    series = [
        synthetic_series(
            "A",
            asset_index,
        )
        for asset_index in range(6)
    ]

    encoder = MarketVisionTemporalEncoder(
        TERRITORIES
    )

    maximum = np.zeros(
        len(c1_indices),
        dtype=np.float64,
    )

    first_positive = np.full(
        len(c1_indices),
        -1,
        dtype=np.int32,
    )

    positive_frames = np.zeros(
        len(c1_indices),
        dtype=np.int32,
    )

    integrated_positive = np.zeros(
        len(c1_indices),
        dtype=np.float64,
    )

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

        frames = encoder.encode_sequence(
            normalized,
            frame_count=FRAME_COUNT,
        )

        for stimulus in frames:
            runtime.step(
                stimulus
                * SENSORY_GAIN
            )

            voltage = np.asarray(
                runtime.voltage[
                    c1_indices
                ],
                dtype=np.float64,
            )

            positive = np.maximum(
                voltage,
                0.0,
            )

            mask = voltage > 0

            newly = (
                mask
                & (
                    first_positive < 0
                )
            )

            first_positive[
                newly
            ] = frame_number

            positive_frames += (
                mask.astype(
                    np.int32
                )
            )

            integrated_positive += (
                positive
            )

            maximum = np.maximum(
                maximum,
                voltage,
            )

            frame_number += 1

    return {
        "maximum": maximum,
        "first_positive": first_positive,
        "positive_frames": positive_frames,
        "integrated_positive": integrated_positive,
    }


def main():
    W = sparse.load_npz(
        CONNECTOME
    ).tocsr()

    retina = np.load(
        RETINA
    )

    consensus = np.load(
        CONSENSUS
    )

    graded = np.load(
        GRADED
    )

    neuron_ids = np.load(
        NEURON_IDS
    )

    retinal_indices = np.asarray(
        retina["neuron_index"],
        dtype=np.int32,
    )

    dn_indices = np.asarray(
        consensus["neuron_index"],
        dtype=np.int32,
    )

    clusters = np.asarray(
        consensus["consensus_cluster"],
        dtype=np.int32,
    )

    c1_indices = dn_indices[
        clusters == 1
    ]

    graded_indices = np.asarray(
        graded["neuron_index"],
        dtype=np.int32,
    )

    graded_types = np.asarray(
        graded["type"],
    ).astype(str)

    results = {}

    print("=" * 88)
    print("MQ-3.2 DN-C1 RESPONDER FINGERPRINT")
    print("=" * 88)

    for subset in SUBSETS:
        name = subset_name(
            subset
        )

        result = run_subset(
            subset,
            W,
            retinal_indices,
            graded_indices,
            graded_types,
            c1_indices,
        )

        results[name] = result

        responders = np.flatnonzero(
            result["maximum"] > 0
        )

        print()
        print("=" * 88)
        print(name)
        print("=" * 88)

        print(
            "responders:",
            len(responders),
        )

        order = responders[
            np.argsort(
                result[
                    "maximum"
                ][responders]
            )[::-1]
        ]

        for local in order:
            model_index = int(
                c1_indices[
                    local
                ]
            )

            body_id = int(
                neuron_ids[
                    model_index
                ]
            )

            print(
                "model_index=",
                model_index,
                "bodyId=",
                body_id,
                "maxV=",
                float(
                    result[
                        "maximum"
                    ][local]
                ),
                "first=",
                int(
                    result[
                        "first_positive"
                    ][local]
                ),
                "frames=",
                int(
                    result[
                        "positive_frames"
                    ][local]
                ),
                "integrated=",
                float(
                    result[
                        "integrated_positive"
                    ][local]
                ),
            )

    print()
    print("=" * 88)
    print("PAIRWISE RESPONDER OVERLAP")
    print("=" * 88)

    names = [
        subset_name(x)
        for x in SUBSETS
    ]

    for i, left in enumerate(names):
        a = set(
            np.flatnonzero(
                results[
                    left
                ][
                    "maximum"
                ] > 0
            ).tolist()
        )

        for right in names[
            i + 1:
        ]:
            b = set(
                np.flatnonzero(
                    results[
                        right
                ][
                    "maximum"
                ] > 0
            ).tolist()
        )

            intersection = (
                a & b
            )

            union = (
                a | b
            )

            jaccard = (
                len(intersection)
                / len(union)
                if union
                else 1.0
            )

            print(
                left,
                "vs",
                right,
                "overlap=",
                len(intersection),
                f"/ {len(a)} + {len(b)}",
                "jaccard=",
                jaccard,
            )

    print()
    print(
        "MQ-3.2 DN-C1 RESPONDER "
        "FINGERPRINT COMPLETE"
    )


if __name__ == "__main__":
    main()
