from __future__ import annotations
from config.paths import data_path

import hashlib
import json
from pathlib import Path
import tomllib

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

CONFIG = Path(
    "config/controls/"
    "mq3-dn-structural-partition-v1.toml"
)

OUTPUT_NPZ = data_path('processed', 'mq3-dn-structural-partition-v1.npz')

OUTPUT_JSON = data_path('processed', 'mq3-dn-structural-partition-v1.json')


def sha256_file(
    path: Path,
) -> str:
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


def normalize_rows(
    matrix: np.ndarray,
) -> np.ndarray:
    norms = np.linalg.norm(
        matrix,
        axis=1,
        keepdims=True,
    )

    nonzero = (
        norms[:, 0] > 0
    )

    result = matrix.copy()

    result[nonzero] /= (
        norms[nonzero]
    )

    return result


def silhouette_from_distance(
    distance: np.ndarray,
    labels: np.ndarray,
) -> float:
    unique_labels = np.unique(
        labels
    )

    silhouettes = np.zeros(
        len(labels),
        dtype=np.float64,
    )

    for index in range(
        len(labels)
    ):
        own_label = labels[index]

        own = np.flatnonzero(
            labels == own_label
        )

        if len(own) <= 1:
            silhouettes[index] = 0.0
            continue

        own_without_self = own[
            own != index
        ]

        a = float(
            distance[
                index,
                own_without_self,
            ].mean()
        )

        b = np.inf

        for other_label in (
            unique_labels
        ):
            if other_label == own_label:
                continue

            other = np.flatnonzero(
                labels == other_label
            )

            candidate = float(
                distance[
                    index,
                    other,
                ].mean()
            )

            b = min(
                b,
                candidate,
            )

        denominator = max(
            a,
            b,
        )

        if denominator > 0:
            silhouettes[index] = (
                b - a
            ) / denominator

    return float(
        silhouettes.mean()
    )


