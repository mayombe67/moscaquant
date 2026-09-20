from __future__ import annotations
from config.paths import data_path

from pathlib import Path

import numpy as np
from scipy import sparse
from scipy.cluster.hierarchy import (
    fcluster,
    linkage,
)
from scipy.spatial.distance import (
    pdist,
    squareform,
)


CONNECTOME = data_path('processed', 'connectome-baseline-v1.npz')

DN_ARTIFACT = data_path('processed', 'mq3-descending-readout-v1.npz')


K_MIN = 2
K_MAX = 40


def normalize_dense_rows(
    matrix: np.ndarray,
) -> np.ndarray:
    norms = np.linalg.norm(
        matrix,
        axis=1,
        keepdims=True,
    )

    valid = norms[:, 0] > 0

    result = matrix.copy()

    result[valid] /= norms[valid]

    return result


def normalize_sparse_rows(
    matrix: sparse.csr_matrix,
) -> sparse.csr_matrix:
    squared = matrix.multiply(
        matrix
    )

    norms = np.sqrt(
        np.asarray(
            squared.sum(axis=1)
        ).ravel()
    )

    inverse = np.zeros_like(
        norms,
        dtype=np.float64,
    )

    valid = norms > 0

    inverse[valid] = (
        1.0 / norms[valid]
    )

    return (
        sparse.diags(inverse)
        @ matrix
    ).tocsr()


def canonical_labels(
    labels: np.ndarray,
) -> np.ndarray:
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
            remap[int(label)]
            for label in labels
        ],
        dtype=np.int32,
    )


def choose_labels(
    hierarchy: np.ndarray,
    k: int,
) -> np.ndarray:
    labels = fcluster(
        hierarchy,
        t=k,
        criterion="maxclust",
    ).astype(
        np.int32
    )

    return canonical_labels(
        labels
    )


def combination2(
    values: np.ndarray,
) -> float:
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


