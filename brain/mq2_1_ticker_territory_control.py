from __future__ import annotations
from config.paths import data_path

import json
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
from brain.market_temporal import (
    MarketVisionTemporalEncoder,
)
from brain.visual_transduction import (
    VisualTransductionConfig,
    VisualTransductionRuntime,
)
from market.features import compute_features
from market.normalization import CausalNormalizer


CONNECTOME = data_path('processed', 'connectome-baseline-v1.npz')

RETINA = data_path('processed', 'visual-r1-r6-map-v1.npz')

RELAY = data_path('processed', 'visual-relay-map-v1.npz')

TERRITORIES = data_path('processed', 'market-retinal-territories-v1.npz')

TRANSDUCTION_CONFIG = Path(
    "config/sensory/visual-transduction-v1.toml"
)

CONTROL_CONFIG = Path(
    "config/controls/"
    "ticker-territory-permutation-v1.toml"
)

OUTPUT = data_path('experiments', 'mq2-1-ticker-territory-permutation-v1.json')


def build_mappings():
    identity = np.arange(
        6,
        dtype=np.int32,
    )

    reversed_order = identity[
        ::-1
    ].copy()

    mappings = []

    for shift in range(6):
        mappings.append(
            (
                f"rotation-{shift}",
                np.roll(
                    identity,
                    -shift,
                ).copy(),
            )
        )

    for shift in range(6):
        mappings.append(
            (
                f"reverse-rotation-{shift}",
                np.roll(
                    reversed_order,
                    -shift,
                ).copy(),
            )
        )

    return mappings


def validate_balance(mappings):
    counts = np.zeros(
        (6, 6),
        dtype=np.int32,
    )

    for _, mapping in mappings:
        if sorted(
            mapping.tolist()
        ) != list(range(6)):
            raise RuntimeError(
                "mapping is not a permutation"
            )

        for territory_index, asset_index in enumerate(
            mapping
        ):
            counts[
                asset_index,
                territory_index,
            ] += 1

    if not np.all(
        counts == 2
    ):
        raise RuntimeError(
            "mapping design is not balanced"
        )

    return counts


