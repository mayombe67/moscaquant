from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy import sparse


REFERENCE_MAX_EDGES = 1_000_000


@dataclass(frozen=True)
class StrictShuffleDiagnostics:
    seed: int
    eligible_edges: int
    target_accepted_swaps: int
    accepted_swaps: int
    attempted_swaps: int
    rejected_sign: int
    rejected_noop: int
    rejected_self_edge: int
    rejected_duplicate: int


def _edge_key(post: int, pre: int, n: int) -> int:
    return int(post) * int(n) + int(pre)


def build_strict_matched_control_reference(
    original: sparse.csr_matrix,
    transmitter_sign: np.ndarray,
    protected_indices: np.ndarray,
    seed: int,
    *,
    accepted_swaps_per_eligible_edge: float = 1.0,
    max_attempt_multiplier: int = 20,
) -> tuple[sparse.csr_matrix, StrictShuffleDiagnostics]:
    """Reference implementation of the MQ-5.TS Arm C directed edge-swap null.

    This implementation is intentionally bounded to small/medium graphs.  It is
    the correctness oracle for the production implementation and MUST NOT be
    used for the full MaleCNS artifact.

    CSR orientation is postsynaptic row, presynaptic column.
    A same-sign double-edge swap:

        a -> x, b -> y  =>  b -> x, a -> y

    changes only CSR column identities at the two selected row positions.
    Keeping the row data values in place preserves each postsynaptic row's
    signed weight multiset exactly.
    """
    matrix = original.tocsr(copy=True)
    matrix.sum_duplicates()
    matrix.sort_indices()

    if matrix.shape[0] != matrix.shape[1]:
        raise ValueError("strict shuffle requires a square connectome")

    n = int(matrix.shape[0])
    sign = np.asarray(transmitter_sign, dtype=np.float32)
    if sign.shape != (n,):
        raise ValueError("transmitter_sign length does not match connectome")

    protected = np.asarray(protected_indices, dtype=np.int32)
    if np.any(protected < 0) or np.any(protected >= n):
        raise ValueError("protected index out of range")

    if matrix.nnz > REFERENCE_MAX_EDGES:
        raise RuntimeError(
            "reference strict shuffle is intentionally bounded; "
            "use the production Arm C backend for full MaleCNS"
        )

    if accepted_swaps_per_eligible_edge < 0:
        raise ValueError("accepted_swaps_per_eligible_edge must be nonnegative")
    if max_attempt_multiplier < 1:
        raise ValueError("max_attempt_multiplier must be >= 1")

    protected_mask = np.zeros(n, dtype=bool)
    protected_mask[protected] = True

    row_counts = np.diff(matrix.indptr)
    rows = np.repeat(
        np.arange(n, dtype=np.int32),
        row_counts,
    )
    cols = matrix.indices.copy()

    eligible_positions = np.flatnonzero(
        ~protected_mask[cols]
    ).astype(np.int64, copy=False)

    eligible_edges = int(len(eligible_positions))
    target = int(
        np.floor(
            eligible_edges
            * float(accepted_swaps_per_eligible_edge)
        )
    )
    max_attempts = int(target * max_attempt_multiplier)

    edge_keys = {
        _edge_key(post, pre, n)
        for post, pre in zip(rows.tolist(), cols.tolist())
    }

    # Frozen Arm-C rule is baseline-relative:
    # x -> x may appear after shuffling only if that exact edge existed in
    # the original graph. Track original self-edge eligibility separately
    # from the mutable current graph.
    baseline_self = np.asarray(matrix.diagonal()) != 0

    rng = np.random.default_rng(seed)

    accepted = 0
    attempted = 0
    rejected_sign = 0
    rejected_noop = 0
    rejected_self = 0
    rejected_duplicate = 0

    while accepted < target and attempted < max_attempts:
        attempted += 1

        i, j = rng.choice(
            eligible_positions,
            size=2,
            replace=False,
        )
        i = int(i)
        j = int(j)

        x = int(rows[i])
        y = int(rows[j])
        a = int(cols[i])
        b = int(cols[j])

        if a == b or x == y:
            rejected_noop += 1
            continue

        if sign[a] != sign[b]:
            rejected_sign += 1
            continue

        # a -> x, b -> y becomes b -> x, a -> y.
        #
        # A proposed x -> x / y -> y edge is legal only when that exact
        # self-edge existed in the original graph. This mirrors the native
        # production backend and the preregistered "no NEW self-edge" rule.
        if (
            (b == x and not baseline_self[x])
            or (a == y and not baseline_self[y])
        ):
            rejected_self += 1
            continue

        old1 = _edge_key(x, a, n)
        old2 = _edge_key(y, b, n)
        new1 = _edge_key(x, b, n)
        new2 = _edge_key(y, a, n)

        if new1 == old1 or new2 == old2 or new1 == new2:
            rejected_noop += 1
            continue

        # Test against the graph with the two selected edges removed.
        edge_keys.remove(old1)
        edge_keys.remove(old2)

        if new1 in edge_keys or new2 in edge_keys:
            edge_keys.add(old1)
            edge_keys.add(old2)
            rejected_duplicate += 1
            continue

        cols[i] = b
        cols[j] = a

        edge_keys.add(new1)
        edge_keys.add(new2)
        accepted += 1

    if accepted != target:
        raise RuntimeError(
            "strict shuffle failed to reach preregistered accepted-swap "
            f"target: accepted={accepted}, target={target}, "
            f"attempted={attempted}, max_attempts={max_attempts}"
        )

    shuffled = sparse.csr_matrix(
        (
            matrix.data.copy(),
            cols,
            matrix.indptr.copy(),
        ),
        shape=matrix.shape,
        dtype=matrix.dtype,
    )
    shuffled.sort_indices()

    diagnostics = StrictShuffleDiagnostics(
        seed=int(seed),
        eligible_edges=eligible_edges,
        target_accepted_swaps=target,
        accepted_swaps=accepted,
        attempted_swaps=attempted,
        rejected_sign=rejected_sign,
        rejected_noop=rejected_noop,
        rejected_self_edge=rejected_self,
        rejected_duplicate=rejected_duplicate,
    )

    return shuffled, diagnostics