def adjusted_rand_index(
    a: np.ndarray,
    b: np.ndarray,
) -> float:
    a_values = np.unique(a)
    b_values = np.unique(b)

    contingency = np.zeros(
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

    for left, right in zip(
        a,
        b,
    ):
        contingency[
            a_lookup[left],
            b_lookup[right],
        ] += 1

    sum_cells = combination2(
        contingency
    )

    row_sum = combination2(
        contingency.sum(axis=1)
    )

    column_sum = combination2(
        contingency.sum(axis=0)
    )

    n = len(a)

    total_pairs = (
        n * (n - 1) / 2.0
    )

    expected = (
        row_sum
        * column_sum
        / total_pairs
    )

    maximum = (
        row_sum
        + column_sum
    ) / 2.0

    denominator = (
        maximum
        - expected
    )

    if denominator == 0:
        return 1.0

    return float(
        (
            sum_cells
            - expected
        )
        / denominator
    )


def silhouette_from_distance(
    distance: np.ndarray,
    labels: np.ndarray,
) -> float:
    unique_labels = np.unique(
        labels
    )

    values = np.zeros(
        len(labels),
        dtype=np.float64,
    )

    for index in range(
        len(labels)
    ):
        own_label = labels[index]

        own_members = np.flatnonzero(
            labels == own_label
        )

        if len(own_members) <= 1:
            values[index] = 0.0
            continue

        other_own = own_members[
            own_members != index
        ]

        a = float(
            distance[
                index,
                other_own
            ].mean()
        )

        b = np.inf

        for candidate_label in (
            unique_labels
        ):
            if (
                candidate_label
                == own_label
            ):
                continue

            members = np.flatnonzero(
                labels
                == candidate_label
            )

            candidate = float(
                distance[
                    index,
                    members
                ].mean()
            )

            if candidate < b:
                b = candidate

        denominator = max(
            a,
            b,
        )

        if denominator > 0:
            values[index] = (
                b - a
            ) / denominator

    return float(
        values.mean()
    )


def build_internal_view(
    connectome,
    dn_indices,
):
    #
    # DN <- DN
    #
    dn_dn = connectome[
        dn_indices,
        :
    ][
        :,
        dn_indices
    ].toarray().astype(
        np.float32
    )

    positive_in = np.maximum(
        dn_dn,
        0.0,
    )

    negative_in = np.maximum(
        -dn_dn,
        0.0,
    )

    positive_out = np.maximum(
        dn_dn.T,
        0.0,
    )

    negative_out = np.maximum(
        -dn_dn.T,
        0.0,
    )

    blocks = [
        normalize_dense_rows(
            positive_in
        ),
        normalize_dense_rows(
            negative_in
        ),
        normalize_dense_rows(
            positive_out
        ),
        normalize_dense_rows(
            negative_out
        ),
    ]

    fingerprint = np.concatenate(
        blocks,
        axis=1,
    )

    fingerprint = normalize_dense_rows(
        fingerprint
    )

    condensed = pdist(
        fingerprint,
        metric="cosine",
    )

    distance = squareform(
        condensed
    )

    hierarchy = linkage(
        condensed,
        method="average",
    )

    return (
        distance,
        hierarchy,
    )


def build_upstream_view(
    connectome,
    dn_indices,
):
    #
    # Rows are receiving DNs.
    # Columns are every neuron in CNS.
    #
    incoming = connectome[
        dn_indices,
        :
    ].tocsr().astype(
        np.float64
    )

    #
    # Remove DN presynaptic columns so
    # this view is independent of the
    # internal DN↔DN representation.
    #
    incoming[
        :,
        dn_indices
    ] = 0.0

    incoming.eliminate_zeros()

    positive = incoming.copy()

    positive.data = np.maximum(
        positive.data,
        0.0,
    )

    positive.eliminate_zeros()

    negative = incoming.copy()

    negative.data = np.maximum(
        -negative.data,
        0.0,
    )

    negative.eliminate_zeros()

    positive = normalize_sparse_rows(
        positive
    )

    negative = normalize_sparse_rows(
        negative
    )

    fingerprint = sparse.hstack(
        [
            positive,
            negative,
        ],
        format="csr",
    )

    fingerprint = normalize_sparse_rows(
        fingerprint
    )

    #
    # Cosine similarity because rows are
    # already L2 normalized.
    #
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
        1.0
        - similarity
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

    hierarchy = linkage(
        condensed,
        method="average",
    )

    return (
        distance,
        hierarchy,
        fingerprint.nnz,
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
            "expected frozen "
            "1314-DN population"
        )

    print(
        "loading frozen connectome..."
    )

    connectome = sparse.load_npz(
        CONNECTOME
    ).tocsr()

    print()
    print("=" * 72)
    print(
        "MQ-3 DN CROSS-VIEW "
        "ANATOMICAL VALIDATION"
    )
    print("=" * 72)

    print()
    print(
        "building internal "
        "DN↔DN view..."
    )

    (
        internal_distance,
        internal_hierarchy,
    ) = build_internal_view(
        connectome,
        dn_indices,
    )

    print(
        "building independent "
        "non-DN upstream view..."
    )

    (
        upstream_distance,
        upstream_hierarchy,
        upstream_nnz,
    ) = build_upstream_view(
        connectome,
        dn_indices,
    )

    print(
        "upstream fingerprint nnz:",
        upstream_nnz,
    )

    print()
    print("=" * 72)
    print("CROSS-VIEW SWEEP")
    print("=" * 72)

    records = []

    for k in range(
        K_MIN,
        K_MAX + 1,
    ):
        internal_labels = (
            choose_labels(
                internal_hierarchy,
                k,
            )
        )

        upstream_labels = (
            choose_labels(
                upstream_hierarchy,
                k,
            )
        )

        internal_actual = len(
            np.unique(
                internal_labels
            )
        )

        upstream_actual = len(
            np.unique(
                upstream_labels
            )
        )

        internal_silhouette = (
            silhouette_from_distance(
                internal_distance,
                internal_labels,
            )
        )

        upstream_silhouette = (
            silhouette_from_distance(
                upstream_distance,
                upstream_labels,
            )
        )

        ari = adjusted_rand_index(
            internal_labels,
            upstream_labels,
        )

        internal_sizes = np.bincount(
            internal_labels
        )

        upstream_sizes = np.bincount(
            upstream_labels
        )

        record = {
            "requested_k": k,
            "internal_k":
                internal_actual,
            "upstream_k":
                upstream_actual,
            "internal_silhouette":
                internal_silhouette,
            "upstream_silhouette":
                upstream_silhouette,
            "ari":
                ari,
            "internal_min_size":
                int(
                    internal_sizes.min()
                ),
            "upstream_min_size":
                int(
                    upstream_sizes.min()
                ),
        }

        records.append(
            record
        )

        print(
            f"k={k:2d}",
            f"internal_sil="
            f"{internal_silhouette:.5f}",
            f"upstream_sil="
            f"{upstream_silhouette:.5f}",
            f"ARI={ari:.5f}",
            f"min_size="
            f"{internal_sizes.min()}/"
            f"{upstream_sizes.min()}",
        )

    best_ari = max(
        records,
        key=lambda item: item[
            "ari"
        ],
    )

    best_internal = max(
        records,
        key=lambda item: item[
            "internal_silhouette"
        ],
    )

    best_upstream = max(
        records,
        key=lambda item: item[
            "upstream_silhouette"
        ],
    )

    print()
    print("=" * 72)
    print("CROSS-VIEW SUMMARY")
    print("=" * 72)

    print(
        "highest cross-view ARI:",
        best_ari,
    )

    print()
    print(
        "best internal silhouette:",
        best_internal,
    )

    print()
    print(
        "best upstream silhouette:",
        best_upstream,
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
        "MQ-3 CROSS-VIEW "
        "ANATOMICAL VALIDATION COMPLETE"
    )


if __name__ == "__main__":
    main()