def main():
    with CONFIG.open(
        "rb"
    ) as handle:
        config = tomllib.load(
            handle
        )

    dn = np.load(
        DN_ARTIFACT
    )

    indices = np.asarray(
        dn["neuron_index"],
        dtype=np.int32,
    )

    body_ids = np.asarray(
        dn["body_id"],
        dtype=np.int64,
    )

    soma_side = np.asarray(
        dn["soma_side"],
    ).astype(str)

    subclass = np.asarray(
        dn["subclass"],
    ).astype(str)

    if len(indices) != 1314:
        raise RuntimeError(
            "expected frozen 1314-DN "
            "population"
        )

    print(
        "loading frozen connectome..."
    )

    connectome = sparse.load_npz(
        CONNECTOME
    ).tocsr()

    #
    # Rows = postsynaptic DN.
    # Columns = presynaptic DN.
    #
    dn_dn = connectome[
        indices,
        :
    ][
        :,
        indices
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

    #
    # Transpose so each row describes
    # that DN's outgoing pattern.
    #
    positive_out = np.maximum(
        dn_dn.T,
        0.0,
    )

    negative_out = np.maximum(
        -dn_dn.T,
        0.0,
    )

    blocks = [
        normalize_rows(
            positive_in
        ),
        normalize_rows(
            negative_in
        ),
        normalize_rows(
            positive_out
        ),
        normalize_rows(
            negative_out
        ),
    ]

    fingerprint = np.concatenate(
        blocks,
        axis=1,
    )

    fingerprint = normalize_rows(
        fingerprint
    )

    norms = np.linalg.norm(
        fingerprint,
        axis=1,
    )

    if np.any(
        norms == 0
    ):
        raise RuntimeError(
            "zero structural fingerprint"
        )

    print()
    print("=" * 72)
    print(
        "MQ-3 DN STRUCTURAL "
        "PARTITION"
    )
    print("=" * 72)

    print(
        "DN count:",
        len(indices),
    )

    print(
        "fingerprint dimensions:",
        fingerprint.shape[1],
    )

    print()
    print(
        "computing cosine distance..."
    )

    condensed = pdist(
        fingerprint,
        metric="cosine",
    )

    if not np.all(
        np.isfinite(condensed)
    ):
        raise RuntimeError(
            "non-finite cosine distance"
        )

    distance = squareform(
        condensed
    )

    print(
        "computing deterministic "
        "average-linkage hierarchy..."
    )

    hierarchy = linkage(
        condensed,
        method="average",
    )

    k_min = int(
        config[
            "selection"
        ][
            "minimum_clusters"
        ]
    )

    k_max = int(
        config[
            "selection"
        ][
            "maximum_clusters"
        ]
    )

    evaluations = []

    print()
    print("=" * 72)
    print("PARTITION SWEEP")
    print("=" * 72)

    for k in range(
        k_min,
        k_max + 1,
    ):
        labels = fcluster(
            hierarchy,
            t=k,
            criterion="maxclust",
        ).astype(
            np.int32
        )

        #
        # Canonical zero-based labels.
        #
        unique = sorted(
            np.unique(labels)
        )

        remap = {
            old: new
            for new, old
            in enumerate(unique)
        }

        labels = np.asarray(
            [
                remap[
                    int(label)
                ]
                for label
                in labels
            ],
            dtype=np.int32,
        )

        actual_k = len(
            np.unique(labels)
        )

        score = (
            silhouette_from_distance(
                distance,
                labels,
            )
        )

        sizes = np.bincount(
            labels
        )

        evaluations.append(
            {
                "requested_k": k,
                "actual_k": actual_k,
                "silhouette": score,
                "min_size":
                    int(
                        sizes.min()
                    ),
                "median_size":
                    float(
                        np.median(
                            sizes
                        )
                    ),
                "max_size":
                    int(
                        sizes.max()
                    ),
            }
        )

        print(
            f"k={k:2d}",
            f"actual={actual_k:2d}",
            f"silhouette={score:.6f}",
            f"size[min/med/max]="
            f"{sizes.min()}/"
            f"{np.median(sizes):.1f}/"
            f"{sizes.max()}",
        )

    #
    # Maximum silhouette.
    # Python max preserves the earlier item
    # only if we make the tie-break explicit.
    #
    best_score = max(
        item["silhouette"]
        for item in evaluations
    )

    tied = [
        item
        for item in evaluations
        if np.isclose(
            item["silhouette"],
            best_score,
            rtol=0.0,
            atol=1e-12,
        )
    ]

    selected = min(
        tied,
        key=lambda item: (
            item["actual_k"]
        ),
    )

    selected_k = int(
        selected["actual_k"]
    )

    labels = fcluster(
        hierarchy,
        t=selected[
            "requested_k"
        ],
        criterion="maxclust",
    ).astype(
        np.int32
    )

    #
    # Canonicalize labels by smallest
    # frozen neuron index in each cluster.
    #
    raw_clusters = []

    for label in np.unique(
        labels
    ):
        members = np.flatnonzero(
            labels == label
        )

        raw_clusters.append(
            (
                int(
                    indices[
                        members
                    ].min()
                ),
                int(label),
                members,
            )
        )

    raw_clusters.sort()

    final_labels = np.empty(
        len(labels),
        dtype=np.int32,
    )

    cluster_records = []

    for new_label, (
        _,
        old_label,
        members,
    ) in enumerate(
        raw_clusters
    ):
        final_labels[
            members
        ] = new_label

        sides = {
            value:
                int(
                    np.count_nonzero(
                        soma_side[
                            members
                        ] == value
                    )
                )
            for value in (
                "L",
                "R",
                "M",
                "",
            )
        }

        subclasses = {}

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

            subclasses[
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
                    new_label,

                "size":
                    len(members),

                "minimum_model_index":
                    int(
                        indices[
                            members
                        ].min()
                    ),

                "soma_side_counts":
                    sides,

                "subclass_counts":
                    subclasses,
            }
        )

    np.savez_compressed(
        OUTPUT_NPZ,
        body_id=body_ids,
        neuron_index=indices,
        cluster=final_labels,
    )

    provenance = {
        "artifact":
            "mq3-dn-structural-partition-v1",

        "population":
            "mq3-descending-readout-v1",

        "method": {
            "fingerprint":
                [
                    "positive_incoming",
                    "negative_incoming",
                    "positive_outgoing",
                    "negative_outgoing",
                ],

            "block_l2_normalization":
                True,

            "final_l2_normalization":
                True,

            "distance":
                "cosine",

            "hierarchy":
                "average_linkage",

            "k_range":
                [
                    k_min,
                    k_max,
                ],

            "selection":
                "maximum_mean_silhouette",

            "tie_break":
                "smallest_k",
        },

        "selection": {
            "selected_k":
                selected_k,

            "selected_silhouette":
                float(
                    selected[
                        "silhouette"
                    ]
                ),
        },

        "evaluations":
            evaluations,

        "clusters":
            cluster_records,

        "contamination_controls": {
            "market_response_used":
                False,

            "financial_semantics_used":
                False,

            "condition_a_used":
                False,

            "condition_b_used":
                False,

            "pnl_used":
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
    print("SELECTED PARTITION")
    print("=" * 72)

    print(
        "selected clusters:",
        selected_k,
    )

    print(
        "silhouette:",
        selected[
            "silhouette"
        ],
    )

    print()

    for cluster in (
        cluster_records
    ):
        print(
            "cluster",
            cluster["cluster"],
            "size=",
            cluster["size"],
            "sides=",
            cluster[
                "soma_side_counts"
            ],
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

    print()
    print(
        "MQ-3 DN STRUCTURAL "
        "PARTITION COMPLETE"
    )


if __name__ == "__main__":
    main()
