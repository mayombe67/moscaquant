"""Compile the deterministic MQ-001 structural connectome."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from scipy import sparse

from brain.preprocess import census_retained_edges, iter_edge_batches, sha256
from config.loader import load_runtime, load_subject
import hashlib
import json
import platform
import sys

import scipy

def map_retained(
    ids: np.ndarray,
    pre_body: np.ndarray,
    post_body: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Map body IDs to MQ-001 indices and return retained endpoints."""

    n = len(ids)

    pre_idx = np.searchsorted(ids, pre_body)
    post_idx = np.searchsorted(ids, post_body)

    pre_valid = pre_idx < n
    post_valid = post_idx < n

    pre_match = np.zeros(len(pre_idx), dtype=bool)
    post_match = np.zeros(len(post_idx), dtype=bool)

    pre_match[pre_valid] = ids[pre_idx[pre_valid]] == pre_body[pre_valid]
    post_match[post_valid] = ids[post_idx[post_valid]] == post_body[post_valid]

    keep = pre_match & post_match

    return pre_idx[keep], post_idx[keep], keep

def array_sha256(array: np.ndarray) -> str:
    """SHA256 of an array's canonical contiguous bytes."""

    digest = hashlib.sha256()
    digest.update(np.ascontiguousarray(array).view(np.uint8))
    return digest.hexdigest()


def logical_csr_sha256(matrix: sparse.csr_matrix) -> str:
    """SHA256 of CSR data, indices, and indptr."""

    digest = hashlib.sha256()

    for array in (matrix.data, matrix.indices, matrix.indptr):
        digest.update(np.ascontiguousarray(array).view(np.uint8))

    return digest.hexdigest()
def verify_sources(raw: Path, subject: dict) -> dict:
    """Verify immutable MaleCNS inputs against the scientific source locks."""

    sources = subject["sources"]

    definitions = {
        "annotations": (
            sources["annotations_file"],
            sources["annotations_sha256"],
        ),
        "neurotransmitters": (
            sources["neurotransmitters_file"],
            sources["neurotransmitters_sha256"],
        ),
        "connectome": (
            sources["connectome_file"],
            sources["connectome_sha256"],
        ),
    }

    verified = {}

    print("Verifying MaleCNS source locks")

    for name, (filename, expected) in definitions.items():
        path = raw / filename

        if not path.exists():
            raise FileNotFoundError(f"Missing source file: {path}")

        actual = sha256(path)

        if actual != expected:
            raise RuntimeError(
                f"{name} SHA256 mismatch:\n"
                f"expected: {expected}\n"
                f"actual:   {actual}"
            )

        verified[name] = {
            "file": filename,
            "sha256": actual,
        }

        print(f"  {name}: OK")

    return verified

