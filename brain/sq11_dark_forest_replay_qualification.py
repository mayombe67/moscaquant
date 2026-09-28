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
from brain.sq11_dark_forest_replay import (
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
    "sq11-dark-forest-replay-qualification-contract-v1.json"
)

OUTPUT = (
    ROOT
    / "artifacts/experiments/"
    "sq11-dark-forest/"
    "sq11-dark-forest-replay-qualification-v1.json"
)

SOURCES = np.asarray(
    [65084, 128590, 135589],
    dtype=np.int64,
)

RESPONDERS = np.asarray(
    [137122, 317, 126002],
    dtype=np.int64,
)

EXPECTED_CONNECTOME_SHA256 = (
    "e00e3f2a9828c921fe1f093cc567bf45"
    "a85adad0526176be0aa1b8be09336eeb"
)

CASE_COUNT = 96


def sha256_file(
    path: Path,
) -> str:
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
            "qualification case outside "
            "frozen universe"
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
        ).astype(
            np.float32
        )

    if case == 5:
        return np.full(
            population,
            np.float32(
                2.0 ** -20
            ),
            dtype=np.float32,
        )

    if case == 6:
        result = np.zeros(
            population,
            dtype=np.float32,
        )

        result[
            np.arange(
                population
            )
            % 17
            == 0
        ] = np.float32(1.0)

        return result

    if case == 7:
        result = np.zeros(
            population,
            dtype=np.float32,
        )

        result[SOURCES] = (
            np.float32(1.0)
        )

        return result

    index = np.arange(
        population,
        dtype=np.uint64,
    )

    seed = np.uint64(
        case
    )

    state = (
        np.uint64(1664525)
        * (
            index
            + seed
            * np.uint64(
                1013904223
            )
        )
        + np.uint64(
            1013904223
        )
    ) & np.uint64(
        0xFFFFFFFF
    )

    mantissa = (
        state >> np.uint64(8)
    ).astype(
        np.uint32
    )

    result = (
        mantissa.astype(
            np.float32
        )
        / np.float32(
            16777216.0
        )
    )

    scales = (
        np.float32(1.0),
        np.float32(0.5),
        np.float32(
            1.0 / 256.0
        ),
        np.float32(
            1.0 / 65536.0
        ),
    )

    scale = scales[
        (case - 8)
        % len(scales)
    ]

    return (
        result
        * scale
    ).astype(
        np.float32,
        copy=False,
    )


def main() -> None:
    if OUTPUT.exists():
        raise RuntimeError(
            "qualification artifact "
            "already exists"
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

    if (
        contract["qualification"][
            "case_count"
        ]
        != CASE_COUNT
    ):
        raise RuntimeError(
            "qualification case-count drift"
        )

    matrix = sparse.load_npz(
        CONNECTOME
    ).tocsr()

    if (
        matrix.dtype
        != np.dtype(np.float32)
    ):
        raise RuntimeError(
            "connectome is not float32"
        )

    geometry = (
        build_body_row_geometry(
            connectome=matrix,
            responder_indices=
                RESPONDERS,
            source_indices=
                SOURCES,
        )
    )

    observed_nnz = np.diff(
        geometry[
            "row_offsets"
        ]
    ).astype(
        np.int64
    )

    expected_nnz = np.asarray(
        contract[
            "target"
        ][
            "expected_row_nnz"
        ],
        dtype=np.int64,
    )

    if not np.array_equal(
        observed_nnz,
        expected_nnz,
    ):
        raise RuntimeError(
            "BODY row-NNZ drift"
        )

    expected_positions = np.asarray(
        contract[
            "target"
        ][
            "expected_body_positions"
        ],
        dtype=np.int64,
    )

    if not np.array_equal(
        geometry[
            "body_positions"
        ],
        expected_positions,
    ):
        raise RuntimeError(
            "BODY CSR-position drift"
        )

    union = geometry[
        "presynaptic_union_indices"
    ]

    reference_rows = (
        matrix[
            RESPONDERS,
            :
        ].tocsr()
    )

    mismatches = []

    for case in range(
        CASE_COUNT
    ):
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
                            reference[
                                row
                            ]
                        ),
                    "replay":
                        float(
                            replay[
                                row
                            ]
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

    status = (
        "PASS"
        if len(mismatches) == 0
        else "FAIL"
    )

    report = {
        "schema_version":
            "moscaquant."
            "sq11-dark-forest-replay-qualification-result/v1",

        "experiment":
            "SQ-11",

        "codename":
            "DARK FOREST",

        "status":
            status,

        "neural_execution_performed":
            False,

        "sq11_neural_evidence_inspected":
            False,

        "case_count":
            CASE_COUNT,

        "row_count":
            3,

        "row_case_comparisons":
            CASE_COUNT * 3,

        "mismatch_count":
            len(mismatches),

        "first_mismatches":
            mismatches[:20],

        "connectome": {
            "path":
                str(CONNECTOME),

            "sha256":
                sha256_file(
                    CONNECTOME
                ),
        },

        "geometry": {
            "row_nnz":
                observed_nnz.tolist(),

            "body_positions":
                geometry[
                    "body_positions"
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
                int(
                    len(union)
                ),
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
                sha256_file(
                    CONTRACT
                ),

            "replay_implementation_sha256":
                sha256_file(
                    ROOT
                    / "brain/"
                    "sq11_dark_forest_replay.py"
                ),

            "qualification_implementation_sha256":
                sha256_file(
                    Path(__file__)
                ),

            "instrumentation_sha256":
                sha256_file(
                    ROOT
                    / "brain/"
                    "sq11_dark_forest_instrumentation.py"
                ),
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
            "DARK FOREST replay "
            "qualification FAILED"
        )


if __name__ == "__main__":
    main()
