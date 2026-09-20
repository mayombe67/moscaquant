from __future__ import annotations
from config.paths import data_path


import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
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
from brain.visual_transduction import VisualTransductionConfig
from market.features import compute_features
from market.normalization import CausalNormalizer


BASE = data_path('processed')

RAW = data_path('raw')

CONNECTOME = BASE / "connectome-baseline-v1.npz"
RETINA = BASE / "visual-r1-r6-map-v1.npz"
RELAY = BASE / "visual-relay-map-v1.npz"
TERRITORIES = BASE / "market-retinal-territories-v1.npz"

GRADED = (
    BASE
    / "mq3-2-graded-visual-types-v1.npz"
)

NEURON_IDS = (
    BASE
    / "neuron_ids.npy"
)

ANNOTATIONS = (
    RAW
    / "body-annotations-male-cns-v1.0-minconf-0.5.feather"
)

OUTPUT = data_path('experiments', 'mq3-2-causal-path-decomposition-v1.json')

RELEASE_GAIN = 0.9981738484618123

SOURCE_TYPES = {
    "Tm2",
    "Tm4",
}

RESPONDERS = (
    92,
    656,
    317,
    137122,
    126002,
    55,
    129,
    51,
    1273,
)

MAX_HOPS = 4
MAX_PATHS = 50


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


def annotation_lookup():
    annotations = pd.read_feather(
        ANNOTATIONS
    ).set_index(
        "bodyId"
    )

    return annotations


def neuron_description(
    model_index,
    neuron_ids,
    annotations,
):
    body_id = int(
        neuron_ids[
            model_index
        ]
    )

    result = {
        "model_index":
            int(model_index),

        "body_id":
            body_id,

        "type":
            None,

        "instance":
            None,

        "superclass":
            None,
    }

    if body_id not in annotations.index:
        return result

    row = annotations.loc[
        body_id
    ]

    for column in (
        "type",
        "instance",
        "superclass",
    ):
        if column not in annotations.columns:
            continue

        value = row[
            column
        ]

        if pd.isna(value):
            continue

        result[
            column
        ] = str(value)

    return result


def activity_value(
    frame_indices,
    frame_values,
    neuron_index,
):
    position = np.searchsorted(
        frame_indices,
        neuron_index,
    )

    if (
        position
        >= len(frame_indices)
    ):
        return 0.0

    if (
        int(
            frame_indices[
                position
            ]
        )
        != neuron_index
    ):
        return 0.0

    return float(
        frame_values[
            position
        ]
    )


def active_positive_parents(
    connectome,
    node,
    frame_indices,
    frame_values,
):
    row = connectome.getrow(
        node
    )

    columns = row.indices
    weights = row.data

    positive = (
        weights > 0
    )

    columns = columns[
        positive
    ]

    weights = weights[
        positive
    ]

    if not len(columns):
        return []

    common, row_positions, activity_positions = (
        np.intersect1d(
            columns,
            frame_indices,
            assume_unique=True,
            return_indices=True,
        )
    )

    if not len(common):
        return []

    results = []

    for (
        parent,
        row_position,
        activity_position,
    ) in zip(
        common,
        row_positions,
        activity_positions,
    ):
        activity = float(
            frame_values[
                activity_position
            ]
        )

        if activity <= 0:
            continue

        weight = float(
            weights[
                row_position
            ]
        )

        contribution = (
            activity
            * weight
        )

        if contribution <= 0:
            continue

        results.append(
            {
                "parent":
                    int(parent),

                "weight":
                    weight,

                "activity":
                    activity,

                "contribution":
                    float(
                        contribution
                    ),
            }
        )

    results.sort(
        key=lambda item:
            item["contribution"],
        reverse=True,
    )

    return results


