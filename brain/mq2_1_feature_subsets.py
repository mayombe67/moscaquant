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
    "config/controls/feature-subsets-v2.toml"
)

OUTPUT = data_path('experiments', 'mq2-1-feature-subsets-v2.json')


FEATURES = (
    "return",
    "momentum",
    "volume_deviation",
    "realized_volatility",
    "spread",
    "order_book_imbalance",
    "return_sign_entropy",
)


def build_experiments():
    experiments = []

    for mask in range(
        1 << len(FEATURES)
    ):
        active_features = [
            FEATURES[index]
            for index in range(
                len(FEATURES)
            )
            if mask & (1 << index)
        ]

        experiments.append(
            {
                "mask": mask,
                "name": (
                    "empty"
                    if not active_features
                    else "+".join(
                        active_features
                    )
                ),
                "features":
                    active_features,
                "feature_count":
                    len(active_features),
            }
        )

    return experiments


def apply_subset(
    normalized,
    active_features,
):
    result = np.zeros_like(
        normalized
    )

    for feature in active_features:
        feature_index = FEATURES.index(
            feature
        )

        result[
            :,
            feature_index
        ] = normalized[
            :,
            feature_index
        ]

    return result


def run_condition(
    condition,
    active_features,
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

    neuron_count = connectome.shape[0]

    retinal_mask = np.zeros(
        neuron_count,
        dtype=bool,
    )
    retinal_mask[
        retinal_indices
    ] = True

    relay_mask = np.zeros(
        neuron_count,
        dtype=bool,
    )
    relay_mask[
        relay_indices
    ] = True

    wider_mask = ~(
        retinal_mask
        | relay_mask
    )

    wider_indices = np.flatnonzero(
        wider_mask
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

    l2_l3_mask = np.isin(
        relay_types,
        (
            "L2",
            "L3",
        ),
    )

    relay_to_wider = connectome[
        wider_indices,
        :
    ][
        :,
        relay_indices
    ].tocsr()

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

    retinal_spikes = 0
    relay_spikes = 0
    wider_spikes = 0

    class_spikes = {
        cell_type: 0
        for cell_type
        in class_masks
    }

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

        subset_input = apply_subset(
            normalized,
            active_features,
        )

        frames = (
            encoder.encode_sequence(
                subset_input,
                frame_count=FRAME_COUNT,
            )
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

                excitatory_voltage += (
                    np.asarray(
                        excitatory_current,
                        dtype=np.float64,
                    ).ravel()
                )

            spikes = (
                runtime.step(
                    stimulus
                    * SENSORY_GAIN
                ) > 0
            )

            retinal_spikes += int(
                np.count_nonzero(
                    spikes
                    & retinal_mask
                )
            )

            relay_spikes += int(
                np.count_nonzero(
                    spikes
                    & relay_mask
                )
            )

            wider_spikes += int(
                np.count_nonzero(
                    spikes
                    & wider_mask
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

            actual_voltage = (
                runtime.voltage[
                    wider_mask
                ]
            )

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
                gap = float(
                    np.min(
                        1.0
                        - actual_voltage[
                            positive_relay
                        ]
                    )
                )

                if (
                    closest_gap is None
                    or gap < closest_gap
                ):
                    closest_gap = gap

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

    configured_features = tuple(
        control[
            "features"
        ][
            "order"
        ]
    )

    if configured_features != FEATURES:
        raise RuntimeError(
            "feature order does not "
            "match precommitted config"
        )

    experiments = build_experiments()

    expected_count = int(
        control[
            "experiment"
        ][
            "subset_count"
        ]
    )

    if len(
        experiments
    ) != expected_count:
        raise RuntimeError(
            "subset count mismatch"
        )

    print(
        "loading frozen connectome..."
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

    print()
    print("=" * 72)
    print(
        "MQ-2.1 EXHAUSTIVE "
        "FEATURE SUBSET CONTROL"
    )
    print("=" * 72)

    print(
        "subsets:",
        len(experiments),
    )

    print(
        "frozen release gain:",
        release_gain,
    )

    for (
        experiment_index,
        experiment,
    ) in enumerate(
        experiments,
        start=1,
    ):
        mask = experiment[
            "mask"
        ]

        name = experiment[
            "name"
        ]

        active_features = experiment[
            "features"
        ]

        feature_count = experiment[
            "feature_count"
        ]

        print()
        print("=" * 72)

        print(
            f"SUBSET "
            f"{experiment_index}/"
            f"{len(experiments)} "
            f"mask={mask:03d}"
        )

        print(
            "features:",
            active_features,
        )

        a = run_condition(
            "A",
            active_features,
            connectome,
            retinal_indices,
            relay_indices,
            relay_types,
            release_gain,
        )

        b = run_condition(
            "B",
            active_features,
            connectome,
            retinal_indices,
            relay_indices,
            relay_types,
            release_gain,
        )

        record = {
            "mask": mask,
            "name": name,
            "feature_count":
                feature_count,
            "features":
                active_features,
            "A": a,
            "B": b,
        }

        records.append(
            record
        )

        print(
            "A relay/excitatory:",
            a["relay_spikes"],
            "/",
            a[
                "excitatory_relay_spikes"
            ],
        )

        print(
            "B relay/excitatory:",
            b["relay_spikes"],
            "/",
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

    a_excitatory = [
        record
        for record in records
        if record[
            "A"
        ][
            "excitatory_relay_spikes"
        ] > 0
    ]

    b_relay_positive = [
        record
        for record in records
        if record[
            "B"
        ][
            "relay_spikes"
        ] > 0
    ]

    b_excitatory = [
        record
        for record in records
        if record[
            "B"
        ][
            "excitatory_relay_spikes"
        ] > 0
    ]

    minimal_count = (
        min(
            record[
                "feature_count"
            ]
            for record
            in a_excitatory
        )
        if a_excitatory
        else None
    )

    minimal_a_excitatory = [
        record
        for record
        in a_excitatory
        if record[
            "feature_count"
        ] == minimal_count
    ]

    volume_in_all_a_excitatory = (
        all(
            "volume_deviation"
            in record[
                "features"
            ]
            for record
            in a_excitatory
        )
        if a_excitatory
        else None
    )

    clean_a_excitatory = [
        record
        for record
        in a_excitatory
        if record[
            "B"
        ][
            "relay_spikes"
        ] == 0
    ]

    minimal_clean_count = (
        min(
            record[
                "feature_count"
            ]
            for record
            in clean_a_excitatory
        )
        if clean_a_excitatory
        else None
    )

    minimal_clean_a_excitatory = [
        record
        for record
        in clean_a_excitatory
        if record[
            "feature_count"
        ] == minimal_clean_count
    ]

    summary = {
        "total_subsets":
            len(records),

        "A_excitatory_subset_count":
            len(a_excitatory),

        "B_relay_positive_subset_count":
            len(b_relay_positive),

        "B_excitatory_subset_count":
            len(b_excitatory),

        "minimal_A_excitatory_feature_count":
            minimal_count,

        "minimal_A_excitatory_subsets": [
            {
                "mask":
                    record["mask"],

                "features":
                    record[
                        "features"
                    ],

                "A_relay_spikes":
                    record[
                        "A"
                    ][
                        "relay_spikes"
                    ],

                "A_excitatory_relay_spikes":
                    record[
                        "A"
                    ][
                        "excitatory_relay_spikes"
                    ],

                "A_l2_l3_only_peak":
                    record[
                        "A"
                    ][
                        "l2_l3_only_peak"
                    ],

                "B_relay_spikes":
                    record[
                        "B"
                    ][
                        "relay_spikes"
                    ],
            }
            for record
            in minimal_a_excitatory
        ],

        "minimal_clean_A_excitatory_feature_count":
            minimal_clean_count,

        "minimal_clean_A_excitatory_subsets": [
            {
                "mask":
                    record["mask"],

                "features":
                    record[
                        "features"
                    ],

                "A_relay_spikes":
                    record[
                        "A"
                    ][
                        "relay_spikes"
                    ],

                "A_excitatory_relay_spikes":
                    record[
                        "A"
                    ][
                        "excitatory_relay_spikes"
                    ],

                "A_l2_l3_only_peak":
                    record[
                        "A"
                    ][
                        "l2_l3_only_peak"
                    ],

                "B_relay_spikes":
                    record[
                        "B"
                    ][
                        "relay_spikes"
                    ],
            }
            for record
            in minimal_clean_a_excitatory
        ],

        "volume_deviation_present_in_all_A_excitatory_subsets":
            volume_in_all_a_excitatory,

        "B_relay_positive_subsets": [
            {
                "mask":
                    record["mask"],

                "features":
                    record[
                        "features"
                    ],

                "B_relay_spikes":
                    record[
                        "B"
                    ][
                        "relay_spikes"
                    ],

                "B_excitatory_relay_spikes":
                    record[
                        "B"
                    ][
                        "excitatory_relay_spikes"
                    ],
            }
            for record
            in b_relay_positive
        ],
    }

    output = {
        "experiment":
            "mq2-1-feature-subsets-v2",

        "release_gain":
            release_gain,

        "feature_order":
            list(FEATURES),

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
    print(
        "EXHAUSTIVE FEATURE "
        "SUBSET SUMMARY"
    )
    print("=" * 72)

    print(
        "total subsets:",
        len(records),
    )

    print(
        "A subsets with "
        "excitatory relay:",
        len(a_excitatory),
    )

    print(
        "B subsets with "
        "relay activity:",
        len(b_relay_positive),
    )

    print(
        "B subsets with "
        "excitatory relay:",
        len(b_excitatory),
    )

    print(
        "minimal A excitatory "
        "feature count:",
        minimal_count,
    )

    print(
        "minimal clean A excitatory "
        "feature count:",
        minimal_clean_count,
    )

    print()
    print(
        "MINIMAL A "
        "EXCITATORY SUBSETS"
    )

    for record in minimal_a_excitatory:
        print(
            record[
                "features"
            ],
            "A relay=",
            record[
                "A"
            ][
                "relay_spikes"
            ],
            "A excit=",
            record[
                "A"
            ][
                "excitatory_relay_spikes"
            ],
            "A peak=",
            record[
                "A"
            ][
                "l2_l3_only_peak"
            ],
            "B relay=",
            record[
                "B"
            ][
                "relay_spikes"
            ],
        )

    print()
    print(
        "MINIMAL CLEAN A "
        "EXCITATORY SUBSETS"
    )

    for record in (
        minimal_clean_a_excitatory
    ):
        print(
            record[
                "features"
            ],
            "A relay=",
            record[
                "A"
            ][
                "relay_spikes"
            ],
            "A excit=",
            record[
                "A"
            ][
                "excitatory_relay_spikes"
            ],
            "A peak=",
            record[
                "A"
            ][
                "l2_l3_only_peak"
            ],
            "B relay=",
            record[
                "B"
            ][
                "relay_spikes"
            ],
        )

    print()
    print(
        "volume_deviation present "
        "in every A-excitatory subset:",
        volume_in_all_a_excitatory,
    )

    print()
    print(
        "B RELAY-POSITIVE SUBSETS"
    )

    for record in b_relay_positive:
        print(
            record[
                "features"
            ],
            "B relay=",
            record[
                "B"
            ][
                "relay_spikes"
            ],
            "B excit=",
            record[
                "B"
            ][
                "excitatory_relay_spikes"
            ],
        )

    print()
    print(
        "results:",
        OUTPUT,
    )

    print()
    print(
        "MQ-2.1 EXHAUSTIVE "
        "FEATURE SUBSET "
        "CONTROL COMPLETE"
    )


if __name__ == "__main__":
    main()
