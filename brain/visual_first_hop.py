from __future__ import annotations
from config.paths import data_path

from collections import Counter
from pathlib import Path

import numpy as np
import pyarrow.feather as feather
from scipy import sparse


CONNECTOME = data_path('processed', 'connectome-baseline-v1.npz')

RETINA = data_path('processed', 'visual-r1-r6-map-v1.npz')

ANNOTATIONS = data_path('raw', 'body-annotations-male-cns-v1.0-minconf-0.5.feather')

NEURON_IDS = data_path('processed', 'neuron_ids.npy')


LABEL_COLUMNS = (
    "superclass",
    "class",
    "subclass",
    "type",
    "supertype",
    "flywireType",
    "instance",
    "rootSide",
    "somaSide",
)


def clean(value):
    if value is None:
        return None

    value = str(value).strip()

    if not value:
        return None

    return value


def main():
    print("loading connectome...")

    connectome = sparse.load_npz(
        CONNECTOME
    ).tocsr()

    print(
        "shape:",
        connectome.shape,
        "nnz:",
        connectome.nnz,
    )

    print("loading retinal mapping...")

    retina = np.load(
        RETINA
    )

    retinal_indices = np.asarray(
        retina["neuron_index"],
        dtype=np.int32,
    )

    print(
        "placed R1-R6 neurons:",
        len(retinal_indices),
    )

    print("loading neuron IDs...")

    neuron_ids = np.load(
        NEURON_IDS
    )

    if len(neuron_ids) != connectome.shape[0]:
        raise RuntimeError(
            "neuron ID population mismatch"
        )

    retinal_mask = np.zeros(
        connectome.shape[0],
        dtype=bool,
    )

    retinal_mask[
        retinal_indices
    ] = True

    #
    # Frozen connectome orientation:
    #
    # connectome[post, pre]
    #
    # Selecting retinal columns therefore gives every
    # postsynaptic target receiving R1-R6 output.
    #
    retinal_output = connectome[
        :,
        retinal_indices
    ].tocsr()

    target_strength = np.asarray(
        np.abs(
            retinal_output
        ).sum(axis=1)
    ).ravel()

    target_edge_count = np.diff(
        retinal_output.indptr
    )

    target_mask = (
        (target_edge_count > 0)
        & ~retinal_mask
    )

    target_indices = np.flatnonzero(
        target_mask
    )

    strengths = target_strength[
        target_indices
    ]

    edge_counts = target_edge_count[
        target_indices
    ]

    order = np.argsort(
        strengths
    )[::-1]

    target_indices = target_indices[
        order
    ]

    strengths = strengths[
        order
    ]

    edge_counts = edge_counts[
        order
    ]

    print()
    print("=" * 72)
    print("R1-R6 FIRST-HOP TARGETS")
    print("=" * 72)

    print(
        "unique downstream targets:",
        len(target_indices),
    )

    print(
        "total retinal->target edges:",
        int(
            edge_counts.sum()
        ),
    )

    print(
        "strongest absolute incoming retinal weight:",
        float(
            strengths.max()
        )
        if len(strengths)
        else 0.0,
    )

    print(
        "median absolute retinal weight:",
        float(
            np.median(
                strengths
            )
        )
        if len(strengths)
        else 0.0,
    )

    for threshold in (
        0.10,
        0.25,
        0.50,
    ):
        print(
            f"targets with >= {threshold:.2f} "
            "retinal drive:",
            int(
                np.count_nonzero(
                    strengths
                    >= threshold
                )
            ),
        )

    print()
    print("top 25 targets:")
    print()

    for rank, (
        index,
        strength,
        edges,
    ) in enumerate(
        zip(
            target_indices[:25],
            strengths[:25],
            edge_counts[:25],
        ),
        start=1,
    ):
        print(
            f"{rank:2d}. "
            f"index={int(index):6d} "
            f"body_id={int(neuron_ids[index])} "
            f"edges={int(edges):3d} "
            f"abs_drive={float(strength):.6f}"
        )

    print()
    print("loading MaleCNS annotations...")

    available = set(
        feather.read_table(
            ANNOTATIONS,
        ).column_names
    )

    requested_columns = [
        "bodyId",
        *[
            column
            for column in LABEL_COLUMNS
            if column in available
        ],
    ]

    table = feather.read_table(
        ANNOTATIONS,
        columns=requested_columns,
    )

    print(
        "annotation rows:",
        table.num_rows,
    )

    print(
        "annotation fields:",
        ", ".join(
            requested_columns
        ),
    )

    #
    # Build a lightweight bodyId -> annotation mapping.
    # No pandas dependency.
    #
    columns = {
        name: table[name].to_pylist()
        for name in requested_columns
    }

    annotation_lookup = {}

    body_ids = columns[
        "bodyId"
    ]

    wanted_body_ids = {
        int(body_id)
        for body_id in neuron_ids[
            target_indices
        ]
    }

    for row_index, body_id in enumerate(
        body_ids
    ):
        if body_id is None:
            continue

        body_id = int(body_id)

        if body_id not in wanted_body_ids:
            continue

        if body_id in annotation_lookup:
            continue

        annotation_lookup[
            body_id
        ] = {
            column: clean(
                columns[column][row_index]
            )
            for column in requested_columns
            if column != "bodyId"
        }

    annotated_count = sum(
        1
        for body_id in wanted_body_ids
        if body_id in annotation_lookup
    )

    print()
    print(
        "first-hop targets with annotations:",
        annotated_count,
    )

    print(
        "annotation coverage:",
        (
            annotated_count
            / len(target_indices)
        )
        if len(target_indices)
        else 0.0,
    )

    print()
    print("=" * 72)
    print("FIRST-HOP ANNOTATION SUMMARY")
    print("=" * 72)

    for column in LABEL_COLUMNS:
        if column not in requested_columns:
            continue

        counter = Counter()

        for body_id in neuron_ids[
            target_indices
        ]:
            row = annotation_lookup.get(
                int(body_id)
            )

            if row is None:
                continue

            value = row.get(
                column
            )

            if value is not None:
                counter[value] += 1

        if not counter:
            continue

        print()
        print(column + ":")

        for value, count in counter.most_common(
            30
        ):
            print(
                f"  {value}: {count}"
            )

    print()
    print("=" * 72)
    print("TOP TARGET ANNOTATIONS")
    print("=" * 72)

    for rank, (
        index,
        strength,
        edges,
    ) in enumerate(
        zip(
            target_indices[:25],
            strengths[:25],
            edge_counts[:25],
        ),
        start=1,
    ):
        body_id = int(
            neuron_ids[index]
        )

        print()
        print(
            f"{rank:2d}. "
            f"index={int(index)} "
            f"body_id={body_id} "
            f"edges={int(edges)} "
            f"abs_drive={float(strength):.6f}"
        )

        row = annotation_lookup.get(
            body_id
        )

        if row is None:
            print(
                "    annotation: unavailable"
            )
            continue

        for column in LABEL_COLUMNS:
            value = row.get(
                column
            )

            if value is not None:
                print(
                    f"    {column}: {value}"
                )

    #
    # Summarize drive by biological class.
    #
    print()
    print("=" * 72)
    print("RETINAL DRIVE BY CLASS")
    print("=" * 72)

    class_stats = {}

    for (
        index,
        strength,
        edges,
    ) in zip(
        target_indices,
        strengths,
        edge_counts,
    ):
        body_id = int(
            neuron_ids[index]
        )

        row = annotation_lookup.get(
            body_id,
            {},
        )

        label = (
            row.get("type")
            or row.get("subclass")
            or row.get("class")
            or row.get("superclass")
            or "UNANNOTATED"
        )

        stats = class_stats.setdefault(
            label,
            {
                "neurons": 0,
                "edges": 0,
                "drive": 0.0,
                "max_drive": 0.0,
            },
        )

        stats["neurons"] += 1
        stats["edges"] += int(
            edges
        )
        stats["drive"] += float(
            strength
        )
        stats["max_drive"] = max(
            stats["max_drive"],
            float(strength),
        )

    ranked_classes = sorted(
        class_stats.items(),
        key=lambda item: (
            item[1]["drive"]
        ),
        reverse=True,
    )

    for label, stats in ranked_classes[
        :40
    ]:
        print(
            f"{label}: "
            f"neurons={stats['neurons']} "
            f"edges={stats['edges']} "
            f"total_drive={stats['drive']:.6f} "
            f"max_drive={stats['max_drive']:.6f}"
        )

    print()
    print(
        "VISUAL FIRST-HOP ANALYSIS PASS"
    )


if __name__ == "__main__":
    main()
