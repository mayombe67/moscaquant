from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import scipy
from scipy import sparse

from brain.sq11_dark_forest_instrumentation import (
    build_body_row_geometry,
)
from brain.sq11_dark_forest_replay_v2 import (
    replay_csr_rows_float32,
)


ROOT = Path(__file__).resolve().parents[1]

CONNECTOME = (
    Path.home()
    / "moscaquant-data"
    / "processed"
    / "connectome-baseline-v1.npz"
)

CONTRACT = (
    ROOT
    / "config/experiments/"
    "sq11-dark-forest-replay-qualification-contract-v2.json"
)

OUTPUT = (
    ROOT
    / "artifacts/experiments/"
    "sq11-dark-forest/"
    "sq11-dark-forest-replay-qualification-v2.json"
)

EXPECTED_CONNECTOME_SHA256 = (
    "e00e3f2a9828c921fe1f093cc567bf45"
    "a85adad0526176be0aa1b8be09336eeb"
)

SOURCES = np.asarray(
    [65084, 128590, 135589],
    dtype=np.int64,
)

RESPONDERS = np.asarray(
    [137122, 317, 126002],
    dtype=np.int64,
)

MASKS = (
    "000",
    "001",
    "010",
    "011",
    "100",
    "101",
    "110",
    "111",
)

CASE_COUNT = 96


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()

    with path.open("rb") as f:
        for block in iter(
            lambda: f.read(
                8 * 1024 * 1024
            ),
            b"",
        ):
            h.update(block)

    return h.hexdigest()


def deterministic_activity(
    *,
    case: int,
    population: int,
) -> np.ndarray:
    if not (
        0 <= case < CASE_COUNT
    ):
        raise ValueError(
            "qualification case outside universe"
        )

    if case == 0:
        return np.zeros(
            population,
            dtype=np.float32,
        )

    if case == 1:
        return np.ones(
            population,
            dtype=np.float32,
        )

    if case == 2:
        return np.linspace(
            0.0,
            1.0,
            population,
            dtype=np.float32,
        )

    if case == 3:
        return np.linspace(
            1.0,
            0.0,
            population,
            dtype=np.float32,
        )

    if case == 4:
        return (
            np.arange(
                population,
                dtype=np.int64,
            )
            % 2
        ).astype(np.float32)

    if case == 5:
        return np.full(
            population,
            np.float32(2.0 ** -20),
            dtype=np.float32,
        )

    if case == 6:
        result = np.zeros(
            population,
            dtype=np.float32,
        )

        result[
            np.arange(population) % 17 == 0
        ] = np.float32(1.0)

        return result

    if case == 7:
        result = np.zeros(
            population,
            dtype=np.float32,
        )

        result[SOURCES] = np.float32(1.0)

        return result

    index = np.arange(
        population,
        dtype=np.uint64,
    )

    seed = np.uint64(case)

    state = (
        np.uint64(1664525)
        * (
            index
            + seed
            * np.uint64(1013904223)
        )
        + np.uint64(1013904223)
    ) & np.uint64(0xFFFFFFFF)

    mantissa = (
        state >> np.uint64(8)
    ).astype(np.uint32)

    result = (
        mantissa.astype(np.float32)
        / np.float32(16777216.0)
    )

    scales = (
        np.float32(1.0),
        np.float32(0.5),
        np.float32(1.0 / 256.0),
        np.float32(1.0 / 65536.0),
    )

    return (
        result
        * scales[
            (case - 8) % len(scales)
        ]
    ).astype(
        np.float32,
        copy=False,
    )


def reference_rows_for_mask(
    *,
    geometry: dict[str, np.ndarray],
    population: int,
    mask: str,
) -> sparse.csr_matrix:
    indices_parts = []
    data_parts = []
    indptr = [0]

    for row in range(3):
        start = int(
            geometry["row_offsets"][row]
        )

        stop = int(
            geometry["row_offsets"][row + 1]
        )

        columns = geometry[
            "row_indices"
        ][start:stop]

        weights = geometry[
            "row_weights"
        ][start:stop]

        if mask[row] == "1":
            local_body_position = int(
                geometry[
                    "body_positions"
                ][row]
            )

            keep = np.ones(
                len(columns),
                dtype=bool,
            )

            keep[
                local_body_position
            ] = False

            columns = columns[keep]
            weights = weights[keep]

        indices_parts.append(
            columns.astype(
                np.int32,
                copy=False,
            )
        )

        data_parts.append(
            weights.astype(
                np.float32,
                copy=False,
            )
        )

        indptr.append(
            indptr[-1]
            + len(columns)
        )

    indices = np.concatenate(
        indices_parts
    )

    data = np.concatenate(
        data_parts
    )

    return sparse.csr_matrix(
        (
            data,
            indices,
            np.asarray(
                indptr,
                dtype=np.int32,
            ),
        ),
        shape=(3, population),
        dtype=np.float32,
    )