def trace_paths(
    connectome,
    activities,
    target,
    target_frame,
    source_indices,
):
    found = []

    #
    # Each state stores path in reverse:
    #
    # target <- parent <- parent ...
    #
    stack = [
        {
            "node":
                int(target),

            "frame":
                int(target_frame),

            "nodes":
                [
                    int(target)
                ],

            "edges":
                [],
        }
    ]

    while stack:
        state = stack.pop()

        node = state[
            "node"
        ]

        frame = state[
            "frame"
        ]

        hops = len(
            state[
                "edges"
            ]
        )

        if hops >= MAX_HOPS:
            continue

        if frame < 0:
            continue

        frame_indices = (
            activities[
                frame
            ][
                "indices"
            ]
        )

        frame_values = (
            activities[
                frame
            ][
                "values"
            ]
        )

        parents = (
            active_positive_parents(
                connectome,
                node,
                frame_indices,
                frame_values,
            )
        )

        for parent_data in parents:

            parent = int(
                parent_data[
                    "parent"
                ]
            )

            edge = {
                "presynaptic":
                    parent,

                "postsynaptic":
                    int(node),

                "frame":
                    int(frame),

                "weight":
                    float(
                        parent_data[
                            "weight"
                        ]
                    ),

                "presynaptic_activity":
                    float(
                        parent_data[
                            "activity"
                        ]
                    ),

                "instantaneous_contribution":
                    float(
                        parent_data[
                            "contribution"
                        ]
                    ),
            }

            new_nodes = (
                state[
                    "nodes"
                ]
                + [
                    parent
                ]
            )

            new_edges = (
                state[
                    "edges"
                ]
                + [
                    edge
                ]
            )

            if parent in source_indices:

                contributions = [
                    item[
                        "instantaneous_contribution"
                    ]
                    for item
                    in new_edges
                ]

                weights = [
                    item[
                        "weight"
                    ]
                    for item
                    in new_edges
                ]

                found.append(
                    {
                        "source":
                            parent,

                        "target":
                            int(target),

                        "target_frame":
                            int(
                                target_frame
                            ),

                        "hop_count":
                            len(
                                new_edges
                            ),

                        #
                        # Reverse into natural
                        # source -> target order.
                        #
                        "nodes":
                            list(
                                reversed(
                                    new_nodes
                                )
                            ),

                        "edges":
                            list(
                                reversed(
                                    new_edges
                                )
                            ),

                        "bottleneck_contribution":
                            float(
                                min(
                                    contributions
                                )
                            ),

                        "path_weight_product":
                            float(
                                np.prod(
                                    weights
                                )
                            ),
                    }
                )

                continue

            #
            # Activity seen before frame F
            # was produced by state resulting
            # from frame F-1.
            #
            next_frame = (
                frame - 1
            )

            if next_frame < 0:
                continue

            stack.append(
                {
                    "node":
                        parent,

                    "frame":
                        next_frame,

                    "nodes":
                        new_nodes,

                    "edges":
                        new_edges,
                }
            )

    found.sort(
        key=lambda item:
            (
                item[
                    "bottleneck_contribution"
                ],
                item[
                    "path_weight_product"
                ],
            ),
        reverse=True,
    )

    return found[
        :MAX_PATHS
    ]


