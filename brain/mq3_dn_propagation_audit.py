from __future__ import annotations

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

CONSENSUS = Path(
    "/home/wil/moscaquant-data/processed/"
    "mq3-dn-consensus-v1.npz"
)

RELEASE_GAIN = 0.9981738484618123


def run(condition):
    W = sparse.load_npz(
        CONNECTOME
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

    relay_types = np.asarray(
        relay["type"],
    ).astype(str)

    consensus = np.load(
        CONSENSUS
    )

    dn_all = np.asarray(
        consensus["neuron_index"],
        dtype=np.int32,
    )

    dn_cluster_all = np.asarray(
        consensus["consensus_cluster"],
        dtype=np.int32,
    )

    assigned = (
        dn_cluster_all >= 0
    )

    dn_indices = dn_all[
        assigned
    ]

    dn_clusters = dn_cluster_all[
        assigned
    ]

    #
    # Direct relay -> assigned DN matrix.
    #
    # Rows = DN postsynaptic targets.
    # Cols = relay presynaptic sources.
    #
    relay_to_dn = W[
        dn_indices,
        :
    ][
        :,
        relay_indices
    ].tocsr()

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
        connectome=W,
        retinal_indices=retinal_indices,
        relay_artifact=RELAY,
        config=VisualTransductionConfig(
            release_gain=RELEASE_GAIN,
        ),
    )

    direct_positive_events = 0
    direct_negative_events = 0

    direct_positive_abs = 0.0
    direct_negative_abs = 0.0

    directly_touched = set()

    positive_touched = set()
    negative_touched = set()

    relay_source_events = 0
    excitatory_source_events = 0

    global_min_voltage = 0.0
    global_max_voltage = 0.0

    min_record = None
    max_record = None

    per_channel = {
        cluster: {
            "min_voltage": 0.0,
            "max_voltage": 0.0,
            "negative_frames": 0,
            "positive_frames": 0,
            "direct_positive_events": 0,
            "direct_negative_events": 0,
        }
        for cluster in range(3)
    }

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
            #
            # runtime.step() uses previous-frame
            # spikes as presynaptic activity.
            #
            prior_relay = (
                runtime.spikes[
                    relay_indices
                ] > 0
            )

            source_count = int(
                np.count_nonzero(
                    prior_relay
                )
            )

            relay_source_events += (
                source_count
            )

            l2_l3 = np.isin(
                relay_types,
                ("L2", "L3"),
            )

            excitatory_source_events += int(
                np.count_nonzero(
                    prior_relay
                    & l2_l3
                )
            )

            direct_current = (
                relay_to_dn
                @ prior_relay.astype(
                    np.float32
                )
            )

            direct_current = np.asarray(
                direct_current,
                dtype=np.float64,
            ).ravel()

            pos = np.flatnonzero(
                direct_current > 0
            )

            neg = np.flatnonzero(
                direct_current < 0
            )

            direct_positive_events += (
                len(pos)
            )

            direct_negative_events += (
                len(neg)
            )

            direct_positive_abs += float(
                direct_current[
                    pos
                ].sum()
            )

            direct_negative_abs += float(
                -direct_current[
                    neg
                ].sum()
            )

            directly_touched.update(
                np.flatnonzero(
                    direct_current != 0
                ).tolist()
            )

            positive_touched.update(
                pos.tolist()
            )

            negative_touched.update(
                neg.tolist()
            )

            for cluster in range(3):
                local = (
                    dn_clusters
                    == cluster
                )

                per_channel[
                    cluster
                ][
                    "direct_positive_events"
                ] += int(
                    np.count_nonzero(
                        direct_current[
                            local
                        ] > 0
                    )
                )

                per_channel[
                    cluster
                ][
                    "direct_negative_events"
                ] += int(
                    np.count_nonzero(
                        direct_current[
                            local
                        ] < 0
                    )
                )

            runtime.step(
                stimulus
                * SENSORY_GAIN
            )

            dn_voltage = np.asarray(
                runtime.voltage[
                    dn_indices
                ],
                dtype=np.float64,
            )

            frame_min = float(
                dn_voltage.min()
            )

            frame_max = float(
                dn_voltage.max()
            )

            if frame_min < global_min_voltage:
                global_min_voltage = (
                    frame_min
                )

                local = int(
                    np.argmin(
                        dn_voltage
                    )
                )

                min_record = {
                    "frame":
                        frame_number,

                    "model_index":
                        int(
                            dn_indices[
                                local
                            ]
                        ),

                    "cluster":
                        int(
                            dn_clusters[
                                local
                            ]
                        ),

                    "voltage":
                        frame_min,
                }

            if frame_max > global_max_voltage:
                global_max_voltage = (
                    frame_max
                )

                local = int(
                    np.argmax(
                        dn_voltage
                    )
                )

                max_record = {
                    "frame":
                        frame_number,

                    "model_index":
                        int(
                            dn_indices[
                                local
                            ]
                        ),

                    "cluster":
                        int(
                            dn_clusters[
                                local
                            ]
                        ),

                    "voltage":
                        frame_max,
                }

            for cluster in range(3):
                local_voltage = dn_voltage[
                    dn_clusters
                    == cluster
                ]

                local_min = float(
                    local_voltage.min()
                )

                local_max = float(
                    local_voltage.max()
                )

                per_channel[
                    cluster
                ][
                    "min_voltage"
                ] = min(
                    per_channel[
                        cluster
                    ][
                        "min_voltage"
                    ],
                    local_min,
                )

                per_channel[
                    cluster
                ][
                    "max_voltage"
                ] = max(
                    per_channel[
                        cluster
                    ][
                        "max_voltage"
                    ],
                    local_max,
                )

                if np.any(
                    local_voltage < 0
                ):
                    per_channel[
                        cluster
                    ][
                        "negative_frames"
                    ] += 1

                if np.any(
                    local_voltage > 0
                ):
                    per_channel[
                        cluster
                    ][
                        "positive_frames"
                    ] += 1

            frame_number += 1

    print()
    print("=" * 72)
    print("CONDITION", condition)
    print("=" * 72)

    print(
        "frames:",
        frame_number,
    )

    print(
        "relay source spike events:",
        relay_source_events,
    )

    print(
        "L2/L3 source spike events:",
        excitatory_source_events,
    )

    print()
    print(
        "direct positive DN-current events:",
        direct_positive_events,
    )

    print(
        "direct negative DN-current events:",
        direct_negative_events,
    )

    print(
        "integrated positive direct current:",
        direct_positive_abs,
    )

    print(
        "integrated negative direct current abs:",
        direct_negative_abs,
    )

    print()
    print(
        "unique directly touched assigned DNs:",
        len(directly_touched),
        "/",
        len(dn_indices),
    )

    print(
        "unique positively touched DNs:",
        len(positive_touched),
    )

    print(
        "unique negatively touched DNs:",
        len(negative_touched),
    )

    print()
    print(
        "global minimum DN voltage:",
        global_min_voltage,
    )

    print(
        "minimum record:",
        min_record,
    )

    print(
        "global maximum DN voltage:",
        global_max_voltage,
    )

    print(
        "maximum record:",
        max_record,
    )

    print()
    print("BY CONSENSUS CHANNEL")

    for cluster in range(3):
        print()
        print(
            f"DN-C{cluster}"
        )

        for key, value in (
            per_channel[
                cluster
            ].items()
        ):
            print(
                f"  {key}:",
                value,
            )


print("=" * 72)
print("MQ-3 ACTIVE RELAY → DN PROPAGATION AUDIT")
print("=" * 72)

run("A")
run("B")

print()
print(
    "MQ-3 ACTIVE PROPAGATION "
    "AUDIT COMPLETE"
)