def run_condition(
    condition,
    mapping,
    connectome,
    retinal_indices,
    relay_indices,
    relay_types,
    release_gain,
):
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

    runtime = VisualTransductionRuntime(
        connectome=connectome,
        retinal_indices=retinal_indices,
        relay_artifact=RELAY,
        config=VisualTransductionConfig(
            release_gain=release_gain,
        ),
    )

    n = connectome.shape[0]

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

    class_masks = {
        cell_type: (
            relay_types
            == cell_type
        )
        for cell_type in (
            "L1",
            "L2",
            "L3",
            "Lai",
        )
    }

    retinal_spikes = 0
    relay_spikes = 0
    wider_spikes = 0

    class_spikes = {
        cell_type: 0
        for cell_type in class_masks
    }

    #
    # Attribution traces.
    #
    wider_indices = np.flatnonzero(
        wider_mask
    )

    relay_to_wider = connectome[
        wider_indices,
        :
    ][
        :,
        relay_indices
    ].tocsr()

    l2_l3_mask = np.isin(
        relay_types,
        (
            "L2",
            "L3",
        ),
    )

    decay = np.exp(
        -1.0 / 20.0
    )

    relay_voltage = np.zeros(
        len(wider_indices),
        dtype=np.float64,
    )

    excitatory_voltage = np.zeros(
        len(wider_indices),
        dtype=np.float64,
    )

    relay_peak = 0.0
    excitatory_peak = 0.0
    actual_peak = 0.0
    closest_gap = None

    for observation in range(
        OBSERVATIONS
    ):
        normalized = np.empty(
            (6, 7),
            dtype=np.float32,
        )

        for asset_index in range(6):
            window = market_window_at(
                series[
                    asset_index
                ],
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

        #
        # Critical control operation:
        #
        # mapping[territory] gives the asset row
        # assigned to that retinal territory.
        #
        permuted = normalized[
            mapping
        ]

        frames = encoder.encode_sequence(
            permuted,
            frame_count=FRAME_COUNT,
        )

        for stimulus in frames:
            prior_relay = (
                runtime.spikes[
                    relay_indices
                ] > 0
            )

            relay_voltage *= decay
            excitatory_voltage *= decay

            if np.any(
                prior_relay
            ):
                relay_current = (
                    relay_to_wider
                    @ prior_relay.astype(
                        np.float32
                    )
                )

                excitatory_sources = (
                    prior_relay
                    & l2_l3_mask
                ).astype(
                    np.float32
                )

                excitatory_current = (
                    relay_to_wider
                    @ excitatory_sources
                )

                relay_voltage += np.asarray(
                    relay_current,
                    dtype=np.float64,
                ).ravel()

                excitatory_voltage += np.asarray(
                    excitatory_current,
                    dtype=np.float64,
                ).ravel()

            spikes = (
                runtime.step(
                    stimulus
                    * SENSORY_GAIN
                ) > 0
            )

            retinal_fired = (
                spikes
                & retinal_mask
            )

            relay_fired = (
                spikes
                & relay_mask
            )

            wider_fired = (
                spikes
                & wider_mask
            )

            retinal_spikes += int(
                np.count_nonzero(
                    retinal_fired
                )
            )

            relay_spikes += int(
                np.count_nonzero(
                    relay_fired
                )
            )

            wider_spikes += int(
                np.count_nonzero(
                    wider_fired
                )
            )

            local_relay = spikes[
                relay_indices
            ]

            for (
                cell_type,
                mask,
            ) in class_masks.items():
                class_spikes[
                    cell_type
                ] += int(
                    np.count_nonzero(
                        local_relay
                        & mask
                    )
                )

            relay_peak = max(
                relay_peak,
                float(
                    relay_voltage.max()
                ),
            )

            excitatory_peak = max(
                excitatory_peak,
                float(
                    excitatory_voltage.max()
                ),
            )

            actual_voltage = runtime.voltage[
                wider_mask
            ]

            actual_peak = max(
                actual_peak,
                float(
                    actual_voltage.max()
                ),
            )

            positive_relay = (
                relay_voltage > 0
            )

            if np.any(
                positive_relay
            ):
                local_gap = float(
                    np.min(
                        1.0
                        - actual_voltage[
                            positive_relay
                        ]
                    )
                )

                if (
                    closest_gap is None
                    or local_gap
                    < closest_gap
                ):
                    closest_gap = (
                        local_gap
                    )

    return {
        "retinal_spikes":
            retinal_spikes,

        "relay_spikes":
            relay_spikes,

        "l1_spikes":
            class_spikes["L1"],

        "l2_spikes":
            class_spikes["L2"],

        "l3_spikes":
            class_spikes["L3"],

        "lai_spikes":
            class_spikes["Lai"],

        "excitatory_relay_spikes":
            (
                class_spikes["L2"]
                + class_spikes["L3"]
            ),

        "wider_spikes":
            wider_spikes,

        "relay_only_peak":
            relay_peak,

        "l2_l3_only_peak":
            excitatory_peak,

        "actual_wider_peak":
            actual_peak,

        "closest_threshold_gap":
            closest_gap,
    }


def main():
    with TRANSDUCTION_CONFIG.open(
        "rb"
    ) as handle:
        transduction = tomllib.load(
            handle
        )

    with CONTROL_CONFIG.open(
        "rb"
    ) as handle:
        control = tomllib.load(
            handle
        )

    release_gain = float(
        transduction[
            "transduction"
        ][
            "release_gain"
        ]
    )

    expected_gain = float(
        control[
            "experiment"
        ][
            "release_gain"
        ]
    )

    if release_gain != expected_gain:
        raise RuntimeError(
            "frozen release gain mismatch"
        )

    mappings = build_mappings()

    expected_count = int(
        control[
            "experiment"
        ][
            "mapping_count"
        ]
    )

    if len(mappings) != expected_count:
        raise RuntimeError(
            "mapping count mismatch"
        )

    balance = validate_balance(
        mappings
    )

    print("=" * 72)
    print("TICKER-TERRITORY CONTROL")
    print("=" * 72)

    print(
        "mappings:",
        len(mappings),
    )

    print(
        "each asset appears in each territory:",
        int(balance[0, 0]),
        "times",
    )

    print(
        "frozen release gain:",
        release_gain,
    )

    connectome = sparse.load_npz(
        CONNECTOME
    ).tocsr()

    retina = np.load(
        RETINA
    )

    retinal_indices = np.asarray(
        retina[
            "neuron_index"
        ],
        dtype=np.int32,
    )

    relay = np.load(
        RELAY
    )

    relay_indices = np.asarray(
        relay[
            "neuron_index"
        ],
        dtype=np.int32,
    )

    relay_types = np.asarray(
        relay[
            "type"
        ],
    )

    records = []

    for mapping_index, (
        name,
        mapping,
    ) in enumerate(
        mappings,
        start=1,
    ):
        territory_assets = [
            ASSETS[
                asset_index
            ]
            for asset_index in mapping
        ]

        print()
        print("=" * 72)

        print(
            f"MAPPING {mapping_index}/"
            f"{len(mappings)} — {name}"
        )

        print(
            "T1..T6:",
            territory_assets,
        )

        a = run_condition(
            "A",
            mapping,
            connectome,
            retinal_indices,
            relay_indices,
            relay_types,
            release_gain,
        )

        b = run_condition(
            "B",
            mapping,
            connectome,
            retinal_indices,
            relay_indices,
            relay_types,
            release_gain,
        )

        record = {
            "name": name,
            "territory_assets":
                territory_assets,
            "A": a,
            "B": b,
        }

        records.append(
            record
        )

        print(
            "A relay spikes:",
            a["relay_spikes"],
        )

        print(
            "B relay spikes:",
            b["relay_spikes"],
        )

        print(
            "A excitatory relay:",
            a[
                "excitatory_relay_spikes"
            ],
        )

        print(
            "B excitatory relay:",
            b[
                "excitatory_relay_spikes"
            ],
        )

        print(
            "A L2/L3 peak:",
            a[
                "l2_l3_only_peak"
            ],
        )

        print(
            "B L2/L3 peak:",
            b[
                "l2_l3_only_peak"
            ],
        )

    a_relay_positive = sum(
        item["A"]["relay_spikes"]
        > 0
        for item in records
    )

    b_relay_positive = sum(
        item["B"]["relay_spikes"]
        > 0
        for item in records
    )

    a_excitatory_positive = sum(
        item["A"][
            "excitatory_relay_spikes"
        ] > 0
        for item in records
    )

    b_excitatory_positive = sum(
        item["B"][
            "excitatory_relay_spikes"
        ] > 0
        for item in records
    )

    a_peaks = np.asarray(
        [
            item["A"][
                "l2_l3_only_peak"
            ]
            for item in records
        ],
        dtype=np.float64,
    )

    b_peaks = np.asarray(
        [
            item["B"][
                "l2_l3_only_peak"
            ]
            for item in records
        ],
        dtype=np.float64,
    )

    summary = {
        "mapping_count":
            len(records),

        "A_relay_positive_mappings":
            int(
                a_relay_positive
            ),

        "B_relay_positive_mappings":
            int(
                b_relay_positive
            ),

        "A_excitatory_positive_mappings":
            int(
                a_excitatory_positive
            ),

        "B_excitatory_positive_mappings":
            int(
                b_excitatory_positive
            ),

        "A_l2_l3_peak": {
            "min": float(
                a_peaks.min()
            ),
            "median": float(
                np.median(
                    a_peaks
                )
            ),
            "max": float(
                a_peaks.max()
            ),
        },

        "B_l2_l3_peak": {
            "min": float(
                b_peaks.min()
            ),
            "median": float(
                np.median(
                    b_peaks
                )
            ),
            "max": float(
                b_peaks.max()
            ),
        },
    }

    output = {
        "experiment":
            "mq2-1-ticker-territory-"
            "permutation-v1",

        "release_gain":
            release_gain,

        "assets":
            list(ASSETS),

        "design":
            "balanced_cyclic_and_"
            "reversed_rotations",

        "records":
            records,

        "summary":
            summary,
    }

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT.write_text(
        json.dumps(
            output,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    print()
    print("=" * 72)
    print("PERMUTATION SUMMARY")
    print("=" * 72)

    print(
        "A mappings with relay spikes:",
        f"{a_relay_positive}/"
        f"{len(records)}",
    )

    print(
        "B mappings with relay spikes:",
        f"{b_relay_positive}/"
        f"{len(records)}",
    )

    print(
        "A mappings with excitatory "
        "relay spikes:",
        f"{a_excitatory_positive}/"
        f"{len(records)}",
    )

    print(
        "B mappings with excitatory "
        "relay spikes:",
        f"{b_excitatory_positive}/"
        f"{len(records)}",
    )

    print()
    print(
        "A L2/L3 peak:",
        summary[
            "A_l2_l3_peak"
        ],
    )

    print(
        "B L2/L3 peak:",
        summary[
            "B_l2_l3_peak"
        ],
    )

    print()
    print(
        "results:",
        OUTPUT,
    )

    print()
    print(
        "MQ-2.1 TICKER-TERRITORY "
        "CONTROL COMPLETE"
    )


if __name__ == "__main__":
    main()
