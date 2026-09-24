import numpy as np
from scipy import sparse

from brain.mq5_ts_strict_shuffle import (
    build_strict_matched_control_reference,
    strict_invariant_report,
)


def toy_connectome():
    # CSR orientation: postsynaptic row, presynaptic column.
    n = 8
    sign = np.array(
        [1, 1, 1, 1, -1, -1, -1, -1],
        dtype=np.float32,
    )
    protected = np.array([0], dtype=np.int32)

    edges = [
        (0, 4, 0.11),
        (0, 5, 0.12),
        (1, 4, 0.21),
        (1, 6, 0.22),
        (2, 5, 0.31),
        (2, 7, 0.32),
        (3, 4, 0.41),
        (3, 7, 0.42),
        (4, 1, -0.51),
        (4, 2, -0.52),
        (5, 2, -0.61),
        (5, 3, -0.62),
        (6, 1, -0.71),
        (6, 3, -0.72),
        (7, 1, -0.81),
        (7, 2, -0.82),
    ]

    rows = np.array([post for pre, post, weight in edges])
    cols = np.array([pre for pre, post, weight in edges])
    data = np.array([weight for pre, post, weight in edges], dtype=np.float32)

    matrix = sparse.csr_matrix(
        (data, (rows, cols)),
        shape=(n, n),
        dtype=np.float32,
    )
    matrix.sort_indices()
    return matrix, sign, protected


def test_reference_shuffle_preserves_preregistered_invariants():
    original, sign, protected = toy_connectome()

    shuffled, diagnostics = build_strict_matched_control_reference(
        original,
        sign,
        protected,
        seed=20263000,
        accepted_swaps_per_eligible_edge=0.5,
        max_attempt_multiplier=50,
    )

    report = strict_invariant_report(
        original,
        shuffled,
        sign,
        protected,
    )

    assert diagnostics.accepted_swaps == diagnostics.target_accepted_swaps
    assert diagnostics.accepted_swaps > 0
    assert all(report.values())
    assert not np.array_equal(original.indices, shuffled.indices)


def test_reference_shuffle_is_deterministic_for_seed():
    original, sign, protected = toy_connectome()

    a, da = build_strict_matched_control_reference(
        original,
        sign,
        protected,
        seed=20263003,
        accepted_swaps_per_eligible_edge=0.25,
        max_attempt_multiplier=50,
    )
    b, db = build_strict_matched_control_reference(
        original,
        sign,
        protected,
        seed=20263003,
        accepted_swaps_per_eligible_edge=0.25,
        max_attempt_multiplier=50,
    )

    assert np.array_equal(a.indptr, b.indptr)
    assert np.array_equal(a.indices, b.indices)
    assert np.array_equal(a.data, b.data)
    assert da == db


def test_reference_shuffle_never_moves_protected_sources():
    original, sign, protected = toy_connectome()

    shuffled, _ = build_strict_matched_control_reference(
        original,
        sign,
        protected,
        seed=20263007,
        accepted_swaps_per_eligible_edge=0.5,
        max_attempt_multiplier=50,
    )

    def protected_triplets(matrix):
        coo = matrix.tocoo()
        mask = np.isin(coo.col, protected)
        return sorted(
            zip(
                coo.row[mask].tolist(),
                coo.col[mask].tolist(),
                coo.data[mask].tolist(),
            )
        )

    assert protected_triplets(original) == protected_triplets(shuffled)

def test_incoming_absolute_normalization_is_order_independent():
    # Same exact signed weight multiset; only canonical column association
    # differs. The normalization invariant must not depend on float32
    # sparse-reduction order.
    original = sparse.csr_matrix(
        (
            np.asarray(
                [1.0e8, 1.0, -1.0e8, 3.0],
                dtype=np.float32,
            ),
            np.asarray(
                [0, 1, 2, 3],
                dtype=np.int32,
            ),
            np.asarray(
                [0, 4, 4, 4, 4],
                dtype=np.int32,
            ),
        ),
        shape=(4, 4),
        dtype=np.float32,
    )

    shuffled = sparse.csr_matrix(
        (
            np.asarray(
                [3.0, -1.0e8, 1.0, 1.0e8],
                dtype=np.float32,
            ),
            np.asarray(
                [0, 1, 2, 3],
                dtype=np.int32,
            ),
            np.asarray(
                [0, 4, 4, 4, 4],
                dtype=np.int32,
            ),
        ),
        shape=(4, 4),
        dtype=np.float32,
    )

    signs = np.ones(4, dtype=np.float32)
    protected = np.asarray([], dtype=np.int32)

    report = strict_invariant_report(
        original,
        shuffled,
        signs,
        protected,
    )

    assert report["row_signed_weight_multiset"]
    assert report["incoming_absolute_normalization"]

def test_reference_recreates_only_baseline_self_edges(monkeypatch):
    import brain.mq5_ts_strict_shuffle as shuffle_module

    # Two original self-edges are first swapped away, then the exact same
    # baseline self-edges are recreated. The frozen rule permits this because
    # those exact x->x edges existed in the source graph.
    graph = sparse.csr_matrix(
        (
            np.asarray([0.25, 0.5], dtype=np.float32),
            (
                np.asarray([0, 2], dtype=np.int32),
                np.asarray([0, 2], dtype=np.int32),
            ),
        ),
        shape=(3, 3),
        dtype=np.float32,
    )
    graph.sort_indices()

    signs = np.ones(3, dtype=np.float32)
    protected = np.asarray([], dtype=np.int32)

    class FixedPairRng:
        def choice(self, values, size, replace):
            assert size == 2
            assert replace is False
            return np.asarray(values[:2], dtype=np.int64)

    monkeypatch.setattr(
        shuffle_module.np.random,
        "default_rng",
        lambda seed: FixedPairRng(),
    )

    shuffled, diagnostics = (
        shuffle_module.build_strict_matched_control_reference(
            graph,
            signs,
            protected,
            seed=123,
            accepted_swaps_per_eligible_edge=1.0,
            max_attempt_multiplier=2,
        )
    )

    assert diagnostics.target_accepted_swaps == 2
    assert diagnostics.accepted_swaps == 2

    report = shuffle_module.strict_invariant_report(
        graph,
        shuffled,
        signs,
        protected,
    )
    assert report["no_new_self_edges"]
    assert all(report.values()), report

    # Two deterministic swaps return the exact baseline edge set.
    assert np.array_equal(shuffled.indptr, graph.indptr)
    assert np.array_equal(shuffled.indices, graph.indices)
    assert np.array_equal(shuffled.data, graph.data)
