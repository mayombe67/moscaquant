from __future__ import annotations

import argparse
import json

import numpy as np
from scipy import sparse

from brain.mq5_ts_runtime import CONNECTOME


AFFECTED_TARGETS = (55, 92, 656, 126002, 137122)
RETAINED_DEPENDENCY_TARGETS = (51, 129, 317, 1273)
MAX_BACKWARD_HOPS = 3
DEFAULT_EDGE_VISIT_CAP = 5_000_000


def _incoming_presynaptic(
    matrix: sparse.csr_matrix,
    postsynaptic_indices: np.ndarray,
) -> tuple[np.ndarray, int]:
    if postsynaptic_indices.size == 0:
        return np.empty(0, dtype=np.int32), 0

    chunks = []
    edge_visits = 0

    for post in postsynaptic_indices:
        start = int(matrix.indptr[int(post)])
        stop = int(matrix.indptr[int(post) + 1])
        edge_visits += stop - start

        if stop > start:
            chunks.append(
                matrix.indices[start:stop].astype(
                    np.int32,
                    copy=False,
                )
            )

    if not chunks:
        return np.empty(0, dtype=np.int32), edge_visits

    presynaptic = np.unique(
        np.concatenate(chunks)
    ).astype(np.int32, copy=False)

    return presynaptic, edge_visits


def count_target_cone(
    matrix: sparse.csr_matrix,
    target: int,
    *,
    max_hops: int = MAX_BACKWARD_HOPS,
    edge_visit_cap: int = DEFAULT_EDGE_VISIT_CAP,
) -> dict:
    frontier = np.asarray([int(target)], dtype=np.int32)

    hop_rows = []
    total_edge_visits = 0
    all_seen_neurons = {int(target)}
    truncated = False

    for hop in range(1, int(max_hops) + 1):
        next_frontier, edge_visits = _incoming_presynaptic(
            matrix,
            frontier,
        )

        total_edge_visits += int(edge_visits)
        all_seen_neurons.update(int(x) for x in next_frontier)

        hop_rows.append(
            {
                "hop": hop,
                "postsynaptic_frontier_count": int(frontier.size),
                "edge_visits": int(edge_visits),
                "unique_presynaptic_count": int(next_frontier.size),
                "cumulative_edge_visits": int(total_edge_visits),
            }
        )

        if total_edge_visits > int(edge_visit_cap):
            truncated = True
            break

        frontier = next_frontier

        if frontier.size == 0:
            break

    return {
        "target": int(target),
        "hops": hop_rows,
        "cumulative_edge_visits": int(total_edge_visits),
        "unique_neuron_count_seen": int(len(all_seen_neurons)),
        "truncated_by_engineering_cap": bool(truncated),
        "engineering_edge_visit_cap": int(edge_visit_cap),
    }


def inventory_connectome(
    connectome,
    *,
    affected_targets=AFFECTED_TARGETS,
    retained_targets=RETAINED_DEPENDENCY_TARGETS,
    max_hops=MAX_BACKWARD_HOPS,
    edge_visit_cap=DEFAULT_EDGE_VISIT_CAP,
) -> dict:
    matrix = sparse.csr_matrix(connectome, copy=False)
    matrix.sum_duplicates()
    matrix.sort_indices()

    targets = (
        tuple(int(x) for x in affected_targets)
        + tuple(int(x) for x in retained_targets)
    )

    rows = [
        count_target_cone(
            matrix,
            target,
            max_hops=max_hops,
            edge_visit_cap=edge_visit_cap,
        )
        for target in targets
    ]

    any_truncated = any(
        row["truncated_by_engineering_cap"]
        for row in rows
    )

    return {
        "max_backward_hops": int(max_hops),
        "affected_targets": [int(x) for x in affected_targets],
        "retained_dependency_targets": [int(x) for x in retained_targets],
        "engineering_edge_visit_cap_per_target": int(edge_visit_cap),
        "any_target_truncated": bool(any_truncated),
        "targets": {
            str(row["target"]): row
            for row in rows
        },
        "implementation_note": (
            "Counts are topology-only. If the engineering cap is exceeded, "
            "the frozen 3-hop scientific rule remains unchanged; the final "
            "runner must use streaming or disk-backed scoring."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--edge-visit-cap",
        type=int,
        default=DEFAULT_EDGE_VISIT_CAP,
    )
    args = parser.parse_args()

    original = sparse.load_npz(CONNECTOME).tocsr()

    payload = inventory_connectome(
        original,
        edge_visit_cap=int(args.edge_visit_cap),
    )

    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
