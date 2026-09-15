"""Deterministic localized visual experiments for MQ-001."""

from argparse import ArgumentParser
from collections import Counter
from pathlib import Path

import numpy as np
import pyarrow.feather as feather
from scipy import sparse

from brain.populations import visual_r1_r6_indices
from brain.retina import load_optic_columns, infer_r1_r6_retina


DEFAULT_DATA = Path.home() / "moscaquant-data"


def run_flash(
    graph,
    neuron_ids: np.ndarray,
    placed,
    eye: str,
    h1: int,
    h2: int,
):
    """Apply one simultaneous spike to R1-R6 neurons at one inferred column."""

    cells = [
        p
        for p in placed
        if (p.eye, p.h1, p.h2) == (eye, h1, h2)
    ]

    if not cells:
        raise ValueError(
            f"No placed R1-R6 neurons at {eye}/{h1}/{h2}"
        )

    pre = np.asarray(
        [p.neuron_index for p in cells],
        dtype=np.int32,
    )

    stimulus = np.zeros(
        len(neuron_ids),
        dtype=np.float32,
    )
    stimulus[pre] = 1.0

    response = graph @ stimulus
    affected = np.flatnonzero(response)

    return cells, response, affected


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("--eye", choices=("L", "R"), required=True)
    parser.add_argument("--h1", type=int, required=True)
    parser.add_argument("--h2", type=int, required=True)
    parser.add_argument(
        "--data",
        type=Path,
        default=DEFAULT_DATA,
    )
    args = parser.parse_args()

    data = args.data

    ids = np.load(
        data / "processed/neuron_ids.npy",
        mmap_mode="r",
    )

    graph = sparse.load_npz(
        data / "processed/connectome-baseline-v1.npz"
    ).tocsr()

    annotations_path = (
        data
        / "raw"
        / "body-annotations-male-cns-v1.0-minconf-0.5.feather"
    )

    annotations = feather.read_table(
        annotations_path,
        columns=[
            "bodyId",
            "superclass",
            "type",
            "flywireType",
            "assignedOlHex1",
            "assignedOlHex2",
            "somaSide",
        ],
    ).to_pandas()

    annotations = (
        annotations
        .drop_duplicates("bodyId")
        .set_index("bodyId")
    )

    r1 = visual_r1_r6_indices(
        annotations_path,
        ids,
    )

    optic_columns = load_optic_columns(
        data
        / "raw"
        / "reference"
        / "optic-column-type-assignments-v1.0.xlsx"
    )

    placed, unplaced = infer_r1_r6_retina(
        graph,
        ids,
        r1,
        optic_columns,
    )

    cells, response, affected = run_flash(
        graph,
        ids,
        placed,
        args.eye,
        args.h1,
        args.h2,
    )

    print("=== MQ-001 SPATIAL FLASH ===")
    print(
        "column:",
        f"{args.eye}/{args.h1}/{args.h2}",
    )
    print("photoreceptors:", len(cells))
    print(
        "bodies:",
        [p.body_id for p in cells],
    )
    print("mapped R1-R6:", len(placed))
    print("unplaced R1-R6:", len(unplaced))
    print("affected:", len(affected))

    positive = affected[response[affected] > 0]
    negative = affected[response[affected] < 0]

    print("positive:", len(positive))
    print("negative:", len(negative))

    superclasses = Counter()
    types = Counter()

    print("\n=== FIRST HOP ===")

    for index in affected:
        body = int(ids[index])

        if body not in annotations.index:
            continue

        row = annotations.loc[body]

        superclass = row["superclass"]
        cell_type = row["type"]

        if isinstance(superclass, str):
            superclasses[superclass] += 1

        if isinstance(cell_type, str):
            types[cell_type] += 1

        print(
            f"body={body:<12d}",
            f"type={str(cell_type):<8s}",
            f"hex=({row['assignedOlHex1']},"
            f"{row['assignedOlHex2']})",
            f"soma={row['somaSide']}",
            f"response={float(response[index]):.8f}",
        )

    print("\n=== SUPERCLASSES ===")
    for name, count in superclasses.most_common():
        print(name, count)

    print("\n=== TYPES ===")
    for name, count in types.most_common():
        print(name, count)


if __name__ == "__main__":
    main()
