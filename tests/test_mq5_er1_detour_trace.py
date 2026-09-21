from __future__ import annotations

import numpy as np
from scipy import sparse

from brain.mq5_er1_detour_trace import (
    ReadOnlySynapticTraceRecorder,
    build_backward_edge_cone,
)


def toy_connectome():
    matrix = np.zeros((6, 6), dtype=np.float32)
    matrix[5, 3] = 0.5
    matrix[5, 4] = -0.25
    matrix[3, 1] = 0.75
    matrix[4, 2] = 0.4
    matrix[1, 0] = 0.2
    return sparse.csr_matrix(matrix)


def test_backward_cone_is_deterministic_and_hop_labeled():
    matrix = toy_connectome()

    first = build_backward_edge_cone(
        matrix,
        [5],
        max_hops=2,
    )
    second = build_backward_edge_cone(
        matrix,
        [5],
        max_hops=2,
    )

    assert first == second

    observed = {
        (
            edge.presynaptic,
            edge.postsynaptic,
            edge.hop_from_target,
        )
        for edge in first
    }

    assert observed == {
        (3, 5, 1),
        (4, 5, 1),
        (1, 3, 2),
        (2, 4, 2),
    }


def test_recorder_is_read_only_and_uses_effective_activity():
    matrix = toy_connectome()

    edges = build_backward_edge_cone(
        matrix,
        [5],
        max_hops=1,
    )

    recorder = ReadOnlySynapticTraceRecorder(
        matrix,
        edges,
    )

    activity = np.asarray(
        [0.0, 0.0, 0.0, 0.8, 0.4, 0.0],
        dtype=np.float32,
    )
    synaptic = np.asarray(
        matrix @ activity,
        dtype=np.float32,
    ).ravel()

    activity_before = activity.copy()
    synaptic_before = synaptic.copy()

    returned = recorder(
        activity,
        synaptic,
    )

    assert returned is synaptic
    np.testing.assert_array_equal(
        activity,
        activity_before,
    )
    np.testing.assert_array_equal(
        synaptic,
        synaptic_before,
    )

    rows = {
        (
            row["presynaptic"],
            row["postsynaptic"],
        ): row
        for row in recorder.frames[0]["edges"]
    }

    assert np.isclose(
        rows[(3, 5)]["edge_contribution"],
        0.5 * 0.8,
    )
    assert np.isclose(
        rows[(4, 5)]["edge_contribution"],
        -0.25 * 0.4,
    )


def test_static_topology_inventory_does_not_rank_candidates():
    matrix = toy_connectome()

    edges = build_backward_edge_cone(
        matrix,
        [5],
        max_hops=3,
    )

    assert edges
    assert not hasattr(edges[0], "score")
    assert not hasattr(edges[0], "candidate_rank")


def test_project_traced_edges_zeroes_lesioned_edge():
    from brain.mq5_er1_detour_trace import (
        build_backward_edge_cone,
        project_traced_edges,
    )

    matrix = toy_connectome()
    edges = build_backward_edge_cone(
        matrix,
        [5],
        max_hops=1,
    )

    lesioned = matrix.copy().tolil()
    lesioned[5, 3] = 0.0
    lesioned = lesioned.tocsr()
    lesioned.eliminate_zeros()

    projected = project_traced_edges(
        lesioned,
        edges,
    )

    weights = {
        (edge.presynaptic, edge.postsynaptic): edge.weight
        for edge in projected
    }

    assert weights[(3, 5)] == 0.0
    assert np.isclose(weights[(4, 5)], -0.25)
