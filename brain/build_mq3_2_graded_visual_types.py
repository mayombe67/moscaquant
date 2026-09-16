from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


NEURON_IDS = Path(
    "/home/wil/moscaquant-data/processed/neuron_ids.npy"
)

ANNOTATIONS = Path(
    "/home/wil/moscaquant-data/raw/"
    "body-annotations-male-cns-v1.0-minconf-0.5.feather"
)

OUTPUT_NPZ = Path(
    "/home/wil/moscaquant-data/processed/"
    "mq3-2-graded-visual-types-v1.npz"
)

OUTPUT_JSON = Path(
    "/home/wil/moscaquant-data/processed/"
    "mq3-2-graded-visual-types-v1.json"
)

ALLOWED_TYPES = (
    "Tm2",
    "Tm3",
    "Tm4",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        while True:
            block = handle.read(1024 * 1024)

            if not block:
                break

            digest.update(block)

    return digest.hexdigest()


def main():
    neuron_ids = np.load(
        NEURON_IDS
    ).astype(np.int64)

    if len(neuron_ids) != 166700:
        raise RuntimeError(
            f"expected 166700 model neurons, got {len(neuron_ids)}"
        )

    annotations = pd.read_feather(
        ANNOTATIONS
    )

    required = {
        "bodyId",
        "type",
    }

    missing = required - set(
        annotations.columns
    )

    if missing:
        raise RuntimeError(
            f"missing annotation columns: {sorted(missing)}"
        )

    #
    # One model index per frozen body ID.
    #
    body_to_index = {
        int(body_id): index
        for index, body_id
        in enumerate(neuron_ids)
    }

    selected = annotations[
        annotations["type"].isin(
            ALLOWED_TYPES
        )
    ].copy()

    #
    # Keep only neurons represented in the
    # frozen 166,700-neuron model.
    #
    selected = selected[
        selected["bodyId"].isin(
            body_to_index
        )
    ].copy()

    selected["neuron_index"] = (
        selected["bodyId"]
        .map(body_to_index)
        .astype(np.int32)
    )

    selected = selected.sort_values(
        "neuron_index"
    )

    indices = selected[
        "neuron_index"
    ].to_numpy(
        dtype=np.int32
    )

    body_ids = selected[
        "bodyId"
    ].to_numpy(
        dtype=np.int64
    )

    types = selected[
        "type"
    ].fillna("").to_numpy(
        dtype=str
    )

    if len(indices) == 0:
        raise RuntimeError(
            "no graded visual neurons selected"
        )

    if len(np.unique(indices)) != len(indices):
        raise RuntimeError(
            "duplicate model indices in graded population"
        )

    observed_types = set(
        np.unique(types)
    )

    if observed_types != set(
        ALLOWED_TYPES
    ):
        raise RuntimeError(
            "expected all frozen graded types; "
            f"got {sorted(observed_types)}"
        )

    counts = {
        cell_type:
            int(
                np.count_nonzero(
                    types == cell_type
                )
            )
        for cell_type in ALLOWED_TYPES
    }

    np.savez_compressed(
        OUTPUT_NPZ,
        neuron_index=indices,
        body_id=body_ids,
        type=types,
    )

    provenance = {
        "artifact":
            "mq3-2-graded-visual-types-v1",

        "selection_basis":
            "body annotation type",

        "allowed_types":
            list(ALLOWED_TYPES),

        "population_count":
            int(len(indices)),

        "type_counts":
            counts,

        "market_response_used":
            False,

        "financial_semantics_used":
            False,

        "bridge_membership_used":
            False,

        "selection_scope":
            "all matching neurons in frozen 166700-neuron model",

        "sources": {
            "neuron_ids":
                str(NEURON_IDS),

            "neuron_ids_sha256":
                sha256_file(
                    NEURON_IDS
                ),

            "annotations":
                str(ANNOTATIONS),

            "annotations_sha256":
                sha256_file(
                    ANNOTATIONS
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

    print("=" * 72)
    print("MQ-3.2 GRADED VISUAL TYPE POPULATION")
    print("=" * 72)

    print(
        "selection:",
        ", ".join(
            ALLOWED_TYPES
        ),
    )

    print(
        "total selected:",
        len(indices),
    )

    print()

    for cell_type in ALLOWED_TYPES:
        print(
            cell_type,
            counts[cell_type],
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
    print("MARKET RESPONSE USED: NO")
    print("BRIDGE MEMBERSHIP USED: NO")
    print("FINANCIAL SEMANTICS USED: NO")


if __name__ == "__main__":
    main()
