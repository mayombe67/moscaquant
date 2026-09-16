from __future__ import annotations

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


CONNECTOME = Path(
    "/home/wil/moscaquant-data/processed/"
    "connectome-baseline-v1.npz"
)

RETINA = Path(
    "/home/wil/moscaquant-data/processed/"
    "visual-r1-r6-map-v1.npz"
)

RELAY = Path(
    "/home/wil/moscaquant-data/processed/"
    "visual-relay-map-v1.npz"
)

TERRITORIES = Path(
    "/home/wil/moscaquant-data/processed/"
    "market-retinal-territories-v1.npz"
)

TRANSDUCTION_CONFIG = Path(
    "config/sensory/visual-transduction-v1.toml"
)

CONTROL_CONFIG = Path(
    "config/controls/feature-ablation-v1.toml"
)

OUTPUT = Path(
    "/home/wil/moscaquant-data/experiments/"
    "mq2-1-feature-ablation-v1.json"
)


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
    experiments = [
        {
            "name": "baseline",
            "mode": "baseline",
            "feature": None,
        }
    ]

    for feature in FEATURES:
        experiments.append(
            {
                "name": f"remove-{feature}",
                "mode": "remove",
                "feature": feature,
            }
        )

    for feature in FEATURES:
        experiments.append(
            {
                "name": f"isolate-{feature}",
                "mode": "isolate",
                "feature": feature,
            }
        )

    return experiments


def apply_ablation(
    normalized,
    mode,
    feature,
):
    result = normalized.copy()

    if mode == "baseline":
        return result

    feature_index = FEATURES.index(
        feature
    )

    if mode == "remove":
        result[
            :,
            feature_index
        ] = 0.0

        return result

    if mode == "isolate":
        keep = result[
            :,
            feature_index
        ].copy()

        result.fill(0.0)

        result[
            :,
            feature_index
        ] = keep

        return result

    raise ValueError(
        f"unknown ablation mode: {mode}"
    )


def run_condition(
    condition,
    mode,
    feature,
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
        for cell_type in class_masks
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

        ablated = apply_ablation(
            normalized,
            mode,
            feature,
        )

        frames = encoder.encode_sequence(
            ablated,
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
            "feature order does not match "
            "precommitted configuration"
        )

    experiments = build_experiments()

    expected_count = int(
        control[
            "experiment"
        ][
            "experiment_count"
        ]
    )

    if len(experiments) != expected_count:
        raise RuntimeError(
            "ablation count mismatch"
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
    print("MQ-2.1 FEATURE ABLATION")
    print("=" * 72)

    print(
        "experiments:",
        len(experiments),
    )

    print(
        "frozen release gain:",
        release_gain,
    )

    for index, experiment in enumerate(
        experiments,
        start=1,
    ):
        name = experiment[
            "name"
        ]

        mode = experiment[
            "mode"
        ]

        feature = experiment[
            "feature"
        ]

        print()
        print("=" * 72)

        print(
            f"EXPERIMENT {index}/"
            f"{len(experiments)} — {name}"
        )

        a = run_condition(
            "A",
            mode,
            feature,
            connectome,
            retinal_indices,
            relay_indices,
            relay_types,
            release_gain,
        )

        b = run_condition(
            "B",
            mode,
            feature,
            connectome,
            retinal_indices,
            relay_indices,
            relay_types,
            release_gain,
        )

        record = {
            "name": name,
            "mode": mode,
            "feature": feature,
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

    baseline = records[0]

    removal_summary = []
    isolation_summary = []

    for record in records[1:8]:
        removal_summary.append(
            {
                "feature":
                    record["feature"],

                "A_relay_spikes":
                    record["A"][
                        "relay_spikes"
                    ],

                "A_excitatory_relay_spikes":
                    record["A"][
                        "excitatory_relay_spikes"
                    ],

                "A_l2_l3_peak":
                    record["A"][
                        "l2_l3_only_peak"
                    ],

                "B_relay_spikes":
                    record["B"][
                        "relay_spikes"
                    ],

                "B_excitatory_relay_spikes":
                    record["B"][
                        "excitatory_relay_spikes"
                    ],
            }
        )

    for record in records[8:]:
        isolation_summary.append(
            {
                "feature":
                    record["feature"],

                "A_relay_spikes":
                    record["A"][
                        "relay_spikes"
                    ],

                "A_excitatory_relay_spikes":
                    record["A"][
                        "excitatory_relay_spikes"
                    ],

                "A_l2_l3_peak":
                    record["A"][
                        "l2_l3_only_peak"
                    ],

                "B_relay_spikes":
                    record["B"][
                        "relay_spikes"
                    ],

                "B_excitatory_relay_spikes":
                    record["B"][
                        "excitatory_relay_spikes"
                    ],
            }
        )

    output = {
        "experiment":
            "mq2-1-feature-ablation-v1",

        "release_gain":
            release_gain,

        "feature_order":
            list(FEATURES),

        "records":
            records,

        "baseline":
            baseline,

        "leave_one_out":
            removal_summary,

        "single_feature_isolation":
            isolation_summary,
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
    print("BASELINE")
    print("=" * 72)

    print(
        "A relay/excitatory:",
        baseline["A"][
            "relay_spikes"
        ],
        "/",
        baseline["A"][
            "excitatory_relay_spikes"
        ],
    )

    print(
        "B relay/excitatory:",
        baseline["B"][
            "relay_spikes"
        ],
        "/",
        baseline["B"][
            "excitatory_relay_spikes"
        ],
    )

    print()
    print("=" * 72)
    print("LEAVE-ONE-OUT SUMMARY")
    print("=" * 72)

    for item in removal_summary:
        print(
            item["feature"],
            "A relay=",
            item[
                "A_relay_spikes"
            ],
            "A excit=",
            item[
                "A_excitatory_relay_spikes"
            ],
            "A peak=",
            item[
                "A_l2_l3_peak"
            ],
            "B relay=",
            item[
                "B_relay_spikes"
            ],
        )

    print()
    print("=" * 72)
    print("SINGLE-FEATURE ISOLATION SUMMARY")
    print("=" * 72)

    for item in isolation_summary:
        print(
            item["feature"],
            "A relay=",
            item[
                "A_relay_spikes"
            ],
            "A excit=",
            item[
                "A_excitatory_relay_spikes"
            ],
            "A peak=",
            item[
                "A_l2_l3_peak"
            ],
            "B relay=",
            item[
                "B_relay_spikes"
            ],
        )

    print()
    print(
        "results:",
        OUTPUT,
    )

    print()
    print(
        "MQ-2.1 FEATURE ABLATION COMPLETE"
    )


if __name__ == "__main__":
    main()
