"""Deterministic MaleCNS preprocessing for MoscaQuant MQ-001."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pyarrow.feather as feather


EXPECTED_NEURONS = 166_700
INHIBITORY = ("gaba", "glutamate", "histamine")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_neuron_index(raw: Path, processed: Path) -> None:
    processed.mkdir(parents=True, exist_ok=True)

    ann_path = raw / "body-annotations-male-cns-v1.0-minconf-0.5.feather"
    nt_path = raw / "body-neurotransmitters-male-cns-v1.0.feather"

    ann = feather.read_table(
        ann_path,
        columns=["bodyId", "superclass"],
    ).to_pandas()

    retained = ann.loc[
        ann["superclass"].notna() & ann["superclass"].ne("")
    ]

    retained = (
        retained
        .drop_duplicates("bodyId")
        .sort_values("bodyId")
    )

    ids = retained["bodyId"].to_numpy(dtype=np.int64)

    if len(ids) != EXPECTED_NEURONS:
        raise RuntimeError(
            f"Expected {EXPECTED_NEURONS:,} neurons, found {len(ids):,}"
        )

    if not np.all(ids[:-1] < ids[1:]):
        raise RuntimeError("Canonical bodyId index is not strictly increasing")

    nt = feather.read_table(
        nt_path,
        columns=["body", "consensus_nt"],
    ).to_pandas()

    labels = (
        nt.drop_duplicates("body")
        .set_index("body")
        .reindex(ids)["consensus_nt"]
        .fillna("unclear")
        .astype(str)
    )

    lower = labels.str.lower()

    inhibitory = np.zeros(len(ids), dtype=bool)
    for transmitter in INHIBITORY:
        inhibitory |= lower.str.contains(
            transmitter,
            regex=False,
        ).to_numpy()

    sign = np.where(inhibitory, -1.0, 1.0).astype(np.float32)

    ids_path = processed / "neuron_ids.npy"
    sign_path = processed / "transmitter_sign.npy"

    np.save(ids_path, ids, allow_pickle=False)
    np.save(sign_path, sign, allow_pickle=False)

    provenance = {
        "subject": "MQ-001",
        "dataset": "MaleCNS v1.0",
        "retention_rule": "superclass != null and superclass != empty",
        "ordering": "bodyId ascending",
        "neuron_count": int(len(ids)),
        "inhibitory_consensus_labels": list(INHIBITORY),
        "unknown_transmitter_sign": "excitatory (+1) for baseline-v1",
        "artifacts": {
            "neuron_ids.npy": sha256(ids_path),
            "transmitter_sign.npy": sha256(sign_path),
        },
    }

    provenance_path = processed / "population-provenance.json"
    provenance_path.write_text(
        json.dumps(provenance, indent=2) + "\n"
    )

    print(f"MQ-001 neurons:       {len(ids):,}")
    print(f"Inhibitory sign:      {(sign < 0).sum():,}")
    print(f"Excitatory/unknown:   {(sign > 0).sum():,}")
    print(f"First bodyId:         {ids[0]}")
    print(f"Last bodyId:          {ids[-1]}")
    print()
    print(f"Saved: {ids_path}")
    print(f"SHA256: {provenance['artifacts']['neuron_ids.npy']}")
    print()
    print(f"Saved: {sign_path}")
    print(f"SHA256: {provenance['artifacts']['transmitter_sign.npy']}")
    print()
    print(f"Saved: {provenance_path}")


if __name__ == "__main__":
    data = Path.home() / "moscaquant-data"
    build_neuron_index(data / "raw", data / "processed")
