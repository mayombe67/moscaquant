from __future__ import annotations

import hashlib
import json
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


CONNECTOME = Path(
    "/home/wil/moscaquant-data/processed/"
    "connectome-baseline-v1.npz"
)

DN_ARTIFACT = Path(
    "/home/wil/moscaquant-data/processed/"
    "mq3-descending-readout-v1.npz"
)

OUTPUT_NPZ = Path(
    "/home/wil/moscaquant-data/processed/"
    "mq3-dn-consensus-v1.npz"
)

OUTPUT_JSON = Path(
    "/home/wil/moscaquant-data/processed/"
    "mq3-dn-consensus-v1.json"
)

K = 3


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        while True:
            block = handle.read(
                1024 * 1024
            )

            if not block:
                break

            digest.update(block)

    return digest.hexdigest()


def normalize_dense_rows(
    matrix: np.ndarray,
) -> np.ndarray:
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


def normalize_sparse_rows(
    matrix: sparse.csr_matrix,
) -> sparse.csr_matrix:
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

    inverse = np.zeros_like(
        norms,
        dtype=np.float64,
    )

    good = norms > 0

    inverse[good] = (
        1.0 / norms[good]
    )

    return (
        sparse.diags(inverse)
        @ matrix
    ).tocsr()


def canonical_labels(
    labels: np.ndarray,
) -> np.ndarray:
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
    condensed: np.ndarray,
) -> np.ndarray:
    hierarchy = linkage(
        condensed,
        method="average",
    )

    labels = fcluster(
        hierarchy,
        t=K,
        criterion="maxclust",
    )

    return canonical_labels(
        labels
    )


