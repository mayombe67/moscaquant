from __future__ import annotations
from config.paths import data_path


import hashlib
import json
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
from brain.physiology_constrained_visual_transduction import (
    PhysiologyConstrainedVisualTransductionRuntime,
)
from brain.visual_transduction import (
    VisualTransductionConfig,
)
from market.features import compute_features
from market.normalization import CausalNormalizer


BASE = data_path('processed')

OUT = data_path('neuroscope')

CONNECTOME = BASE / "connectome-baseline-v1.npz"
RETINA = BASE / "visual-r1-r6-map-v1.npz"
RELAY = BASE / "visual-relay-map-v1.npz"
GRADED = BASE / "mq3-2-graded-visual-types-v1.npz"
CONSENSUS = BASE / "mq3-dn-consensus-v1.npz"
NEURON_IDS = BASE / "neuron_ids.npy"
TERRITORIES = BASE / "market-retinal-territories-v1.npz"

RELEASE_GAIN = 0.9981738484618123

RESPONDERS = np.asarray(
    [
        92,
        656,
        317,
        137122,
        126002,
        55,
        129,
        51,
        1273,
    ],
    dtype=np.int32,
)

SCHEMA_VERSION = (
    "mq4-neuroscope-telemetry-v1"
)


def sha256_file(
    path: Path,
) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        while True:
            chunk = handle.read(
                1024 * 1024
            )

            if not chunk:
                break

            digest.update(
                chunk
            )

    return digest.hexdigest()


def append_sparse_frame(
    values,
    threshold=0.0,
):
    indices = np.flatnonzero(
        values > threshold
    ).astype(
        np.int32
    )

    data = np.asarray(
        values[
            indices
        ],
        dtype=np.float32,
    )

    return indices, data


def flatten_sparse_frames(
    frames,
):
    offsets = [0]
    all_indices = []
    all_values = []

    total = 0

    for indices, values in frames:
        all_indices.append(
            indices
        )

        all_values.append(
            values
        )

        total += len(
            indices
        )

        offsets.append(
            total
        )

    if all_indices:
        indices = np.concatenate(
            all_indices
        ).astype(
            np.int32
        )

        values = np.concatenate(
            all_values
        ).astype(
            np.float32
        )

    else:
        indices = np.asarray(
            [],
            dtype=np.int32,
        )

        values = np.asarray(
            [],
            dtype=np.float32,
        )

    return (
        np.asarray(
            offsets,
            dtype=np.int64,
        ),
        indices,
        values,
    )


