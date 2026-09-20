from __future__ import annotations
from config.paths import data_path

import hashlib
from pathlib import Path

import numpy as np
import pyarrow.feather as feather
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


CONNECTOME = data_path('processed', 'connectome-baseline-v1.npz')

RETINA = data_path('processed', 'visual-r1-r6-map-v1.npz')

TERRITORIES = data_path('processed', 'market-retinal-territories-v1.npz')

NEURON_IDS = data_path('processed', 'neuron_ids.npy')

ANNOTATIONS = data_path('raw', 'body-annotations-male-cns-v1.0-minconf-0.5.feather')


RELAY_TYPES = (
    "L1",
    "L2",
    "L3",
    "Lai",
)


def normalized_stream(condition: str):
    if condition == "NEUTRAL":
        for _ in range(OBSERVATIONS):
            yield np.zeros(
                (6, 7),
                dtype=np.float32,
            )
        return

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

        yield normalized


def load_relay_population(
    connectome,
    neuron_ids,
    retinal_indices,
):
    print("loading MaleCNS relay annotations...")

    table = feather.read_table(
        ANNOTATIONS,
        columns=[
            "bodyId",
            "type",
        ],
    )

    body_ids = table[
        "bodyId"
    ].to_pylist()

    types = table[
        "type"
    ].to_pylist()

    type_by_body = {}

    for body_id, cell_type in zip(
        body_ids,
        types,
    ):
        if (
            body_id is not None
            and cell_type
        ):
            type_by_body[
                int(body_id)
            ] = str(cell_type)

    retinal_mask = np.zeros(
        connectome.shape[0],
        dtype=bool,
    )

    retinal_mask[
        retinal_indices
    ] = True

    #
    # Direct R1-R6 targets only.
    #
    retinal_output = connectome[
        :,
        retinal_indices
    ].tocsr()

    target_mask = (
        np.diff(
            retinal_output.indptr
        ) > 0
    ) & ~retinal_mask

    candidate_indices = np.flatnonzero(
        target_mask
    )

    relay_indices = []
    relay_types = []

    for index in candidate_indices:
        body_id = int(
            neuron_ids[index]
        )

        cell_type = type_by_body.get(
            body_id
        )

        if cell_type in RELAY_TYPES:
            relay_indices.append(
                int(index)
            )

            relay_types.append(
                cell_type
            )

    relay_indices = np.asarray(
        relay_indices,
        dtype=np.int32,
    )

    relay_types = np.asarray(
        relay_types,
        dtype="U8",
    )

    class_masks = {
        relay_type: (
            relay_types
            == relay_type
        )
        for relay_type in RELAY_TYPES
    }

    print()
    print("MQ-2.1 RELAY POPULATION")

    print(
        "  total relay neurons:",
        len(relay_indices),
    )

    for relay_type in RELAY_TYPES:
        print(
            f"  {relay_type}:",
            int(
                np.count_nonzero(
                    class_masks[
                        relay_type
                    ]
                )
            ),
        )

    #
    # Small first-hop matrix only:
    #
    # rows = L1/L2/L3/Lai
    # cols = placed R1-R6
    #
    relay_from_retina = connectome[
        relay_indices,
        :
    ][
        :,
        retinal_indices
    ].tocsr()

    return (
        relay_indices,
        class_masks,
        relay_from_retina,
    )


def sha256_array(array):
    digest = hashlib.sha256()

    digest.update(
        np.ascontiguousarray(
            array
        ).tobytes()
    )

    return digest.hexdigest()