def build_internal_labels(
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

    blocks = [
        normalize_dense_rows(
            np.maximum(
                dn_dn,
                0.0,
            )
        ),
        normalize_dense_rows(
            np.maximum(
                -dn_dn,
                0.0,
            )
        ),
        normalize_dense_rows(
            np.maximum(
                dn_dn.T,
                0.0,
            )
        ),
        normalize_dense_rows(
            np.maximum(
                -dn_dn.T,
                0.0,
            )
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

    return cluster_labels(
        condensed
    )


def build_upstream_labels(
    connectome,
    dn_indices,
):
    incoming = connectome[
        dn_indices,
        :
    ].tocsr().astype(
        np.float64
    )

    #
    # Explicitly remove DN presynaptic
    # columns so this is an independent
    # non-DN upstream structural view.
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

    return cluster_labels(
        condensed
    )


def match_upstream_to_internal(
    internal,
    upstream,
):
    table = np.zeros(
        (K, K),
        dtype=np.int64,
    )

    for left, right in zip(
        internal,
        upstream,
    ):
        table[
            int(left),
            int(right),
        ] += 1

    rows, columns = (
        linear_sum_assignment(
            -table
        )
    )

    mapping = {
        int(column): int(row)
        for row, column
        in zip(
            rows,
            columns,
        )
    }

    matched = np.asarray(
        [
            mapping[
                int(label)
            ]
            for label
            in upstream
        ],
        dtype=np.int32,
    )

    return (
        matched,
        table,
        mapping,
    )


def main():
    dn = np.load(
        DN_ARTIFACT
    )

    body_ids = np.asarray(
        dn["body_id"],
        dtype=np.int64,
    )

    indices = np.asarray(
        dn["neuron_index"],
        dtype=np.int32,
    )

    soma_side = np.asarray(
        dn["soma_side"],
    ).astype(str)

    subclass = np.asarray(
        dn["subclass"],
    ).astype(str)

    if len(indices) != 1314:
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

    print(
        "building internal anatomy view..."
    )

    internal = build_internal_labels(
        connectome,
        indices,
    )

    print(
        "building non-DN upstream view..."
    )

    upstream = build_upstream_labels(
        connectome,
        indices,
    )

    (
        upstream_matched,
        contingency,
        mapping,
    ) = match_upstream_to_internal(
        internal,
        upstream,
    )

    agreed = (
        internal
        == upstream_matched
    )

    #
    # -1 means deliberately unassigned.
    #
    consensus = np.full(
        len(indices),
        -1,
        dtype=np.int32,
    )

    consensus[agreed] = (
        internal[agreed]
    )

    assigned_count = int(
        np.count_nonzero(
            consensus >= 0
        )
    )

    unassigned_count = int(
        np.count_nonzero(
            consensus < 0
        )
    )

    if assigned_count != 1191:
        raise RuntimeError(
            "expected 1191 consensus "
            f"assignments, got "
            f"{assigned_count}"
        )

    if unassigned_count != 123:
        raise RuntimeError(
            "expected 123 unassigned "
            f"DNs, got "
            f"{unassigned_count}"
        )

    cluster_sizes = {
        int(cluster):
            int(
                np.count_nonzero(
                    consensus
                    == cluster
                )
            )
        for cluster
        in range(K)
    }

    expected_sizes = {
        0: 6,
        1: 646,
        2: 539,
    }

    if cluster_sizes != expected_sizes:
        raise RuntimeError(
            "consensus cluster sizes "
            f"changed: {cluster_sizes}"
        )

    np.savez_compressed(
        OUTPUT_NPZ,
        body_id=body_ids,
        neuron_index=indices,
        internal_cluster=internal,
        upstream_cluster=upstream,
        upstream_matched_cluster=(
            upstream_matched
        ),
        consensus_cluster=consensus,
        assigned=agreed,
        soma_side=soma_side,
        subclass=subclass,
    )

    cluster_records = []

    for cluster in range(K):
        members = np.flatnonzero(
            consensus == cluster
        )

        side_counts = {
            side:
                int(
                    np.count_nonzero(
                        soma_side[
                            members
                        ] == side
                    )
                )
            for side in (
                "L",
                "R",
                "M",
                "",
            )
        }

        subclass_counts = {}

        for value in np.unique(
            subclass[
                members
            ]
        ):
            key = (
                value
                if value
                else "<missing>"
            )

            subclass_counts[
                key
            ] = int(
                np.count_nonzero(
                    subclass[
                        members
                    ] == value
                )
            )

        cluster_records.append(
            {
                "cluster":
                    cluster,

                "anonymous_name":
                    f"DN-C{cluster}",

                "size":
                    len(members),

                "soma_side_counts":
                    side_counts,

                "subclass_counts":
                    subclass_counts,

                "body_ids":
                    [
                        int(
                            body_ids[
                                member
                            ]
                        )
                        for member
                        in members
                    ],
            }
        )

    provenance = {
        "artifact":
            "mq3-dn-consensus-v1",

        "population":
            "mq3-descending-readout-v1",

        "cluster_count":
            K,

        "anonymous_channels": [
            "DN-C0",
            "DN-C1",
            "DN-C2",
        ],

        "assignment_rule":
            (
                "intersection_after_"
                "optimal_label_matching"
            ),

        "discordant_rule":
            "unassigned",

        "population_counts": {
            "total":
                1314,

            "assigned":
                assigned_count,

            "unassigned":
                unassigned_count,

            "DN-C0":
                cluster_sizes[0],

            "DN-C1":
                cluster_sizes[1],

            "DN-C2":
                cluster_sizes[2],
        },

        "contingency_internal_by_upstream":
            contingency.tolist(),

        "upstream_to_internal_mapping":
            {
                str(key): int(value)
                for key, value
                in mapping.items()
            },

        "clusters":
            cluster_records,

        "contamination_controls": {
            "market_response_used":
                False,

            "financial_semantics_used":
                False,

            "pnl_used":
                False,

            "condition_a_used":
                False,

            "condition_b_used":
                False,

            "discordant_neurons_forced":
                False,
        },

        "sources": {
            "connectome":
                str(CONNECTOME),

            "connectome_sha256":
                sha256_file(
                    CONNECTOME
                ),

            "dn_artifact":
                str(DN_ARTIFACT),

            "dn_artifact_sha256":
                sha256_file(
                    DN_ARTIFACT
                ),
        },
    }

    OUTPUT_JSON.write_text(
        json.dumps(
            provenance,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    print()
    print("=" * 72)
    print("MQ-3 DN CONSENSUS READOUT")
    print("=" * 72)

    print(
        "total DNs:",
        len(indices),
    )

    print(
        "assigned:",
        assigned_count,
    )

    print(
        "unassigned:",
        unassigned_count,
    )

    print()

    for cluster in range(K):
        members = np.flatnonzero(
            consensus == cluster
        )

        print(
            f"DN-C{cluster}:",
            len(members),
            "neurons",
        )

    print()
    print(
        "contingency:"
    )

    print(
        contingency
    )

    print()
    print(
        "artifact:",
        OUTPUT_NPZ,
    )

    print(
        "artifact sha256:",
        sha256_file(
            OUTPUT_NPZ
        ),
    )

    print(
        "provenance:",
        OUTPUT_JSON,
    )

    print(
        "provenance sha256:",
        sha256_file(
            OUTPUT_JSON
        ),
    )

    print()
    print(
        "MARKET RESPONSE USED: NO"
    )

    print(
        "FINANCIAL SEMANTICS USED: NO"
    )

    print(
        "DISCORDANT DNs FORCED: NO"
    )

    print()
    print(
        "MQ-3 ANONYMOUS OUTPUT "
        "POPULATIONS FROZEN"
    )


if __name__ == "__main__":
    main()
