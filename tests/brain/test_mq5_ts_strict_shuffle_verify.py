from __future__ import annotations

import numpy as np
from scipy import sparse

from brain.mq5_ts_strict_shuffle_native import (
    build_strict_matched_control_native,
)
from brain.mq5_ts_strict_shuffle_verify import (
    verify_strict_matched_control_scalable,
)


def _graph():
    edges = [
        (0, 1), (0, 2), (0, 4),
        (1, 0), (1, 3), (1, 5),
        (2, 1), (2, 4), (2, 6),
        (3, 0), (3, 5), (3, 7),
        (4, 1), (4, 2), (4, 6),
        (5, 0), (5, 3), (5, 7),
        (6, 1), (6, 4), (6, 5),
        (7, 0), (7, 2), (7, 3),
    ]

    rows = np.asarray(
        [x for x, _ in edges],
        dtype=np.int32,
    )
    cols = np.asarray(
        [y for _, y in edges],
        dtype=np.int32,
    )

    data = np.linspace(
        0.1,
        2.4,
        len(edges),
        dtype=np.float32,
    )

    matrix = sparse.csr_matrix(
        (data, (rows, cols)),
        shape=(8, 8),
        dtype=np.float32,
    )
    matrix.sort_indices()

    signs = np.asarray(
        [1, 1, 1, 1, -1, -1, -1, -1],
        dtype=np.float32,
    )

    protected = np.asarray(
        [0, 4],
        dtype=np.int32,
    )

    return matrix, signs, protected


def test_scalable_verifier_accepts_native_valid_realization():
    graph, signs, protected = _graph()

    shuffled, _ = build_strict_matched_control_native(
        graph,
        signs,
        protected,
        seed=5001,
        accepted_swaps_per_eligible_edge=0.25,
        max_attempt_multiplier=100,
    )

    report = verify_strict_matched_control_scalable(
        graph,
        shuffled,
        signs,
        protected,
    )

    assert all(report.values()), report


def test_scalable_verifier_detects_new_self_edge():
    graph, signs, protected = _graph()

    bad = graph.copy()

    lo = int(bad.indptr[0])
    hi = int(bad.indptr[1])

    position = next(
        k
        for k in range(lo, hi)
        if bad.indices[k] not in protected
    )

    bad.indices[position] = 0
    bad.sort_indices()

    report = verify_strict_matched_control_scalable(
        graph,
        bad,
        signs,
        protected,
    )

    assert not report["no_new_self_edges"]


def test_scalable_verifier_allows_preexisting_self_edge():
    graph, signs, protected = _graph()

    self_edge = sparse.csr_matrix(
        (
            np.asarray([0.125], dtype=np.float32),
            (
                np.asarray([7], dtype=np.int32),
                np.asarray([7], dtype=np.int32),
            ),
        ),
        shape=graph.shape,
        dtype=np.float32,
    )

    original = (graph + self_edge).tocsr()
    candidate = original.copy()
    original.sort_indices()
    candidate.sort_indices()

    report = verify_strict_matched_control_scalable(
        original,
        candidate,
        signs,
        protected,
    )

    assert report["no_new_self_edges"]
    assert all(report.values()), report


def test_scalable_verifier_detects_changed_weight_multiset():
    graph, signs, protected = _graph()

    bad = graph.copy()
    bad.data[0] = np.float32(
        bad.data[0] + 0.25
    )

    report = verify_strict_matched_control_scalable(
        graph,
        bad,
        signs,
        protected,
    )

    assert not report["row_signed_weight_multiset"]
    assert not report["incoming_absolute_normalization"]
