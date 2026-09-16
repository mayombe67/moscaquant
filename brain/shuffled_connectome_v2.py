from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy import sparse


VERSION = "shuffled-mosca-v2"
SEED = 20260915


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def build_interface_preserving_permutation(
    transmitter_sign: np.ndarray,
    protected_indices: np.ndarray,
    seed: int,
) -> np.ndarray:
    sign = np.asarray(
        transmitter_sign,
        dtype=np.float32,
    )

    n = len(sign)

    protected_indices = np.asarray(
        protected_indices,
        dtype=np.int32,
    )

    protected_mask = np.zeros(
        n,
        dtype=bool,
    )

    protected_mask[
        protected_indices
    ] = True

    permutation = np.arange(
        n,
        dtype=np.int32,
    )

    rng = np.random.default_rng(seed)

    #
    # R1-R6 identities remain completely fixed.
    #
    # Everything else is permuted only among neurons
    # carrying the same frozen transmitter sign.
    #
    for value in np.unique(sign):
        members = np.flatnonzero(
            (sign == value)
            & ~protected_mask
        ).astype(
            np.int32,
            copy=False,
        )

        if len(members) <= 1:
            continue

        shuffled = members.copy()
        rng.shuffle(shuffled)

        permutation[
            members
        ] = shuffled

    if not np.array_equal(
        permutation[
            protected_indices
        ],
        protected_indices,
    ):
        raise RuntimeError(
            "protected retinal identity changed"
        )

    if not np.array_equal(
        sign,
        sign[
            permutation
        ],
    ):
        raise RuntimeError(
            "transmitter-sign preservation failed"
        )

    if len(
        np.unique(
            permutation
        )
    ) != n:
        raise RuntimeError(
            "permutation is not bijective"
        )

    #
    # Nothing outside the protected population
    # may be reassigned into a retinal identity.
    #
    nonprotected = np.flatnonzero(
        ~protected_mask
    )

    if np.any(
        protected_mask[
            permutation[
                nonprotected
            ]
        ]
    ):
        raise RuntimeError(
            "non-retinal identity mapped into "
            "protected retinal population"
        )

    return permutation


