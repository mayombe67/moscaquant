import numpy as np

from brain.mq5_er6r_the_warrant_control_selector import (
    ALL_TARGETS,
    CANDIDATE,
    EXPECTED_1952_HOPS,
    MAX_HOPS,
    rank_key,
)


def test_candidate_identity_frozen():
    assert CANDIDATE == 1952


def test_hop_depth_frozen():
    assert MAX_HOPS == 3


def test_expected_candidate_signature_order():
    observed = tuple(
        EXPECTED_1952_HOPS[
            int(target)
        ]
        for target
        in ALL_TARGETS
    )

    assert observed == (
        2,  # 51
        3,  # 55
        2,  # 92
        3,  # 129
        3,  # 317
        2,  # 656
        2,  # 1273
        3,  # 126002
        2,  # 137122
    )


def test_exact_hop_match_beats_structurally_closer_nonmatch():
    n = 3000

    indegree = np.full(
        n,
        10,
        dtype=np.int64,
    )

    outdegree = np.full(
        n,
        10,
        dtype=np.int64,
    )

    incoming = np.full(
        n,
        10.0,
        dtype=np.float64,
    )

    outgoing = np.full(
        n,
        10.0,
        dtype=np.float64,
    )

    #
    # Candidate has deliberately odd degree/weight values.
    #
    indegree[CANDIDATE] = 100
    outdegree[CANDIDATE] = 100
    incoming[CANDIDATE] = 100.0
    outgoing[CANDIDATE] = 100.0

    candidate_signature = (
        2, 3, 2, 2, 3, 2, 2, 2, 2
    )

    #
    # Node 100 is terrible structurally but has an exact hop signature.
    #
    exact = rank_key(
        node=100,
        candidate_signature=candidate_signature,
        control_signature=candidate_signature,
        indegree=indegree,
        outdegree=outdegree,
        incoming_abs=incoming,
        outgoing_abs=outgoing,
    )

    #
    # Node 101 is structurally identical to candidate but misses one hop.
    #
    indegree[101] = 100
    outdegree[101] = 100
    incoming[101] = 100.0
    outgoing[101] = 100.0

    near_signature = (
        2, 3, 2, 2, 3, 2, 2, 2, 3
    )

    near = rank_key(
        node=101,
        candidate_signature=candidate_signature,
        control_signature=near_signature,
        indegree=indegree,
        outdegree=outdegree,
        incoming_abs=incoming,
        outgoing_abs=outgoing,
    )

    assert exact < near


def test_node_id_is_final_tiebreak():
    n = 3000

    indegree = np.full(
        n,
        20,
        dtype=np.int64,
    )

    outdegree = np.full(
        n,
        30,
        dtype=np.int64,
    )

    incoming = np.full(
        n,
        40.0,
        dtype=np.float64,
    )

    outgoing = np.full(
        n,
        50.0,
        dtype=np.float64,
    )

    indegree[CANDIDATE] = 20
    outdegree[CANDIDATE] = 30
    incoming[CANDIDATE] = 40.0
    outgoing[CANDIDATE] = 50.0

    signature = (
        2, 3, 2, 2, 3, 2, 2, 2, 2
    )

    low = rank_key(
        node=100,
        candidate_signature=signature,
        control_signature=signature,
        indegree=indegree,
        outdegree=outdegree,
        incoming_abs=incoming,
        outgoing_abs=outgoing,
    )

    high = rank_key(
        node=101,
        candidate_signature=signature,
        control_signature=signature,
        indegree=indegree,
        outdegree=outdegree,
        incoming_abs=incoming,
        outgoing_abs=outgoing,
    )

    assert low < high


# THE WARRANT corrected-orientation additions.

import numpy as np
import pytest
from scipy import sparse

import brain.mq5_er6r_the_warrant_control_selector as warrant


def test_corrected_candidate_signature_exact():
    assert warrant.EXPECTED_1952_HOPS == {
        51: 2,
        55: 3,
        92: 2,
        129: 3,
        317: 3,
        656: 2,
        1273: 2,
        126002: 3,
        137122: 2,
    }


def test_corrected_way_down_top_five_exact():
    assert tuple(warrant.WAY_DOWN_TOP5) == (
        1952,
        1963,
        2641,
        1944,
        23640,
    )


def test_reverse_hop_array_obeys_declared_orientation():
    #
    # graph[post, pre]
    #
    # 0 -> 1 -> 2 -> 3
    #
    graph = sparse.csr_matrix(
        (
            np.asarray(
                [1.0, 1.0, 1.0],
                dtype=np.float32,
            ),
            (
                np.asarray(
                    [1, 2, 3],
                    dtype=np.int32,
                ),
                np.asarray(
                    [0, 1, 2],
                    dtype=np.int32,
                ),
            ),
        ),
        shape=(4, 4),
    )

    observed = warrant.reverse_hop_array(
        graph,
        target=2,
        max_hops=3,
    )

    assert int(observed[1]) == 1
    assert int(observed[0]) == 2
    assert int(observed[3]) == -1


def test_real_control_selection_remains_disabled():
    with pytest.raises(
        warrant.ControlSelectionError,
        match="remains disabled",
    ):
        warrant.require_control_selection_authorization()


def test_rank_contract_prefers_exact_hop_match():
    candidate = (
        2, 3, 2, 3, 3, 2, 2, 3, 2
    )

    exact = candidate

    one_mismatch = (
        2, 3, 2, 2, 3, 2, 2, 3, 2
    )

    n = 3

    indegree = np.ones(
        n,
        dtype=np.float64,
    )

    outdegree = np.ones(
        n,
        dtype=np.float64,
    )

    incoming_abs = np.ones(
        n,
        dtype=np.float64,
    )

    outgoing_abs = np.ones(
        n,
        dtype=np.float64,
    )

    #
    # rank_key expects arrays indexable at candidate node 1952,
    # so use a realistic-sized synthetic structural profile.
    #
    size = warrant.CANDIDATE + 3

    indegree = np.ones(
        size,
        dtype=np.float64,
    )

    outdegree = np.ones(
        size,
        dtype=np.float64,
    )

    incoming_abs = np.ones(
        size,
        dtype=np.float64,
    )

    outgoing_abs = np.ones(
        size,
        dtype=np.float64,
    )

    exact_key = warrant.rank_key(
        node=1953,
        candidate_signature=candidate,
        control_signature=exact,
        indegree=indegree,
        outdegree=outdegree,
        incoming_abs=incoming_abs,
        outgoing_abs=outgoing_abs,
    )

    mismatch_key = warrant.rank_key(
        node=1954,
        candidate_signature=candidate,
        control_signature=one_mismatch,
        indegree=indegree,
        outdegree=outdegree,
        incoming_abs=incoming_abs,
        outgoing_abs=outgoing_abs,
    )

    assert exact_key < mismatch_key
