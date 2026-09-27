from __future__ import annotations

from scipy import sparse

from brain.sq08_three_body_topology_frontier_freezer import (
    BODY_RESPONDERS,
    EXPECTED_ABC,
    EXPECTED_COUNTS,
    direct_targets,
)


def test_body_responder_identity_is_frozen():
    assert BODY_RESPONDERS == {
        "A": 137122,
        "B": 317,
        "C": 126002,
    }


def test_direct_target_direction_is_post_by_pre():
    # 0 -> 2
    # 0 -> 3
    graph = sparse.csc_matrix(
        (
            [0.25, 0.75],
            (
                [2, 3],
                [0, 0],
            ),
        ),
        shape=(4, 4),
    )

    assert direct_targets(graph, 0) == {
        2: 0.25,
        3: 0.75,
    }


def test_expected_frontier_cardinality_is_frozen():
    assert EXPECTED_COUNTS["ABC"] == 18
    assert EXPECTED_COUNTS["AB"] == 73
    assert EXPECTED_COUNTS["AC"] == 152
    assert EXPECTED_COUNTS["BC"] == 212

    assert (
        EXPECTED_COUNTS["AB_only"]
        + EXPECTED_COUNTS["ABC"]
        == EXPECTED_COUNTS["AB"]
    )

    assert (
        EXPECTED_COUNTS["AC_only"]
        + EXPECTED_COUNTS["ABC"]
        == EXPECTED_COUNTS["AC"]
    )

    assert (
        EXPECTED_COUNTS["BC_only"]
        + EXPECTED_COUNTS["ABC"]
        == EXPECTED_COUNTS["BC"]
    )


def test_expected_three_way_frontier_is_frozen():
    assert EXPECTED_ABC == (
        7,
        72,
        129,
        411,
        470,
        1472,
        1574,
        1662,
        1919,
        2009,
        2327,
        3712,
        4068,
        14273,
        16349,
        18196,
        130134,
        131527,
    )


def test_frontier_does_not_contain_body_responders():
    assert not (
        set(BODY_RESPONDERS.values())
        & set(EXPECTED_ABC)
    )
