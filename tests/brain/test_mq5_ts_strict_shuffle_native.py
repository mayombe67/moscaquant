from __future__ import annotations

import numpy as np
import pytest
from scipy import sparse

from brain.mq5_ts_strict_shuffle import (
    build_strict_matched_control_reference,
    strict_invariant_report,
)
from brain.mq5_ts_strict_shuffle_native import (
    build_strict_matched_control_native,
    native_backend_available,
)


pytestmark = pytest.mark.skipif(
    not native_backend_available(),
    reason="native C compiler unavailable",
)


def _fixture_graph():
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
        [post for post, _ in edges],
        dtype=np.int32,
    )
    cols = np.asarray(
        [pre for _, pre in edges],
        dtype=np.int32,
    )

    weights = np.asarray(
        [
            0.5, 0.7, -0.2,
            0.4, 0.8, -0.3,
            0.9, -0.6, 0.2,
            0.3, -0.5, 0.4,
            0.6, 0.1, -0.7,
            0.2, 0.9, -0.4,
            0.8, -0.2, 0.5,
            0.7, 0.3, -0.6,
        ],
        dtype=np.float32,
    )

    graph = sparse.csr_matrix(
        (weights, (rows, cols)),
        shape=(8, 8),
        dtype=np.float32,
    )
    graph.sort_indices()

    signs = np.asarray(
        [1, 1, 1, 1, -1, -1, -1, -1],
        dtype=np.float32,
    )

    protected = np.asarray(
        [0, 4],
        dtype=np.int32,
    )

    return graph, signs, protected


def test_native_reaches_target_and_preserves_reference_invariants():
    graph, signs, protected = _fixture_graph()

    shuffled, diagnostics = build_strict_matched_control_native(
        graph,
        signs,
        protected,
        seed=12345,
        accepted_swaps_per_eligible_edge=0.5,
        max_attempt_multiplier=100,
    )

    assert diagnostics.accepted_swaps == diagnostics.target_accepted_swaps
    assert diagnostics.target_accepted_swaps > 0

    report = strict_invariant_report(
        graph,
        shuffled,
        signs,
        protected,
    )

    assert all(report.values()), report


def test_native_is_deterministic_for_fixed_seed():
    graph, signs, protected = _fixture_graph()

    first, first_diag = build_strict_matched_control_native(
        graph,
        signs,
        protected,
        seed=20263000,
        accepted_swaps_per_eligible_edge=0.5,
        max_attempt_multiplier=100,
    )

    second, second_diag = build_strict_matched_control_native(
        graph,
        signs,
        protected,
        seed=20263000,
        accepted_swaps_per_eligible_edge=0.5,
        max_attempt_multiplier=100,
    )

    assert np.array_equal(first.indptr, second.indptr)
    assert np.array_equal(first.indices, second.indices)
    assert np.array_equal(first.data, second.data)
    assert first_diag == second_diag


def test_native_and_reference_are_both_valid_realizations():
    graph, signs, protected = _fixture_graph()

    reference, reference_diag = build_strict_matched_control_reference(
        graph,
        signs,
        protected,
        seed=77,
        accepted_swaps_per_eligible_edge=0.25,
        max_attempt_multiplier=100,
    )

    native, native_diag = build_strict_matched_control_native(
        graph,
        signs,
        protected,
        seed=77,
        accepted_swaps_per_eligible_edge=0.25,
        max_attempt_multiplier=100,
    )

    assert (
        reference_diag.target_accepted_swaps
        == native_diag.target_accepted_swaps
    )
    assert (
        reference_diag.eligible_edges
        == native_diag.eligible_edges
    )

    assert all(
        strict_invariant_report(
            graph,
            reference,
            signs,
            protected,
        ).values()
    )
    assert all(
        strict_invariant_report(
            graph,
            native,
            signs,
            protected,
        ).values()
    )


def test_native_does_not_modify_input():
    graph, signs, protected = _fixture_graph()

    before_indices = graph.indices.copy()
    before_data = graph.data.copy()
    before_indptr = graph.indptr.copy()

    build_strict_matched_control_native(
        graph,
        signs,
        protected,
        seed=9,
        accepted_swaps_per_eligible_edge=0.25,
        max_attempt_multiplier=100,
    )

    assert np.array_equal(graph.indices, before_indices)
    assert np.array_equal(graph.data, before_data)
    assert np.array_equal(graph.indptr, before_indptr)

def test_native_accepts_preexisting_self_edge_without_creating_new_ones():
    graph, signs, protected = _fixture_graph()

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

    graph = (graph + self_edge).tocsr()
    graph.sort_indices()

    shuffled, diagnostics = build_strict_matched_control_native(
        graph,
        signs,
        protected,
        seed=88001,
        accepted_swaps_per_eligible_edge=0.25,
        max_attempt_multiplier=100,
    )

    assert diagnostics.accepted_swaps == diagnostics.target_accepted_swaps

    report = strict_invariant_report(
        graph,
        shuffled,
        signs,
        protected,
    )

    assert report["no_new_self_edges"]
    assert all(report.values()), report
def test_native_long_churn_preserves_invariants_and_reaches_target():
    # Regression for repeated native erase/insert churn.
    n = 64
    degree = 12

    rows = []
    cols = []

    for post in range(n):
        for offset in range(1, degree + 1):
            rows.append(post)
            cols.append((post + offset) % n)

    rows = np.asarray(rows, dtype=np.int32)
    cols = np.asarray(cols, dtype=np.int32)

    data = np.linspace(
        0.001,
        1.0,
        len(rows),
        dtype=np.float32,
    )

    graph = sparse.csr_matrix(
        (
            data,
            (rows, cols),
        ),
        shape=(n, n),
        dtype=np.float32,
    )
    graph.sum_duplicates()
    graph.sort_indices()

    signs = np.ones(n, dtype=np.float32)
    protected = np.asarray([], dtype=np.int32)

    shuffled, diagnostics = build_strict_matched_control_native(
        graph,
        signs,
        protected,
        seed=991337777,
        accepted_swaps_per_eligible_edge=20.0,
        max_attempt_multiplier=100,
    )

    assert diagnostics.accepted_swaps == diagnostics.target_accepted_swaps
    assert diagnostics.target_accepted_swaps == graph.nnz * 20

    report = strict_invariant_report(
        graph,
        shuffled,
        signs,
        protected,
    )

    assert all(report.values()), report
