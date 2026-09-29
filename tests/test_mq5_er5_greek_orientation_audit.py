from scipy import sparse

from brain.mq5_er4_stevedores_structural_audit import (
    reverse_hop_map,
)
from brain.mq5_er5_greek_orientation_audit import (
    correct_reverse_hops,
    legacy_greek_reverse_hops,
)


def tiny_chain():
    #
    # graph[post, pre]
    #
    # 0 -> 1 -> 2 -> 3
    #
    return sparse.csr_matrix(
        (
            [1.0, 1.0, 1.0],
            (
                [1, 2, 3],
                [0, 1, 2],
            ),
        ),
        shape=(4, 4),
    )


def test_correct_reverse_ancestry_follows_csr_rows():
    graph = tiny_chain()

    observed = correct_reverse_hops(
        graph,
        target=2,
        max_hops=3,
    )

    assert observed == {
        1: 1,
        0: 2,
    }


def test_correct_auditor_matches_existing_er4_orientation_contract():
    graph = tiny_chain()

    expected = reverse_hop_map(
        graph,
        target=2,
        max_hops=3,
    )

    observed = correct_reverse_hops(
        graph,
        target=2,
        max_hops=3,
    )

    assert observed == expected


def test_sealed_greek_semantics_walk_opposite_direction():
    graph = tiny_chain()

    observed = legacy_greek_reverse_hops(
        graph,
        target=2,
        max_hops=3,
    )

    #
    # Column 2 contains the edge 2 -> 3.
    # This therefore walks away from target 2
    # rather than into its predecessors.
    #
    assert observed == {
        3: 1,
    }


def test_legacy_and_correct_semantics_are_not_equivalent():
    graph = tiny_chain()

    legacy = legacy_greek_reverse_hops(
        graph,
        target=2,
        max_hops=3,
    )

    correct = correct_reverse_hops(
        graph,
        target=2,
        max_hops=3,
    )

    assert legacy != correct
