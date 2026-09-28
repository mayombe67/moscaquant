import numpy as np
from scipy import sparse

from brain.sq12_resonance_cascade_topology import (
    derive_topology,
)


def test_one_hop_union_and_convergence():
    #
    # Matrix orientation follows MoscaQuant:
    # row = postsynaptic
    # column = presynaptic
    #
    rows = np.asarray([
        3, 4, 5,
        4, 5, 6,
        5, 6, 7,
    ])

    cols = np.asarray([
        0, 0, 0,
        1, 1, 1,
        2, 2, 2,
    ])

    data = np.ones(
        len(rows),
        dtype=np.float32,
    )

    graph = sparse.coo_matrix(
        (
            data,
            (rows, cols),
        ),
        shape=(8, 8),
        dtype=np.float32,
    ).tocsc()

    topology = derive_topology(
        graph,
        {
            "A": 0,
            "B": 1,
            "C": 2,
        },
    )

    assert topology["union"] == {
        3, 4, 5, 6, 7
    }

    assert topology["A_only"] == {3}
    assert topology["B_only"] == set()
    assert topology["C_only"] == {7}

    assert topology["AB_only"] == {4}
    assert topology["AC_only"] == set()
    assert topology["BC_only"] == {6}

    assert topology["ABC"] == {5}

    assert topology["convergence"] == {
        4, 5, 6
    }

    assert topology["scan"] == {
        3, 4, 5, 6, 7
    }


def test_body_responders_are_excluded():
    rows = np.asarray([
        1, 3,
        3,
        3,
    ])

    cols = np.asarray([
        0, 0,
        1,
        2,
    ])

    data = np.ones(
        len(rows),
        dtype=np.float32,
    )

    graph = sparse.coo_matrix(
        (
            data,
            (rows, cols),
        ),
        shape=(5, 5),
        dtype=np.float32,
    ).tocsc()

    topology = derive_topology(
        graph,
        {
            "A": 0,
            "B": 1,
            "C": 2,
        },
    )

    assert 1 in topology["union"]

    assert topology[
        "excluded_body_nodes"
    ] == {1}

    assert 1 not in topology["scan"]

    assert topology["scan"] == {3}
