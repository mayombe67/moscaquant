from __future__ import annotations

import hashlib
import json
import os
import subprocess
import tempfile
from collections import Counter
from pathlib import Path

import numpy as np
from scipy import sparse

from brain.sq05_two_betrayals_runner import CONNECTOME
from brain.sq11_dark_forest_independent_verify import (
    EXPECTED_KEYS,
    verify_evidence_arrays,
)
from brain.sq11_dark_forest_replay_v2 import (
    replay_csr_rows_float32,
)


ROOT = Path(__file__).resolve().parents[1]

EVIDENCE = (
    ROOT
    / "artifacts/experiments/"
    "sq11-dark-forest/"
    "sq11-dark-forest-evidence-v2.npz"
)

RECEIPT = (
    ROOT
    / "artifacts/experiments/"
    "sq11-dark-forest/"
    "sq11-dark-forest-publication-receipt-v2.json"
)

OUTPUT = (
    ROOT
    / "artifacts/experiments/"
    "sq11-dark-forest/"
    "sq11-dark-forest-analysis-v1.json"
)

REPLAY_SOURCE = (
    ROOT
    / "brain/"
    "sq11_dark_forest_replay_v2.py"
)

EXPECTED_EVIDENCE_SHA256 = (
    "cef49b5e581d6c9b2f21aafc701d06e8"
    "d53b0abc03f8453c9fe6c5d19ede9c37"
)

EXPECTED_RECEIPT_SHA256 = (
    "2f0f7aeb6d0183d8dd918abd81563ac1"
    "87eb70e2b3f6ea1559856625bf090eff"
)

EXPECTED_REPLAY_SHA256 = (
    "76245bfab248c0d4bf374da94ad79485f"
    "2e0e386d86707de9e52bad26ff772e5"
)

EXPECTED_EVIDENCE_COMMIT = (
    "06c31e216683025a49db6b2a1e7252aff37addb1"
)

EDGE_NAMES = ("A", "B", "C")

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

DUPLICATE_KEYS = (
    "condition_edge_zeroed",
    "local_effective_activity_pre_synaptic",
    "source_voltage_pre_step",
    "source_spikes_pre_step",
    "source_effective_activity_pre_synaptic",
    "responder_synaptic_p3",
    "responder_voltage_pre_threshold",
    "responder_fired",
    "responder_voltage_post_reset",
    "responder_spikes_post_commit",
)


class AnalysisRefusal(RuntimeError):
    pass


def refuse(message: str) -> None:
    raise AnalysisRefusal(message)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()

    with path.open("rb") as handle:
        for block in iter(
            lambda: handle.read(8 * 1024 * 1024),
            b"",
        ):
            h.update(block)

    return h.hexdigest()


def git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    if result.returncode != 0:
        refuse(
            f"git {' '.join(args)} failed:\n"
            f"{result.stdout}"
        )

    return result.stdout.strip()


def git_bytes(*args: str) -> bytes:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    if result.returncode != 0:
        refuse(
            f"git {' '.join(args)} failed"
        )

    return result.stdout


