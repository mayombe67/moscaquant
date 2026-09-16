from __future__ import annotations

import hashlib
import itertools
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
from brain.visual_transduction import (
    VisualTransductionConfig,
)
from market.features import compute_features
from market.normalization import CausalNormalizer


BASE = Path(
    "/home/wil/moscaquant-data/processed"
)

CONNECTOME = BASE / "connectome-baseline-v1.npz"
RETINA = BASE / "visual-r1-r6-map-v1.npz"
RELAY = BASE / "visual-relay-map-v1.npz"
TERRITORIES = BASE / "market-retinal-territories-v1.npz"
CONSENSUS = BASE / "mq3-dn-consensus-v1.npz"
GRADED = BASE / "mq3-2-graded-visual-types-v1.npz"

OUTPUT = Path(
    "/home/wil/moscaquant-data/experiments/"
    "mq3-2-graded-type-subsets-v1.json"
)

RELEASE_GAIN = 0.9981738484618123

ORDERED_TYPES = (
    "Tm2",
    "Tm3",
    "Tm4",
)

CHANNELS = (
    "DN-C0",
    "DN-C1",
    "DN-C2",
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


class SubsetVisualRuntime:
    """
    MQ-3.2 mechanistic subset runtime.

    Preserves MQ-2.1 retinal transduction.

    Only neurons belonging to the supplied
    frozen annotation-type subset may transmit
    positive subthreshold voltage.
    """

    def __init__(
        self,
        connectome,
        retinal_indices,
        relay_artifact,
        graded_indices,
        config,
    ):
        self.connectome = (
            connectome.tocsr()
        )

        self.config = config

        self.population_size = (
            self.connectome.shape[0]
        )

        self.retinal_indices = np.asarray(
            retinal_indices,
            dtype=np.int32,
        )

        self.graded_indices = np.asarray(
            graded_indices,
            dtype=np.int32,
        )

        relay = np.load(
            relay_artifact
        )

        self.relay_indices = np.asarray(
            relay["neuron_index"],
            dtype=np.int32,
        )

        self.relay_from_retina = (
            self.connectome[
                self.relay_indices,
                :
            ][
                :,
                self.retinal_indices
            ].tocsr()
        )

        if (
            self.relay_from_retina.nnz
            and np.any(
                self.relay_from_retina.data
                > 0
            )
        ):
            raise RuntimeError(
                "positive R1-R6 -> relay edge"
            )

        self.voltage = np.zeros(
            self.population_size,
            dtype=np.float32,
        )

        self.spikes = np.zeros(
            self.population_size,
            dtype=np.float32,
        )

        self.relay_inhibition = np.zeros(
            len(self.relay_indices),
            dtype=np.float32,
        )

        self.last_release = np.zeros(
            len(self.relay_indices),
            dtype=np.float32,
        )

        self.decay = np.exp(
            -config.dt_ms
            / config.tau_ms
        )

    def effective_activity(self):
        activity = self.spikes.copy()

        if len(
            self.graded_indices
        ):
            graded = np.clip(
                self.voltage[
                    self.graded_indices
                ],
                0.0,
                self.config.threshold,
            )

            graded /= (
                self.config.threshold
            )

            activity[
                self.graded_indices
            ] = np.maximum(
                self.spikes[
                    self.graded_indices
                ],
                graded,
            )

        return activity

    def step(
        self,
        stimulus,
    ):
        stimulus = np.asarray(
            stimulus,
            dtype=np.float32,
        )

        prior_spikes = self.spikes

        retinal_spikes = prior_spikes[
            self.retinal_indices
        ]

        direct_retinal_current = (
            self.relay_from_retina
            @ retinal_spikes
        )

        direct_retinal_current = np.asarray(
            direct_retinal_current,
            dtype=np.float32,
        ).ravel()

        inhibition = np.maximum(
            -direct_retinal_current,
            0.0,
        )

        release = np.maximum(
            self.relay_inhibition
            - inhibition,
            0.0,
        )

        activity = (
            self.effective_activity()
        )

        synaptic = (
            self.connectome
            @ activity
        )

        synaptic = np.asarray(
            synaptic,
            dtype=np.float32,
        ).ravel()

        synaptic[
            self.relay_indices
        ] -= direct_retinal_current

        self.voltage *= self.decay
        self.voltage += synaptic
        self.voltage += stimulus

        self.voltage[
            self.relay_indices
        ] += (
            release
            * self.config.release_gain
        )

        fired = (
            self.voltage
            >= self.config.threshold
        )

        self.spikes.fill(0.0)

        self.spikes[
            fired
        ] = 1.0

        self.voltage[
            fired
        ] = self.config.reset

        self.relay_inhibition[:] = (
            inhibition
        )

        self.last_release[:] = release

        return self.spikes


def build_subsets():
    subsets = []

    for size in range(
        len(ORDERED_TYPES) + 1
    ):
        for combo in itertools.combinations(
            ORDERED_TYPES,
            size,
        ):
            subsets.append(
                tuple(combo)
            )

    return subsets


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

    return result


def neutral_series():
    return np.zeros(
        (6, 7),
        dtype=np.float32,
    )


def run_condition(
    condition,
    subset,
    connectome,
    retinal_indices,
    graded_indices,
    graded_types,
    channel_indices,
):
    mask = np.isin(
        graded_types,
        subset,
    )

    selected_indices = (
        graded_indices[
            mask
        ]
    )

    runtime = SubsetVisualRuntime(
        connectome=connectome,
        retinal_indices=retinal_indices,
        relay_artifact=RELAY,
        graded_indices=selected_indices,
        config=VisualTransductionConfig(
            release_gain=RELEASE_GAIN,
        ),
    )

    encoder = MarketVisionTemporalEncoder(
        TERRITORIES
    )

    if condition != "neutral":
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
            for asset_index
            in range(6)
        ]

    scores_sum = {
        channel: 0.0
        for channel in CHANNELS
    }

    peak = {
        channel: 0.0
        for channel in CHANNELS
    }

    spike_count = {
        channel: 0
        for channel in CHANNELS
    }

    ever_positive = {
        channel:
            np.zeros(
                len(
                    channel_indices[
                        channel
                    ]
                ),
                dtype=bool,
            )
        for channel in CHANNELS
    }

    max_voltage = {
        channel:
            np.zeros(
                len(
                    channel_indices[
                        channel
                    ]
                ),
                dtype=np.float64,
            )
        for channel in CHANNELS
    }

    first_positive = {
        channel:
            np.full(
                len(
                    channel_indices[
                        channel
                    ]
                ),
                -1,
                dtype=np.int32,
            )
        for channel in CHANNELS
    }

    frame_number = 0

    for observation in range(
        OBSERVATIONS
    ):
        if condition == "neutral":
            normalized = neutral_series()

        else:
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
            runtime.step(
                stimulus
                * SENSORY_GAIN
            )

            for channel in CHANNELS:
                indices = channel_indices[
                    channel
                ]

                voltage = np.asarray(
                    runtime.voltage[
                        indices
                    ],
                    dtype=np.float64,
                )

                spikes = (
                    runtime.spikes[
                        indices
                    ] > 0
                )

                positive = np.maximum(
                    voltage,
                    0.0,
                )

                frame_metric = float(
                    positive.mean()
                )

                scores_sum[
                    channel
                ] += frame_metric

                peak[
                    channel
                ] = max(
                    peak[
                        channel
                    ],
                    frame_metric,
                )

                spike_count[
                    channel
                ] += int(
                    np.count_nonzero(
                        spikes
                    )
                )

                positive_mask = (
                    voltage > 0
                )

                newly = (
                    positive_mask
                    & (
                        first_positive[
                            channel
                        ]
                        < 0
                    )
                )

                first_positive[
                    channel
                ][
                    newly
                ] = frame_number

                ever_positive[
                    channel
                ] |= positive_mask

                max_voltage[
                    channel
                ] = np.maximum(
                    max_voltage[
                        channel
                    ],
                    voltage,
                )

            frame_number += 1

    result = {
        "condition":
            condition,

        "subset":
            list(subset),

        "graded_population_count":
            int(
                len(
                    selected_indices
                )
            ),

        "frames":
            frame_number,

        "channels": {},
    }

    for channel in CHANNELS:
        indices = channel_indices[
            channel
        ]

        result[
            "channels"
        ][
            channel
        ] = {
            "score":
                float(
                    scores_sum[
                        channel
                    ]
                    / frame_number
                ),

            "peak_frame_metric":
                float(
                    peak[
                        channel
                    ]
                ),

            "spike_count":
                int(
                    spike_count[
                        channel
                    ]
                ),

            "ever_positive_count":
                int(
                    np.count_nonzero(
                        ever_positive[
                            channel
                        ]
                    )
                ),

            "ever_positive_fraction":
                float(
                    np.mean(
                        ever_positive[
                            channel
                        ]
                    )
                ),

            "maximum_voltage":
                float(
                    max_voltage[
                        channel
                    ].max()
                ),

            "count_ge_0_001":
                int(
                    np.count_nonzero(
                        max_voltage[
                            channel
                        ]
                        >= 0.001
                    )
                ),

            "count_ge_0_002":
                int(
                    np.count_nonzero(
                        max_voltage[
                            channel
                        ]
                        >= 0.002
                    )
                ),

            "count_ge_0_004":
                int(
                    np.count_nonzero(
                        max_voltage[
                            channel
                        ]
                        >= 0.004
                    )
                ),

            "first_positive_frame":
                int(
                    first_positive[
                        channel
                    ][
                        first_positive[
                            channel
                        ] >= 0
                    ].min()
                )
                if np.any(
                    first_positive[
                        channel
                    ] >= 0
                )
                else None,
        }

    values = np.asarray(
        [
            result[
                "channels"
            ][
                channel
            ][
                "score"
            ]
            for channel in CHANNELS
        ],
        dtype=np.float64,
    )

    if np.all(
        values == 0.0
    ):
        outcome = {
            "outcome": "ABSTAIN",
            "winner": None,
        }

    else:
        maximum = float(
            values.max()
        )

        winners = np.flatnonzero(
            values == maximum
        )

        if len(winners) == 1:
            outcome = {
                "outcome": "WINNER",
                "winner":
                    CHANNELS[
                        int(
                            winners[0]
                        )
                    ],
            }
        else:
            outcome = {
                "outcome": "ABSTAIN",
                "winner": None,
            }

    result[
        "anonymous_outcome"
    ] = outcome

    return result


