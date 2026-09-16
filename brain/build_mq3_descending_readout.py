from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


RAW = Path(
    "/home/wil/moscaquant-data/raw/"
    "body-annotations-male-cns-v1.0-minconf-0.5.feather"
)

NEURON_IDS = Path(
    "/home/wil/moscaquant-data/processed/"
    "neuron_ids.npy"
)

OUTPUT_NPZ = Path(
    "/home/wil/moscaquant-data/processed/"
    "mq3-descending-readout-v1.npz"
)

OUTPUT_JSON = Path(
    "/home/wil/moscaquant-data/processed/"
    "mq3-descending-readout-v1.json"
)


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


def clean_string_array(
    series: pd.Series,
) -> np.ndarray:
    return (
        series
        .fillna("")
        .astype(str)
        .to_numpy(dtype="U")
    )


def main():
    annotations = pd.read_feather(
        RAW
    )

    required = {
        "bodyId",
        "superclass",
        "subclass",
        "type",
        "instance",
        "somaSide",
        "somaNeuromere",
    }

    missing = (
        required
        - set(annotations.columns)
    )

    if missing:
        raise RuntimeError(
            f"missing annotation columns: "
            f"{sorted(missing)}"
        )

    confirmed = annotations[
        annotations["superclass"]
        == "descending_neuron"
    ].copy()

    tbc = annotations[
        annotations["superclass"]
        == "descending_neuron_tbc"
    ].copy()

    if len(confirmed) != 1314:
        raise RuntimeError(
            "expected 1314 confirmed "
            f"descending neurons, found "
            f"{len(confirmed)}"
        )

    neuron_ids = np.load(
        NEURON_IDS
    ).astype(np.int64)

    index_by_body = {
        int(body_id): index
        for index, body_id
        in enumerate(neuron_ids)
    }

    body_ids = confirmed[
        "bodyId"
    ].astype(np.int64).to_numpy()

    missing_from_model = [
        int(body_id)
        for body_id in body_ids
        if int(body_id)
        not in index_by_body
    ]

    if missing_from_model:
        raise RuntimeError(
            "confirmed DNs missing "
            "from frozen model: "
            f"{missing_from_model[:10]}"
        )

    neuron_indices = np.asarray(
        [
            index_by_body[
                int(body_id)
            ]
            for body_id in body_ids
        ],
        dtype=np.int32,
    )

    #
    # Canonicalize artifact order by
    # frozen model neuron index.
    #
    order = np.argsort(
        neuron_indices
    )

    body_ids = body_ids[order]

    neuron_indices = (
        neuron_indices[order]
    )

    confirmed = (
        confirmed.iloc[
            order
        ].reset_index(drop=True)
    )

    if len(
        np.unique(neuron_indices)
    ) != 1314:
        raise RuntimeError(
            "descending neuron indices "
            "are not unique"
        )

    if len(
        np.unique(body_ids)
    ) != 1314:
        raise RuntimeError(
            "descending body IDs "
            "are not unique"
        )

    np.savez_compressed(
        OUTPUT_NPZ,
        body_id=body_ids,
        neuron_index=neuron_indices,
        subclass=clean_string_array(
            confirmed["subclass"]
        ),
        type=clean_string_array(
            confirmed["type"]
        ),
        instance=clean_string_array(
            confirmed["instance"]
        ),
        soma_side=clean_string_array(
            confirmed["somaSide"]
        ),
        soma_neuromere=(
            clean_string_array(
                confirmed[
                    "somaNeuromere"
                ]
            )
        ),
    )

    side_counts = (
        confirmed["somaSide"]
        .fillna("<missing>")
        .value_counts()
        .to_dict()
    )

    subclass_counts = (
        confirmed["subclass"]
        .fillna("<missing>")
        .value_counts()
        .to_dict()
    )

    provenance = {
        "artifact":
            "mq3-descending-readout-v1",

        "selection_rule": {
            "annotation_superclass":
                "descending_neuron",

            "exclude_superclass":
                "descending_neuron_tbc",

            "market_response_used":
                False,

            "financial_semantics_used":
                False,
        },

        "population": {
            "confirmed_descending":
                len(confirmed),

            "tbc_excluded":
                len(tbc),

            "represented_in_model":
                len(neuron_indices),

            "soma_side_counts":
                {
                    str(key): int(value)
                    for key, value
                    in side_counts.items()
                },

            "subclass_counts":
                {
                    str(key): int(value)
                    for key, value
                    in subclass_counts.items()
                },
        },

        "sources": {
            "annotations":
                str(RAW),

            "neuron_ids":
                str(NEURON_IDS),

            "annotations_sha256":
                sha256_file(RAW),

            "neuron_ids_sha256":
                sha256_file(
                    NEURON_IDS
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
    print(
        "MQ-3 DESCENDING READOUT "
        "BOUNDARY"
    )
    print("=" * 72)

    print(
        "confirmed DNs:",
        len(neuron_indices),
    )

    print(
        "TBC excluded:",
        len(tbc),
    )

    print(
        "index min/max:",
        int(
            neuron_indices.min()
        ),
        int(
            neuron_indices.max()
        ),
    )

    print(
        "soma sides:",
        side_counts,
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
        "MQ-3 BIOLOGICAL OUTPUT "
        "BOUNDARY FROZEN"
    )


if __name__ == "__main__":
    main()
