from __future__ import annotations

import numpy as np
from scipy import sparse

from brain import mq5_er4_stevedores_control_selector as selector


def test_candidate_freeze():
    assert [c["id"] for c in selector.CANDIDATES] == ["S1", "S2", "S3"]
    assert selector.CANDIDATES[0]["weight"] == -0.23459716141223907
    assert selector.CANDIDATES[1]["weight"] == -0.3401360511779785
    assert selector.CANDIDATES[2]["weight"] == 0.35854342579841614
    assert selector.CANDIDATES[0]["hop_signature"] == (3, 3, 3)
    assert selector.CANDIDATES[1]["hop_signature"] == (3, 2, 3)
    assert selector.CANDIDATES[2]["hop_signature"] == (3, 2, 2)


def test_log_distance_is_symmetric():
    a = selector.log_distance(0.25, 0.5)
    b = selector.log_distance(0.5, 0.25)
    assert a == b


def test_reverse_hop_array():
    graph = sparse.lil_matrix((6, 6), dtype=np.float32)
    graph[5, 4] = 1.0
    graph[4, 3] = 1.0
    graph[3, 2] = 1.0
    graph = graph.tocsr()

    hops = selector.reverse_hop_array(graph, 5, 3)
    assert int(hops[4]) == 1
    assert int(hops[3]) == 2
    assert int(hops[2]) == 3
    assert int(hops[1]) == -1


def test_rank_key_prefers_better_max_mismatch():
    candidate = {
        "weight": 0.25,
        "pre_outdegree": 10,
        "post_indegree": 20,
    }

    good = selector.rank_key(
        weight=0.24,
        pre_degree=11,
        post_degree=21,
        candidate=candidate,
        pre=100,
        post=200,
    )
    bad = selector.rank_key(
        weight=0.10,
        pre_degree=30,
        post_degree=60,
        candidate=candidate,
        pre=101,
        post=201,
    )

    assert good < bad