def subset_name(
    subset,
):
    if not subset:
        return "NONE"

    return "+".join(
        subset
    )


def main():
    connectome = sparse.load_npz(
        CONNECTOME
    ).tocsr()

    retina = np.load(
        RETINA
    )

    consensus = np.load(
        CONSENSUS
    )

    graded = np.load(
        GRADED
    )

    retinal_indices = np.asarray(
        retina[
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

    channel_indices = (
        build_channel_indices(
            consensus
        )
    )

    subsets = build_subsets()

    if len(subsets) != 8:
        raise RuntimeError(
            "expected exactly 8 subsets"
        )

    conditions = (
        "neutral",
        "A",
        "B",
    )

    records = []

    print("=" * 72)
    print(
        "MQ-3.2 GRADED TYPE "
        "SUBSET ATTRIBUTION"
    )
    print("=" * 72)

    for subset in subsets:
        name = subset_name(
            subset
        )

        population_count = int(
            np.count_nonzero(
                np.isin(
                    graded_types,
                    subset,
                )
            )
        )

        print()
        print("=" * 72)
        print(
            "SUBSET:",
            name,
        )
        print(
            "graded neurons:",
            population_count,
        )
        print("=" * 72)

        for condition in conditions:
            result = run_condition(
                condition,
                subset,
                connectome,
                retinal_indices,
                graded_indices,
                graded_types,
                channel_indices,
            )

            records.append(
                result
            )

            print()
            print(
                condition,
                result[
                    "anonymous_outcome"
                ],
            )

            for channel in CHANNELS:
                data = result[
                    "channels"
                ][
                    channel
                ]

                print(
                    " ",
                    channel,
                    "score=",
                    data["score"],
                    "ever+=",
                    data[
                        "ever_positive_count"
                    ],
                    "maxV=",
                    data[
                        "maximum_voltage"
                    ],
                    "spikes=",
                    data[
                        "spike_count"
                    ],
                    "first+=",
                    data[
                        "first_positive_frame"
                    ],
                )

    output = {
        "experiment":
            "mq3-2-graded-type-subsets-v1",

        "purpose":
            "post-hoc mechanistic attribution",

        "ordered_types":
            list(
                ORDERED_TYPES
            ),

        "subset_count":
            len(subsets),

        "condition_count":
            len(conditions),

        "total_runs":
            len(records),

        "financial_semantics_used":
            False,

        "discovery_claim_permitted":
            False,

        "records":
            records,

        "sources": {
            "connectome_sha256":
                sha256_file(
                    CONNECTOME
                ),

            "graded_population_sha256":
                sha256_file(
                    GRADED
                ),

            "consensus_sha256":
                sha256_file(
                    CONSENSUS
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
    print("SUMMARY MATRIX")
    print("=" * 72)

    for subset in subsets:
        name = subset_name(
            subset
        )

        relevant = [
            record
            for record in records
            if tuple(
                record["subset"]
            ) == subset
        ]

        row = []

        for condition in conditions:
            record = next(
                item
                for item in relevant
                if item[
                    "condition"
                ] == condition
            )

            outcome = record[
                "anonymous_outcome"
            ]

            if (
                outcome[
                    "outcome"
                ]
                == "ABSTAIN"
            ):
                value = "ABSTAIN"

            else:
                value = (
                    outcome[
                        "winner"
                    ]
                )

            row.append(
                f"{condition}={value}"
            )

        print(
            f"{name:12s}",
            " ".join(row),
        )

    print()
    print(
        "results:",
        OUTPUT,
    )

    print(
        "sha256:",
        sha256_file(
            OUTPUT
        ),
    )

    print()
    print(
        "FINANCIAL SEMANTICS USED: NO"
    )

    print(
        "POST-HOC MECHANISTIC "
        "ATTRIBUTION ONLY"
    )

    print()
    print(
        "MQ-3.2 GRADED TYPE "
        "SUBSET ATTRIBUTION COMPLETE"
    )


if __name__ == "__main__":
    main()
