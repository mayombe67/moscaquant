from __future__ import annotations

import json

import numpy as np

from brain.mq5_er3_retour_eligibility import (
    build_runtime_inputs,
    classify_edge,
)
from brain.mq5_ts_runtime import frozen_edges


CANDIDATES = (
    ("S1", 11725, 29921, (55, 126002, 137122)),
    ("S2", 11345, 47350, (92, 656, 126002)),
    ("S3", 10647, 51642, (55, 92, 656)),
)

RTOL = 1e-6
ATOL = 1e-12


def reverse_hop_map(graph, target: int, max_hops: int = 3) -> dict[int, int]:
    """
    Vectorized reverse BFS over CSR rows.

    graph[post, pre] stores pre -> post, so slicing rows for the current
    frontier yields all presynaptic predecessors in bulk. This avoids the
    millions of Python-level per-edge iterations in the first audit version.
    """
    result: dict[int, int] = {}
    seen = np.zeros(graph.shape[0], dtype=bool)
    frontier = np.asarray([int(target)], dtype=np.int32)
    seen[frontier] = True

    for hop in range(1, int(max_hops) + 1):
        if frontier.size == 0:
            break

        block = graph[frontier]
        pres = np.unique(block.indices.astype(np.int32, copy=False))
        if pres.size == 0:
            break

        new_pres = pres[~seen[pres]]
        for node in new_pres.tolist():
            result[int(node)] = int(hop)

        seen[pres] = True
        frontier = new_pres

    return result


def degree_arrays(graph):
    indegree = np.diff(graph.indptr).astype(np.int64)
    outdegree = np.bincount(
        graph.indices,
        minlength=graph.shape[0],
    ).astype(np.int64)
    return indegree, outdegree


def main():
    graph, runtime = build_runtime_inputs()
    indegree, outdegree = degree_arrays(graph)

    frozen13 = {
        (int(pre), int(post))
        for pre, post, _weight in frozen_edges()
    }

    unique_targets = sorted({
        int(t)
        for _sid, _pre, _post, targets in CANDIDATES
        for t in targets
    })
    hop_maps = {
        target: reverse_hop_map(graph, target, 3)
        for target in unique_targets
    }

    payload = {
        "kind": "PRE-OUTCOME STRUCTURAL AUDIT",
        "neural_outcomes_used": False,
        "candidates": [],
    }

    for sid, pre, post, targets in CANDIDATES:
        row = classify_edge(
            original=graph,
            runtime=runtime,
            pre=pre,
            post=post,
            rtol=RTOL,
            atol=ATOL,
        )

        row.update({
            "id": sid,
            "associated_targets": list(targets),
            "hop_signature": [
                hop_maps[int(t)].get(int(pre))
                for t in targets
            ],
            "presynaptic_outdegree": int(outdegree[pre]),
            "postsynaptic_indegree": int(indegree[post]),
            "is_original_13_edge": (pre, post) in frozen13,
        })

        payload["candidates"].append(row)

    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