def main() -> None:
    if OUTPUT.exists():
        raise RuntimeError(
            "v2 qualification artifact exists"
        )

    if (
        sha256_file(CONNECTOME)
        != EXPECTED_CONNECTOME_SHA256
    ):
        raise RuntimeError(
            "connectome SHA drift"
        )

    contract = json.loads(
        CONTRACT.read_text(
            encoding="utf-8"
        )
    )

    matrix = sparse.load_npz(
        CONNECTOME
    ).tocsr()

    if matrix.dtype != np.dtype(np.float32):
        raise RuntimeError(
            "connectome must be float32"
        )

    geometry = build_body_row_geometry(
        connectome=matrix,
        responder_indices=RESPONDERS,
        source_indices=SOURCES,
    )

    if np.diff(
        geometry["row_offsets"]
    ).tolist() != [
        2830,
        841,
        897,
    ]:
        raise RuntimeError(
            "BODY row geometry drift"
        )

    if geometry[
        "body_positions"
    ].tolist() != [
        1908,
        671,
        767,
    ]:
        raise RuntimeError(
            "BODY positions drift"
        )

    if geometry[
        "body_flat_positions"
    ].tolist() != [
        1908,
        3501,
        4438,
    ]:
        raise RuntimeError(
            "BODY flat positions drift"
        )

    union = geometry[
        "presynaptic_union_indices"
    ]

    references = {
        mask:
            reference_rows_for_mask(
                geometry=geometry,
                population=matrix.shape[1],
                mask=mask,
            )
        for mask in MASKS
    }

    mismatches = []

    for mask in MASKS:
        zeroed = np.asarray(
            [
                [
                    int(mask[0]),
                    int(mask[1]),
                    int(mask[2]),
                ]
            ],
            dtype=np.uint8,
        )

        reference_rows = references[
            mask
        ]

        for case in range(CASE_COUNT):
            full_activity = (
                deterministic_activity(
                    case=case,
                    population=
                        matrix.shape[1],
                )
            )

            local_activity = (
                full_activity[
                    union
                ][None, :]
            )

            replay = (
                replay_csr_rows_float32(
                    local_activity=
                        local_activity,
                    row_offsets=
                        geometry[
                            "row_offsets"
                        ],
                    row_weights=
                        geometry[
                            "row_weights"
                        ],
                    row_union_positions=
                        geometry[
                            "row_union_positions"
                        ],
                    body_flat_positions=
                        geometry[
                            "body_flat_positions"
                        ],
                    condition_edge_zeroed=
                        zeroed,
                )[0]
            )

            reference = np.asarray(
                reference_rows
                @ full_activity,
                dtype=np.float32,
            ).ravel()

            unequal = np.flatnonzero(
                replay != reference
            )

            for row in unequal:
                mismatches.append(
                    {
                        "mask":
                            mask,
                        "case":
                            int(case),
                        "row":
                            int(row),
                        "responder":
                            int(
                                RESPONDERS[
                                    row
                                ]
                            ),
                        "reference":
                            float(
                                reference[row]
                            ),
                        "replay":
                            float(
                                replay[row]
                            ),
                        "reference_bits":
                            int(
                                reference[
                                    row
                                ].view(
                                    np.uint32
                                )
                            ),
                        "replay_bits":
                            int(
                                replay[
                                    row
                                ].view(
                                    np.uint32
                                )
                            ),
                    }
                )

    comparisons = (
        len(MASKS)
        * CASE_COUNT
        * 3
    )

    status = (
        "PASS"
        if not mismatches
        else "FAIL"
    )

    report = {
        "schema_version":
            "moscaquant."
            "sq11-dark-forest-replay-qualification-result/v2",

        "experiment":
            "SQ-11",

        "codename":
            "DARK FOREST",

        "status":
            status,

        "supersedes_for_execution":
            "sq11-dark-forest-replay-qualification-result/v1",

        "neural_execution_performed":
            False,

        "sq11_neural_evidence_inspected":
            False,

        "activity_case_count":
            CASE_COUNT,

        "mask_count":
            len(MASKS),

        "row_count":
            3,

        "row_case_mask_comparisons":
            comparisons,

        "mismatch_count":
            len(mismatches),

        "first_mismatches":
            mismatches[:20],

        "connectome": {
            "path":
                str(CONNECTOME),

            "sha256":
                sha256_file(CONNECTOME),
        },

        "geometry": {
            "row_nnz":
                np.diff(
                    geometry[
                        "row_offsets"
                    ]
                ).tolist(),

            "body_positions":
                geometry[
                    "body_positions"
                ].tolist(),

            "body_flat_positions":
                geometry[
                    "body_flat_positions"
                ].tolist(),

            "flat_entry_count":
                int(
                    len(
                        geometry[
                            "row_weights"
                        ]
                    )
                ),

            "presynaptic_union_count":
                int(len(union)),
        },

        "criterion": {
            "equality":
                "exact float32",

            "absolute_tolerance":
                0.0,

            "relative_tolerance":
                0.0,

            "required_mismatch_count":
                0,

            "lesioned_entry_semantics":
                "structurally skipped",
        },

        "software": {
            "python":
                sys.version.split()[0],

            "numpy":
                np.__version__,

            "scipy":
                scipy.__version__,
        },

        "artifacts": {
            "qualification_contract_sha256":
                sha256_file(CONTRACT),

            "replay_implementation_sha256":
                sha256_file(
                    ROOT
                    / "brain/"
                    "sq11_dark_forest_replay_v2.py"
                ),

            "qualification_implementation_sha256":
                sha256_file(
                    Path(__file__)
                ),
        },
    }

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT.write_text(
        json.dumps(
            report,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    print(
        json.dumps(
            report,
            indent=2,
            sort_keys=True,
        )
    )

    if status != "PASS":
        raise SystemExit(
            "DARK FOREST v2 replay "
            "qualification FAILED"
        )


if __name__ == "__main__":
    main()
