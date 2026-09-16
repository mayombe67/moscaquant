from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tomllib

import numpy as np
from scipy import sparse

from brain.market_replay import (
    FRAME_COUNT,
    OBSERVATIONS,
    SENSORY_GAIN,
)
from brain.market_temporal import (
    MarketVisionTemporalEncoder,
)
from brain.visual_transduction import (
    VisualTransductionConfig,
    VisualTransductionRuntime,
)


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

TRANSDUCTION_CONFIG = Path(
    "config/sensory/visual-transduction-v1.toml"
)

READOUT_CONFIG = Path(
    "config/controls/mq3-readout-metric-v1.toml"
)

OUTPUT = Path(
    "/home/wil/moscaquant-data/experiments/"
    "mq3-neutral-readout-calibration-v1.json"
)


def sha256_file(path: Path) -> str:
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


def channel_metrics(
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

        "mean_voltage":
            float(
                local_voltage.mean()
            ),

        "rms_voltage":
            float(
                np.sqrt(
                    np.mean(
                        local_voltage
                        * local_voltage
                    )
                )
            ),

        "maximum_voltage":
            float(
                local_voltage.max()
            ),

        "positive_fraction":
            float(
                np.mean(
                    local_voltage > 0.0
                )
            ),

        "quarter_threshold_fraction":
            float(
                np.mean(
                    local_voltage >= 0.25
                )
            ),

        "spike_rate_per_neuron":
            float(
                local_spikes.mean()
            ),
    }


def summarize(values):
    values = np.asarray(
        values,
        dtype=np.float64,
    )

    return {
        "mean":
            float(values.mean()),

        "median":
            float(
                np.median(values)
            ),

        "minimum":
            float(values.min()),

        "maximum":
            float(values.max()),

        "p95":
            float(
                np.quantile(
                    values,
                    0.95,
                )
            ),

        "p99":
            float(
                np.quantile(
                    values,
                    0.99,
                )
            ),
    }


def run_once(
    connectome,
    retinal_indices,
    release_gain,
    channel_indices,
):
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

    traces = {
        channel: []
        for channel
        in channel_indices
    }

    voltage_hash = hashlib.sha256()
    spike_hash = hashlib.sha256()

    frame_number = 0

    for _ in range(
        OBSERVATIONS
    ):
        frames = encoder.encode_sequence(
            neutral,
            frame_count=FRAME_COUNT,
        )

        for stimulus in frames:
            spikes = (
                runtime.step(
                    stimulus
                    * SENSORY_GAIN
                ) > 0
            )

            voltage_hash.update(
                np.ascontiguousarray(
                    runtime.voltage
                ).tobytes()
            )

            spike_hash.update(
                np.packbits(
                    spikes
                ).tobytes()
            )

            for (
                channel,
                indices,
            ) in channel_indices.items():
                metrics = channel_metrics(
                    runtime.voltage,
                    spikes,
                    indices,
                )

                traces[channel].append(
                    metrics
                )

            frame_number += 1

    if frame_number != 192:
        raise RuntimeError(
            f"expected 192 frames, "
            f"got {frame_number}"
        )

    summaries = {}

    for channel, frames in (
        traces.items()
    ):
        summaries[channel] = {}

        metric_names = (
            frames[0].keys()
        )

        for metric in metric_names:
            summaries[
                channel
            ][
                metric
            ] = summarize(
                [
                    frame[metric]
                    for frame in frames
                ]
            )

    return {
        "frames":
            frame_number,

        "voltage_trace_sha256":
            voltage_hash.hexdigest(),

        "spike_trace_sha256":
            spike_hash.hexdigest(),

        "channels":
            traces,

        "summary":
            summaries,
    }


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

    primary_metric = (
        readout_config[
            "primary_metric"
        ][
            "name"
        ]
    )

    if (
        primary_metric
        != "mean_positive_voltage"
    ):
        raise RuntimeError(
            "unexpected primary "
            "readout metric"
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

    channel_indices = {}

    for cluster in range(3):
        members = dn_indices[
            clusters == cluster
        ]

        channel_indices[
            f"DN-C{cluster}"
        ] = members

    expected_sizes = {
        "DN-C0": 6,
        "DN-C1": 646,
        "DN-C2": 539,
    }

    actual_sizes = {
        channel: len(indices)
        for channel, indices
        in channel_indices.items()
    }

    if actual_sizes != expected_sizes:
        raise RuntimeError(
            "frozen consensus sizes "
            f"changed: {actual_sizes}"
        )

    print("=" * 72)
    print(
        "MQ-3 NEUTRAL READOUT "
        "CALIBRATION"
    )
    print("=" * 72)

    print(
        "primary metric:",
        primary_metric,
    )

    print(
        "release gain:",
        release_gain,
    )

    print(
        "channel sizes:",
        actual_sizes,
    )

    print()
    print(
        "running neutral replay N1..."
    )

    n1 = run_once(
        connectome,
        retinal_indices,
        release_gain,
        channel_indices,
    )

    print(
        "running neutral replay N2..."
    )

    n2 = run_once(
        connectome,
        retinal_indices,
        release_gain,
        channel_indices,
    )

    if (
        n1[
            "voltage_trace_sha256"
        ]
        != n2[
            "voltage_trace_sha256"
        ]
    ):
        raise RuntimeError(
            "neutral voltage replay "
            "is not deterministic"
        )

    if (
        n1[
            "spike_trace_sha256"
        ]
        != n2[
            "spike_trace_sha256"
        ]
    ):
        raise RuntimeError(
            "neutral spike replay "
            "is not deterministic"
        )

    output = {
        "experiment":
            "mq3-neutral-readout-"
            "calibration-v1",

        "primary_metric":
            primary_metric,

        "release_gain":
            release_gain,

        "channel_sizes":
            actual_sizes,

        "market_response_used":
            False,

        "financial_semantics_used":
            False,

        "neutral_replay":
            n1,

        "sources": {
            "consensus_artifact":
                str(CONSENSUS),

            "consensus_sha256":
                sha256_file(
                    CONSENSUS
                ),

            "connectome_sha256":
                sha256_file(
                    CONNECTOME
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

    print()
    print("=" * 72)
    print(
        "NEUTRAL PRIMARY METRIC"
    )
    print("=" * 72)

    for channel in (
        "DN-C0",
        "DN-C1",
        "DN-C2",
    ):
        stats = n1[
            "summary"
        ][
            channel
        ][
            "mean_positive_voltage"
        ]

        print(
            channel,
            "size=",
            actual_sizes[
                channel
            ],
        )

        print(
            "  mean:",
            stats["mean"],
        )

        print(
            "  median:",
            stats["median"],
        )

        print(
            "  max:",
            stats["maximum"],
        )

        print(
            "  p95:",
            stats["p95"],
        )

        print(
            "  p99:",
            stats["p99"],
        )

    print()
    print("=" * 72)
    print("NEUTRAL SPIKE RATE")
    print("=" * 72)

    for channel in (
        "DN-C0",
        "DN-C1",
        "DN-C2",
    ):
        stats = n1[
            "summary"
        ][
            channel
        ][
            "spike_rate_per_neuron"
        ]

        print(
            channel,
            stats,
        )

    print()
    print(
        "N1 == N2 exact replay: PASS"
    )

    print(
        "MARKET RESPONSE USED: NO"
    )

    print(
        "FINANCIAL SEMANTICS USED: NO"
    )

    print()
    print(
        "results:",
        OUTPUT,
    )

    print()
    print(
        "MQ-3 NEUTRAL READOUT "
        "CALIBRATION COMPLETE"
    )


if __name__ == "__main__":
    main()