def compile_control(
    connectome_path: Path,
    transmitter_path: Path,
    retina_path: Path,
    relay_path: Path,
    output_path: Path,
    provenance_path: Path,
    seed: int,
):
    connectome_path = (
        connectome_path.resolve()
    )

    transmitter_path = (
        transmitter_path.resolve()
    )

    retina_path = (
        retina_path.resolve()
    )

    relay_path = (
        relay_path.resolve()
    )

    output_path = (
        output_path.resolve()
    )

    provenance_path = (
        provenance_path.resolve()
    )

    print(
        "loading frozen connectome..."
    )

    original = sparse.load_npz(
        connectome_path
    ).tocsr()

    transmitter_sign = np.load(
        transmitter_path
    )

    retina = np.load(
        retina_path
    )

    retinal_indices = np.asarray(
        retina[
            "neuron_index"
        ],
        dtype=np.int32,
    )

    relay = np.load(
        relay_path
    )

    relay_indices = np.asarray(
        relay[
            "neuron_index"
        ],
        dtype=np.int32,
    )

    n = original.shape[0]

    if original.shape != (
        n,
        n,
    ):
        raise ValueError(
            "connectome must be square"
        )

    if transmitter_sign.shape != (
        n,
    ):
        raise ValueError(
            "transmitter sign length mismatch"
        )

    if len(
        np.unique(
            retinal_indices
        )
    ) != len(
        retinal_indices
    ):
        raise ValueError(
            "duplicate retinal indices"
        )

    print(
        "shape:",
        original.shape,
    )

    print(
        "nnz:",
        original.nnz,
    )

    print(
        "protected retinal identities:",
        len(retinal_indices),
    )

    print(
        "frozen relay population:",
        len(relay_indices),
    )

    permutation = (
        build_interface_preserving_permutation(
            transmitter_sign,
            retinal_indices,
            seed,
        )
    )

    print(
        "building interface-preserving "
        "shuffled control..."
    )

    #
    # Same control principle as v1:
    #
    # every postsynaptic row keeps the exact
    # sequence of incoming weights;
    # only presynaptic identity is reassigned.
    #
    # Difference from v1:
    #
    # all mapped R1-R6 presynaptic identities
    # are excluded from the permutation.
    #
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

    #
    # Exact pre-sort row invariants.
    #
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
            "postsynaptic weight sequence changed"
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

    shuffled.sort_indices()

    #
    # Entire mapped retinal output interface
    # must remain bit-for-bit identical.
    #
    original_retinal_output = (
        original[
            :,
            retinal_indices
        ].tocsr()
    )

    shuffled_retinal_output = (
        shuffled[
            :,
            retinal_indices
        ].tocsr()
    )

    retinal_difference = (
        original_retinal_output
        != shuffled_retinal_output
    )

    if retinal_difference.nnz != 0:
        raise RuntimeError(
            "protected retinal output "
            "interface changed"
        )

    #
    # Explicitly verify the MQ-2.1
    # R1-R6 -> relay interface as well.
    #
    original_visual_interface = (
        original[
            relay_indices,
            :
        ][
            :,
            retinal_indices
        ].tocsr()
    )

    shuffled_visual_interface = (
        shuffled[
            relay_indices,
            :
        ][
            :,
            retinal_indices
        ].tocsr()
    )

    visual_difference = (
        original_visual_interface
        != shuffled_visual_interface
    )

    if visual_difference.nnz != 0:
        raise RuntimeError(
            "R1-R6 -> relay interface changed"
        )

    retinal_interface_edges = int(
        original_retinal_output.nnz
    )

    visual_interface_edges = int(
        original_visual_interface.nnz
    )

    #
    # Incoming absolute normalization should
    # remain equal except for float32 summation
    # order after canonical sorting.
    #
    original_abs_rows = np.asarray(
        abs(original).sum(
            axis=1
        )
    ).ravel()

    shuffled_abs_rows = np.asarray(
        abs(shuffled).sum(
            axis=1
        )
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

    #
    # Because this is still a bijective
    # presynaptic identity permutation,
    # global outdegree distribution is retained.
    #
    original_outdegree = np.bincount(
        original.indices,
        minlength=n,
    )

    shuffled_outdegree = np.bincount(
        shuffled.indices,
        minlength=n,
    )

    if not np.array_equal(
        np.sort(
            original_outdegree
        ),
        np.sort(
            shuffled_outdegree
        ),
    ):
        raise RuntimeError(
            "global outdegree distribution changed"
        )

    protected_mask = np.zeros(
        n,
        dtype=bool,
    )

    protected_mask[
        retinal_indices
    ] = True

    moved_mask = (
        permutation
        != np.arange(
            n,
            dtype=np.int32,
        )
    )

    moved_total = int(
        np.count_nonzero(
            moved_mask
        )
    )

    moved_protected = int(
        np.count_nonzero(
            moved_mask
            & protected_mask
        )
    )

    moved_nonprotected = int(
        np.count_nonzero(
            moved_mask
            & ~protected_mask
        )
    )

    inhibitory = int(
        np.count_nonzero(
            transmitter_sign
            == -1.0
        )
    )

    excitatory_unknown = int(
        np.count_nonzero(
            transmitter_sign
            == 1.0
        )
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    print(
        "saving control artifact..."
    )

    sparse.save_npz(
        output_path,
        shuffled,
        compressed=True,
    )

    provenance = {
        "version": VERSION,
        "seed": seed,
        "method": (
            "retinal_interface_preserving_"
            "presynaptic_identity_permutation"
        ),
        "source_connectome": (
            connectome_path.name
        ),
        "source_connectome_sha256": (
            sha256_file(
                connectome_path
            )
        ),
        "transmitter_sign_source": (
            transmitter_path.name
        ),
        "transmitter_sign_sha256": (
            sha256_file(
                transmitter_path
            )
        ),
        "retinal_artifact": (
            retina_path.name
        ),
        "retinal_artifact_sha256": (
            sha256_file(
                retina_path
            )
        ),
        "relay_artifact": (
            relay_path.name
        ),
        "relay_artifact_sha256": (
            sha256_file(
                relay_path
            )
        ),
        "shape": list(
            original.shape
        ),
        "nnz": int(
            original.nnz
        ),
        "protected_retinal_identities": int(
            len(
                retinal_indices
            )
        ),
        "protected_retinal_output_edges": (
            retinal_interface_edges
        ),
        "protected_r1_r6_relay_edges": (
            visual_interface_edges
        ),
        "moved_neuron_identities": (
            moved_total
        ),
        "moved_protected_identities": (
            moved_protected
        ),
        "moved_nonprotected_identities": (
            moved_nonprotected
        ),
        "inhibitory_population": (
            inhibitory
        ),
        "excitatory_unknown_population": (
            excitatory_unknown
        ),
        "preserved": {
            "mapped_r1_r6_identity": True,
            "mapped_r1_r6_output_interface": True,
            "r1_r6_to_visual_relay_interface": True,
            "transmitter_sign": True,
            "postsynaptic_row_degree": True,
            "postsynaptic_weight_sequence": True,
            "incoming_absolute_normalization": True,
            "edge_count": True,
            "global_outdegree_distribution": True,
        },
        "destroyed": {
            "nonretinal_biological_"
            "presynaptic_identity": True,
            "downstream_biological_"
            "source_target_topology": True,
        },
        "principles": {
            "market_condition_independent": True,
            "pnl_independent": True,
            "decoder_independent": True,
            "mq2_1_release_gain_unchanged": True,
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
    print("=" * 72)
    print(
        "SHUFFLED MOSCA v2"
    )
    print("=" * 72)

    print(
        "protected retinal identities:",
        len(retinal_indices),
    )

    print(
        "protected retinal output edges:",
        retinal_interface_edges,
    )

    print(
        "protected R1-R6 -> relay edges:",
        visual_interface_edges,
    )

    print()
    print(
        "moved identities:",
        moved_total,
    )

    print(
        "moved protected identities:",
        moved_protected,
    )

    print(
        "moved nonprotected identities:",
        moved_nonprotected,
    )

    print()
    print(
        "row degree preserved: PASS"
    )

    print(
        "incoming normalization preserved: PASS"
    )

    print(
        "outdegree distribution preserved: PASS"
    )

    print(
        "transmitter sign preserved: PASS"
    )

    print(
        "entire retinal output interface "
        "preserved: PASS"
    )

    print(
        "R1-R6 -> MQ-2.1 relay interface "
        "preserved: PASS"
    )

    print()
    print(
        "max normalization roundoff:",
        normalization_error,
    )

    print()
    print(
        "artifact:",
        output_path,
    )

    print(
        "artifact sha256:",
        sha256_file(
            output_path
        ),
    )

    print(
        "provenance:",
        provenance_path,
    )

    print()
    print(
        "SHUFFLED MOSCA v2 BUILD PASS"
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
        "--retina",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--relay",
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

    compile_control(
        connectome_path=args.connectome,
        transmitter_path=args.transmitter_sign,
        retina_path=args.retina,
        relay_path=args.relay,
        output_path=args.output,
        provenance_path=args.provenance,
        seed=args.seed,
    )


if __name__ == "__main__":
    main()
