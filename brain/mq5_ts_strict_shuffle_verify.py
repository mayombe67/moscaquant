from __future__ import annotations

import numpy as np
from scipy import sparse


def verify_strict_matched_control_scalable(
    original: sparse.csr_matrix,
    shuffled: sparse.csr_matrix,
    transmitter_sign: np.ndarray,
    protected_indices: np.ndarray,
) -> dict[str, bool]:
    """Full-scale Arm C invariant verifier without a giant Python edge set."""
    a = original.tocsr(copy=True)
    b = shuffled.tocsr(copy=True)

    a.sum_duplicates()
    b.sum_duplicates()
    a.sort_indices()
    b.sort_indices()

    if a.shape != b.shape:
        return {"shape": False}

    n = int(a.shape[0])
    sign = np.asarray(transmitter_sign, dtype=np.float32)
    protected = np.asarray(protected_indices, dtype=np.int32)

    if sign.shape != (n,):
        raise ValueError("transmitter_sign length mismatch")

    protected_mask = np.zeros(n, dtype=bool)
    protected_mask[protected] = True

    indegree_equal = np.array_equal(
        np.diff(a.indptr),
        np.diff(b.indptr),
    )

    outdegree_equal = np.array_equal(
        np.bincount(a.indices, minlength=n),
        np.bincount(b.indices, minlength=n),
    )

    protected_exact = True
    incoming_sign_equal = True
    row_weight_multiset_equal = True
    incoming_abs_equal = True
    no_duplicates = True
    no_new_self_edges = True

    for row in range(n):
        a0 = int(a.indptr[row])
        a1 = int(a.indptr[row + 1])
        b0 = int(b.indptr[row])
        b1 = int(b.indptr[row + 1])

        ai = a.indices[a0:a1]
        bi = b.indices[b0:b1]

        ad = a.data[a0:a1]
        bd = b.data[b0:b1]

        if len(ai) != len(bi):
            indegree_equal = False
            continue

        if len(bi) > 1 and np.any(bi[1:] == bi[:-1]):
            no_duplicates = False

        original_has_self = bool(np.any(ai == row))
        shuffled_has_self = bool(np.any(bi == row))

        if shuffled_has_self and not original_has_self:
            no_new_self_edges = False

        am = protected_mask[ai]
        bm = protected_mask[bi]

        if np.count_nonzero(am) != np.count_nonzero(bm):
            protected_exact = False
        elif np.any(am):
            if not (
                np.array_equal(ai[am], bi[bm])
                and np.array_equal(ad[am], bd[bm])
            ):
                protected_exact = False

        a_sign = sign[ai]
        b_sign = sign[bi]

        a_neg = int(np.count_nonzero(a_sign < 0))
        b_neg = int(np.count_nonzero(b_sign < 0))
        a_pos = int(np.count_nonzero(a_sign > 0))
        b_pos = int(np.count_nonzero(b_sign > 0))
        a_zero = len(a_sign) - a_neg - a_pos
        b_zero = len(b_sign) - b_neg - b_pos

        if (
            a_neg != b_neg
            or a_pos != b_pos
            or a_zero != b_zero
        ):
            incoming_sign_equal = False

        a_sorted_w = np.sort(
            np.asarray(ad, dtype=np.float32)
        )
        b_sorted_w = np.sort(
            np.asarray(bd, dtype=np.float32)
        )

        if not np.array_equal(
            a_sorted_w,
            b_sorted_w,
        ):
            row_weight_multiset_equal = False

        a_abs = np.sum(
            np.sort(
                np.abs(
                    np.asarray(
                        ad,
                        dtype=np.float64,
                    )
                )
            ),
            dtype=np.float64,
        )

        b_abs = np.sum(
            np.sort(
                np.abs(
                    np.asarray(
                        bd,
                        dtype=np.float64,
                    )
                )
            ),
            dtype=np.float64,
        )

        if a_abs != b_abs:
            incoming_abs_equal = False

    return {
        "shape": a.shape == b.shape,
        "edge_count": a.nnz == b.nnz,
        "exact_indegree_per_neuron": bool(indegree_equal),
        "exact_outdegree_per_neuron": bool(outdegree_equal),
        "protected_retinal_origin_edges_exact": bool(protected_exact),
        "incoming_sign_counts_per_target": bool(incoming_sign_equal),
        "row_signed_weight_multiset": bool(row_weight_multiset_equal),
        "incoming_absolute_normalization": bool(incoming_abs_equal),
        "no_duplicate_edges": bool(no_duplicates),
        "no_new_self_edges": bool(no_new_self_edges),
    }
