from __future__ import annotations
from config.paths import data_path


import hashlib
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

CONSENSUS = data_path('processed', 'mq3-dn-consensus-v1.npz')

TRANSDUCTION_CONFIG = Path(
    "config/sensory/visual-transduction-v1.toml"
)

READOUT_CONFIG = Path(
    "config/controls/"
    "mq3-anonymous-market-readout-v1.toml"
)

OUTPUT = data_path('experiments', 'mq3-anonymous-market-readout-v1.json')


CHANNELS = (
    "DN-C0",
    "DN-C1",
    "DN-C2",
)


def sha256_file(
    path: Path,
) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        while True:
            block = handle.read(
                1024 * 1024
            )

            if not block:
                break

            digest.update(block)

    return digest.hexdigest()


def build_channel_indices(
    consensus,
):
    dn_indices = np.asarray(
        consensus[
            "neuron_index"
        ],
        dtype=np.int32,
    )

    clusters = np.asarray(
        consensus[
            "consensus_cluster"
        ],
        dtype=np.int32,
    )

    result = {}

    for cluster in range(3):
        result[
            f"DN-C{cluster}"
        ] = dn_indices[
            clusters == cluster
        ]

    expected = {
        "DN-C0": 6,
        "DN-C1": 646,
        "DN-C2": 539,
    }

    actual = {
        name: len(indices)
        for name, indices
        in result.items()
    }

    if actual != expected:
        raise RuntimeError(
            "frozen MQ-3 consensus "
            f"sizes changed: {actual}"
        )

    return result


def frame_metrics(
    voltage,
    spikes,
    indices,
):
    local_voltage = np.asarray(
        voltage[indices],
        dtype=np.float64,
    )

    local_spikes = np.asarray(
        spikes[indices],
        dtype=bool,
    )

    positive = np.maximum(
        local_voltage,
        0.0,
    )

    return {
        "mean_positive_voltage":
            float(
                positive.mean()
            ),

        "integrated_positive_voltage":
            float(
                positive.sum()
            ),

        "maximum_neuron_voltage":
            float(
                local_voltage.max()
            ),

        "positive_neuron_fraction":
            float(
                np.mean(
                    local_voltage > 0.0
                )
            ),

        "spike_count":
            int(
                np.count_nonzero(
                    local_spikes
                )
            ),

        "spike_rate_per_neuron":
            float(
                np.mean(
                    local_spikes
                )
            ),
    }


def decide(
    scores,
):
    values = np.asarray(
        [
            scores[channel]
            for channel in CHANNELS
        ],
        dtype=np.float64,
    )

    if np.all(
        values == 0.0
    ):
        return {
            "outcome": "ABSTAIN",
            "winner": None,
            "reason":
                "all_channel_scores_exactly_zero",
        }

    maximum = float(
        values.max()
    )

    winners = np.flatnonzero(
        values == maximum
    )

    if len(winners) != 1:
        return {
            "outcome": "ABSTAIN",
            "winner": None,
            "reason":
                "maximum_channel_score_tie",
        }

    winner = CHANNELS[
        int(winners[0])
    ]

    return {
        "outcome": "WINNER",
        "winner": winner,
        "reason":
            "unique_maximum_channel_score",
    }


