from __future__ import annotations

import numpy as np
import pytest
from scipy import sparse

from brain import (
    mq5_er5r_way_down_in_the_hole_runner
    as wd,
)


def tiny_graph():
    #
    # graph[post, pre]
    #
    #       1
    #      / \
    #     0   3
    #      \ /
    #       2
    #
    # Directed:
    #
    # 0 -> 1 -> 3
    # 0 -> 2 -> 3
    #
    return sparse.csr_matrix(
        (
            np.asarray(
                [
                    1.0,
                    1.0,
                    1.0,
                    1.0,
                ],
                dtype=np.float32,
            ),
            (
                np.asarray(
                    [1, 2, 3, 3],
                    dtype=np.int32,
                ),
                np.asarray(
                    [0, 0, 1, 2],
                    dtype=np.int32,
                ),
            ),
        ),
        shape=(4, 4),
    )


def test_frozen_identity():
    assert (
        wd.EXPERIMENT_ID
        ==
        "mq5-er5r-way-down-in-the-hole-v1"
    )

    assert (
        wd.CODENAME
        == "WAY DOWN IN THE HOLE"
    )

    assert wd.MAX_BACKWARD_HOPS == 3
    assert wd.TOP_K == 5

    assert (
        wd.FOCUSED_MIN_AFFECTED_COVERAGE
        == 4
    )


def test_reverse_ancestry_uses_correct_orientation():
    graph = tiny_graph()

    observed = wd.reverse_hop_map(
        graph,
        target=3,
        max_hops=3,
    )

    assert observed == {
        1: 1,
        2: 1,
        0: 2,
    }


def test_reverse_ancestry_does_not_walk_downstream():
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

    observed = wd.reverse_hop_map(
        graph,
        target=2,
        max_hops=3,
    )

    assert observed == {
        1: 1,
        0: 2,
    }

    assert 3 not in observed


def test_shortest_path_first_hops_finds_both_branches():
    graph = tiny_graph()

    ancestry = wd.reverse_hop_map(
        graph,
        target=3,
        max_hops=3,
    )

    first_hops = (
        wd.shortest_path_first_hops(
            graph.tocsc(),
            candidate=0,
            target=3,
            ancestry=ancestry,
        )
    )

    assert first_hops == {
        1,
        2,
    }


def test_shortest_path_first_hops_handles_direct_edge():
    graph = sparse.csr_matrix(
        (
            [1.0],
            (
                [1],
                [0],
            ),
        ),
        shape=(2, 2),
    )

    ancestry = wd.reverse_hop_map(
        graph,
        target=1,
        max_hops=3,
    )

    first_hops = (
        wd.shortest_path_first_hops(
            graph.tocsc(),
            candidate=0,
            target=1,
            ancestry=ancestry,
        )
    )

    assert first_hops == {
        1,
    }


def test_orientation_contract_passes():
    wd.orientation_contract()


def test_classification_focused():
    rows = [
        {
            "affected_coverage": 4,
            "affected_targets": [
                55,
                92,
                656,
                126002,
            ],
        }
    ]

    assert (
        wd.classify(rows)
        ==
        "GREEK_FOCUSED_COORDINATOR_CANDIDATE"
    )


def test_classification_distributed():
    rows = [
        {
            "affected_coverage": 3,
            "affected_targets": [
                55,
                92,
                656,
            ],
        },
        {
            "affected_coverage": 2,
            "affected_targets": [
                126002,
                137122,
            ],
        },
    ]

    assert (
        wd.classify(rows)
        ==
        "GREEK_DISTRIBUTED_COORDINATOR_PATTERN"
    )


def test_classification_none():
    rows = [
        {
            "affected_coverage": 2,
            "affected_targets": [
                55,
                92,
            ],
        }
    ]

    assert (
        wd.classify(rows)
        ==
        "NO_CLEAR_GREEK_COORDINATOR"
    )


def test_execution_gate_contract_after_authorization():
    protocol = wd.load_protocol()

    #
    # Canonical config is now explicitly authorized.
    #
    assert (
        protocol[
            "result_execution_enabled"
        ]
        is True
    )

    #
    # The gate itself must still fail closed if handed
    # an otherwise identical disabled protocol.
    #
    disabled = dict(protocol)
    disabled[
        "result_execution_enabled"
    ] = False

    with pytest.raises(
        wd.WayDownError,
        match="result_execution_enabled",
    ):
        wd.execution_gate(
            disabled
        )
