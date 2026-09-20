from __future__ import annotations
from config.paths import data_path

from pathlib import Path

import numpy as np
from scipy import sparse
from scipy.cluster.hierarchy import (
    fcluster,
    linkage,
)
from scipy.optimize import linear_sum_assignment
from scipy.spatial.distance import (
    pdist,
    squareform,
)


CONNECTOME = data_path('processed', 'connectome-baseline-v1.npz')

DN_ARTIFACT = data_path('processed', 'mq3-descending-readout-v1.npz')

K = 3

#
# Fixed before results.
#
NULL_SEED = 20260916
NULL_PERMUTATIONS = 10000


def normalize_dense_rows(matrix):
    matrix = matrix.astype(
        np.float64,
        copy=True,
    )

    norms = np.linalg.norm(
        matrix,
        axis=1,
        keepdims=True,
    )

    good = norms[:, 0] > 0

    matrix[good] /= norms[good]

    return matrix


def normalize_sparse_rows(matrix):
    matrix = matrix.tocsr().astype(
        np.float64
    )

    norms = np.sqrt(
        np.asarray(
            matrix.multiply(
                matrix
            ).sum(axis=1)
        ).ravel()
    )

    inverse = np.zeros_like(norms)

    good = norms > 0

    inverse[good] = (
        1.0 / norms[good]
    )

    return (
        sparse.diags(inverse)
        @ matrix
    ).tocsr()


def canonical_labels(labels):
    labels = np.asarray(
        labels,
        dtype=np.int32,
    )

    unique = sorted(
        np.unique(labels)
    )

    remap = {
        old: new
        for new, old
        in enumerate(unique)
    }

    return np.asarray(
        [
            remap[int(value)]
            for value in labels
        ],
        dtype=np.int32,
    )


def cluster_labels(
    condensed,
    k=K,
):
    hierarchy = linkage(
        condensed,
        method="average",
    )

    labels = fcluster(
        hierarchy,
        t=k,
        criterion="maxclust",
    )

    return canonical_labels(
        labels
    )


def combination2(values):
    values = np.asarray(
        values,
        dtype=np.float64,
    )

    return float(
        np.sum(
            values
            * (values - 1.0)
            / 2.0
        )
    )


def adjusted_rand_index(a, b):
    a_values = np.unique(a)
    b_values = np.unique(b)

    table = np.zeros(
        (
            len(a_values),
            len(b_values),
        ),
        dtype=np.int64,
    )

    a_lookup = {
        value: index
        for index, value
        in enumerate(a_values)
    }

    b_lookup = {
        value: index
        for index, value
        in enumerate(b_values)
    }

    for left, right in zip(a, b):
        table[
            a_lookup[left],
            b_lookup[right],
        ] += 1

    cell = combination2(table)

    rows = combination2(
        table.sum(axis=1)
    )

    cols = combination2(
        table.sum(axis=0)
    )

    n = len(a)

    total = (
        n * (n - 1) / 2.0
    )

    expected = (
        rows * cols / total
    )

    maximum = (
        rows + cols
    ) / 2.0

    denominator = (
        maximum - expected
    )

    if denominator == 0:
        return 1.0

    return float(
        (
            cell - expected
        )
        / denominator
    )


def contingency(a, b):
    table = np.zeros(
        (K, K),
        dtype=np.int64,
    )

    for left, right in zip(a, b):
        table[
            int(left),
            int(right),
        ] += 1

    return table


def best_matched_accuracy(table):
    #
    # Maximize overlap between anonymous
    # cluster labels.
    #
    rows, cols = linear_sum_assignment(
        -table
    )

    matched = int(
        table[
            rows,
            cols,
        ].sum()
    )

    return (
        matched,
        matched / table.sum(),
        list(
            zip(
                rows.tolist(),
                cols.tolist(),
            )
        ),
    )


def build_internal_blocks(
    connectome,
    dn_indices,
):
    dn_dn = connectome[
        dn_indices,
        :
    ][
        :,
        dn_indices
    ].toarray().astype(
        np.float64
    )

    return {
        "positive_in": np.maximum(
            dn_dn,
            0.0,
        ),

        "negative_in": np.maximum(
            -dn_dn,
            0.0,
        ),

        "positive_out": np.maximum(
            dn_dn.T,
            0.0,
        ),

        "negative_out": np.maximum(
            -dn_dn.T,
            0.0,
        ),
    }


def internal_labels_from_blocks(
    blocks,
    exclude=None,
):
    matrices = []

    for name, block in blocks.items():
        if name == exclude:
            continue

        matrices.append(
            normalize_dense_rows(
                block
            )
        )

    fingerprint = np.concatenate(
        matrices,
        axis=1,
    )

    fingerprint = normalize_dense_rows(
        fingerprint
    )

    condensed = pdist(
        fingerprint,
        metric="cosine",
    )

    return cluster_labels(
        condensed
    )