def verify_frozen_inputs() -> dict:
    if sha256_file(EVIDENCE) != EXPECTED_EVIDENCE_SHA256:
        refuse(
            "SQ-11 evidence SHA drift"
        )

    if sha256_file(RECEIPT) != EXPECTED_RECEIPT_SHA256:
        refuse(
            "SQ-11 receipt SHA drift"
        )

    if sha256_file(REPLAY_SOURCE) != EXPECTED_REPLAY_SHA256:
        refuse(
            "SQ-11 replay-v2 source SHA drift"
        )

    git(
        "cat-file",
        "-e",
        f"{EXPECTED_EVIDENCE_COMMIT}^{{commit}}",
    )

    result = subprocess.run(
        [
            "git",
            "merge-base",
            "--is-ancestor",
            EXPECTED_EVIDENCE_COMMIT,
            "HEAD",
        ],
        cwd=ROOT,
    )

    if result.returncode != 0:
        refuse(
            "HEAD does not descend from "
            "frozen SQ-11 evidence commit"
        )

    evidence_relative = str(
        EVIDENCE.relative_to(ROOT)
    )

    receipt_relative = str(
        RECEIPT.relative_to(ROOT)
    )

    committed_evidence = git_bytes(
        "show",
        f"{EXPECTED_EVIDENCE_COMMIT}:"
        f"{evidence_relative}",
    )

    committed_receipt = git_bytes(
        "show",
        f"{EXPECTED_EVIDENCE_COMMIT}:"
        f"{receipt_relative}",
    )

    if (
        hashlib.sha256(
            committed_evidence
        ).hexdigest()
        != EXPECTED_EVIDENCE_SHA256
    ):
        refuse(
            "frozen evidence commit/byte "
            "binding mismatch"
        )

    if (
        hashlib.sha256(
            committed_receipt
        ).hexdigest()
        != EXPECTED_RECEIPT_SHA256
    ):
        refuse(
            "frozen receipt commit/byte "
            "binding mismatch"
        )

    receipt = json.loads(
        RECEIPT.read_text(
            encoding="utf-8",
        )
    )

    if (
        receipt.get("status")
        != "FROZEN_EXECUTION_COMPLETE"
    ):
        refuse(
            "SQ-11 execution receipt "
            "status drift"
        )

    if (
        receipt.get("work_units_executed")
        != 16
    ):
        refuse(
            "SQ-11 receipt work-unit drift"
        )

    if (
        receipt.get(
            "all_deterministic_duplicate_pairs_exact"
        )
        is not True
    ):
        refuse(
            "SQ-11 receipt duplicate "
            "verification drift"
        )

    independent = receipt.get(
        "independent_verification",
        {},
    )

    if (
        independent.get("pre_publication")
        != "PASS"
        or independent.get("post_publication")
        != "PASS"
        or independent.get(
            "baseline_binding_verified"
        )
        is not True
    ):
        refuse(
            "SQ-11 execution verification "
            "receipt drift"
        )

    if (
        receipt.get("analysis", {}).get(
            "performed"
        )
        is not False
    ):
        refuse(
            "SQ-11 receipt unexpectedly "
            "claims prior analysis"
        )

    return receipt


def load_verified_evidence() -> tuple[
    dict[str, np.ndarray],
    dict,
]:
    with np.load(
        EVIDENCE,
        allow_pickle=False,
    ) as z:
        arrays = {
            key: z[key].copy()
            for key in z.files
        }

    if set(arrays) != set(EXPECTED_KEYS):
        refuse(
            "SQ-11 evidence key-set drift"
        )

    baseline = sparse.load_npz(
        CONNECTOME
    ).tocsr()

    report = verify_evidence_arrays(
        arrays,
        baseline=baseline,
    )

    if report.get("status") != "PASS":
        refuse(
            "SQ-11 independent verifier failed"
        )

    if (
        report.get(
            "baseline_binding_verified"
        )
        is not True
    ):
        refuse(
            "SQ-11 baseline binding failed"
        )

    return arrays, report


def condition_index(
    arrays: dict[str, np.ndarray],
    mask: str,
    replicate: int,
) -> int:
    masks = (
        arrays["condition_mask"]
        .astype(str)
    )

    replicates = (
        arrays["condition_replicate"]
        .astype(int)
    )

    hits = np.flatnonzero(
        (masks == mask)
        & (replicates == replicate)
    )

    if len(hits) != 1:
        refuse(
            "SQ-11 condition lookup failure: "
            f"{mask} r{replicate}"
        )

    return int(hits[0])


def verify_duplicate_pairs(
    arrays: dict[str, np.ndarray],
) -> int:
    comparisons = 0

    for mask in MASKS:
        r1 = condition_index(
            arrays,
            mask,
            1,
        )

        r2 = condition_index(
            arrays,
            mask,
            2,
        )

        for key in DUPLICATE_KEYS:
            if not np.array_equal(
                arrays[key][r1],
                arrays[key][r2],
            ):
                refuse(
                    "SQ-11 post-publication "
                    "duplicate mismatch: "
                    f"{mask} {key}"
                )

            comparisons += 1

    return comparisons


