from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

import numpy as np


VERSION = "market-retinal-territories-v1"
TERRITORY_COUNT = 6


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def build_columns(
    eye: np.ndarray,
    h1: np.ndarray,
    h2: np.ndarray,
    eye_value: int,
):
    mask = eye == eye_value

    receptor_coords = list(zip(h1[mask], h2[mask]))
    counts = Counter(receptor_coords)

    coords = np.array(
        sorted(counts),
        dtype=np.int16,
    )

    weights = np.array(
        [counts[tuple(coord)] for coord in coords],
        dtype=np.int16,
    )

    return coords, weights


def weighted_split(
    indices,
    coords: np.ndarray,
    weights: np.ndarray,
    axis: int,
    parts: int,
):
    """
    Split whole retinal columns along one spatial axis while
    approximately equalizing receptor count.

    No column is ever split.
    """

    other_axis = 1 - axis

    ordered = sorted(
        indices,
        key=lambda i: (
            int(coords[i, axis]),
            int(coords[i, other_axis]),
        ),
    )

    groups = []
    start = 0

    for part in range(parts - 1):
        remaining_parts = parts - part

        remaining_weight = sum(
            int(weights[i])
            for i in ordered[start:]
        )

        target = remaining_weight / remaining_parts

        running = 0
        best_end = start + 1
        best_error = float("inf")

        max_end = len(ordered) - (remaining_parts - 1)

        for end in range(start + 1, max_end + 1):
            running += int(weights[ordered[end - 1]])

            error = abs(running - target)

            if error < best_error:
                best_error = error
                best_end = end

            if running >= target and error > best_error:
                break

        groups.append(ordered[start:best_end])
        start = best_end

    groups.append(ordered[start:])

    return groups


def partition_eye(
    coords: np.ndarray,
    weights: np.ndarray,
):
    """
    Deterministic 2 x 3 retinal partition.

    First:
        split h1 into two receptor-balanced spatial halves.

    Then:
        split each half along h2 into three receptor-balanced bands.

    Result:
        six anonymous territories.
    """

    indices = list(range(len(coords)))

    halves = weighted_split(
        indices,
        coords,
        weights,
        axis=0,
        parts=2,
    )

    territories = []

    for half in halves:
        territories.extend(
            weighted_split(
                half,
                coords,
                weights,
                axis=1,
                parts=3,
            )
        )

    if len(territories) != TERRITORY_COUNT:
        raise RuntimeError(
            f"expected {TERRITORY_COUNT} territories, "
            f"got {len(territories)}"
        )

    return territories


def build_territory_lookup(
    eye: np.ndarray,
    h1: np.ndarray,
    h2: np.ndarray,
):
    lookup = {}
    summary = []

    for eye_value, eye_name in (
        (0, "left"),
        (1, "right"),
    ):
        coords, weights = build_columns(
            eye,
            h1,
            h2,
            eye_value,
        )

        territories = partition_eye(
            coords,
            weights,
        )

        for territory_index, indices in enumerate(
            territories,
            start=1,
        ):
            receptor_count = int(weights[indices].sum())
            column_count = len(indices)

            territory_coords = coords[indices]

            for coord in territory_coords:
                key = (
                    eye_value,
                    int(coord[0]),
                    int(coord[1]),
                )

                if key in lookup:
                    raise RuntimeError(
                        f"duplicate retinal column assignment: {key}"
                    )

                lookup[key] = territory_index

            summary.append(
                {
                    "eye": eye_name,
                    "eye_value": eye_value,
                    "territory": territory_index,
                    "receptors": receptor_count,
                    "columns": column_count,
                    "h1_min": int(
                        territory_coords[:, 0].min()
                    ),
                    "h1_max": int(
                        territory_coords[:, 0].max()
                    ),
                    "h2_min": int(
                        territory_coords[:, 1].min()
                    ),
                    "h2_max": int(
                        territory_coords[:, 1].max()
                    ),
                }
            )

    return lookup, summary


