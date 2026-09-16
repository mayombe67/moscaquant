from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pyarrow.feather as feather
from scipy import sparse


CONNECTOME = Path(
    "/home/wil/moscaquant-data/processed/connectome-baseline-v1.npz"
)

RETINA = Path(
    "/home/wil/moscaquant-data/processed/visual-r1-r6-map-v1.npz"
)

NEURON_IDS = Path(
    "/home/wil/moscaquant-data/processed/neuron_ids.npy"
)

ANNOTATIONS = Path(
    "/home/wil/moscaquant-data/raw/"
    "body-annotations-male-cns-v1.0-minconf-0.5.feather"
)

OUTPUT = Path(
    "/home/wil/moscaquant-data/processed/visual-relay-map-v1.npz"
)

PROVENANCE = Path(
    "/home/wil/moscaquant-data/processed/visual-relay-map-v1.json"
)

RELAY_TYPES = (
    "L1",
    "L2",
    "L3",
    "Lai",
)

VERSION = "visual-relay-map-v1"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def main():
    print("loading frozen connectome...")

    connectome = sparse.load_npz(
        CONNECTOME
    ).tocsr()

    retina = np.load(
        RETINA
    )

    retinal_indices = np.asarray(
        retina["neuron_index"],
        dtype=np.int32,
    )

    neuron_ids = np.load(
        NEURON_IDS
    )

    if len(neuron_ids) != connectome.shape[0]:
        raise RuntimeError(
            "neuron population mismatch"
        )

    print("loading MaleCNS annotations...")

    table = feather.read_table(
        ANNOTATIONS,
        columns=[
            "bodyId",
            "type",
        ],
    )

    body_ids = table[
        "bodyId"
    ].to_pylist()

    cell_types = table[
        "type"
    ].to_pylist()

    type_by_body = {}

    for body_id, cell_type in zip(
        body_ids,
        cell_types,
    ):
        if (
            body_id is not None
            and cell_type
        ):
            type_by_body[
                int(body_id)
            ] = str(cell_type)

    retinal_mask = np.zeros(
        connectome.shape[0],
        dtype=bool,
    )

    retinal_mask[
        retinal_indices
    ] = True

    #
    # connectome[post, pre]
    #
    retinal_output = connectome[
        :,
        retinal_indices
    ].tocsr()

    target_mask = (
        np.diff(
            retinal_output.indptr
        ) > 0
    ) & ~retinal_mask

    candidate_indices = np.flatnonzero(
        target_mask
    )

    records = []

    for index in candidate_indices:
        body_id = int(
            neuron_ids[index]
        )

        cell_type = type_by_body.get(
            body_id
        )

        if cell_type not in RELAY_TYPES:
            continue

        records.append(
            (
                int(index),
                body_id,
                cell_type,
            )
        )

    #
    # Canonical artifact ordering:
    # neural population index ascending.
    #
    records.sort(
        key=lambda row: row[0]
    )

    relay_indices = np.asarray(
        [
            row[0]
            for row in records
        ],
        dtype=np.int32,
    )

    relay_body_ids = np.asarray(
        [
            row[1]
            for row in records
        ],
        dtype=np.int64,
    )

    relay_type = np.asarray(
        [
            row[2]
            for row in records
        ],
        dtype="U8",
    )

    if len(relay_indices) != 2430:
        raise RuntimeError(
            "expected 2430 L1/L2/L3/Lai "
            f"relay neurons, got {len(relay_indices)}"
        )

    if len(np.unique(relay_indices)) != len(
        relay_indices
    ):
        raise RuntimeError(
            "duplicate relay neuron indices"
        )

    if np.any(
        retinal_mask[
            relay_indices
        ]
    ):
        raise RuntimeError(
            "relay population overlaps placed R1-R6"
        )

    expected_counts = {
        "L1": 804,
        "L2": 789,
        "L3": 762,
        "Lai": 75,
    }

    observed_counts = {
        cell_type: int(
            np.count_nonzero(
                relay_type
                == cell_type
            )
        )
        for cell_type in RELAY_TYPES
    }

    if observed_counts != expected_counts:
        raise RuntimeError(
            "relay class counts changed: "
            f"{observed_counts}"
        )

    #
    # Confirm every frozen relay is directly contacted
    # by at least one mapped R1-R6 neuron.
    #
    relay_from_retina = connectome[
        relay_indices,
        :
    ][
        :,
        retinal_indices
    ].tocsr()

    incoming_edges = np.diff(
        relay_from_retina.indptr
    )

    if np.any(
        incoming_edges == 0
    ):
        raise RuntimeError(
            "relay neuron without direct R1-R6 input"
        )

    incoming_abs_drive = np.asarray(
        np.abs(
            relay_from_retina
        ).sum(axis=1)
    ).ravel().astype(
        np.float32,
        copy=False,
    )

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    np.savez_compressed(
        OUTPUT,
        version=np.asarray(
            VERSION
        ),
        neuron_index=relay_indices,
        body_id=relay_body_ids,
        type=relay_type,
        retinal_edge_count=(
            incoming_edges.astype(
                np.int32,
                copy=False,
            )
        ),
        retinal_abs_drive=(
            incoming_abs_drive
        ),
    )

    provenance = {
        "version": VERSION,
        "selection": (
            "direct mapped R1-R6 targets "
            "with MaleCNS type in "
            "L1/L2/L3/Lai"
        ),
        "relay_types": list(
            RELAY_TYPES
        ),
        "relay_neurons": int(
            len(relay_indices)
        ),
        "type_counts": (
            observed_counts
        ),
        "retinal_edges": int(
            incoming_edges.sum()
        ),
        "source_connectome": (
            CONNECTOME.name
        ),
        "source_connectome_sha256": (
            sha256_file(
                CONNECTOME
            )
        ),
        "source_retina": (
            RETINA.name
        ),
        "source_retina_sha256": (
            sha256_file(
                RETINA
            )
        ),
        "source_annotations": (
            ANNOTATIONS.name
        ),
        "source_annotations_sha256": (
            sha256_file(
                ANNOTATIONS
            )
        ),
        "principles": {
            "market_condition_independent": True,
            "pnl_independent": True,
            "decoder_independent": True,
            "structural_connectome_unchanged": True,
        },
    }

    PROVENANCE.write_text(
        json.dumps(
            provenance,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    print()
    print("MQ-2.1 VISUAL RELAY MAP")
    print(
        "  total:",
        len(relay_indices),
    )

    for cell_type in RELAY_TYPES:
        print(
            f"  {cell_type}:",
            observed_counts[
                cell_type
            ],
        )

    print(
        "  direct retinal edges:",
        int(
            incoming_edges.sum()
        ),
    )

    print(
        "  artifact:",
        OUTPUT,
    )

    print(
        "  artifact sha256:",
        sha256_file(
            OUTPUT
        ),
    )

    print(
        "  provenance:",
        PROVENANCE,
    )

    print()
    print(
        "MQ-2.1 VISUAL RELAY MAP PASS"
    )


if __name__ == "__main__":
    main()