def verify_replay_v2_exact(
    arrays: dict[str, np.ndarray],
) -> dict:
    local = arrays[
        "local_effective_activity_pre_synaptic"
    ]

    observed = arrays[
        "responder_synaptic_p3"
    ]

    zeroed = arrays[
        "condition_edge_zeroed"
    ]

    frame_count = observed.shape[1]

    comparisons = 0

    for frame in range(frame_count):
        replayed = replay_csr_rows_float32(
            local_activity=
                local[:, frame, :],
            row_offsets=
                arrays["row_offsets"],
            row_weights=
                arrays["row_weights"],
            row_union_positions=
                arrays["row_union_positions"],
            body_flat_positions=
                arrays["body_flat_positions"],
            condition_edge_zeroed=
                zeroed,
        )

        expected = observed[
            :,
            frame,
            :,
        ]

        if not np.array_equal(
            replayed,
            expected,
        ):
            mismatch = np.argwhere(
                replayed != expected
            )

            first = mismatch[0]

            refuse(
                "SQ-11 replay-v2 mismatch "
                f"frame={frame} "
                f"condition={int(first[0])} "
                f"row={int(first[1])}"
            )

        comparisons += (
            replayed.shape[0]
            * replayed.shape[1]
        )

    if comparisons != 9216:
        refuse(
            "SQ-11 replay comparison "
            f"count drift: {comparisons}"
        )

    return {
        "status":
            "PASS",
        "exact_float32_comparisons":
            comparisons,
        "mismatch_count":
            0,
    }


def classify_contrast(
    *,
    divergence_exists: bool,
    body_source_exact: bool,
    row_source_exact: bool,
    runtime_delta: np.float64 | None,
    direct_term_f32: np.float32 | None,
) -> tuple[str, float | None]:
    if not divergence_exists:
        return (
            "NO_P3_DIVERGENCE",
            None,
        )

    if (
        not body_source_exact
        or not row_source_exact
    ):
        return (
            "SOURCE_STATE_DIVERGES_"
            "BEFORE_OR_AT_P3",
            None,
        )

    assert runtime_delta is not None
    assert direct_term_f32 is not None

    residual = (
        np.float64(runtime_delta)
        - np.float64(direct_term_f32)
    )

    if residual == 0.0:
        return (
            "DIRECT_TERM_EXACT_FLOAT32",
            0.0,
        )

    return (
        "DIRECT_TERM_WITH_"
        "FLOAT32_ROUNDING_PATH",
        float(residual),
    )