def main():
    connectome = sparse.load_npz(
        CONNECTOME
    ).tocsr()

    retina = np.load(
        RETINA
    )

    graded = np.load(
        GRADED
    )

    neuron_ids = np.load(
        NEURON_IDS
    )

    annotations = (
        annotation_lookup()
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
        ]
    ).astype(str)

    source_mask = np.isin(
        graded_types,
        list(
            SOURCE_TYPES
        ),
    )

    source_indices_array = (
        graded_indices[
            source_mask
        ]
    )

    source_indices = set(
        int(x)
        for x in source_indices_array
    )

    source_type = {
        int(index):
            str(cell_type)
        for index, cell_type
        in zip(
            graded_indices,
            graded_types,
        )
        if cell_type
        in SOURCE_TYPES
    }

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

    activities = []

    responder_voltage = {
        responder:
            []
        for responder
        in RESPONDERS
    }

    print("=" * 88)
    print(
        "MQ-3.2 CAUSAL PATH "
        "DECOMPOSITION"
    )
    print("=" * 88)

    print(
        "source types:",
        sorted(
            SOURCE_TYPES
        ),
    )

    print(
        "source population:",
        len(
            source_indices
        ),
    )

    print(
        "targets:",
        len(
            RESPONDERS
        ),
    )

    print()
    print(
        "replaying Condition A..."
    )

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

            #
            # IMPORTANT:
            #
            # Capture the exact presynaptic
            # effective activity that will
            # drive this step.
            #
            effective = (
                runtime.effective_activity()
            )

            active_indices = np.flatnonzero(
                effective > 0
            ).astype(
                np.int32
            )

            active_values = np.asarray(
                effective[
                    active_indices
                ],
                dtype=np.float32,
            )

            activities.append(
                {
                    "indices":
                        active_indices,

                    "values":
                        active_values,
                }
            )

            runtime.step(
                stimulus
                * SENSORY_GAIN
            )

            for responder in RESPONDERS:
                responder_voltage[
                    responder
                ].append(
                    float(
                        runtime.voltage[
                            responder
                        ]
                    )
                )

    frame_count = len(
        activities
    )

    if frame_count != (
        OBSERVATIONS
        * FRAME_COUNT
    ):
        raise RuntimeError(
            "unexpected replay frame count"
        )

    print(
        "frames:",
        frame_count,
    )

    #
    # Determine first-positive and peak
    # frames independently for every target.
    #
    target_results = []

    for responder in RESPONDERS:

        voltage = np.asarray(
            responder_voltage[
                responder
            ],
            dtype=np.float64,
        )

        positive_frames = (
            np.flatnonzero(
                voltage > 0
            )
        )

        if not len(
            positive_frames
        ):
            raise RuntimeError(
                f"responder {responder} "
                "did not reproduce"
            )

        first_frame = int(
            positive_frames[
                0
            ]
        )

        peak_frame = int(
            np.argmax(
                voltage
            )
        )

        target_info = neuron_description(
            responder,
            neuron_ids,
            annotations,
        )

        print()
        print("=" * 88)
        print(
            "TARGET",
            responder,
            target_info[
                "body_id"
            ],
            target_info[
                "type"
            ],
            target_info[
                "instance"
            ],
        )
        print("=" * 88)

        print(
            "first positive:",
            first_frame,
            "V=",
            float(
                voltage[
                    first_frame
                ]
            ),
        )

        print(
            "peak:",
            peak_frame,
            "V=",
            float(
                voltage[
                    peak_frame
                ]
            ),
        )

        frame_results = []

        for label, frame in (
            (
                "first_positive",
                first_frame,
            ),
            (
                "peak",
                peak_frame,
            ),
        ):

            paths = trace_paths(
                connectome,
                activities,
                responder,
                frame,
                source_indices,
            )

            #
            # Add biological labels.
            #
            for path in paths:

                path[
                    "source_type"
                ] = source_type[
                    path[
                        "source"
                    ]
                ]

                path[
                    "source_info"
                ] = neuron_description(
                    path[
                        "source"
                    ],
                    neuron_ids,
                    annotations,
                )

                path[
                    "node_info"
                ] = [
                    neuron_description(
                        index,
                        neuron_ids,
                        annotations,
                    )
                    for index
                    in path[
                        "nodes"
                    ]
                ]

            print()
            print(
                label,
                "frame",
                frame,
                "paths=",
                len(paths),
            )

            if paths:

                type_counts = {}

                for path in paths:
                    cell_type = path[
                        "source_type"
                    ]

                    type_counts[
                        cell_type
                    ] = (
                        type_counts.get(
                            cell_type,
                            0,
                        )
                        + 1
                    )

                print(
                    "source type counts:",
                    type_counts,
                )

                for rank, path in enumerate(
                    paths[
                        :10
                    ],
                    start=1,
                ):
                    labels = []

                    for node in path[
                        "node_info"
                    ]:
                        name = (
                            node[
                                "type"
                            ]
                            or node[
                                "instance"
                            ]
                            or str(
                                node[
                                    "body_id"
                                ]
                            )
                        )

                        labels.append(
                            f"{name}"
                            f"[{node['model_index']}]"
                        )

                    print(
                        f"  #{rank}",
                        " -> ".join(
                            labels
                        ),
                    )

                    print(
                        "     hops=",
                        path[
                            "hop_count"
                        ],
                        "source=",
                        path[
                            "source_type"
                        ],
                        "bottleneck=",
                        path[
                            "bottleneck_contribution"
                        ],
                        "weight_product=",
                        path[
                            "path_weight_product"
                        ],
                    )

                    for edge in path[
                        "edges"
                    ]:
                        print(
                            "       frame",
                            edge[
                                "frame"
                            ],
                            edge[
                                "presynaptic"
                            ],
                            "->",
                            edge[
                                "postsynaptic"
                            ],
                            "w=",
                            edge[
                                "weight"
                            ],
                            "activity=",
                            edge[
                                "presynaptic_activity"
                            ],
                            "contribution=",
                            edge[
                                "instantaneous_contribution"
                            ],
                        )

            frame_results.append(
                {
                    "label":
                        label,

                    "frame":
                        frame,

                    "target_voltage":
                        float(
                            voltage[
                                frame
                            ]
                        ),

                    "path_count_reported":
                        len(
                            paths
                        ),

                    "paths":
                        paths,
                }
            )

        target_results.append(
            {
                "target":
                    target_info,

                "first_positive_frame":
                    first_frame,

                "peak_frame":
                    peak_frame,

                "maximum_voltage":
                    float(
                        voltage[
                            peak_frame
                        ]
                    ),

                "frames":
                    frame_results,
            }
        )

    output = {
        "experiment":
            "mq3-2-causal-path-decomposition-v1",

        "condition":
            "A",

        "method":
            (
                "time-unrolled positive-edge "
                "activity-supported path search"
            ),

        "max_hops":
            MAX_HOPS,

        "max_paths_per_target_frame":
            MAX_PATHS,

        "sources": {
            "types":
                sorted(
                    SOURCE_TYPES
                ),

            "population_count":
                len(
                    source_indices
                ),
        },

        "targets":
            target_results,

        "interpretation_limits": [
            (
                "Structural connectivity alone "
                "is not treated as causal evidence."
            ),
            (
                "Every reported edge had positive "
                "presynaptic modeled activity at "
                "the corresponding replay frame."
            ),
            (
                "Only positive-weight transmission "
                "is followed in this decomposition."
            ),
            (
                "These are activity-supported causal "
                "candidate paths, not interventional "
                "causal proof."
            ),
        ],

        "artifact_hashes": {
            "connectome":
                sha256_file(
                    CONNECTOME
                ),

            "graded_population":
                sha256_file(
                    GRADED
                ),
        },

        "financial_semantics_used":
            False,
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
    print("=" * 88)
    print("CAUSAL PATH SUMMARY")
    print("=" * 88)

    for target in target_results:

        info = target[
            "target"
        ]

        print()
        print(
            info[
                "model_index"
            ],
            info[
                "body_id"
            ],
            info[
                "type"
            ],
            info[
                "instance"
            ],
        )

        for frame_result in target[
            "frames"
        ]:

            paths = frame_result[
                "paths"
            ]

            source_types = sorted(
                set(
                    path[
                        "source_type"
                    ]
                    for path
                    in paths
                )
            )

            hop_counts = sorted(
                set(
                    path[
                        "hop_count"
                    ]
                    for path
                    in paths
                )
            )

            print(
                " ",
                frame_result[
                    "label"
                ],
                "frame=",
                frame_result[
                    "frame"
                ],
                "paths=",
                len(
                    paths
                ),
                "sources=",
                source_types,
                "hops=",
                hop_counts,
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
        "CAUSAL CLAIM LEVEL: "
        "ACTIVITY-SUPPORTED CANDIDATE PATHS"
    )

    print()
    print(
        "MQ-3.2 CAUSAL PATH "
        "DECOMPOSITION COMPLETE"
    )


if __name__ == "__main__":
    main()
