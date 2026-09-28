from __future__ import annotations

import hashlib
import json
from collections import deque
from pathlib import Path

import numpy as np
from scipy import sparse

from config.paths import data_path


CONNECTOME = data_path("processed", "connectome-baseline-v1.npz")

OUTPUT = Path("config/controls/sq08-three-body-topology-v1.json")

MAX_HOPS = 4

BODY_RESPONDERS = {
    "A": 137122,
    "B": 317,
    "C": 126002,
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def downstream_distances(
    graph: sparse.csr_matrix,
    source: int,
    max_hops: int,
) -> dict[int, int]:
    """
    Return the minimum directed hop distance from source to every reachable
    downstream node within max_hops.

    Connectome convention:
        graph[postsynaptic, presynaptic] = weight
    Therefore downstream targets of presynaptic node `u` are nonzero rows
    in column `u`.
    """
    if source < 0 or source >= graph.shape[1]:
        raise RuntimeError(f"source index out of range: {source}")

    csc = graph.tocsc()

    distances = {int(source): 0}
    queue = deque([int(source)])

    while queue:
        node = queue.popleft()
        hop = distances[node]

        if hop >= max_hops:
            continue

        start = csc.indptr[node]
        stop = csc.indptr[node + 1]
        targets = csc.indices[start:stop]

        for target in targets:
            target = int(target)

            if target in distances:
                continue

            distances[target] = hop + 1
            queue.append(target)

    return distances


def canonical_branch(distances: dict[int, int], source: int) -> list[dict]:
    rows = []

    for node, hop in sorted(
        distances.items(),
        key=lambda item: (item[1], item[0]),
    ):
        if node == source:
            continue

        rows.append(
            {
                "node": int(node),
                "min_hops": int(hop),
            }
        )

    return rows


def node_set(branch: list[dict]) -> set[int]:
    return {int(row["node"]) for row in branch}


def main() -> None:
    graph = sparse.load_npz(CONNECTOME).tocsr()

    if graph.shape[0] != graph.shape[1]:
        raise RuntimeError("connectome must be square")

    connectome_sha256 = sha256_file(CONNECTOME)

    branches = {}
    branch_sets = {}

    for body in ("A", "B", "C"):
        source = BODY_RESPONDERS[body]

        distances = downstream_distances(
            graph=graph,
            source=source,
            max_hops=MAX_HOPS,
        )

        branch = canonical_branch(
            distances=distances,
            source=source,
        )

        branches[body] = branch
        branch_sets[body] = node_set(branch)

    ab = sorted(branch_sets["A"] & branch_sets["B"])
    ac = sorted(branch_sets["A"] & branch_sets["C"])
    bc = sorted(branch_sets["B"] & branch_sets["C"])
    abc = sorted(
        branch_sets["A"]
        & branch_sets["B"]
        & branch_sets["C"]
    )

    payload = {
        "schema_version": "moscaquant.sq08-three-body-topology/v1",
        "experiment": "SQ-08",
        "codename": "THREE BODY PROBLEM",
        "derivation": {
            "connectome_path": str(CONNECTOME),
            "connectome_sha256": connectome_sha256,
            "directed": True,
            "maximum_hops": MAX_HOPS,
            "selection_uses_sq08_outcomes": False,
            "branch_membership_rule": (
                "all downstream nodes reachable from the frozen BODY "
                "responder within <= 4 directed connectome hops"
            ),
        },
        "bodies": {
            "A": {
                "edge_id": "E10",
                "responder": 137122,
            },
            "B": {
                "edge_id": "E11",
                "responder": 317,
            },
            "C": {
                "edge_id": "E12",
                "responder": 126002,
            },
        },
        "branches": branches,
        "convergence": {
            "AB": ab,
            "AC": ac,
            "BC": bc,
            "ABC": abc,
        },
        "counts": {
            "branch_A": len(branches["A"]),
            "branch_B": len(branches["B"]),
            "branch_C": len(branches["C"]),
            "AB": len(ab),
            "AC": len(ac),
            "BC": len(bc),
            "ABC": len(abc),
        },
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    encoded = (
        json.dumps(payload, indent=2, sort_keys=True)
        + "\n"
    )

    OUTPUT.write_text(encoded)

    print("SQ-08 THREE BODY topology frozen")
    print("connectome:", CONNECTOME)
    print("connectome sha256:", connectome_sha256)

    for key, value in payload["counts"].items():
        print(f"{key}: {value}")

    print("output:", OUTPUT)
    print("output sha256:", sha256_file(OUTPUT))


if __name__ == "__main__":
    main()