def probe_condition(
    condition,
    connectome,
    retinal_indices,
    relay_indices,
    class_masks,
    relay_from_retina,
):
    print()
    print("=" * 72)
    print(
        f"VISUAL RELAY PROBE — {condition}"
    )
    print("=" * 72)

    encoder = MarketVisionTemporalEncoder(
        TERRITORIES
    )

    runtime = LIFRuntime(
        connectome
    )

    class_data = {
        relay_type: {
            "mean_inhibition": [],
            "total_inhibition": [],
            "total_release": [],
            "peak_release": [],
            "release_cells": [],
        }
        for relay_type in RELAY_TYPES
    }

    previous_magnitude = np.zeros(
        len(relay_indices),
        dtype=np.float32,
    )

    retinal_spike_frames = 0
    frame_number = 0

    for normalized in normalized_stream(
        condition
    ):
        retinal_frames = (
            encoder.encode_sequence(
                normalized,
                frame_count=FRAME_COUNT,
            )
        )

        for stimulus in retinal_frames:
            #
            # LIFRuntime uses prior-frame spikes for
            # synaptic transmission.
            #
            previous_retinal_spikes = (
                runtime.spikes[
                    retinal_indices
                ]
            )

            if np.any(
                previous_retinal_spikes
            ):
                retinal_spike_frames += 1

            direct_current = (
                relay_from_retina
                @ previous_retinal_spikes
            )

            direct_current = np.asarray(
                direct_current
            ).ravel()

            #
            # Histaminergic R1-R6 output is negative
            # in the frozen signed connectome.
            #
            # Convert it to a positive inhibition
            # magnitude for measurement only.
            #
            inhibition_magnitude = np.maximum(
                -direct_current,
                0.0,
            )

            #
            # Release from inhibition:
            #
            # positive only when inhibition becomes
            # weaker compared with the prior frame.
            #
            release = np.maximum(
                previous_magnitude
                - inhibition_magnitude,
                0.0,
            )

            for relay_type in RELAY_TYPES:
                mask = class_masks[
                    relay_type
                ]

                magnitude = (
                    inhibition_magnitude[
                        mask
                    ]
                )

                class_release = release[
                    mask
                ]

                class_data[
                    relay_type
                ][
                    "mean_inhibition"
                ].append(
                    float(
                        magnitude.mean()
                    )
                )

                class_data[
                    relay_type
                ][
                    "total_inhibition"
                ].append(
                    float(
                        magnitude.sum()
                    )
                )

                class_data[
                    relay_type
                ][
                    "total_release"
                ].append(
                    float(
                        class_release.sum()
                    )
                )

                class_data[
                    relay_type
                ][
                    "peak_release"
                ].append(
                    float(
                        class_release.max()
                    )
                    if len(class_release)
                    else 0.0
                )

                class_data[
                    relay_type
                ][
                    "release_cells"
                ].append(
                    int(
                        np.count_nonzero(
                            class_release
                            > 0
                        )
                    )
                )

            previous_magnitude = (
                inhibition_magnitude
            )

            runtime.step(
                stimulus
                * SENSORY_GAIN
            )

            frame_number += 1

    print(
        "frames:",
        frame_number,
    )

    print(
        "retinal spike source frames:",
        retinal_spike_frames,
    )

    print()

    result = {}

    for relay_type in RELAY_TYPES:
        arrays = {
            key: np.asarray(
                values
            )
            for key, values in class_data[
                relay_type
            ].items()
        }

        active_inhibition_frames = int(
            np.count_nonzero(
                arrays[
                    "total_inhibition"
                ] > 0
            )
        )

        release_frames = int(
            np.count_nonzero(
                arrays[
                    "total_release"
                ] > 0
            )
        )

        total_inhibition = float(
            arrays[
                "total_inhibition"
            ].sum()
        )

        total_release = float(
            arrays[
                "total_release"
            ].sum()
        )

        max_mean_inhibition = float(
            arrays[
                "mean_inhibition"
            ].max()
        )

        peak_release = float(
            arrays[
                "peak_release"
            ].max()
        )

        max_release_cells = int(
            arrays[
                "release_cells"
            ].max()
        )

        trajectory = np.column_stack(
            (
                arrays[
                    "mean_inhibition"
                ],
                arrays[
                    "total_inhibition"
                ],
                arrays[
                    "total_release"
                ],
                arrays[
                    "release_cells"
                ],
            )
        )

        trajectory_hash = (
            sha256_array(
                trajectory
            )
        )

        result[
            relay_type
        ] = {
            "total_inhibition": (
                total_inhibition
            ),
            "total_release": (
                total_release
            ),
            "release_frames": (
                release_frames
            ),
            "hash": trajectory_hash,
        }

        print(relay_type)
        print(
            "  inhibition-active frames:",
            active_inhibition_frames,
        )
        print(
            "  release-active frames:",
            release_frames,
        )
        print(
            "  integrated inhibition:",
            total_inhibition,
        )
        print(
            "  integrated release:",
            total_release,
        )
        print(
            "  max mean inhibition:",
            max_mean_inhibition,
        )
        print(
            "  peak single-cell release:",
            peak_release,
        )
        print(
            "  max releasing cells/frame:",
            max_release_cells,
        )
        print(
            "  trajectory sha256:",
            trajectory_hash,
        )
        print()

    return result


def main():
    print("loading frozen biological connectome...")

    connectome = sparse.load_npz(
        CONNECTOME
    ).tocsr()

    print(
        "shape:",
        connectome.shape,
        "nnz:",
        connectome.nnz,
    )

    retina = np.load(
        RETINA
    )

    retinal_indices = np.asarray(
        retina[
            "neuron_index"
        ],
        dtype=np.int32,
    )

    neuron_ids = np.load(
        NEURON_IDS
    )

    (
        relay_indices,
        class_masks,
        relay_from_retina,
    ) = load_relay_population(
        connectome,
        neuron_ids,
        retinal_indices,
    )

    results = {}

    for condition in (
        "NEUTRAL",
        "A",
        "B",
    ):
        results[
            condition
        ] = probe_condition(
            condition,
            connectome,
            retinal_indices,
            relay_indices,
            class_masks,
            relay_from_retina,
        )

    print()
    print("=" * 72)
    print("CONDITION DISCRIMINATION")
    print("=" * 72)

    for relay_type in RELAY_TYPES:
        neutral = results[
            "NEUTRAL"
        ][
            relay_type
        ]

        a = results[
            "A"
        ][
            relay_type
        ]

        b = results[
            "B"
        ][
            relay_type
        ]

        print()
        print(relay_type)

        print(
            "  neutral != A:",
            neutral["hash"]
            != a["hash"],
        )

        print(
            "  neutral != B:",
            neutral["hash"]
            != b["hash"],
        )

        print(
            "  A != B:",
            a["hash"]
            != b["hash"],
        )

        print(
            "  release totals "
            "(neutral / A / B):",
            neutral[
                "total_release"
            ],
            "/",
            a[
                "total_release"
            ],
            "/",
            b[
                "total_release"
            ],
        )

        print(
            "  release frames "
            "(neutral / A / B):",
            neutral[
                "release_frames"
            ],
            "/",
            a[
                "release_frames"
            ],
            "/",
            b[
                "release_frames"
            ],
        )

    print()
    print(
        "VISUAL RELAY PROBE PASS"
    )


if __name__ == "__main__":
    main()
