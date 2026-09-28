from __future__ import annotations

from scipy import sparse

from brain.sq08_three_body_topology_freezer import (
    BODY_RESPONDERS,
    MAX_HOPS,
    canonical_branch,
    downstream_distances,
)


def test_sq08_body_responder_identity_is_frozen():
    assert BODY_RESPONDERS == {
        "A": 137122,
        "B": 317,
        "C": 126002,
    }


def test_sq08_topology_depth_is_frozen():
    assert MAX_HOPS == 4


def test_downstream_direction_matches_connectome_convention():
    # graph[post, pre]
    #
    # 0 -> 1 -> 2
    graph = sparse.csr_matrix(
        (
            [1.0, 1.0],
            (
                [1, 2],
                [0, 1],
            ),
        ),
        shape=(4, 4),
    )

    distances = downstream_distances(
        graph,
        source=0,
        max_hops=4,
    )

    assert distances[0] == 0
    assert distances[1] == 1
    assert distances[2] == 2
    assert 3 not in distances


def test_hop_limit_is_enforced():
    graph = sparse.csr_matrix(
        (
            [1.0, 1.0, 1.0],
            (
                [1, 2, 3],
                [0, 1, 2],
            ),
        ),
        shape=(4, 4),
    )

    distances = downstream_distances(
        graph,
        source=0,
        max_hops=2,
    )

    assert set(distances) == {0, 1, 2}


def test_branch_is_deterministic_and_excludes_source():
    distances = {
        10: 0,
        30: 2,
        20: 1,
        15: 1,
    }

    assert canonical_branch(
        distances,
        source=10,
    ) == [
        {"node": 15, "min_hops": 1},
        {"node": 20, "min_hops": 1},
        {"node": 30, "min_hops": 2},
    ]
