from __future__ import annotations

from pathlib import Path
import math
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

    #
    # Counterfactual membrane state containing ONLY
    # current caused by relay spikes.
    #
    relay_voltage = np.zeros(
        len(wider_indices),
        dtype=np.float64,
    )

    excitatory_voltage = np.zeros(
        len(wider_indices),
        dtype=np.float64,
    )

    inhibitory_voltage = np.zeros(
        len(wider_indices),
        dtype=np.float64,
    )

    decay = math.exp(
        -1.0 / 20.0
    )

    l2_l3_mask = np.isin(
        relay_types,
        (
            "L2",
            "L3",
        ),
    )

    l1_lai_mask = np.isin(
        relay_types,
        (
            "L1",
            "Lai",
        ),
    )

    relay_peak = 0.0
    relay_peak_frame = None
    relay_peak_target = None

    excitatory_peak = 0.0
    excitatory_peak_frame = None
    excitatory_peak_target = None

    inhibitory_min = 0.0
    inhibitory_min_frame = None
    inhibitory_min_target = None

    actual_peak = 0.0
    actual_peak_frame = None
    actual_peak_target = None

    closest_gap = None
    closest_gap_frame = None
    closest_gap_target = None
    closest_actual_voltage = None
    closest_relay_contribution = None

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
            prior_relay = (
                runtime.spikes[
                    relay_indices
                ] > 0
            )

            relay_voltage *= decay
            excitatory_voltage *= decay
            inhibitory_voltage *= decay

            if np.any(prior_relay):
                all_sources = (
                    prior_relay.astype(
                        np.float32
                    )
                )

                excit_sources = (
                    prior_relay
                    & l2_l3_mask
                ).astype(
                    np.float32
                )

                inhib_sources = (
                    prior_relay
                    & l1_lai_mask
                ).astype(
                    np.float32
                )

                relay_current = (
                    relay_to_wider
                    @ all_sources
                )

                excit_current = (
                    relay_to_wider
                    @ excit_sources
                )

                inhib_current = (
                    relay_to_wider
                    @ inhib_sources
                )

                relay_voltage += np.asarray(
                    relay_current,
                    dtype=np.float64,
                ).ravel()

                excitatory_voltage += np.asarray(
                    excit_current,
                    dtype=np.float64,
                ).ravel()

                inhibitory_voltage += np.asarray(
                    inhib_current,
                    dtype=np.float64,
                ).ravel()

            spikes = runtime.step(
                stimulus
                * SENSORY_GAIN
            ) > 0

            actual_voltage = runtime.voltage[
                wider_mask
            ].astype(
                np.float64,
                copy=False,
            )

            rv_index = int(
                np.argmax(
                    relay_voltage
                )
            )

            rv_peak = float(
                relay_voltage[
                    rv_index
                ]
            )

            if rv_peak > relay_peak:
                relay_peak = rv_peak
                relay_peak_frame = frame_number
                relay_peak_target = int(
                    wider_indices[
                        rv_index
                    ]
                )

            ev_index = int(
                np.argmax(
                    excitatory_voltage
                )
            )

            ev_peak = float(
                excitatory_voltage[
                    ev_index
                ]
            )

            if ev_peak > excitatory_peak:
                excitatory_peak = ev_peak
                excitatory_peak_frame = frame_number
                excitatory_peak_target = int(
                    wider_indices[
                        ev_index
                    ]
                )

            iv_index = int(
                np.argmin(
                    inhibitory_voltage
                )
            )

            iv_min = float(
                inhibitory_voltage[
                    iv_index
                ]
            )

            if iv_min < inhibitory_min:
                inhibitory_min = iv_min
                inhibitory_min_frame = frame_number
                inhibitory_min_target = int(
                    wider_indices[
                        iv_index
                    ]
                )

            av_index = int(
                np.argmax(
                    actual_voltage
                )
            )

            av_peak = float(
                actual_voltage[
                    av_index
                ]
            )

            if av_peak > actual_peak:
                actual_peak = av_peak
                actual_peak_frame = frame_number
                actual_peak_target = int(
                    wider_indices[
                        av_index
                    ]
                )

            #
            # Among cells receiving positive relay-derived
            # voltage, find the one currently closest to
            # the +1 threshold in the actual runtime.
            #
            positive_relay = (
                relay_voltage > 0
            )

            if np.any(
                positive_relay
            ):
                candidate_actual = actual_voltage[
                    positive_relay
                ]

                candidate_relay = relay_voltage[
                    positive_relay
                ]

                candidate_indices = wider_indices[
                    positive_relay
                ]

                gaps = (
                    1.0
                    - candidate_actual
                )

                local = int(
                    np.argmin(
                        gaps
                    )
                )

                gap = float(
                    gaps[
                        local
                    ]
                )

                if (
                    closest_gap is None
                    or gap < closest_gap
                ):
                    closest_gap = gap
                    closest_gap_frame = (
                        frame_number
                    )

                    closest_gap_target = int(
                        candidate_indices[
                            local
                        ]
                    )

                    closest_actual_voltage = float(
                        candidate_actual[
                            local
                        ]
                    )

                    closest_relay_contribution = float(
                        candidate_relay[
                            local
                        ]
                    )

            frame_number += 1

    def body(index):
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

        "relay_peak":
            relay_peak,

        "relay_peak_frame":
            relay_peak_frame,

        "relay_peak_target":
            relay_peak_target,

        "relay_peak_body":
            body(
                relay_peak_target
            ),

        "excitatory_peak":
            excitatory_peak,

        "excitatory_peak_frame":
            excitatory_peak_frame,

        "excitatory_peak_target":
            excitatory_peak_target,

        "excitatory_peak_body":
            body(
                excitatory_peak_target
            ),

        "inhibitory_min":
            inhibitory_min,

        "inhibitory_min_frame":
            inhibitory_min_frame,

        "inhibitory_min_target":
            inhibitory_min_target,

        "inhibitory_min_body":
            body(
                inhibitory_min_target
            ),

        "actual_peak":
            actual_peak,

        "actual_peak_frame":
            actual_peak_frame,

        "actual_peak_target":
            actual_peak_target,

        "actual_peak_body":
            body(
                actual_peak_target
            ),

        "closest_gap":
            closest_gap,

        "closest_gap_frame":
            closest_gap_frame,

        "closest_gap_target":
            closest_gap_target,

        "closest_gap_body":
            body(
                closest_gap_target
            ),

        "closest_actual_voltage":
            closest_actual_voltage,

        "closest_relay_contribution":
            closest_relay_contribution,
    }