def upstream_labels(
    connectome,
    dn_indices,
    include_positive=True,
    include_negative=True,
):
    incoming = connectome[
        dn_indices,
        :
    ].tocsr().astype(
        np.float64
    )

    incoming[
        :,
        dn_indices
    ] = 0.0

    incoming.eliminate_zeros()

    matrices = []

    if include_positive:
        positive = incoming.copy()

        positive.data = np.maximum(
            positive.data,
            0.0,
        )

        positive.eliminate_zeros()

        matrices.append(
            normalize_sparse_rows(
                positive
            )
        )

    if include_negative:
        negative = incoming.copy()

        negative.data = np.maximum(
            -negative.data,
            0.0,
        )

        negative.eliminate_zeros()

        matrices.append(
            normalize_sparse_rows(
                negative
            )
        )

    fingerprint = sparse.hstack(
        matrices,
        format="csr",
    )

    fingerprint = normalize_sparse_rows(
        fingerprint
    )

    similarity = (
        fingerprint
        @ fingerprint.T
    ).toarray()

    similarity = np.clip(
        similarity,
        -1.0,
        1.0,
    )

    distance = (
        1.0 - similarity
    )

    distance = (
        distance
        + distance.T
    ) / 2.0

    np.fill_diagonal(
        distance,
        0.0,
    )

    condensed = squareform(
        distance,
        checks=False,
    )

    return cluster_labels(
        condensed
    )


def main():
    dn = np.load(
        DN_ARTIFACT
    )

    dn_indices = np.asarray(
        dn["neuron_index"],
        dtype=np.int32,
    )

    if len(dn_indices) != 1314:
        raise RuntimeError(
            "expected 1314 frozen DNs"
        )

    print(
        "loading frozen connectome..."
    )

    connectome = sparse.load_npz(
        CONNECTOME
    ).tocsr()

    blocks = build_internal_blocks(
        connectome,
        dn_indices,
    )

    internal = (
        internal_labels_from_blocks(
            blocks
        )
    )

    upstream = upstream_labels(
        connectome,
        dn_indices,
    )

    observed_ari = (
        adjusted_rand_index(
            internal,
            upstream,
        )
    )

    table = contingency(
        internal,
        upstream,
    )

    (
        matched,
        matched_fraction,
        matching,
    ) = best_matched_accuracy(
        table
    )

    print()
    print("=" * 72)
    print("MQ-3 K=3 CONSENSUS VALIDATION")
    print("=" * 72)

    print()
    print("INTERNAL CLUSTER SIZES")
    print(
        np.bincount(internal)
    )

    print()
    print("UPSTREAM CLUSTER SIZES")
    print(
        np.bincount(upstream)
    )

    print()
    print("CONTINGENCY")
    print(table)

    print()
    print(
        "best cluster matching:",
        matching,
    )

    print(
        "matched neurons:",
        matched,
        "/",
        len(internal),
    )

    print(
        "matched fraction:",
        matched_fraction,
    )

    print(
        "observed ARI:",
        observed_ari,
    )

    print()
    print("=" * 72)
    print("INTERNAL LEAVE-ONE-BLOCK-OUT")
    print("=" * 72)

    for excluded in blocks:
        variant = (
            internal_labels_from_blocks(
                blocks,
                exclude=excluded,
            )
        )

        print(
            excluded,
            "ARI vs full internal=",
            adjusted_rand_index(
                internal,
                variant,
            ),
            "ARI vs upstream=",
            adjusted_rand_index(
                variant,
                upstream,
            ),
            "sizes=",
            np.bincount(
                variant
            ).tolist(),
        )

    print()
    print("=" * 72)
    print("UPSTREAM SIGN ABLATION")
    print("=" * 72)

    positive_only = upstream_labels(
        connectome,
        dn_indices,
        include_positive=True,
        include_negative=False,
    )

    negative_only = upstream_labels(
        connectome,
        dn_indices,
        include_positive=False,
        include_negative=True,
    )

    print(
        "positive only:",
        "ARI vs full upstream=",
        adjusted_rand_index(
            upstream,
            positive_only,
        ),
        "ARI vs internal=",
        adjusted_rand_index(
            internal,
            positive_only,
        ),
        "sizes=",
        np.bincount(
            positive_only
        ).tolist(),
    )

    print(
        "negative only:",
        "ARI vs full upstream=",
        adjusted_rand_index(
            upstream,
            negative_only,
        ),
        "ARI vs internal=",
        adjusted_rand_index(
            internal,
            negative_only,
        ),
        "sizes=",
        np.bincount(
            negative_only
        ).tolist(),
    )

    print()
    print("=" * 72)
    print("PERMUTATION NULL")
    print("=" * 72)

    rng = np.random.default_rng(
        NULL_SEED
    )

    null_ari = np.empty(
        NULL_PERMUTATIONS,
        dtype=np.float64,
    )

    shuffled = upstream.copy()

    for index in range(
        NULL_PERMUTATIONS
    ):
        shuffled[:] = (
            rng.permutation(
                upstream
            )
        )

        null_ari[index] = (
            adjusted_rand_index(
                internal,
                shuffled,
            )
        )

    exceed = int(
        np.count_nonzero(
            null_ari
            >= observed_ari
        )
    )

    empirical_p = (
        exceed + 1
    ) / (
        NULL_PERMUTATIONS + 1
    )

    print(
        "permutations:",
        NULL_PERMUTATIONS,
    )

    print(
        "seed:",
        NULL_SEED,
    )

    print(
        "null min:",
        float(
            null_ari.min()
        ),
    )

    print(
        "null median:",
        float(
            np.median(
                null_ari
            )
        ),
    )

    print(
        "null max:",
        float(
            null_ari.max()
        ),
    )

    print(
        "null >= observed:",
        exceed,
    )

    print(
        "empirical p (+1):",
        empirical_p,
    )

    print()
    print(
        "MARKET RESPONSE USED: NO"
    )

    print(
        "FINANCIAL SEMANTICS USED: NO"
    )

    print()
    print(
        "MQ-3 K=3 CONSENSUS "
        "VALIDATION COMPLETE"
    )


if __name__ == "__main__":
    main()
