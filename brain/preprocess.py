"""Deterministic MaleCNS preprocessing for MoscaQuant MQ-001."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import numpy as np
import pyarrow.feather as feather
import argparse

from config.loader import load_runtime, load_subject


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

def iter_edge_batches(edge_path: Path):
    """Yield native Arrow record batches without materializing the edge table."""

    table = feather.read_table(
        edge_path,
        columns=["body_pre", "body_post", "weight"],
        memory_map=True,
    )

    yield from table.to_batches()



def census_retained_edges(
    edge_path: Path,
    ids: np.ndarray,
    expected_connections: int,
    expected_synaptic_weight: int,
) -> tuple[int, np.ndarray]:
    """Count MQ-001 edges and accumulate raw incoming synaptic weight."""

    n = len(ids)
    retained_edges = 0
    incoming = np.zeros(n, dtype=np.float64)

    for batch_number, batch in enumerate(iter_edge_batches(edge_path), start=1):
        pre_body = batch.column("body_pre").to_numpy(zero_copy_only=False)
        post_body = batch.column("body_post").to_numpy(zero_copy_only=False)
        weight = batch.column("weight").to_numpy(zero_copy_only=False)

        pre_idx = np.searchsorted(ids, pre_body)
        post_idx = np.searchsorted(ids, post_body)

        pre_valid = pre_idx < n
        post_valid = post_idx < n

        pre_match = np.zeros(len(pre_idx), dtype=bool)
        post_match = np.zeros(len(post_idx), dtype=bool)

        pre_match[pre_valid] = ids[pre_idx[pre_valid]] == pre_body[pre_valid]
        post_match[post_valid] = ids[post_idx[post_valid]] == post_body[post_valid]

        keep = pre_match & post_match

        kept_post = post_idx[keep]
        kept_weight = weight[keep]

        retained_edges += int(keep.sum())

        np.add.at(
            incoming,
            kept_post,
            np.abs(kept_weight),
        )

        if batch_number % 250 == 0:
            print(
                f"Edge census: {batch_number:,} batches | "
                f"{retained_edges:,} retained"
            )
    if retained_edges != expected_connections:
        raise RuntimeError(
            f"Expected {expected_connections:,} retained edges, "
            f"found {retained_edges:,}"
        )

    synaptic_weight = int(incoming.sum())

    if synaptic_weight != expected_synaptic_weight:
        raise RuntimeError(
            f"Expected synaptic weight {expected_synaptic_weight:,}, "
            f"found {synaptic_weight:,}"
        )

    return retained_edges, incoming


def build_neuron_index(
    raw: Path,
    processed: Path,
    subject: dict,
) -> None:
    expected_neurons = subject["population"]["expected_neurons"]
    inhibitory_labels = tuple(subject["transmitters"]["inhibitory"])
    unknown_sign = float(subject["transmitters"]["unknown_sign"])
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

    if len(ids) != expected_neurons:
        raise RuntimeError(
            f"Expected {expected_neurons:,} neurons, found {len(ids):,}"
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
    for transmitter in inhibitory_labels:
        inhibitory |= lower.str.contains(
            transmitter,
            regex=False,
        ).to_numpy()

    sign = np.where(inhibitory, -1.0, unknown_sign).astype(np.float32)

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
        "inhibitory_consensus_labels": list(inhibitory_labels),
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


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build deterministic MoscaQuant MaleCNS artifacts."
    )
    parser.add_argument(
        "--runtime",
        default="habitat",
        help="Runtime profile from config/runtime/<name>.toml",
    )
    args = parser.parse_args()

    subject = load_subject("mq001")
    runtime = load_runtime(args.runtime)

    data = runtime["paths"]["data_dir"]

    print(f"Subject: {subject['subject']['id']}")
    print(f"Baseline: {subject['subject']['baseline']}")
    print(f"Runtime: {runtime['runtime']['name']}")
    print()

    build_neuron_index(
        data / "raw",
        data / "processed",
        subject,
    )


if __name__ == "__main__":
    main()
