from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy import sparse


VERSION = "shuffled-mosca-v1"
SEED = 20260915


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def build_sign_preserving_permutation(
    transmitter_sign: np.ndarray,
    seed: int,
) -> np.ndarray:
    sign = np.asarray(
        transmitter_sign,
        dtype=np.float32,
    )

    n = len(sign)

    permutation = np.arange(
        n,
        dtype=np.int32,
    )

    rng = np.random.default_rng(seed)

    for value in (-1.0, 1.0):
        members = np.flatnonzero(
            sign == value
        ).astype(
            np.int32,
            copy=False,
        )

        shuffled = members.copy()
        rng.shuffle(shuffled)

        permutation[members] = shuffled

    if not np.array_equal(
        sign,
        sign[permutation],
    ):
        raise RuntimeError(
            "transmitter-sign preservation failed"
        )

    if np.array_equal(
        permutation,
        np.arange(n, dtype=np.int32),
    ):
        raise RuntimeError(
            "permutation unexpectedly identical"
        )

    if len(np.unique(permutation)) != n:
        raise RuntimeError(
            "permutation is not bijective"
        )

    return permutation


def compile_shuffled_connectome(
    connectome_path: Path,
    transmitter_path: Path,
    output_path: Path,
    provenance_path: Path,
    seed: int,
):
    connectome_path = connectome_path.resolve()
    transmitter_path = transmitter_path.resolve()
    output_path = output_path.resolve()
    provenance_path = provenance_path.resolve()

    print("loading connectome...")
    original = sparse.load_npz(
        connectome_path
    ).tocsr()

    transmitter_sign = np.load(
        transmitter_path
    )

    n = original.shape[0]

    if original.shape != (n, n):
        raise ValueError(
            "connectome must be square"
        )

    if transmitter_sign.shape != (n,):
        raise ValueError(
            "transmitter sign length mismatch"
        )

    print(
        "shape:",
        original.shape,
        "nnz:",
        original.nnz,
    )

    permutation = (
        build_sign_preserving_permutation(
            transmitter_sign,
            seed,
        )
    )

    print("building shuffled control...")

    # Preserve CSR row structure and exact edge weights.
    #
    # Only the presynaptic column identity is reassigned.
    shuffled = sparse.csr_matrix(
        (
            original.data.copy(),
            permutation[
                original.indices
            ].astype(
                np.int32,
                copy=False,
            ),
            original.indptr.copy(),
        ),
        shape=original.shape,
        dtype=original.dtype,
    )

    if shuffled.nnz != original.nnz:
        raise RuntimeError(
            "edge count changed"
        )

    # Exact structural invariant before canonical sorting:
    #
    # Every postsynaptic row retains the exact same sequence of
    # incoming weights. Only presynaptic column identity changes.
    if not np.array_equal(
        shuffled.indptr,
        original.indptr,
    ):
        raise RuntimeError(
            "postsynaptic row boundaries changed"
        )

    if not np.array_equal(
        shuffled.data,
        original.data,
    ):
        raise RuntimeError(
            "postsynaptic weight multiset changed"
        )

    original_row_degree = np.diff(
        original.indptr
    )

    shuffled_row_degree = np.diff(
        shuffled.indptr
    )

    if not np.array_equal(
        original_row_degree,
        shuffled_row_degree,
    ):
        raise RuntimeError(
            "postsynaptic row degree changed"
        )

    # Canonical ordering for stable serialization.
    #
    # Sorting only reorders (column, weight) pairs inside each row.
    # Float32 row sums can therefore differ by tiny rounding amounts.
    shuffled.sort_indices()

    original_abs_rows = np.asarray(
        abs(original).sum(axis=1)
    ).ravel()

    shuffled_abs_rows = np.asarray(
        abs(shuffled).sum(axis=1)
    ).ravel()

    normalization_error = float(
        np.max(
            np.abs(
                original_abs_rows
                - shuffled_abs_rows
            )
        )
    )

    if not np.allclose(
        original_abs_rows,
        shuffled_abs_rows,
        atol=1e-5,
        rtol=1e-6,
    ):
        raise RuntimeError(
            "incoming normalization changed "
            f"(max error={normalization_error})"
        )

    print(
        "max normalization roundoff:",
        normalization_error,
    )

    original_outdegree = np.bincount(
        original.indices,
        minlength=n,
    )

    shuffled_outdegree = np.bincount(
        shuffled.indices,
        minlength=n,
    )

    if not np.array_equal(
        np.sort(original_outdegree),
        np.sort(shuffled_outdegree),
    ):
        raise RuntimeError(
            "global outdegree distribution changed"
        )

    moved = int(
        np.count_nonzero(
            permutation
            != np.arange(
                n,
                dtype=np.int32,
            )
        )
    )

    inhibitory = int(
        np.count_nonzero(
            transmitter_sign == -1.0
        )
    )

    excitatory_unknown = int(
        np.count_nonzero(
            transmitter_sign == 1.0
        )
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    print("saving control artifact...")

    sparse.save_npz(
        output_path,
        shuffled,
        compressed=True,
    )

    provenance = {
        "version": VERSION,
        "seed": seed,
        "method": (
            "presynaptic_identity_permutation"
        ),
        "source_connectome": (
            connectome_path.name
        ),
        "source_connectome_sha256": (
            sha256_file(connectome_path)
        ),
        "transmitter_sign_source": (
            transmitter_path.name
        ),
        "transmitter_sign_sha256": (
            sha256_file(transmitter_path)
        ),
        "shape": list(
            original.shape
        ),
        "nnz": int(
            original.nnz
        ),
        "moved_neuron_identities": moved,
        "inhibitory_population": inhibitory,
        "excitatory_unknown_population": (
            excitatory_unknown
        ),
        "preserved": {
            "transmitter_sign": True,
            "postsynaptic_row_degree": True,
            "postsynaptic_weight_multiset": True,
            "incoming_absolute_normalization": True,
            "edge_count": True,
            "global_outdegree_distribution": True,
        },
        "destroyed": {
            "biological_presynaptic_identity": True,
            "biological_source_target_topology": True,
        },
    }

    provenance_path.write_text(
        json.dumps(
            provenance,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    print()
    print("SHUFFLED MOSCA CONTROL")
    print("  moved identities:", moved)
    print("  inhibitory:", inhibitory)
    print(
        "  excitatory/unknown:",
        excitatory_unknown,
    )
    print(
        "  row degree preserved: PASS"
    )
    print(
        "  incoming normalization preserved: PASS"
    )
    print(
        "  outdegree distribution preserved: PASS"
    )
    print(
        "  transmitter sign preserved: PASS"
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

    print()
    print(
        "SHUFFLED MOSCA BUILD PASS"
    )


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--connectome",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--transmitter-sign",
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

    parser.add_argument(
        "--seed",
        type=int,
        default=SEED,
    )

    args = parser.parse_args()

    compile_shuffled_connectome(
        connectome_path=args.connectome,
        transmitter_path=args.transmitter_sign,
        output_path=args.output,
        provenance_path=args.provenance,
        seed=args.seed,
    )


if __name__ == "__main__":
    main()