def strict_invariant_report(
    original: sparse.csr_matrix,
    shuffled: sparse.csr_matrix,
    transmitter_sign: np.ndarray,
    protected_indices: np.ndarray,
) -> dict[str, bool]:
    """Return exact structural invariant checks for an Arm C candidate."""
    a = original.tocsr(copy=True)
    b = shuffled.tocsr(copy=True)
    a.sum_duplicates()
    b.sum_duplicates()
    a.sort_indices()
    b.sort_indices()

    if a.shape != b.shape:
        return {"shape": False}

    n = a.shape[0]
    sign = np.asarray(transmitter_sign, dtype=np.float32)
    protected = np.asarray(protected_indices, dtype=np.int32)

    indegree_a = np.diff(a.indptr)
    indegree_b = np.diff(b.indptr)

    outdegree_a = np.bincount(a.indices, minlength=n)
    outdegree_b = np.bincount(b.indices, minlength=n)

    protected_mask = np.zeros(n, dtype=bool)
    protected_mask[protected] = True

    def protected_edges(matrix: sparse.csr_matrix) -> list[tuple[int, int, float]]:
        rows = np.repeat(
            np.arange(n, dtype=np.int32),
            np.diff(matrix.indptr),
        )
        mask = protected_mask[matrix.indices]
        return sorted(
            (
                int(rows[k]),
                int(matrix.indices[k]),
                float(matrix.data[k]),
            )
            for k in np.flatnonzero(mask)
        )

    incoming_sign_counts_equal = True
    row_signed_weight_multiset_equal = True

    for row in range(n):
        a0, a1 = a.indptr[row], a.indptr[row + 1]
        b0, b1 = b.indptr[row], b.indptr[row + 1]

        a_pre = a.indices[a0:a1]
        b_pre = b.indices[b0:b1]

        a_sign = sign[a_pre]
        b_sign = sign[b_pre]

        if not np.array_equal(
            np.unique(a_sign, return_counts=True),
            np.unique(b_sign, return_counts=True),
        ):
            incoming_sign_counts_equal = False

        if not np.array_equal(
            np.sort(a.data[a0:a1]),
            np.sort(b.data[b0:b1]),
        ):
            row_signed_weight_multiset_equal = False

    # Incoming absolute normalization is a property of each row's
    # absolute weight multiset, not of CSR storage/summation order.
    #
    # A valid edge swap can change column sort order. After canonical CSR
    # sorting, float32 reduction order may therefore differ even when the
    # exact same weights are present, producing a few-ULP artifact.
    #
    # Canonicalize the reduction order by sorting absolute row weights and
    # accumulating in float64. This remains an exact invariant check for
    # the preserved multiset while removing dependence on sparse storage
    # ordering.
    incoming_abs_a = np.empty(n, dtype=np.float64)
    incoming_abs_b = np.empty(n, dtype=np.float64)

    for row in range(n):
        a0, a1 = a.indptr[row], a.indptr[row + 1]
        b0, b1 = b.indptr[row], b.indptr[row + 1]

        incoming_abs_a[row] = np.sum(
            np.sort(
                np.abs(
                    np.asarray(
                        a.data[a0:a1],
                        dtype=np.float64,
                    )
                )
            ),
            dtype=np.float64,
        )

        incoming_abs_b[row] = np.sum(
            np.sort(
                np.abs(
                    np.asarray(
                        b.data[b0:b1],
                        dtype=np.float64,
                    )
                )
            ),
            dtype=np.float64,
        )

    return {
        "shape": a.shape == b.shape,
        "edge_count": a.nnz == b.nnz,
        "exact_indegree_per_neuron": np.array_equal(
            indegree_a, indegree_b
        ),
        "exact_outdegree_per_neuron": np.array_equal(
            outdegree_a, outdegree_b
        ),
        "protected_retinal_origin_edges_exact": (
            protected_edges(a) == protected_edges(b)
        ),
        "incoming_sign_counts_per_target": incoming_sign_counts_equal,
        "row_signed_weight_multiset": row_signed_weight_multiset_equal,
        "incoming_absolute_normalization": np.array_equal(
            incoming_abs_a, incoming_abs_b
        ),
        "no_duplicate_edges": b.nnz == len(
            {
                _edge_key(post, pre, n)
                for post, pre in zip(
                    np.repeat(
                        np.arange(n, dtype=np.int32),
                        np.diff(b.indptr),
                    ).tolist(),
                    b.indices.tolist(),
                )
            }
        ),
        "no_new_self_edges": bool(
            all(
                (
                    int(row) not in b.indices[
                        b.indptr[row]:
                        b.indptr[row + 1]
                    ]
                )
                or (
                    int(row) in a.indices[
                        a.indptr[row]:
                        a.indptr[row + 1]
                    ]
                )
                for row in range(n)
            )
        ),
    }
