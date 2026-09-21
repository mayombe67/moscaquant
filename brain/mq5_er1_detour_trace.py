from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
from scipy import sparse


@dataclass(frozen=True, order=True)
class TracedEdge:
    presynaptic: int
    postsynaptic: int
    weight: float
    hop_from_target: int


def build_backward_edge_cone(
    connectome,
    targets: Iterable[int],
    *,
    max_hops: int,
) -> list[TracedEdge]:
    if max_hops < 1:
        raise ValueError("max_hops must be >= 1")

    matrix = sparse.csr_matrix(connectome, copy=False)
    matrix.sum_duplicates()
    matrix.sort_indices()

    frontier = sorted({int(x) for x in targets})
    seen_edges: dict[tuple[int, int], TracedEdge] = {}

    for hop in range(1, max_hops + 1):
        next_frontier: set[int] = set()

        for post in frontier:
            start = int(matrix.indptr[post])
            stop = int(matrix.indptr[post + 1])

            pres = matrix.indices[start:stop]
            weights = matrix.data[start:stop]

            for pre_raw, weight_raw in zip(pres, weights):
                pre = int(pre_raw)
                weight = float(weight_raw)

                if weight == 0.0:
                    continue

                key = (pre, post)
                candidate = TracedEdge(
                    presynaptic=pre,
                    postsynaptic=post,
                    weight=weight,
                    hop_from_target=hop,
                )

                previous = seen_edges.get(key)
                if previous is None or hop < previous.hop_from_target:
                    seen_edges[key] = candidate

                next_frontier.add(pre)

        frontier = sorted(next_frontier)

        if not frontier:
            break

    return sorted(
        seen_edges.values(),
        key=lambda edge: (
            edge.hop_from_target,
            edge.postsynaptic,
            edge.presynaptic,
            edge.weight,
        ),
    )


class ReadOnlySynapticTraceRecorder:
    def __init__(
        self,
        connectome,
        traced_edges: Iterable[TracedEdge],
    ):
        self.connectome = sparse.csr_matrix(connectome, copy=False)
        self.connectome.sum_duplicates()
        self.connectome.sort_indices()

        self.traced_edges = tuple(traced_edges)
        self.frames: list[dict] = []

        for edge in self.traced_edges:
            observed = float(
                self.connectome[
                    edge.postsynaptic,
                    edge.presynaptic,
                ]
            )

            if not np.isclose(
                observed,
                edge.weight,
                rtol=1e-6,
                atol=1e-12,
            ):
                raise ValueError(
                    "traced edge weight mismatch "
                    f"{edge.presynaptic}->{edge.postsynaptic}: "
                    f"{observed} != {edge.weight}"
                )

    def __call__(
        self,
        activity: np.ndarray,
        synaptic: np.ndarray,
    ) -> np.ndarray:
        activity = np.asarray(activity)
        synaptic_view = np.asarray(synaptic)

        contributions = []

        for edge in self.traced_edges:
            value = (
                float(edge.weight)
                * float(activity[edge.presynaptic])
            )

            contributions.append(
                {
                    "presynaptic": int(edge.presynaptic),
                    "postsynaptic": int(edge.postsynaptic),
                    "hop_from_target": int(edge.hop_from_target),
                    "weight": float(edge.weight),
                    "effective_activity": float(
                        activity[edge.presynaptic]
                    ),
                    "edge_contribution": float(value),
                    "postsynaptic_aggregate_before_runtime_controls": float(
                        synaptic_view[edge.postsynaptic]
                    ),
                }
            )

        self.frames.append(
            {
                "frame": len(self.frames),
                "edges": contributions,
            }
        )

        return synaptic


def post_step_snapshot(
    runtime,
    neuron_indices: Iterable[int],
) -> dict:
    indices = np.asarray(
        sorted({int(x) for x in neuron_indices}),
        dtype=np.int64,
    )

    return {
        "indices": indices.tolist(),
        "voltage": np.asarray(
            runtime.voltage[indices],
            dtype=np.float64,
        ).tolist(),
        "spikes": np.asarray(
            runtime.spikes[indices],
            dtype=np.float64,
        ).tolist(),
    }


def project_traced_edges(
    connectome,
    traced_edges: Iterable[TracedEdge],
) -> list[TracedEdge]:
    """
    Project a frozen endpoint/hop template onto a condition-specific topology.

    This is required for C-LESION13: endpoints remain part of the preregistered
    search template, but a lesioned edge must contribute exactly zero rather
    than retaining its original baseline weight.
    """
    matrix = sparse.csr_matrix(connectome, copy=False)
    matrix.sum_duplicates()
    matrix.sort_indices()

    projected = []

    for edge in traced_edges:
        observed = float(
            matrix[
                int(edge.postsynaptic),
                int(edge.presynaptic),
            ]
        )

        projected.append(
            TracedEdge(
                presynaptic=int(edge.presynaptic),
                postsynaptic=int(edge.postsynaptic),
                weight=observed,
                hop_from_target=int(edge.hop_from_target),
            )
        )

    return projected