def compile_connectome(
    data_dir: Path,
    scratch_dir: Path,
    subject: dict,
) -> None:
    """Build baseline-v1 using a two-pass, disk-backed compiler."""

    processed = data_dir / "processed"
    raw = data_dir / "raw"
    verified_sources = verify_sources(raw, subject)

    ids = np.load(processed / "neuron_ids.npy", allow_pickle=False)
    sign = np.load(processed / "transmitter_sign.npy", allow_pickle=False)

    population = subject["population"]
    connectome = subject["connectome"]

    expected_edges = int(population["expected_connections"])
    expected_weight = int(population["expected_synaptic_weight"])

    edge_path = (
        raw
        / "connectome-weights-male-cns-v1.0-minconf-0.5.feather"
    )

    print("Pass 1/2: structural census")

    retained_edges, incoming64 = census_retained_edges(
        edge_path,
        ids,
        expected_edges,
        expected_weight,
    )

    incoming = incoming64.astype(np.float32)

    scratch = scratch_dir / "mq001-baseline-v1"
    scratch.mkdir(parents=True, exist_ok=True)

    pre_path = scratch / "pre.int32"
    post_path = scratch / "post.int32"
    weight_path = scratch / "weight.float32"

    pre = np.memmap(
        pre_path,
        dtype=np.int32,
        mode="w+",
        shape=(retained_edges,),
    )
    post = np.memmap(
        post_path,
        dtype=np.int32,
        mode="w+",
        shape=(retained_edges,),
    )
    weight = np.memmap(
        weight_path,
        dtype=np.float32,
        mode="w+",
        shape=(retained_edges,),
    )

    print("Pass 2/2: materializing retained edges")

    offset = 0

    for batch_number, batch in enumerate(iter_edge_batches(edge_path), start=1):
        pre_body = batch.column("body_pre").to_numpy(zero_copy_only=False)
        post_body = batch.column("body_post").to_numpy(zero_copy_only=False)
        raw_weight = batch.column("weight").to_numpy(zero_copy_only=False)

        pre_idx, post_idx, keep = map_retained(
            ids,
            pre_body,
            post_body,
        )

        count = len(pre_idx)
        end = offset + count

        pre[offset:end] = pre_idx.astype(np.int32, copy=False)
        post[offset:end] = post_idx.astype(np.int32, copy=False)

        normalized = raw_weight[keep].astype(np.float32)
        normalized *= sign[pre_idx]
        normalized /= np.maximum(incoming[post_idx], 1.0)

        weight[offset:end] = normalized

        offset = end

        if batch_number % 250 == 0:
            print(
                f"Pass 2: {batch_number:,} batches | "
                f"{offset:,}/{retained_edges:,} edges"
            )

    if offset != retained_edges:
        raise RuntimeError(
            f"Expected to write {retained_edges:,} edges, wrote {offset:,}"
        )

    pre.flush()
    post.flush()
    weight.flush()

    print("Building CSR")

    n = len(ids)

    matrix = sparse.csr_matrix(
        (weight, (post, pre)),
        shape=(n, n),
        dtype=np.float32,
    )

    if matrix.nnz != expected_edges:
        raise RuntimeError(
            f"Expected {expected_edges:,} CSR nonzeros, "
            f"found {matrix.nnz:,}"
        )

    incoming_check = np.asarray(abs(matrix).sum(axis=1)).ravel()
    active = incoming_check > 0

    provenance = {
        "sources": verified_sources,
        "references": subject["references"],
        "subject": subject["subject"]["id"],
        "dataset": subject["subject"]["dataset"],
        "baseline": subject["subject"]["baseline"],
        "population": {
            "neurons": int(n),
            "connections": int(matrix.nnz),
            "synaptic_weight": expected_weight,
            "rows_with_input": int(active.sum()),
            "rows_without_input": int((~active).sum()),
        },
        "connectome": {
            "shape": [int(matrix.shape[0]), int(matrix.shape[1])],
            "format": "csr",
            "weight_dtype": str(matrix.data.dtype),
            "index_dtype": str(matrix.indices.dtype),
            "orientation": connectome["orientation"],
            "normalization": connectome["normalization"],
            "max_normalization_error": float(
                np.max(np.abs(incoming_check[active] - 1.0))
            ),
        },
        "hashes": {
            "neuron_ids_sha256": array_sha256(ids),
            "transmitter_sign_sha256": array_sha256(sign),
            "csr_data_sha256": array_sha256(matrix.data),
            "csr_indices_sha256": array_sha256(matrix.indices),
            "csr_indptr_sha256": array_sha256(matrix.indptr),
            "logical_csr_sha256": logical_csr_sha256(matrix),
        },
        "build_environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "platform": platform.platform(),
            "byteorder": sys.byteorder,
        },
    }
    output = processed / "connectome-baseline-v1.npz"

    sparse.save_npz(
        output,
        matrix,
        compressed=False,
    )
    provenance_path = processed / "connectome-provenance.json"

    provenance_path.write_text(
        json.dumps(provenance, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print()
    print("=== MQ-001 CONNECTOME ===")
    print("Shape:       ", matrix.shape)
    print("Nonzeros:    ", f"{matrix.nnz:,}")
    print("Orientation: ", connectome["orientation"])
    print("Normalization:", connectome["normalization"])
    print("Artifact:    ", output)
    print("Provenance:  ", provenance_path)
    print(
        "Logical CSR: ",
        provenance["hashes"]["logical_csr_sha256"],
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime", default="habitat")
    args = parser.parse_args()

    subject = load_subject("mq001")
    runtime = load_runtime(args.runtime)

    compile_connectome(
        runtime["paths"]["data_dir"],
        runtime["paths"]["scratch_dir"],
        subject,
    )


if __name__ == "__main__":
    main()