def summarize(result):
    print()
    print("=" * 72)
    print(
        f"CONDITION {result['condition']}"
    )
    print("=" * 72)

    print(
        "relay-only max positive voltage:",
        result["relay_peak"],
    )

    print(
        "  frame:",
        result[
            "relay_peak_frame"
        ],
    )

    print(
        "  target index:",
        result[
            "relay_peak_target"
        ],
    )

    print(
        "  body_id:",
        result[
            "relay_peak_body"
        ],
    )

    print()
    print(
        "L2/L3-only max positive voltage:",
        result["excitatory_peak"],
    )

    print(
        "  frame:",
        result[
            "excitatory_peak_frame"
        ],
    )

    print(
        "  target index:",
        result[
            "excitatory_peak_target"
        ],
    )

    print(
        "  body_id:",
        result[
            "excitatory_peak_body"
        ],
    )

    print()
    print(
        "L1/Lai-only minimum voltage:",
        result["inhibitory_min"],
    )

    print(
        "  frame:",
        result[
            "inhibitory_min_frame"
        ],
    )

    print(
        "  target index:",
        result[
            "inhibitory_min_target"
        ],
    )

    print(
        "  body_id:",
        result[
            "inhibitory_min_body"
        ],
    )

    print()
    print(
        "actual wider-network max:",
        result["actual_peak"],
    )

    print(
        "  frame:",
        result[
            "actual_peak_frame"
        ],
    )

    print(
        "  target index:",
        result[
            "actual_peak_target"
        ],
    )

    print(
        "  body_id:",
        result[
            "actual_peak_body"
        ],
    )

    print()
    print(
        "closest threshold approach among "
        "relay-excited targets:"
    )

    print(
        "  gap to +1:",
        result["closest_gap"],
    )

    print(
        "  frame:",
        result[
            "closest_gap_frame"
        ],
    )

    print(
        "  target index:",
        result[
            "closest_gap_target"
        ],
    )

    print(
        "  body_id:",
        result[
            "closest_gap_body"
        ],
    )

    print(
        "  actual membrane voltage:",
        result[
            "closest_actual_voltage"
        ],
    )

    print(
        "  relay-attributed voltage:",
        result[
            "closest_relay_contribution"
        ],
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
    print("CAUSAL ATTRIBUTION")
    print("=" * 72)

    print(
        "relay-only max:",
        f"A={a['relay_peak']}",
        f"B={b['relay_peak']}",
    )

    print(
        "L2/L3-only max:",
        f"A={a['excitatory_peak']}",
        f"B={b['excitatory_peak']}",
    )

    print()
    print(
        "MQ-2.1 RELAY ATTRIBUTION "
        "PROBE COMPLETE"
    )


if __name__ == "__main__":
    main()
