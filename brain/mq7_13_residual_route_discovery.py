from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

from brain.mq7_o1_o2_activation import (
    csr_digest,
    load_inputs,
)


SOURCE = 68045
KNOWN_NODE = 1273
TOP_N = 25
MAX_EDGES = 3

OUTPUT = (
    Path.home()
    / "moscaquant-data"
    / "experiments"
    / "mq7-13-residual-route-discovery-v1.json"
)


def outgoing(csc, presynaptic: int):
    column = csc.getcol(
        presynaptic
    )

    return [
        (
            int(post),
            float(weight),
        )
        for post, weight
        in zip(
            column.indices,
            column.data,
        )
        if float(weight) != 0.0
    ]


def enumerate_paths(
    *,
    csc,
    source,
    destinations,
    max_edges,
):
    routes = []

    def walk(
        node,
        path,
        weights,
    ):
        edge_count = len(weights)

        if (
            edge_count > 0
            and node in destinations
        ):
            strength = 1.0

            for weight in weights:
                strength *= weight

            routes.append({
                "path":
                    list(path),
                "weights":
                    list(weights),
                "edge_count":
                    edge_count,
                "path_strength":
                    abs(strength),
                "signed_product":
                    strength,
            })

        if edge_count >= max_edges:
            return

        for next_node, weight in outgoing(
            csc,
            node,
        ):
            if next_node in path:
                continue

            walk(
                next_node,
                path + [next_node],
                weights + [weight],
            )

    walk(
        source,
        [source],
        [],
    )

    return routes


def sort_key(route):
    return (
        -route["path_strength"],
        route["edge_count"],
        tuple(route["path"]),
    )


def main():
    (
        connectome,
        _retinal_indices,
        channel_indices,
        _release_gain,
    ) = load_inputs()

    digest_before = csr_digest(
        connectome
    )

    dn_c1 = {
        int(index)
        for index
        in channel_indices["DN-C1"]
    }

    csc = connectome.tocsc()

    known_weight = float(
        connectome[
            KNOWN_NODE,
            SOURCE,
        ]
    )

    print("=" * 72)
    print(
        "MQ-7.13 RESIDUAL ROUTE DISCOVERY"
    )
    print("=" * 72)

    print(
        "source:",
        SOURCE,
    )

    print(
        "DN-C1 destination count:",
        len(dn_c1),
    )

    print(
        "max path length:",
        MAX_EDGES,
    )

    print(
        "known edge:",
        f"{SOURCE}->{KNOWN_NODE}",
        "weight=",
        known_weight,
    )

    routes = enumerate_paths(
        csc=csc,
        source=SOURCE,
        destinations=dn_c1,
        max_edges=MAX_EDGES,
    )

    print(
        "total candidate routes:",
        len(routes),
    )

    known_routes = [
        route
        for route in routes
        if KNOWN_NODE in route["path"][1:]
    ]

    residual_routes = [
        route
        for route in routes
        if KNOWN_NODE not in route["path"][1:]
    ]

    residual_routes.sort(
        key=sort_key
    )

    top_routes = (
        residual_routes[:TOP_N]
    )

    print(
        "routes containing 1273:",
        len(known_routes),
    )

    print(
        "residual routes:",
        len(residual_routes),
    )

    print()
    print("=" * 72)
    print(
        f"TOP {TOP_N} RESIDUAL ROUTES"
    )
    print("=" * 72)

    intermediate_stats = defaultdict(
        lambda: {
            "route_count": 0,
            "summed_path_strength": 0.0,
        }
    )

    for rank, route in enumerate(
        top_routes,
        start=1,
    ):
        path = route["path"]

        print()
        print(
            rank,
            " -> ".join(
                str(node)
                for node in path
            ),
        )

        print(
            "weights:",
            route["weights"],
        )

        print(
            "edges:",
            route["edge_count"],
        )

        print(
            "strength:",
            route["path_strength"],
        )

        print(
            "signed product:",
            route["signed_product"],
        )

        #
        # Exclude source and terminal DN-C1
        # neuron from intermediate-node stats.
        #
        for node in path[1:-1]:
            stats = intermediate_stats[
                node
            ]

            stats["route_count"] += 1
            stats[
                "summed_path_strength"
            ] += route[
                "path_strength"
            ]

    ranked_intermediates = [
        {
            "node": int(node),
            "route_count":
                stats["route_count"],
            "summed_path_strength":
                stats[
                    "summed_path_strength"
                ],
        }
        for node, stats
        in intermediate_stats.items()
    ]

    ranked_intermediates.sort(
        key=lambda item: (
            -item[
                "summed_path_strength"
            ],
            -item["route_count"],
            item["node"],
        )
    )

    print()
    print("=" * 72)
    print(
        "INTERMEDIATE NODE RANKING"
    )
    print("=" * 72)

    for rank, item in enumerate(
        ranked_intermediates,
        start=1,
    ):
        print(
            rank,
            "node=",
            item["node"],
            "routes=",
            item["route_count"],
            "summed_strength=",
            item[
                "summed_path_strength"
            ],
        )

    if (
        csr_digest(connectome)
        != digest_before
    ):
        raise RuntimeError(
            "structural connectome mutated"
        )

    payload = {
        "schema_version":
            "mq7-residual-route-discovery/v1",
        "source":
            SOURCE,
        "known_node":
            KNOWN_NODE,
        "known_edge_weight":
            known_weight,
        "dn_c1_destination_count":
            len(dn_c1),
        "max_edges":
            MAX_EDGES,
        "total_candidate_routes":
            len(routes),
        "known_node_route_count":
            len(known_routes),
        "residual_route_count":
            len(residual_routes),
        "top_residual_routes":
            top_routes,
        "ranked_intermediate_nodes":
            ranked_intermediates,
        "connectome_unchanged":
            True,
    }

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT.write_text(
        json.dumps(
            payload,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )

    print()
    print(
        "connectome unchanged: True"
    )

    print(
        "results:",
        OUTPUT,
    )

    print(
        "MQ-7.13 COMPLETE"
    )


if __name__ == "__main__":
    main()
