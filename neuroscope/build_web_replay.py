from __future__ import annotations

import json
from pathlib import Path

import numpy as np


SOURCE = Path(
    "/home/wil/moscaquant-data/neuroscope/"
    "mq4-neuroscope-replay-A-v1.npz"
)

CAUSAL = Path(
    "/home/wil/moscaquant-data/processed/"
    "mq3-2-first-onset-causal-edges-v1.json"
)

OUTPUT = Path(
    "neuroscope/web/data/replay-A-v1.json"
)


ROLE_RETINA = 1
ROLE_RELAY = 2
ROLE_GRADED = 4
ROLE_DN = 8
ROLE_RESPONDER = 16


def sparse_frame(
    offsets,
    indices,
    values,
    frame,
    selected_lookup,
):
    start = int(
        offsets[frame]
    )

    end = int(
        offsets[frame + 1]
    )

    output = []

    for index, value in zip(
        indices[start:end],
        values[start:end],
    ):
        index = int(index)

        local = selected_lookup.get(
            index
        )

        if local is None:
            continue

        output.append(
            [
                local,
                float(value),
            ]
        )

    return output


def main():
    data = np.load(
        SOURCE,
        allow_pickle=False,
    )

    causal_data = json.loads(
        CAUSAL.read_text(
            encoding="utf-8"
        )
    )

    neuron_ids = np.asarray(
        data["neuron_ids"],
        dtype=np.int64,
    )

    retina = set(
        int(x)
        for x in data[
            "retinal_indices"
        ]
    )

    relay = set(
        int(x)
        for x in data[
            "relay_indices"
        ]
    )

    graded_indices = np.asarray(
        data["graded_indices"],
        dtype=np.int32,
    )

    graded_types = np.asarray(
        data["graded_types"],
    ).astype(str)

    graded = {
        int(index): str(cell_type)
        for index, cell_type
        in zip(
            graded_indices,
            graded_types,
        )
    }

    dn_indices = np.asarray(
        data["dn_indices"],
        dtype=np.int32,
    )

    dn_clusters = np.asarray(
        data["dn_clusters"],
        dtype=np.int32,
    )

    dn = {
        int(index): int(cluster)
        for index, cluster
        in zip(
            dn_indices,
            dn_clusters,
        )
    }

    responders = set(
        int(x)
        for x in data[
            "responder_indices"
        ]
    )

    #
    # Causal-path endpoints are first-class
    # Neuroscope nodes even when they are not
    # members of the four primary populations.
    #
    causal_nodes = set()

    for edge in causal_data[
        "edges"
    ]:
        causal_nodes.add(
            int(
                edge[
                    "presynaptic"
                ]
            )
        )

        causal_nodes.add(
            int(
                edge[
                    "postsynaptic"
                ]
            )
        )

    selected = sorted(
        retina
        | relay
        | set(graded)
        | set(dn)
        | causal_nodes
    )

    lookup = {
        model_index:
            local_index
        for local_index, model_index
        in enumerate(selected)
    }

    #
    # Translate frozen model-index causal
    # edges into viewer-local node indices.
    #
    causal_edges = []

    for edge in causal_data[
        "edges"
    ]:
        pre = int(
            edge[
                "presynaptic"
            ]
        )

        post = int(
            edge[
                "postsynaptic"
            ]
        )

        if (
            pre not in lookup
            or post not in lookup
        ):
            raise RuntimeError(
                "causal endpoint missing "
                f"from viewer population: "
                f"{pre}->{post}"
            )

        causal_edges.append(
            {
                "pre":
                    lookup[
                        pre
                    ],

                "post":
                    lookup[
                        post
                    ],

                "preModel":
                    pre,

                "postModel":
                    post,

                "weight":
                    float(
                        edge[
                            "weight"
                        ]
                    ),

                "frames":
                    [
                        int(x)
                        for x
                        in edge[
                            "observed_frames"
                        ]
                    ],

                "targets":
                    [
                        int(x)
                        for x
                        in edge[
                            "targets"
                        ]
                    ],
            }
        )

    expected_causal_edges = len(
        causal_data[
            "edges"
        ]
    )

    if (
        len(
            causal_edges
        )
        != expected_causal_edges
    ):
        raise RuntimeError(
            "causal edge export incomplete: "
            f"expected "
            f"{expected_causal_edges}, "
            f"exported "
            f"{len(causal_edges)}"
        )

    nodes = []

    for model_index in selected:

        roles = 0

        if model_index in retina:
            roles |= ROLE_RETINA

        if model_index in relay:
            roles |= ROLE_RELAY

        if model_index in graded:
            roles |= ROLE_GRADED

        if model_index in dn:
            roles |= ROLE_DN

        if model_index in responders:
            roles |= ROLE_RESPONDER

        nodes.append(
            {
                "i":
                    model_index,

                "body":
                    int(
                        neuron_ids[
                            model_index
                        ]
                    ),

                "roles":
                    roles,

                "gradedType":
                    graded.get(
                        model_index
                    ),

                "dnCluster":
                    dn.get(
                        model_index
                    ),

                "causalNode":
                    bool(
                        model_index
                        in causal_nodes
                    ),
            }
        )

    effective_offsets = data[
        "effective_offsets"
    ]

    effective_indices = data[
        "effective_indices"
    ]

    effective_values = data[
        "effective_values"
    ]

    spike_offsets = data[
        "spike_offsets"
    ]

    spike_indices = data[
        "spike_indices"
    ]

    spike_values = data[
        "spike_values"
    ]

    voltage_offsets = data[
        "positive_voltage_offsets"
    ]

    voltage_indices = data[
        "positive_voltage_indices"
    ]

    voltage_values = data[
        "positive_voltage_values"
    ]

    frame_count = (
        len(
            effective_offsets
        )
        - 1
    )

    frames = []

    for frame in range(
        frame_count
    ):
        frames.append(
            {
                "effective":
                    sparse_frame(
                        effective_offsets,
                        effective_indices,
                        effective_values,
                        frame,
                        lookup,
                    ),

                "spikes":
                    sparse_frame(
                        spike_offsets,
                        spike_indices,
                        spike_values,
                        frame,
                        lookup,
                    ),

                "voltage":
                    sparse_frame(
                        voltage_offsets,
                        voltage_indices,
                        voltage_values,
                        frame,
                        lookup,
                    ),

                "dnMean":
                    [
                        float(x)
                        for x in data[
                            "dn_mean_positive"
                        ][
                            frame
                        ]
                    ],

                "dnMax":
                    [
                        float(x)
                        for x in data[
                            "dn_max_positive"
                        ][
                            frame
                        ]
                    ],

                "dnSpikes":
                    [
                        int(x)
                        for x in data[
                            "dn_spike_count"
                        ][
                            frame
                        ]
                    ],

                "retinalSpikes":
                    int(
                        data[
                            "retinal_spike_count"
                        ][
                            frame
                        ]
                    ),

                "relaySpikes":
                    int(
                        data[
                            "relay_spike_count"
                        ][
                            frame
                        ]
                    ),

                "gradedActive":
                    int(
                        data[
                            "graded_active_count"
                        ][
                            frame
                        ]
                    ),

                "responders":
                    [
                        float(x)
                        for x in data[
                            "responder_voltage"
                        ][
                            frame
                        ]
                    ],
            }
        )

    payload = {
        "schema":
            "mq4-neuroscope-web-v1",

        "source":
            SOURCE.name,

        "layout":
            "signal-flow",

        "anatomicalCoordinates":
            False,

        "roleBits": {
            "retina":
                ROLE_RETINA,

            "relay":
                ROLE_RELAY,

            "graded":
                ROLE_GRADED,

            "dn":
                ROLE_DN,

            "responder":
                ROLE_RESPONDER,
        },

        "frameCount":
            frame_count,

        "populationCount":
            len(
                nodes
            ),

        "nodes":
            nodes,

        "responderModelIndices":
            [
                int(x)
                for x in data[
                    "responder_indices"
                ]
            ],

        "causalEdges":
            causal_edges,

        "frames":
            frames,
    }

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT.write_text(
        json.dumps(
            payload,
            separators=(
                ",",
                ":",
            ),
        ),
        encoding="utf-8",
    )

    print("=" * 72)
    print(
        "MQ-4.2 NEUROSCOPE WEB REPLAY"
    )
    print("=" * 72)

    print(
        "selected nodes:",
        len(
            nodes
        ),
    )

    print(
        "causal nodes:",
        len(
            causal_nodes
        ),
    )

    print(
        "causal edges:",
        len(
            causal_edges
        ),
    )

    print(
        "frames:",
        frame_count,
    )

    print(
        "output:",
        OUTPUT,
    )

    print(
        "size MiB:",
        round(
            OUTPUT.stat().st_size
            / 1024
            / 1024,
            2,
        ),
    )

    print()
    print(
        "LAYOUT: SIGNAL FLOW"
    )

    print(
        "ANATOMICAL COORDINATES: NO"
    )


if __name__ == "__main__":
    main()
