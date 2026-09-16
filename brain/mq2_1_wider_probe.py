from __future__ import annotations

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

NEURON_IDS = Path(
    "/home/wil/moscaquant-data/processed/"
    "neuron_ids.npy"
)

CONFIG = Path(
    "config/sensory/visual-transduction-v1.toml"
)


def run_condition(
    condition,
    connectome,
    retinal_indices,
    relay_indices,
    relay_types,
    neuron_ids,
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
    retinal_mask[retinal_indices] = True

    relay_mask = np.zeros(
        n,
        dtype=bool,
    )
    relay_mask[relay_indices] = True

    wider_mask = ~(
        retinal_mask
        | relay_mask
    )

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

    total_positive_events = 0
    total_negative_events = 0

    total_positive_current = 0.0
    total_negative_abs_current = 0.0

    strongest_positive_current = 0.0
    strongest_negative_current = 0.0

    strongest_positive_frame = None
    strongest_negative_frame = None

    strongest_positive_target = None
    strongest_negative_target = None

    frames_with_positive_current = 0
    frames_with_negative_current = 0

    relay_source_frames = 0
    excitatory_source_frames = 0
    inhibitory_source_frames = 0

    l2_source_spikes = 0
    l3_source_spikes = 0
    l1_source_spikes = 0
    lai_source_spikes = 0

    max_wider_voltage = 0.0
    min_wider_voltage = 0.0

    max_voltage_frame = None
    min_voltage_frame = None

    max_voltage_target = None
    min_voltage_target = None

    wider_spikes = 0

    frame_number = 0

    neutral_or_market_peak_history = []

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
            # These are the relay spikes from
            # the previous frame. They are the
            # presynaptic sources consumed by
            # this frame's connectome update.
            #
            prior_relay_spikes = (
                runtime.spikes[
                    relay_indices
                ] > 0
            )

            if np.any(
                prior_relay_spikes
            ):
                relay_source_frames += 1

                local_types = relay_types[
                    prior_relay_spikes
                ]

                l1_count = int(
                    np.count_nonzero(
                        local_types == "L1"
                    )
                )

                l2_count = int(
                    np.count_nonzero(
                        local_types == "L2"
                    )
                )

                l3_count = int(
                    np.count_nonzero(
                        local_types == "L3"
                    )
                )

                lai_count = int(
                    np.count_nonzero(
                        local_types == "Lai"
                    )
                )

                l1_source_spikes += l1_count
                l2_source_spikes += l2_count
                l3_source_spikes += l3_count
                lai_source_spikes += lai_count

                if (
                    l2_count
                    + l3_count
                ) > 0:
                    excitatory_source_frames += 1

                if (
                    l1_count
                    + lai_count
                ) > 0:
                    inhibitory_source_frames += 1

                source_vector = (
                    prior_relay_spikes.astype(
                        np.float32
                    )
                )

                wider_current = (
                    relay_to_wider
                    @ source_vector
                )

                wider_current = np.asarray(
                    wider_current,
                    dtype=np.float32,
                ).ravel()

                positive_mask = (
                    wider_current > 0
                )

                negative_mask = (
                    wider_current < 0
                )

                positive_count = int(
                    np.count_nonzero(
                        positive_mask
                    )
                )

                negative_count = int(
                    np.count_nonzero(
                        negative_mask
                    )
                )

                total_positive_events += (
                    positive_count
                )

                total_negative_events += (
                    negative_count
                )

                if positive_count:
                    frames_with_positive_current += 1

                    positive_values = (
                        wider_current[
                            positive_mask
                        ]
                    )

                    total_positive_current += float(
                        positive_values.sum()
                    )

                    local_index = int(
                        np.argmax(
                            wider_current
                        )
                    )

                    value = float(
                        wider_current[
                            local_index
                        ]
                    )

                    if (
                        value
                        > strongest_positive_current
                    ):
                        strongest_positive_current = (
                            value
                        )

                        strongest_positive_frame = (
                            frame_number
                        )

                        strongest_positive_target = int(
                            wider_indices[
                                local_index
                            ]
                        )

                if negative_count:
                    frames_with_negative_current += 1

                    negative_values = (
                        wider_current[
                            negative_mask
                        ]
                    )

                    total_negative_abs_current += float(
                        -negative_values.sum()
                    )

                    local_index = int(
                        np.argmin(
                            wider_current
                        )
                    )

                    value = float(
                        wider_current[
                            local_index
                        ]
                    )

                    if (
                        value
                        < strongest_negative_current
                    ):
                        strongest_negative_current = (
                            value
                        )

                        strongest_negative_frame = (
                            frame_number
                        )

                        strongest_negative_target = int(
                            wider_indices[
                                local_index
                            ]
                        )

            spikes = runtime.step(
                stimulus
                * SENSORY_GAIN
            ) > 0

            wider_fired = (
                spikes
                & wider_mask
            )

            wider_spikes += int(
                np.count_nonzero(
                    wider_fired
                )
            )

            wider_voltage = runtime.voltage[
                wider_mask
            ]

            frame_max = float(
                wider_voltage.max()
            )

            frame_min = float(
                wider_voltage.min()
            )

            neutral_or_market_peak_history.append(
                frame_max
            )

            if (
                max_voltage_frame is None
                or frame_max
                > max_wider_voltage
            ):
                max_wider_voltage = (
                    frame_max
                )

                local_index = int(
                    np.argmax(
                        wider_voltage
                    )
                )

                max_voltage_frame = (
                    frame_number
                )

                max_voltage_target = int(
                    wider_indices[
                        local_index
                    ]
                )

            if (
                min_voltage_frame is None
                or frame_min
                < min_wider_voltage
            ):
                min_wider_voltage = (
                    frame_min
                )

                local_index = int(
                    np.argmin(
                        wider_voltage
                    )
                )

                min_voltage_frame = (
                    frame_number
                )

                min_voltage_target = int(
                    wider_indices[
                        local_index
                    ]
                )

            frame_number += 1

    def body_id(index):
        if index is None:
            return None

        return int(
            neuron_ids[
                index
            ]
        )

    return {
        "condition":
            condition,

        "frames":
            frame_number,

        "relay_source_frames":
            relay_source_frames,

        "excitatory_source_frames":
            excitatory_source_frames,

        "inhibitory_source_frames":
            inhibitory_source_frames,

        "l1_source_spikes":
            l1_source_spikes,

        "l2_source_spikes":
            l2_source_spikes,

        "l3_source_spikes":
            l3_source_spikes,

        "lai_source_spikes":
            lai_source_spikes,

        "positive_events":
            total_positive_events,

        "negative_events":
            total_negative_events,

        "positive_current":
            total_positive_current,

        "negative_abs_current":
            total_negative_abs_current,

        "positive_frames":
            frames_with_positive_current,

        "negative_frames":
            frames_with_negative_current,

        "strongest_positive":
            strongest_positive_current,

        "strongest_positive_frame":
            strongest_positive_frame,

        "strongest_positive_target":
            strongest_positive_target,

        "strongest_positive_body":
            body_id(
                strongest_positive_target
            ),

        "strongest_negative":
            strongest_negative_current,

        "strongest_negative_frame":
            strongest_negative_frame,

        "strongest_negative_target":
            strongest_negative_target,

        "strongest_negative_body":
            body_id(
                strongest_negative_target
            ),

        "max_voltage":
            max_wider_voltage,

        "max_voltage_frame":
            max_voltage_frame,

        "max_voltage_target":
            max_voltage_target,

        "max_voltage_body":
            body_id(
                max_voltage_target
            ),

        "distance_to_threshold":
            1.0
            - max_wider_voltage,

        "min_voltage":
            min_wider_voltage,

        "min_voltage_frame":
            min_voltage_frame,

        "min_voltage_target":
            min_voltage_target,

        "min_voltage_body":
            body_id(
                min_voltage_target
            ),

        "wider_spikes":
            wider_spikes,
    }


def summarize(result):
    print()
    print("=" * 72)
    print(
        f"CONDITION {result['condition']}"
    )
    print("=" * 72)

    print(
        "relay-source frames:",
        result[
            "relay_source_frames"
        ],
    )

    print(
        "excitatory-source frames:",
        result[
            "excitatory_source_frames"
        ],
    )

    print(
        "inhibitory-source frames:",
        result[
            "inhibitory_source_frames"
        ],
    )

    print()
    print("relay source spikes:")

    print(
        "  L1:",
        result["l1_source_spikes"],
    )

    print(
        "  L2:",
        result["l2_source_spikes"],
    )

    print(
        "  L3:",
        result["l3_source_spikes"],
    )

    print(
        "  Lai:",
        result["lai_source_spikes"],
    )

    print()
    print("second-hop current:")

    print(
        "  positive events:",
        result["positive_events"],
    )

    print(
        "  negative events:",
        result["negative_events"],
    )

    print(
        "  frames with positive:",
        result["positive_frames"],
    )

    print(
        "  frames with negative:",
        result["negative_frames"],
    )

    print(
        "  integrated positive:",
        result["positive_current"],
    )

    print(
        "  integrated negative abs:",
        result["negative_abs_current"],
    )

    print()
    print(
        "strongest positive:",
        result["strongest_positive"],
    )

    print(
        "  frame:",
        result[
            "strongest_positive_frame"
        ],
    )

    print(
        "  target index:",
        result[
            "strongest_positive_target"
        ],
    )

    print(
        "  target body_id:",
        result[
            "strongest_positive_body"
        ],
    )

    print()
    print(
        "strongest negative:",
        result["strongest_negative"],
    )

    print(
        "  frame:",
        result[
            "strongest_negative_frame"
        ],
    )

    print(
        "  target index:",
        result[
            "strongest_negative_target"
        ],
    )

    print(
        "  target body_id:",
        result[
            "strongest_negative_body"
        ],
    )

    print()
    print("wider membrane:")

    print(
        "  max voltage:",
        result["max_voltage"],
    )

    print(
        "  frame:",
        result[
            "max_voltage_frame"
        ],
    )

    print(
        "  target index:",
        result[
            "max_voltage_target"
        ],
    )

    print(
        "  target body_id:",
        result[
            "max_voltage_body"
        ],
    )

    print(
        "  distance to +1:",
        result[
            "distance_to_threshold"
        ],
    )

    print()
    print(
        "  min voltage:",
        result["min_voltage"],
    )

    print(
        "  min frame:",
        result[
            "min_voltage_frame"
        ],
    )

    print(
        "  min target index:",
        result[
            "min_voltage_target"
        ],
    )

    print(
        "  min target body_id:",
        result[
            "min_voltage_body"
        ],
    )

    print()
    print(
        "actual wider spikes:",
        result["wider_spikes"],
    )


def main():
    with CONFIG.open(
        "rb"
    ) as handle:
        config = tomllib.load(
            handle
        )

    release_gain = float(
        config[
            "transduction"
        ][
            "release_gain"
        ]
    )

    print(
        "frozen release gain:",
        release_gain,
    )

    print(
        "loading frozen artifacts..."
    )

    connectome = sparse.load_npz(
        CONNECTOME
    ).tocsr()

    retina = np.load(
        RETINA
    )

    retinal_indices = np.asarray(
        retina["neuron_index"],
        dtype=np.int32,
    )

    relay = np.load(
        RELAY
    )

    relay_indices = np.asarray(
        relay["neuron_index"],
        dtype=np.int32,
    )

    relay_types = np.asarray(
        relay["type"],
    )

    neuron_ids = np.load(
        NEURON_IDS
    )

    a = run_condition(
        "A",
        connectome,
        retinal_indices,
        relay_indices,
        relay_types,
        neuron_ids,
        release_gain,
    )

    b = run_condition(
        "B",
        connectome,
        retinal_indices,
        relay_indices,
        relay_types,
        neuron_ids,
        release_gain,
    )

    summarize(a)
    summarize(b)

    print()
    print("=" * 72)
    print("A/B SECOND-HOP COMPARISON")
    print("=" * 72)

    print(
        "positive current events:",
        f"A={a['positive_events']}",
        f"B={b['positive_events']}",
    )

    print(
        "negative current events:",
        f"A={a['negative_events']}",
        f"B={b['negative_events']}",
    )

    print(
        "max wider voltage:",
        f"A={a['max_voltage']}",
        f"B={b['max_voltage']}",
    )

    print(
        "wider spikes:",
        f"A={a['wider_spikes']}",
        f"B={b['wider_spikes']}",
    )

    if (
        a["positive_events"] > 0
    ):
        print()
        print(
            "A relay -> wider positive "
            "synaptic propagation: OBSERVED"
        )

    if (
        b["positive_events"] == 0
    ):
        print(
            "B relay -> wider positive "
            "synaptic propagation: NOT OBSERVED"
        )

    print()
    print(
        "MQ-2.1 WIDER-NETWORK "
        "PROBE COMPLETE"
    )


if __name__ == "__main__":
    main()