def run_replay(
    condition,
    connectome,
    retinal_indices,
    channel_indices,
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

    traces = {
        channel: []
        for channel in CHANNELS
    }

    positive_sum = {
        channel: 0.0
        for channel in CHANNELS
    }

    peak_frame_metric = {
        channel: 0.0
        for channel in CHANNELS
    }

    integrated_positive_voltage = {
        channel: 0.0
        for channel in CHANNELS
    }

    maximum_neuron_voltage = {
        channel: 0.0
        for channel in CHANNELS
    }

    spike_count = {
        channel: 0
        for channel in CHANNELS
    }

    first_positive_frame = {
        channel: None
        for channel in CHANNELS
    }

    voltage_digest = hashlib.sha256()
    spike_digest = hashlib.sha256()

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

        frames = encoder.encode_sequence(
            normalized,
            frame_count=FRAME_COUNT,
        )

        for stimulus in frames:
            spikes = (
                runtime.step(
                    stimulus
                    * SENSORY_GAIN
                ) > 0
            )

            voltage_digest.update(
                np.ascontiguousarray(
                    runtime.voltage
                ).tobytes()
            )

            spike_digest.update(
                np.packbits(
                    spikes
                ).tobytes()
            )

            for channel in CHANNELS:
                metrics = frame_metrics(
                    runtime.voltage,
                    spikes,
                    channel_indices[
                        channel
                    ],
                )

                traces[
                    channel
                ].append(
                    metrics
                )

                primary = metrics[
                    "mean_positive_voltage"
                ]

                positive_sum[
                    channel
                ] += primary

                peak_frame_metric[
                    channel
                ] = max(
                    peak_frame_metric[
                        channel
                    ],
                    primary,
                )

                integrated_positive_voltage[
                    channel
                ] += metrics[
                    "integrated_positive_voltage"
                ]

                maximum_neuron_voltage[
                    channel
                ] = max(
                    maximum_neuron_voltage[
                        channel
                    ],
                    metrics[
                        "maximum_neuron_voltage"
                    ],
                )

                spike_count[
                    channel
                ] += metrics[
                    "spike_count"
                ]

                if (
                    primary > 0.0
                    and first_positive_frame[
                        channel
                    ] is None
                ):
                    first_positive_frame[
                        channel
                    ] = frame_number

            frame_number += 1

    if frame_number != 192:
        raise RuntimeError(
            "expected 192 frames, "
            f"got {frame_number}"
        )

    scores = {
        channel:
            (
                positive_sum[
                    channel
                ]
                / frame_number
            )
        for channel in CHANNELS
    }

    diagnostics = {}

    for channel in CHANNELS:
        size = len(
            channel_indices[
                channel
            ]
        )

        diagnostics[
            channel
        ] = {
            "channel_size":
                size,

            "episode_mean_positive_voltage":
                scores[
                    channel
                ],

            "peak_frame_mean_positive_voltage":
                peak_frame_metric[
                    channel
                ],

            "integrated_positive_voltage":
                integrated_positive_voltage[
                    channel
                ],

            "maximum_neuron_voltage":
                maximum_neuron_voltage[
                    channel
                ],

            "spike_count":
                spike_count[
                    channel
                ],

            "spike_rate_per_neuron_per_frame":
                (
                    spike_count[
                        channel
                    ]
                    / (
                        size
                        * frame_number
                    )
                ),

            "first_positive_frame":
                first_positive_frame[
                    channel
                ],
        }

    return {
        "condition":
            condition,

        "frames":
            frame_number,

        "scores":
            scores,

        "decision":
            decide(
                scores
            ),

        "diagnostics":
            diagnostics,

        "voltage_trace_sha256":
            voltage_digest.hexdigest(),

        "spike_trace_sha256":
            spike_digest.hexdigest(),
    }


def assert_exact_replay(
    first,
    second,
    condition,
):
    if (
        first[
            "voltage_trace_sha256"
        ]
        != second[
            "voltage_trace_sha256"
        ]
    ):
        raise RuntimeError(
            f"{condition} voltage replay "
            "is not deterministic"
        )

    if (
        first[
            "spike_trace_sha256"
        ]
        != second[
            "spike_trace_sha256"
        ]
    ):
        raise RuntimeError(
            f"{condition} spike replay "
            "is not deterministic"
        )

    if (
        first["scores"]
        != second["scores"]
    ):
        raise RuntimeError(
            f"{condition} channel scores "
            "are not deterministic"
        )

    if (
        first["decision"]
        != second["decision"]
    ):
        raise RuntimeError(
            f"{condition} decision "
            "is not deterministic"
        )


def print_replay(
    label,
    result,
):
    print()
    print("=" * 72)
    print(label)
    print("=" * 72)

    for channel in CHANNELS:
        diagnostics = result[
            "diagnostics"
        ][
            channel
        ]

        print(
            channel,
        )

        print(
            "  score:",
            result[
                "scores"
            ][
                channel
            ],
        )

        print(
            "  peak frame metric:",
            diagnostics[
                "peak_frame_mean_positive_voltage"
            ],
        )

        print(
            "  max neuron voltage:",
            diagnostics[
                "maximum_neuron_voltage"
            ],
        )

        print(
            "  spikes:",
            diagnostics[
                "spike_count"
            ],
        )

        print(
            "  spike rate/neuron/frame:",
            diagnostics[
                "spike_rate_per_neuron_per_frame"
            ],
        )

        print(
            "  first positive frame:",
            diagnostics[
                "first_positive_frame"
            ],
        )

    print()
    print(
        "outcome:",
        result[
            "decision"
        ][
            "outcome"
        ],
    )

    print(
        "winner:",
        result[
            "decision"
        ][
            "winner"
        ],
    )

    print(
        "reason:",
        result[
            "decision"
        ][
            "reason"
        ],
    )


def main():
    with TRANSDUCTION_CONFIG.open(
        "rb"
    ) as handle:
        transduction = tomllib.load(
            handle
        )

    with READOUT_CONFIG.open(
        "rb"
    ) as handle:
        readout_config = tomllib.load(
            handle
        )

    release_gain = float(
        transduction[
            "transduction"
        ][
            "release_gain"
        ]
    )

    configured_conditions = tuple(
        readout_config[
            "experiment"
        ][
            "conditions"
        ]
    )

    if configured_conditions != (
        "A",
        "B",
    ):
        raise RuntimeError(
            "unexpected condition config"
        )

    configured_channels = tuple(
        readout_config[
            "population"
        ][
            "channels"
        ]
    )

    if configured_channels != CHANNELS:
        raise RuntimeError(
            "unexpected channel config"
        )

    primary_metric = (
        readout_config[
            "score"
        ][
            "primary_metric"
        ]
    )

    if (
        primary_metric
        != "episode_mean_positive_voltage"
    ):
        raise RuntimeError(
            "unexpected primary metric"
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

    consensus = np.load(
        CONSENSUS
    )

    channel_indices = (
        build_channel_indices(
            consensus
        )
    )

    print("=" * 72)
    print(
        "MQ-3 ANONYMOUS "
        "MARKET READOUT"
    )
    print("=" * 72)

    print(
        "release gain:",
        release_gain,
    )

    print(
        "primary metric:",
        primary_metric,
    )

    print(
        "channels:",
        {
            channel:
                len(
                    channel_indices[
                        channel
                    ]
                )
            for channel
            in CHANNELS
        },
    )

    print()
    print(
        "FINANCIAL SEMANTICS USED: NO"
    )

    print(
        "BUY/SELL/HOLD LABELS USED: NO"
    )

    print()
    print("running A1...")

    a1 = run_replay(
        "A",
        connectome,
        retinal_indices,
        channel_indices,
        release_gain,
    )

    print("running A2...")

    a2 = run_replay(
        "A",
        connectome,
        retinal_indices,
        channel_indices,
        release_gain,
    )

    print("running B1...")

    b1 = run_replay(
        "B",
        connectome,
        retinal_indices,
        channel_indices,
        release_gain,
    )

    print("running B2...")

    b2 = run_replay(
        "B",
        connectome,
        retinal_indices,
        channel_indices,
        release_gain,
    )

    assert_exact_replay(
        a1,
        a2,
        "A",
    )

    assert_exact_replay(
        b1,
        b2,
        "B",
    )

    output = {
        "experiment":
            "mq3-anonymous-market-"
            "readout-v1",

        "release_gain":
            release_gain,

        "primary_metric":
            primary_metric,

        "channel_sizes": {
            channel:
                len(
                    channel_indices[
                        channel
                    ]
                )
            for channel
            in CHANNELS
        },

        "financial_semantics_used":
            False,

        "buy_sell_hold_labels_used":
            False,

        "A1":
            a1,

        "A2":
            a2,

        "B1":
            b1,

        "B2":
            b2,

        "reproducibility": {
            "A_exact":
                True,

            "B_exact":
                True,
        },

        "sources": {
            "connectome":
                str(CONNECTOME),

            "connectome_sha256":
                sha256_file(
                    CONNECTOME
                ),

            "consensus":
                str(CONSENSUS),

            "consensus_sha256":
                sha256_file(
                    CONSENSUS
                ),

            "readout_config":
                str(READOUT_CONFIG),

            "readout_config_sha256":
                sha256_file(
                    READOUT_CONFIG
                ),
        },
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

    print_replay(
        "CONDITION A",
        a1,
    )

    print_replay(
        "CONDITION B",
        b1,
    )

    print()
    print("=" * 72)
    print("REPRODUCIBILITY")
    print("=" * 72)

    print(
        "A1 == A2 exact: PASS"
    )

    print(
        "B1 == B2 exact: PASS"
    )

    print()
    print("=" * 72)
    print("ANONYMOUS OUTCOME SUMMARY")
    print("=" * 72)

    print(
        "A:",
        a1[
            "decision"
        ],
    )

    print(
        "B:",
        b1[
            "decision"
        ],
    )

    print()
    print(
        "results:",
        OUTPUT,
    )

    print()
    print(
        "FINANCIAL SEMANTICS USED: NO"
    )

    print(
        "MQ-3 ANONYMOUS MARKET "
        "READOUT COMPLETE"
    )


if __name__ == "__main__":
    main()
