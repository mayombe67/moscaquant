"""Audit normalized retinal inference against raw synaptic weights."""

from collections import Counter
from pathlib import Path

import numpy as np
import pyarrow.feather as feather
from scipy import sparse

from brain.populations import visual_r1_r6_indices
from brain.retina import load_optic_columns, infer_r1_r6_retina


DATA = Path.home() / "moscaquant-data"


def main() -> None:
    ids = np.load(
        DATA / "processed/neuron_ids.npy",
        mmap_mode="r",
    )

    graph = sparse.load_npz(
        DATA / "processed/connectome-baseline-v1.npz"
    ).tocsr()

    annotations_path = (
        DATA / "raw"
        / "body-annotations-male-cns-v1.0-minconf-0.5.feather"
    )

    edge_path = (
        DATA / "raw"
        / "connectome-weights-male-cns-v1.0-minconf-0.5.feather"
    )

    optic_path = (
        DATA / "raw/reference"
        / "optic-column-type-assignments-v1.0.xlsx"
    )

    r1 = visual_r1_r6_indices(
        annotations_path,
        ids,
    )

    columns = load_optic_columns(
        optic_path
    )

    normalized, _ = infer_r1_r6_retina(
        graph,
        ids,
        r1,
        columns,
    )

    normalized_by_body = {
        p.body_id: (
            p.eye,
            p.h1,
            p.h2,
            p.partner_body_id,
        )
        for p in normalized
    }

    r1_bodies = set(
        int(ids[i])
        for i in r1
    )

    known_bodies = set(columns)

    # Best raw officially column-assigned postsynaptic
    # partner for each R1-R6 body.
    #
    # Feather is read in Arrow record batches so the
    # ~1 GB edge table is never converted wholesale
    # into pandas.
    table = feather.read_table(
        edge_path,
        columns=[
            "body_pre",
            "body_post",
            "weight",
        ],
        memory_map=True,
    )

    best = {}

    batches = table.to_batches()

    for batch_no, batch in enumerate(batches, 1):
        pre = batch.column(0).to_numpy(
            zero_copy_only=False
        )
        post = batch.column(1).to_numpy(
            zero_copy_only=False
        )
        weight = batch.column(2).to_numpy(
            zero_copy_only=False
        )

        # Dataset-scale membership masks. This is an
        # audit, not part of the runtime hot path.
        keep_pre = np.fromiter(
            (int(x) in r1_bodies for x in pre),
            dtype=bool,
            count=len(pre),
        )

        if not np.any(keep_pre):
            continue

        candidate_indices = np.flatnonzero(
            keep_pre
        )

        for j in candidate_indices:
            pre_body = int(pre[j])
            post_body = int(post[j])

            if post_body not in known_bodies:
                continue

            w = int(weight[j])

            previous = best.get(pre_body)

            if (
                previous is None
                or w > previous[0]
                or (
                    w == previous[0]
                    and post_body < previous[1]
                )
            ):
                best[pre_body] = (
                    w,
                    post_body,
                )

        if batch_no % 250 == 0:
            print(
                f"processed {batch_no:,} batches",
                f"raw placements={len(best):,}",
            )

    same_coordinate = 0
    different_coordinate = 0
    same_partner = 0
    normalized_only = 0
    raw_only = 0

    disagreements = []

    all_bodies = (
        set(normalized_by_body)
        | set(best)
    )

    for body in sorted(all_bodies):
        norm = normalized_by_body.get(body)
        raw = best.get(body)

        if norm is None:
            raw_only += 1
            continue

        if raw is None:
            normalized_only += 1
            continue

        raw_weight, raw_partner = raw
        raw_coord = columns[raw_partner]

        norm_coord = norm[:3]
        norm_partner = norm[3]

        if raw_coord == norm_coord:
            same_coordinate += 1
        else:
            different_coordinate += 1

            disagreements.append(
                (
                    body,
                    norm_coord,
                    norm_partner,
                    raw_coord,
                    raw_partner,
                    raw_weight,
                )
            )

        if raw_partner == norm_partner:
            same_partner += 1

    comparable = (
        same_coordinate
        + different_coordinate
    )

    print("\n=== MQ-001 RETINAL INFERENCE AUDIT ===")
    print(
        "normalized placements:",
        f"{len(normalized_by_body):,}",
    )
    print(
        "raw placements:",
        f"{len(best):,}",
    )
    print(
        "comparable:",
        f"{comparable:,}",
    )
    print(
        "same coordinate:",
        f"{same_coordinate:,}",
    )
    print(
        "different coordinate:",
        f"{different_coordinate:,}",
    )

    if comparable:
        print(
            "coordinate agreement:",
            f"{100 * same_coordinate / comparable:.2f}%",
        )

        print(
            "partner agreement:",
            f"{100 * same_partner / comparable:.2f}%",
        )

    print(
        "normalized only:",
        normalized_only,
    )
    print(
        "raw only:",
        raw_only,
    )

    print("\n=== FIRST COORDINATE DISAGREEMENTS ===")

    for (
        body,
        norm_coord,
        norm_partner,
        raw_coord,
        raw_partner,
        raw_weight,
    ) in disagreements[:25]:
        print(
            f"R1-R6={body}",
            f"normalized={norm_coord}",
            f"partner={norm_partner}",
            f"raw={raw_coord}",
            f"partner={raw_partner}",
            f"raw_weight={raw_weight}",
        )

    print("\n=== DISAGREEMENT COUNT ===")
    print(len(disagreements))

    norm_coords = Counter(
        value[:3]
        for value in normalized_by_body.values()
    )

    raw_coords = Counter(
        columns[value[1]]
        for value in best.values()
    )

    print(
        "normalized unique columns:",
        len(norm_coords),
    )
    print(
        "raw unique columns:",
        len(raw_coords),
    )


if __name__ == "__main__":
    main()
