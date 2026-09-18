from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.sparse.csgraph import shortest_path

from brain.mq7_o1_o2_activation import (
    load_inputs,
)


RESULTS = (
    Path.home()
    / "moscaquant-data"
    / "experiments"
    / "mq7-9-shock-target-specificity-v1.json"
)

OUTPUT = (
    Path.home()
    / "moscaquant-data"
    / "experiments"
    / "mq7-10-recruitment-topology-v1.json"
)

REFERENCE_NODES = (
    56393,
    68045,
    1273,
)


def fmt_distance(value):
    if np.isinf(value):
        return None
    return int(value)


def direct_weight(
    connectome,
    pre,
    post,
):
    return float(
        connectome[
            post,
            pre,
        ]
    )


def main():
    payload = json.loads(
        RESULTS.read_text()
    )

    (
        connectome,
        _retinal_indices,
        _channel_indices,
        _release_gain,
    ) = load_inputs()

    #
    # connectome[post, pre]
    #
    # scipy graph convention is graph[from, to],
    # therefore transpose for pre -> post.
    #
    graph = connectome.transpose().tocsr().copy()
    graph.data[:] = 1.0

    targets = [
        int(target)
        for target
        in payload["target_pool"]
    ]

    print("=" * 72)
    print(
        "MQ-7.10 RECRUITMENT TOPOLOGY"
    )
    print("=" * 72)

    print(
        "targets:",
        len(targets),
    )

    print(
        "reference pathway:",
        "56393 -> 68045 -> 1273",
    )

    #
    # Compute shortest unweighted directed
    # paths from all 13 targets at once.
    #
    distances = shortest_path(
        graph,
        directed=True,
        unweighted=True,
        indices=targets,
    )

    result_by_target = {
        int(record["target"]): record
        for record
        in payload["targets"]
    }

    records = []

    for row, target in enumerate(targets):
        mq7_record = (
            result_by_target[target]
        )

        deltas = (
            mq7_record[
                "difference"
            ][
                "score_deltas"
            ]
        )

        dn_c1_delta = float(
            deltas["DN-C1"]
        )

        exposed = (
            not mq7_record[
                "difference"
            ][
                "voltage_identical"
            ]
            or not mq7_record[
                "difference"
            ][
                "scores_identical"
            ]
        )

        distance_data = {
            str(node): fmt_distance(
                distances[row, node]
            )
            for node
            in REFERENCE_NODES
        }

        direct_data = {
            str(node): direct_weight(
                connectome,
                target,
                node,
            )
            for node
            in REFERENCE_NODES
        }

        record = {
            "target": target,
            "exposed_plasticity":
                exposed,
            "dn_c1_delta":
                dn_c1_delta,
            "abs_dn_c1_delta":
                abs(dn_c1_delta),
            "direct_weights":
                direct_data,
            "hop_distances":
                distance_data,
        }

        records.append(record)

    records.sort(
        key=lambda record:
            record[
                "abs_dn_c1_delta"
            ],
        reverse=True,
    )

    for record in records:
        print()
        print("-" * 72)

        print(
            "target:",
            record["target"],
        )

        print(
            "exposed:",
            record[
                "exposed_plasticity"
            ],
        )

        print(
            "|DN-C1 delta|:",
            record[
                "abs_dn_c1_delta"
            ],
        )

        print(
            "hops -> 56393:",
            record[
                "hop_distances"
            ]["56393"],
        )

        print(
            "hops -> 68045:",
            record[
                "hop_distances"
            ]["68045"],
        )

        print(
            "hops -> 1273:",
            record[
                "hop_distances"
            ]["1273"],
        )

        print(
            "direct -> 56393:",
            record[
                "direct_weights"
            ]["56393"],
        )

        print(
            "direct -> 68045:",
            record[
                "direct_weights"
            ]["68045"],
        )

        print(
            "direct -> 1273:",
            record[
                "direct_weights"
            ]["1273"],
        )

    print()
    print("=" * 72)
    print("RANKED BY EXPRESSION MAGNITUDE")
    print("=" * 72)

    for rank, record in enumerate(
        records,
        start=1,
    ):
        print(
            rank,
            record["target"],
            record[
                "abs_dn_c1_delta"
            ],
            "hops:",
            record[
                "hop_distances"
            ],
        )

    output = {
        "schema_version":
            "mq7-recruitment-topology/v1",
        "reference_pathway": [
            56393,
            68045,
            1273,
        ],
        "records":
            records,
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
        + "\n"
    )

    print()
    print(
        "results:",
        OUTPUT,
    )

    print(
        "MQ-7.10 COMPLETE"
    )


if __name__ == "__main__":
    main()