def main():
    OUT.mkdir(
        parents=True,
        exist_ok=True,
    )

    connectome = sparse.load_npz(
        CONNECTOME
    ).tocsr()

    neuron_ids = np.load(
        NEURON_IDS
    ).astype(
        np.int64
    )

    retina = np.load(
        RETINA
    )

    relay = np.load(
        RELAY
    )

    graded = np.load(
        GRADED
    )

    consensus = np.load(
        CONSENSUS
    )

    retinal_indices = np.asarray(
        retina[
            "neuron_index"
        ],
        dtype=np.int32,
    )

    relay_indices = np.asarray(
        relay[
            "neuron_index"
        ],
        dtype=np.int32,
    )

    graded_indices = np.asarray(
        graded[
            "neuron_index"
        ],
        dtype=np.int32,
    )

    graded_types = np.asarray(
        graded[
            "type"
        ],
    ).astype(str)

    dn_indices = np.asarray(
        consensus[
            "neuron_index"
        ],
        dtype=np.int32,
    )

    dn_clusters = np.asarray(
        consensus[
            "consensus_cluster"
        ],
        dtype=np.int32,
    )

    runtime = (
        PhysiologyConstrainedVisualTransductionRuntime(
            connectome=connectome,
            retinal_indices=retinal_indices,
            relay_artifact=RELAY,
            graded_artifact=GRADED,
            config=VisualTransductionConfig(
                release_gain=RELEASE_GAIN,
            ),
        )
    )

    normalizers = [
        CausalNormalizer(
            window_size=64,
            min_history=8,
        )
        for _ in ASSETS
    ]

    series = [
        synthetic_series(
            "A",
            asset_index,
        )
        for asset_index
        in range(6)
    ]

    encoder = (
        MarketVisionTemporalEncoder(
            TERRITORIES
        )
    )

    #
    # Sparse full-CNS telemetry.
    #
    effective_frames = []
    spike_frames = []
    positive_voltage_frames = []

    #
    # Dense small-population telemetry.
    #
    responder_voltage = []

    dn_mean_positive = []
    dn_max_positive = []
    dn_spike_count = []

    retinal_spike_count = []
    relay_spike_count = []
    graded_active_count = []

    #
    # Market input snapshot per observation.
    #
    normalized_features = []

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

        normalized_features.append(
            normalized.copy()
        )

        frames = encoder.encode_sequence(
            normalized,
            frame_count=FRAME_COUNT,
        )

        for stimulus in frames:

            #
            # BEFORE STEP:
            # exact presynaptic activity
            # used by this simulation step.
            #
            effective = (
                runtime.effective_activity()
            )

            effective_frames.append(
                append_sparse_frame(
                    effective
                )
            )

            runtime.step(
                stimulus
                * SENSORY_GAIN
            )

            #
            # AFTER STEP:
            # resulting state.
            #
            spike_frames.append(
                append_sparse_frame(
                    runtime.spikes
                )
            )

            positive_voltage_frames.append(
                append_sparse_frame(
                    np.maximum(
                        runtime.voltage,
                        0.0,
                    )
                )
            )

            responder_voltage.append(
                np.asarray(
                    runtime.voltage[
                        RESPONDERS
                    ],
                    dtype=np.float32,
                )
            )

            channel_means = []
            channel_maxes = []
            channel_spikes = []

            for cluster in range(3):
                indices = dn_indices[
                    dn_clusters
                    == cluster
                ]

                voltage = np.maximum(
                    runtime.voltage[
                        indices
                    ],
                    0.0,
                )

                channel_means.append(
                    float(
                        voltage.mean()
                    )
                )

                channel_maxes.append(
                    float(
                        voltage.max()
                    )
                )

                channel_spikes.append(
                    int(
                        np.count_nonzero(
                            runtime.spikes[
                                indices
                            ] > 0
                        )
                    )
                )

            dn_mean_positive.append(
                channel_means
            )

            dn_max_positive.append(
                channel_maxes
            )

            dn_spike_count.append(
                channel_spikes
            )

            retinal_spike_count.append(
                int(
                    np.count_nonzero(
                        runtime.spikes[
                            retinal_indices
                        ] > 0
                    )
                )
            )

            relay_spike_count.append(
                int(
                    np.count_nonzero(
                        runtime.spikes[
                            relay_indices
                        ] > 0
                    )
                )
            )

            graded_active_count.append(
                int(
                    np.count_nonzero(
                        effective[
                            graded_indices
                        ] > 0
                    )
                )
            )

            frame_number += 1

    expected_frames = (
        OBSERVATIONS
        * FRAME_COUNT
    )

    if frame_number != expected_frames:
        raise RuntimeError(
            f"expected {expected_frames} "
            f"frames, got {frame_number}"
        )

    (
        effective_offsets,
        effective_indices,
        effective_values,
    ) = flatten_sparse_frames(
        effective_frames
    )

    (
        spike_offsets,
        spike_indices,
        spike_values,
    ) = flatten_sparse_frames(
        spike_frames
    )

    (
        voltage_offsets,
        voltage_indices,
        voltage_values,
    ) = flatten_sparse_frames(
        positive_voltage_frames
    )

    npz_path = (
        OUT
        / "mq4-neuroscope-replay-A-v1.npz"
    )

    np.savez_compressed(
        npz_path,

        schema_version=np.asarray(
            SCHEMA_VERSION
        ),

        neuron_ids=neuron_ids,

        retinal_indices=retinal_indices,
        relay_indices=relay_indices,

        graded_indices=graded_indices,
        graded_types=graded_types,

        dn_indices=dn_indices,
        dn_clusters=dn_clusters,

        responder_indices=RESPONDERS,

        effective_offsets=effective_offsets,
        effective_indices=effective_indices,
        effective_values=effective_values,

        spike_offsets=spike_offsets,
        spike_indices=spike_indices,
        spike_values=spike_values,

        positive_voltage_offsets=voltage_offsets,
        positive_voltage_indices=voltage_indices,
        positive_voltage_values=voltage_values,

        responder_voltage=np.asarray(
            responder_voltage,
            dtype=np.float32,
        ),

        dn_mean_positive=np.asarray(
            dn_mean_positive,
            dtype=np.float32,
        ),

        dn_max_positive=np.asarray(
            dn_max_positive,
            dtype=np.float32,
        ),

        dn_spike_count=np.asarray(
            dn_spike_count,
            dtype=np.int32,
        ),

        retinal_spike_count=np.asarray(
            retinal_spike_count,
            dtype=np.int32,
        ),

        relay_spike_count=np.asarray(
            relay_spike_count,
            dtype=np.int32,
        ),

        graded_active_count=np.asarray(
            graded_active_count,
            dtype=np.int32,
        ),

        normalized_features=np.asarray(
            normalized_features,
            dtype=np.float32,
        ),
    )

    metadata = {
        "schema_version":
            SCHEMA_VERSION,

        "phase":
            "MQ-4.1",

        "condition":
            "A",

        "source_checkpoint":
            "mq-3.2",

        "frame_count":
            frame_number,

        "observation_count":
            OBSERVATIONS,

        "frames_per_observation":
            FRAME_COUNT,

        "population_size":
            int(
                connectome.shape[0]
            ),

        "retinal_population":
            int(
                len(
                    retinal_indices
                )
            ),

        "relay_population":
            int(
                len(
                    relay_indices
                )
            ),

        "graded_population":
            int(
                len(
                    graded_indices
                )
            ),

        "dn_population":
            int(
                len(
                    dn_indices
                )
            ),

        "responder_population":
            int(
                len(
                    RESPONDERS
                )
            ),

        "read_only":
            True,

        "simulation_feedback":
            False,

        "financial_semantics_used":
            False,

        "artifacts": {
            "replay_npz":
                str(
                    npz_path
                ),

            "connectome_sha256":
                sha256_file(
                    CONNECTOME
                ),

            "graded_population_sha256":
                sha256_file(
                    GRADED
                ),

            "dn_consensus_sha256":
                sha256_file(
                    CONSENSUS
                ),
        },
    }

    json_path = (
        OUT
        / "mq4-neuroscope-replay-A-v1.json"
    )

    json_path.write_text(
        json.dumps(
            metadata,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    print("=" * 80)
    print(
        "MQ-4.1 NEUROSCOPE TELEMETRY EXPORT"
    )
    print("=" * 80)

    print(
        "schema:",
        SCHEMA_VERSION,
    )

    print(
        "frames:",
        frame_number,
    )

    print(
        "population:",
        connectome.shape[0],
    )

    print(
        "retina:",
        len(
            retinal_indices
        ),
    )

    print(
        "relay:",
        len(
            relay_indices
        ),
    )

    print(
        "graded:",
        len(
            graded_indices
        ),
    )

    print(
        "DN:",
        len(
            dn_indices
        ),
    )

    print(
        "responders:",
        len(
            RESPONDERS
        ),
    )

    print()
    print(
        "effective activity entries:",
        len(
            effective_values
        ),
    )

    print(
        "spike entries:",
        len(
            spike_values
        ),
    )

    print(
        "positive voltage entries:",
        len(
            voltage_values
        ),
    )

    print()
    print(
        "replay:",
        npz_path,
    )

    print(
        "replay sha256:",
        sha256_file(
            npz_path
        ),
    )

    print(
        "metadata:",
        json_path,
    )

    print(
        "metadata sha256:",
        sha256_file(
            json_path
        ),
    )

    print()
    print(
        "READ ONLY: YES"
    )

    print(
        "SIMULATION FEEDBACK: NO"
    )

    print(
        "FINANCIAL SEMANTICS USED: NO"
    )

    print()
    print(
        "MQ-4.1 TELEMETRY EXPORT COMPLETE"
    )


if __name__ == "__main__":
    main()