def analyze_contrasts(
    arrays: dict[str, np.ndarray],
) -> list[dict]:
    p3 = arrays[
        "responder_synaptic_p3"
    ]

    source_p2 = arrays[
        "source_effective_activity_pre_synaptic"
    ]

    local_p2 = arrays[
        "local_effective_activity_pre_synaptic"
    ]

    row_offsets = arrays[
        "row_offsets"
    ]

    row_union_positions = arrays[
        "row_union_positions"
    ]

    body_flat_positions = arrays[
        "body_flat_positions"
    ]

    row_weights = arrays[
        "row_weights"
    ]

    body_weights = arrays[
        "body_edge_weight"
    ]

    #
    # The separately stored BODY weights must
    # be identical to the actual CSR entries
    # used by replay-v2.
    #
    csr_body_weights = np.asarray(
        [
            row_weights[
                int(body_flat_positions[i])
            ]
            for i in range(3)
        ],
        dtype=np.float32,
    )

    if not np.array_equal(
        csr_body_weights,
        body_weights,
    ):
        refuse(
            "SQ-11 BODY edge weight "
            "binding mismatch"
        )

    rows = []

    for edge_i, edge_name in enumerate(
        EDGE_NAMES
    ):
        other = [
            i
            for i in range(3)
            if i != edge_i
        ]

        start = int(
            row_offsets[edge_i]
        )

        stop = int(
            row_offsets[edge_i + 1]
        )

        row_positions = (
            row_union_positions[
                start:stop
            ]
        )

        for x in (0, 1):
            for y in (0, 1):
                retained_bits = [0, 0, 0]

                retained_bits[
                    other[0]
                ] = x

                retained_bits[
                    other[1]
                ] = y

                lesioned_bits = (
                    retained_bits.copy()
                )

                lesioned_bits[
                    edge_i
                ] = 1

                retained_mask = "".join(
                    str(v)
                    for v in retained_bits
                )

                lesioned_mask = "".join(
                    str(v)
                    for v in lesioned_bits
                )

                retained_i = condition_index(
                    arrays,
                    retained_mask,
                    1,
                )

                lesioned_i = condition_index(
                    arrays,
                    lesioned_mask,
                    1,
                )

                retained_trace = p3[
                    retained_i,
                    :,
                    edge_i,
                ]

                lesioned_trace = p3[
                    lesioned_i,
                    :,
                    edge_i,
                ]

                divergence = np.flatnonzero(
                    retained_trace
                    != lesioned_trace
                )

                if len(divergence) == 0:
                    classification, residual = (
                        classify_contrast(
                            divergence_exists=False,
                            body_source_exact=True,
                            row_source_exact=True,
                            runtime_delta=None,
                            direct_term_f32=None,
                        )
                    )

                    rows.append({
                        "edge":
                            edge_name,
                        "retained_mask":
                            retained_mask,
                        "lesioned_mask":
                            lesioned_mask,
                        "first_p3_divergence_frame":
                            None,
                        "classification":
                            classification,
                        "rounding_path_residual":
                            residual,
                    })

                    continue

                frame = int(
                    divergence[0]
                )

                body_source_exact = (
                    np.array_equal(
                        source_p2[
                            retained_i,
                            : frame + 1,
                            edge_i,
                        ],
                        source_p2[
                            lesioned_i,
                            : frame + 1,
                            edge_i,
                        ],
                    )
                )

                row_source_exact = (
                    np.array_equal(
                        local_p2[
                            retained_i,
                            : frame + 1,
                            row_positions,
                        ],
                        local_p2[
                            lesioned_i,
                            : frame + 1,
                            row_positions,
                        ],
                    )
                )

                source = np.float32(
                    source_p2[
                        retained_i,
                        frame,
                        edge_i,
                    ]
                )

                weight = np.float32(
                    body_weights[
                        edge_i
                    ]
                )

                direct_term_f32 = np.float32(
                    source
                    * weight
                )

                runtime_delta = (
                    np.float64(
                        retained_trace[
                            frame
                        ]
                    )
                    - np.float64(
                        lesioned_trace[
                            frame
                        ]
                    )
                )

                classification, residual = (
                    classify_contrast(
                        divergence_exists=True,
                        body_source_exact=
                            body_source_exact,
                        row_source_exact=
                            row_source_exact,
                        runtime_delta=
                            runtime_delta,
                        direct_term_f32=
                            direct_term_f32,
                    )
                )

                rows.append({
                    "edge":
                        edge_name,
                    "retained_mask":
                        retained_mask,
                    "lesioned_mask":
                        lesioned_mask,
                    "first_p3_divergence_frame":
                        frame,
                    "body_source_exact_through_p3":
                        body_source_exact,
                    "responder_row_source_exact_through_p3":
                        row_source_exact,
                    "source_p2":
                        float(source),
                    "body_edge_weight_f32":
                        float(weight),
                    "runtime_delta":
                        float(runtime_delta),
                    "direct_term_f32":
                        float(direct_term_f32),
                    "rounding_path_residual":
                        residual,
                    "classification":
                        classification,
                })

    if len(rows) != 12:
        refuse(
            "SQ-11 matched contrast "
            f"count drift: {len(rows)}"
        )

    return rows


