from __future__ import annotations

import numpy as np
import pytest
from scipy import sparse

from brain.mq5_ts_runtime import (
    build_arm_b_topology,
    lesion_frozen_edges,
)


def test_arm_b_builder_preserves_edge_count_and_protected_origin_edges():
    rows = np.asarray([0, 0, 1, 2, 3, 3], dtype=np.int32)
    cols = np.asarray([1, 2, 0, 1, 2, 3], dtype=np.int32)
    data = np.asarray([1, 2, 3, 4, 5, 6], dtype=np.float32)

    graph = sparse.csr_matrix(
        (data, (rows, cols)),
        shape=(4, 4),
    )
    graph.sort_indices()

    signs = np.asarray([1, 1, 1, 1], dtype=np.float32)
    protected = np.asarray([0], dtype=np.int32)

    shuffled = build_arm_b_topology(
        graph,
        signs,
        protected,
        seed=123,
    )

    assert shuffled.nnz == graph.nnz

    original_protected = graph[:, protected].tocsr()
    shuffled_protected = shuffled[:, protected].tocsr()

    assert (original_protected != shuffled_protected).nnz == 0


def test_arm_b_builder_is_deterministic():
    rows = np.asarray([0, 1, 2, 3], dtype=np.int32)
    cols = np.asarray([1, 2, 3, 0], dtype=np.int32)
    data = np.ones(4, dtype=np.float32)

    graph = sparse.csr_matrix(
        (data, (rows, cols)),
        shape=(4, 4),
    )
    graph.sort_indices()

    signs = np.ones(4, dtype=np.float32)
    protected = np.asarray([], dtype=np.int32)

    a = build_arm_b_topology(graph, signs, protected, seed=55)
    b = build_arm_b_topology(graph, signs, protected, seed=55)

    assert np.array_equal(a.indptr, b.indptr)
    assert np.array_equal(a.indices, b.indices)
    assert np.array_equal(a.data, b.data)


def test_arm_d_lesions_exact_frozen_edge():
    graph = sparse.csr_matrix(
        (
            np.asarray([0.25, 0.5], dtype=np.float32),
            (
                np.asarray([1, 2], dtype=np.int32),
                np.asarray([0, 1], dtype=np.int32),
            ),
        ),
        shape=(3, 3),
    )
    graph.sort_indices()

    lesioned = lesion_frozen_edges(
        graph,
        [(0, 1, 0.25)],
    )

    assert float(lesioned[1, 0]) == 0.0
    assert float(lesioned[2, 1]) == pytest.approx(0.5)
    assert lesioned.nnz == graph.nnz - 1


def test_arm_d_fails_closed_on_weight_mismatch():
    graph = sparse.csr_matrix(
        (
            np.asarray([0.25], dtype=np.float32),
            (
                np.asarray([1], dtype=np.int32),
                np.asarray([0], dtype=np.int32),
            ),
        ),
        shape=(2, 2),
    )

    with pytest.raises(RuntimeError, match="weight mismatch"):
        lesion_frozen_edges(
            graph,
            [(0, 1, 0.5)],
        )