def compile_territories(
    retinal_map_path: Path,
    output_path: Path,
    provenance_path: Path,
):
    retinal_map_path = retinal_map_path.resolve()
    output_path = output_path.resolve()
    provenance_path = provenance_path.resolve()

    data = np.load(retinal_map_path)

    required = {
        "neuron_index",
        "body_id",
        "eye",
        "h1",
        "h2",
    }

    missing = required - set(data.files)

    if missing:
        raise ValueError(
            "retinal map missing arrays: "
            + ", ".join(sorted(missing))
        )

    neuron_index = data["neuron_index"]
    body_id = data["body_id"]
    eye = data["eye"]
    h1 = data["h1"]
    h2 = data["h2"]

    size = len(neuron_index)

    for name, array in (
        ("body_id", body_id),
        ("eye", eye),
        ("h1", h1),
        ("h2", h2),
    ):
        if len(array) != size:
            raise ValueError(
                f"{name} length {len(array)} != {size}"
            )

    lookup, summary = build_territory_lookup(
        eye,
        h1,
        h2,
    )

    territory = np.empty(
        size,
        dtype=np.int8,
    )

    for i in range(size):
        key = (
            int(eye[i]),
            int(h1[i]),
            int(h2[i]),
        )

        try:
            territory[i] = lookup[key]
        except KeyError as exc:
            raise RuntimeError(
                f"unassigned retinal receptor: {key}"
            ) from exc

    if np.any(territory < 1) or np.any(
        territory > TERRITORY_COUNT
    ):
        raise RuntimeError(
            "invalid territory assignment"
        )

    bilateral_loads = np.array(
        [
            int(np.count_nonzero(territory == t))
            for t in range(
                1,
                TERRITORY_COUNT + 1,
            )
        ],
        dtype=np.int32,
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    np.savez_compressed(
        output_path,
        version=np.array(VERSION),
        neuron_index=neuron_index.astype(
            np.int32,
            copy=False,
        ),
        body_id=body_id.astype(
            np.int64,
            copy=False,
        ),
        eye=eye.astype(
            np.int8,
            copy=False,
        ),
        h1=h1.astype(
            np.int16,
            copy=False,
        ),
        h2=h2.astype(
            np.int16,
            copy=False,
        ),
        territory=territory,
    )

    provenance = {
        "version": VERSION,
        "source_retinal_map": retinal_map_path.name,
        "source_retinal_map_sha256": sha256_file(
            retinal_map_path
        ),
        "placed_receptors": size,
        "territory_count": TERRITORY_COUNT,
        "partition": {
            "type": "deterministic_2x3_receptor_balanced_grid",
            "first_axis": "h1",
            "first_parts": 2,
            "second_axis": "h2",
            "second_parts": 3,
            "whole_columns_only": True,
            "ticker_agnostic": True,
        },
        "bilateral_receptor_loads": bilateral_loads.tolist(),
        "bilateral_target": float(
            size / TERRITORY_COUNT
        ),
        "bilateral_range": [
            int(bilateral_loads.min()),
            int(bilateral_loads.max()),
        ],
        "bilateral_max_delta": int(
            bilateral_loads.max()
            - bilateral_loads.min()
        ),
        "territories": summary,
    }

    provenance_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    provenance_path.write_text(
        json.dumps(
            provenance,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    print(
        f"version: {VERSION}"
    )
    print(
        f"placed receptors: {size}"
    )

    print()

    for record in summary:
        print(
            f"{record['eye']:5s} "
            f"T{record['territory']}: "
            f"receptors={record['receptors']:4d} "
            f"columns={record['columns']:3d} "
            f"h1={record['h1_min']:2d}"
            f"->{record['h1_max']:2d} "
            f"h2={record['h2_min']:2d}"
            f"->{record['h2_max']:2d}"
        )

    print()
    print(
        "bilateral loads:",
        bilateral_loads.tolist(),
    )
    print(
        "target:",
        size / TERRITORY_COUNT,
    )
    print(
        "range:",
        int(bilateral_loads.min()),
        "->",
        int(bilateral_loads.max()),
    )
    print(
        "max delta:",
        int(
            bilateral_loads.max()
            - bilateral_loads.min()
        ),
    )

    print()
    print(
        "artifact:",
        output_path,
    )
    print(
        "artifact sha256:",
        sha256_file(output_path),
    )
    print(
        "provenance:",
        provenance_path,
    )


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--retina",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--output",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--provenance",
        type=Path,
        required=True,
    )

    args = parser.parse_args()

    compile_territories(
        retinal_map_path=args.retina,
        output_path=args.output,
        provenance_path=args.provenance,
    )


if __name__ == "__main__":
    main()