def build_result() -> dict:
    receipt = verify_frozen_inputs()

    arrays, verifier = (
        load_verified_evidence()
    )

    duplicate_comparisons = (
        verify_duplicate_pairs(
            arrays
        )
    )

    replay = (
        verify_replay_v2_exact(
            arrays
        )
    )

    contrasts = (
        analyze_contrasts(
            arrays
        )
    )

    counts = Counter(
        row["classification"]
        for row in contrasts
    )

    per_edge = {}

    for edge in EDGE_NAMES:
        subset = [
            row
            for row in contrasts
            if row["edge"] == edge
        ]

        frames = sorted({
            row[
                "first_p3_divergence_frame"
            ]
            for row in subset
            if row[
                "first_p3_divergence_frame"
            ]
            is not None
        })

        classes = sorted({
            row["classification"]
            for row in subset
        })

        residuals = sorted({
            row[
                "rounding_path_residual"
            ]
            for row in subset
            if row[
                "rounding_path_residual"
            ]
            is not None
        })

        per_edge[edge] = {
            "contrast_count":
                len(subset),
            "first_p3_divergence_frames":
                frames,
            "classifications":
                classes,
            "rounding_path_residuals":
                residuals,
        }

    residuals = [
        abs(
            row[
                "rounding_path_residual"
            ]
        )
        for row in contrasts
        if row[
            "rounding_path_residual"
        ]
        is not None
    ]

    analyzer_path = Path(__file__)

    return {
        "schema_version":
            "moscaquant."
            "sq11-dark-forest-analysis/v1",

        "experiment":
            "SQ-11",

        "codename":
            "DARK FOREST",

        "status":
            "ANALYSIS_COMPLETE",

        "provenance": {
            "evidence": {
                "path":
                    str(
                        EVIDENCE.relative_to(
                            ROOT
                        )
                    ),
                "sha256":
                    EXPECTED_EVIDENCE_SHA256,
                "git_commit":
                    EXPECTED_EVIDENCE_COMMIT,
            },

            "execution_receipt": {
                "path":
                    str(
                        RECEIPT.relative_to(
                            ROOT
                        )
                    ),
                "sha256":
                    EXPECTED_RECEIPT_SHA256,
                "status":
                    receipt["status"],
            },

            "replay_v2": {
                "path":
                    str(
                        REPLAY_SOURCE.relative_to(
                            ROOT
                        )
                    ),
                "sha256":
                    EXPECTED_REPLAY_SHA256,
            },

            "analyzer": {
                "path":
                    str(
                        analyzer_path.relative_to(
                            ROOT
                        )
                    ),
                "sha256":
                    sha256_file(
                        analyzer_path
                    ),
                "git_commit":
                    git(
                        "rev-parse",
                        "HEAD",
                    ),
            },
        },

        "verification": {
            "independent_verifier":
                verifier["status"],

            "baseline_binding_verified":
                verifier[
                    "baseline_binding_verified"
                ],

            "post_publication_duplicate_field_comparisons":
                duplicate_comparisons,

            "replay_v2":
                replay,
        },

        "matched_contrast_count":
            12,

        "classification_counts":
            dict(
                sorted(
                    counts.items()
                )
            ),

        "per_edge":
            per_edge,

        "max_absolute_rounding_path_residual":
            max(residuals)
            if residuals
            else None,

        "contrasts":
            contrasts,

        "interpretation_boundary": {
            "source_state_divergence_observed":
                any(
                    row["classification"]
                    == (
                        "SOURCE_STATE_DIVERGES_"
                        "BEFORE_OR_AT_P3"
                    )
                    for row in contrasts
                ),

            "background_dependence_observed_at_first_p3_divergence":
                any(
                    len(
                        per_edge[edge][
                            "first_p3_divergence_frames"
                        ]
                    ) != 1
                    or len(
                        per_edge[edge][
                            "classifications"
                        ]
                    ) != 1
                    for edge in EDGE_NAMES
                ),

            "claim_scope":
                (
                    "Frozen SQ-11 computational "
                    "endpoint only; no biological "
                    "mechanism claim."
                ),
        },

        "neural_execution_performed":
            False,

        "analysis_only":
            True,
    }


def publish_result(
    payload: dict,
) -> str:
    if OUTPUT.exists():
        refuse(
            "SQ-11 analysis result "
            "already exists; overwrite forbidden"
        )

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    data = (
        json.dumps(
            payload,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    ).encode("utf-8")

    fd, temporary = tempfile.mkstemp(
        prefix=".sq11-analysis-",
        dir=OUTPUT.parent,
    )

    temp_path = Path(temporary)

    try:
        with os.fdopen(
            fd,
            "wb",
        ) as handle:
            handle.write(data)
            handle.flush()
            os.fsync(
                handle.fileno()
            )

        os.link(
            temp_path,
            OUTPUT,
        )

        directory_fd = os.open(
            OUTPUT.parent,
            os.O_RDONLY,
        )

        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)

    finally:
        try:
            temp_path.unlink()
        except FileNotFoundError:
            pass

    return sha256_file(
        OUTPUT
    )


def main() -> None:
    result = build_result()

    output_sha = publish_result(
        result
    )

    print(
        "SQ-11 DARK FOREST ANALYSIS COMPLETE"
    )

    print(
        "matched contrasts:",
        result[
            "matched_contrast_count"
        ],
    )

    print(
        "classification counts:",
        result[
            "classification_counts"
        ],
    )

    print(
        "A:",
        result["per_edge"]["A"],
    )

    print(
        "B:",
        result["per_edge"]["B"],
    )

    print(
        "C:",
        result["per_edge"]["C"],
    )

    print(
        "replay comparisons:",
        result[
            "verification"
        ][
            "replay_v2"
        ][
            "exact_float32_comparisons"
        ],
    )

    print(
        "replay mismatches:",
        result[
            "verification"
        ][
            "replay_v2"
        ][
            "mismatch_count"
        ],
    )

    print(
        "neural execution performed:",
        result[
            "neural_execution_performed"
        ],
    )

    print(
        "analysis sha256:",
        output_sha,
    )


if __name__ == "__main__":
    main()
