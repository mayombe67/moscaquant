"""Build the frozen MQ-001 retinal map."""

import hashlib
import json
from pathlib import Path

import numpy as np
from scipy import sparse

from brain.populations import visual_r1_r6_indices
from brain.retina import (
    infer_r1_r6_retina,
    load_optic_columns,
    save_retinal_map,
)


DATA = Path.home() / "moscaquant-data"

OPTIC_SHA256 = (
    "d4af1cacb751036f7e84bfecc9bec79ca010066ac066559c29b566003ec080d3"
)


def sha256(path: Path) -> str:
    h = hashlib.sha256()

    with path.open("rb") as f:
        for chunk in iter(
            lambda: f.read(1024 * 1024),
            b"",
        ):
            h.update(chunk)

    return h.hexdigest()


def main() -> None:
    processed = DATA / "processed"

    ids_path = processed / "neuron_ids.npy"

    graph_path = (
        processed
        / "connectome-baseline-v1.npz"
    )

    annotations_path = (
        DATA
        / "raw"
        / "body-annotations-male-cns-v1.0-minconf-0.5.feather"
    )

    optic_path = (
        DATA
        / "raw/reference"
        / "optic-column-type-assignments-v1.0.xlsx"
    )

    output_path = (
        processed
        / "visual-r1-r6-map-v1.npz"
    )

    provenance_path = (
        processed
        / "visual-r1-r6-map-v1.json"
    )

    actual_optic_sha = sha256(
        optic_path
    )

    if actual_optic_sha != OPTIC_SHA256:
        raise RuntimeError(
            "Optic-column workbook SHA256 mismatch: "
            f"{actual_optic_sha}"
        )

    ids = np.load(
        ids_path,
        mmap_mode="r",
    )

    graph = sparse.load_npz(
        graph_path
    ).tocsr()

    r1 = visual_r1_r6_indices(
        annotations_path,
        ids,
    )

    columns = load_optic_columns(
        optic_path
    )

    assignments, unplaced = (
        infer_r1_r6_retina(
            graph,
            ids,
            r1,
            columns,
        )
    )

    save_retinal_map(
        output_path,
        assignments,
        unplaced,
    )

    # Reload what was actually serialized.
    frozen = np.load(
        output_path,
        allow_pickle=False,
    )

    placed_count = len(
        frozen["neuron_index"]
    )

    unplaced_count = len(
        frozen["unplaced_neuron_index"]
    )

    unique_columns = len(
        set(
            zip(
                frozen["eye"].tolist(),
                frozen["h1"].tolist(),
                frozen["h2"].tolist(),
            )
        )
    )

    if placed_count != 3241:
        raise RuntimeError(
            f"Expected 3241 placed R1-R6, "
            f"found {placed_count}"
        )

    if unplaced_count != 136:
        raise RuntimeError(
            f"Expected 136 unplaced R1-R6, "
            f"found {unplaced_count}"
        )

    if unique_columns != 800:
        raise RuntimeError(
            f"Expected 800 retinal columns, "
            f"found {unique_columns}"
        )

    artifact_sha = sha256(
        output_path
    )

    provenance = {
        "version": "retinal-map-v1",
        "subject": "MQ-001",
        "dataset": "MaleCNS v1.0",
        "method": (
            "strongest normalized connection from "
            "R1-R6 to officially column-assigned "
            "L1/R7/R8 partner"
        ),
        "optic_columns": {
            "file": optic_path.name,
            "sha256": actual_optic_sha,
            "workbook_semantics": {
                "column": "column ROI name",
                "L1": "bodyId assigned to column",
                "R7": "bodyId assigned to column",
                "R8": "bodyId assigned to column",
                "missing": -99,
            },
        },
        "counts": {
            "r1_r6": 3377,
            "placed": placed_count,
            "unplaced": unplaced_count,
            "unique_columns": unique_columns,
        },
        "audit": {
            "normalized_placements": 3241,
            "raw_placements": 3241,
            "comparable": 3241,
            "same_coordinate": 3239,
            "different_coordinate": 2,
            "coordinate_agreement_percent": 99.94,
            "partner_agreement_percent": 99.85,
            "disagreements": [
                {
                    "body_id": 187441,
                    "normalized": ["R", 9, 20],
                    "raw": ["R", 9, 21],
                },
                {
                    "body_id": 210647,
                    "normalized": ["R", 9, 20],
                    "raw": ["R", 9, 21],
                },
            ],
        },
        "mq1_sequence": [
            ["L", 23, 32],
            ["L", 24, 32],
            ["L", 25, 32],
        ],
        "artifact": {
            "file": output_path.name,
            "sha256": artifact_sha,
        },
    }

    provenance_path.write_text(
        json.dumps(
            provenance,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )

    print(
        "=== MQ-001 RETINAL MAP V1 ==="
    )
    print(
        "R1-R6:",
        len(r1),
    )
    print(
        "placed:",
        placed_count,
    )
    print(
        "unplaced:",
        unplaced_count,
    )
    print(
        "unique columns:",
        unique_columns,
    )
    print(
        "artifact:",
        output_path,
    )
    print(
        "artifact sha256:",
        artifact_sha,
    )
    print(
        "provenance:",
        provenance_path,
    )


if __name__ == "__main__":
    main()
