from __future__ import annotations
from config.paths import data_path

from pathlib import Path
import tomllib

import numpy as np
from scipy import sparse

from brain.market_replay import (
    FRAME_COUNT,
    OBSERVATIONS,
    SENSORY_GAIN,
)
from brain.market_temporal import MarketVisionTemporalEncoder
from brain.visual_transduction import (
    VisualTransductionConfig,
    VisualTransductionRuntime,
)


CONNECTOME = data_path('processed', 'connectome-baseline-v1.npz')

RETINA = data_path('processed', 'visual-r1-r6-map-v1.npz')

TERRITORIES = data_path('processed', 'market-retinal-territories-v1.npz')

RELAY = data_path('processed', 'visual-relay-map-v1.npz')

CONFIG = Path(
    "config/sensory/visual-transduction-v1.toml"
)


def main():
    with CONFIG.open("rb") as handle:
        config = tomllib.load(handle)

    release_gain = float(
        config["transduction"]["release_gain"]
    )

    print("frozen release gain:", release_gain)
    print("loading frozen connectome...")

    connectome = sparse.load_npz(
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

    relay_body_ids = np.asarray(
        relay["body_id"],
        dtype=np.int64,
    )

    relay_types = np.asarray(
        relay["type"],
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

    neutral = np.zeros(
        (6, 7),
        dtype=np.float32,
    )

    first_relay_spike_frame = None
    relay_source_indices = None

    second_hop_frame = None

    relay_positive_events = 0
    relay_negative_events = 0

    strongest_positive = 0.0
    strongest_negative = 0.0

    positive_target_count = 0
    negative_target_count = 0

    max_target_voltage_before = None
    max_target_voltage_after = None
    min_target_voltage_after = None

    strongest_positive_target = None
    strongest_negative_target = None

    actual_second_hop_spikes = 0

    frame_number = 0

    for _ in range(OBSERVATIONS):
        frames = encoder.encode_sequence(
            neutral,
            frame_count=FRAME_COUNT,
        )

        for stimulus in frames:

            #
            # runtime.spikes contains spikes from
            # the immediately preceding frame.
            #
            prior_relay_local = (
                runtime.spikes[
                    relay_indices
                ] > 0
            )

            if np.any(prior_relay_local):
                if second_hop_frame is None:
                    second_hop_frame = frame_number

                    source_local = np.flatnonzero(
                        prior_relay_local
                    )

                    source_global = relay_indices[
                        source_local
                    ]

                    relay_source_indices = (
                        source_global.copy()
                    )

                    print()
                    print("=" * 72)
                    print("RELAY SOURCE EVENT")
                    print("=" * 72)

                    for local, global_index in zip(
                        source_local,
                        source_global,
                    ):
                        print(
                            "source:",
                            "index=",
                            int(global_index),
                            "body_id=",
                            int(
                                relay_body_ids[
                                    local
                                ]
                            ),
                            "type=",
                            str(
                                relay_types[
                                    local
                                ]
                            ),
                        )

                    #
                    # Isolate ONLY synaptic current
                    # caused by the relay spike(s).
                    #
                    relay_spike_vector = (
                        prior_relay_local.astype(
                            np.float32
                        )
                    )

                    relay_current = (
                        connectome[
                            :,
                            relay_indices
                        ]
                        @ relay_spike_vector
                    )

                    relay_current = np.asarray(
                        relay_current,
                        dtype=np.float32,
                    ).ravel()

                    wider_current = relay_current[
                        wider_mask
                    ]

                    positive = wider_current[
                        wider_current > 0
                    ]

                    negative = wider_current[
                        wider_current < 0
                    ]

                    relay_positive_events = int(
                        len(positive)
                    )

                    relay_negative_events = int(
                        len(negative)
                    )

                    positive_target_count = int(
                        np.count_nonzero(
                            wider_current > 0
                        )
                    )

                    negative_target_count = int(
                        np.count_nonzero(
                            wider_current < 0
                        )
                    )

                    if len(positive):
                        strongest_positive = float(
                            positive.max()
                        )

                    if len(negative):
                        strongest_negative = float(
                            negative.min()
                        )

                    wider_indices = np.flatnonzero(
                        wider_mask
                    )

                    if len(positive):
                        local_max = int(
                            np.argmax(
                                wider_current
                            )
                        )

                        strongest_positive_target = int(
                            wider_indices[
                                local_max
                            ]
                        )

                    if len(negative):
                        local_min = int(
                            np.argmin(
                                wider_current
                            )
                        )

                        strongest_negative_target = int(
                            wider_indices[
                                local_min
                            ]
                        )

                    max_target_voltage_before = float(
                        runtime.voltage[
                            wider_mask
                        ].max()
                    )

            spikes = runtime.step(
                stimulus * SENSORY_GAIN
            ) > 0

            relay_fired = (
                spikes
                & relay_mask
            )

            if (
                first_relay_spike_frame
                is None
                and np.any(relay_fired)
            ):
                first_relay_spike_frame = (
                    frame_number
                )

            #
            # Immediately after the frame that
            # consumed a relay spike, inspect the
            # wider connectome state.
            #
            if (
                second_hop_frame is not None
                and frame_number
                == second_hop_frame
            ):
                wider_voltage = (
                    runtime.voltage[
                        wider_mask
                    ]
                )

                max_target_voltage_after = float(
                    wider_voltage.max()
                )

                min_target_voltage_after = float(
                    wider_voltage.min()
                )

                actual_second_hop_spikes = int(
                    np.count_nonzero(
                        spikes
                        & wider_mask
                    )
                )

            frame_number += 1

    print()
    print("=" * 72)
    print("MQ-2.1 NEUTRAL SECOND-HOP PROBE")
    print("=" * 72)

    print(
        "first relay spike frame:",
        first_relay_spike_frame,
    )

    print(
        "relay current evaluated frame:",
        second_hop_frame,
    )

    print(
        "relay source indices:",
        (
            relay_source_indices.tolist()
            if relay_source_indices
            is not None
            else []
        ),
    )

    print()
    print(
        "positive second-hop targets:",
        positive_target_count,
    )

    print(
        "negative second-hop targets:",
        negative_target_count,
    )

    print(
        "positive second-hop events:",
        relay_positive_events,
    )

    print(
        "negative second-hop events:",
        relay_negative_events,
    )

    print()
    print(
        "strongest positive relay current:",
        strongest_positive,
    )

    print(
        "strongest negative relay current:",
        strongest_negative,
    )

    print(
        "strongest positive target index:",
        strongest_positive_target,
    )

    print(
        "strongest negative target index:",
        strongest_negative_target,
    )

    print()
    print(
        "max wider voltage before relay event:",
        max_target_voltage_before,
    )

    print(
        "max wider voltage after relay event:",
        max_target_voltage_after,
    )

    print(
        "min wider voltage after relay event:",
        min_target_voltage_after,
    )

    print(
        "LIF threshold:",
        runtime.config.threshold,
    )

    print(
        "actual wider-connectome spikes:",
        actual_second_hop_spikes,
    )

    print()
    print(
        "MQ-2.1 NEUTRAL SECOND-HOP "
        "PROBE PASS"
    )


if __name__ == "__main__":
    main()
