from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import numpy as np

from brain.visual_transduction import (
    VisualTransductionConfig,
)


ROOT = Path(__file__).resolve().parents[1]

PREREG = (
    ROOT
    / "docs/experiments/"
    "sq13-surface-tension-preregistration.md"
)

EVIDENCE = (
    ROOT
    / "artifacts/experiments/"
    "sq11-dark-forest/"
    "sq11-dark-forest-evidence-v2.npz"
)

SQ12_GATE = (
    ROOT
    / "artifacts/experiments/"
    "sq12-resonance-cascade/"
    "sq12-transmission-gate-audit-v1.json"
)

SQ12_VERIFY = (
    ROOT
    / "artifacts/experiments/"
    "sq12-resonance-cascade/"
    "sq12-transmission-gate-verification-v1.json"
)

SQ12_SEAL = (
    ROOT
    / "artifacts/experiments/"
    "sq12-resonance-cascade/"
    "sq12-resonance-cascade-result-seal-v1.json"
)

VISUAL_RUNTIME = (
    ROOT
    / "brain/"
    "visual_transduction.py"
)

PHYSIOLOGY_RUNTIME = (
    ROOT
    / "brain/"
    "physiology_constrained_visual_transduction.py"
)

OUTPUT = (
    ROOT
    / "artifacts/experiments/"
    "sq13-surface-tension/"
    "sq13-surface-tension-analysis-v1.json"
)

EXPECTED_SHA256 = {
    "preregistration":
        "21f31896acef9b9b14517ef10e7d7cb1f80719ececeb8c8b7238cb3a5af28813",
    "evidence":
        (
            "cef49b5e581d6c9b2f21aafc701d06e"
            "8d53b0abc03f8453c9fe6c5d19ede9c37"
        ),
    "sq12_gate":
        (
            "916cb99c1bec589467c6ab6fbff79289"
            "d0d0d52c6e2110e95b4d7964f24dd065"
        ),
    "sq12_verification":
        (
            "8cf58f322a397e6a5bd0798d64c45066"
            "1655f0e2afa9b49fed000c93c716c353"
        ),
    "sq12_seal":
        (
            "c67db35a6fec7adc5855f9310651caa3"
            "bd731c63647696814c59366cf27b0faf"
        ),
    "visual_runtime":
        "015cc699f49e16bb59f6e7e5f04f92cca7bfc1a3c7057e73fe54398c755831f6",
    "physiology_runtime":
        "bf754a29155ade789349fbdfc3c579f1b2c8dbea3c63804f2cf3d858d0a2f605",
}

THRESHOLD = 1.0

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

EXPECTED_CONDITION_IDS = tuple(
    f"sq11:{mask}:r{replicate}"
    for mask in MASKS
    for replicate in (1, 2)
)

BODY_SOURCES = np.asarray(
    [65084, 128590, 135589],
    dtype=np.int64,
)

BODY_RESPONDERS = np.asarray(
    [137122, 317, 126002],
    dtype=np.int64,
)

CONTRASTS = (
    {
        "body": "A",
        "body_axis": 0,
        "source": 65084,
        "responder": 137122,
        "retained": "000",
        "lesioned": "100",
    },
    {
        "body": "A",
        "body_axis": 0,
        "source": 65084,
        "responder": 137122,
        "retained": "001",
        "lesioned": "101",
    },
    {
        "body": "A",
        "body_axis": 0,
        "source": 65084,
        "responder": 137122,
        "retained": "010",
        "lesioned": "110",
    },
    {
        "body": "A",
        "body_axis": 0,
        "source": 65084,
        "responder": 137122,
        "retained": "011",
        "lesioned": "111",
    },
    {
        "body": "B",
        "body_axis": 1,
        "source": 128590,
        "responder": 317,
        "retained": "000",
        "lesioned": "010",
    },
    {
        "body": "B",
        "body_axis": 1,
        "source": 128590,
        "responder": 317,
        "retained": "001",
        "lesioned": "011",
    },
    {
        "body": "B",
        "body_axis": 1,
        "source": 128590,
        "responder": 317,
        "retained": "100",
        "lesioned": "110",
    },
    {
        "body": "B",
        "body_axis": 1,
        "source": 128590,
        "responder": 317,
        "retained": "101",
        "lesioned": "111",
    },
    {
        "body": "C",
        "body_axis": 2,
        "source": 135589,
        "responder": 126002,
        "retained": "000",
        "lesioned": "001",
    },
    {
        "body": "C",
        "body_axis": 2,
        "source": 135589,
        "responder": 126002,
        "retained": "010",
        "lesioned": "011",
    },
    {
        "body": "C",
        "body_axis": 2,
        "source": 135589,
        "responder": 126002,
        "retained": "100",
        "lesioned": "101",
    },
    {
        "body": "C",
        "body_axis": 2,
        "source": 135589,
        "responder": 126002,
        "retained": "110",
        "lesioned": "111",
    },
)

FIELDS = (
    "responder_voltage_pre_threshold",
    "responder_fired",
    "responder_spikes_post_commit",
)


class SurfaceTensionError(RuntimeError):
    pass


def refuse(message: str) -> None:
    raise SurfaceTensionError(message)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()

    with path.open("rb") as handle:
        for block in iter(
            lambda: handle.read(8 * 1024 * 1024),
            b"",
        ):
            h.update(block)

    return h.hexdigest()


def verify_sha(
    name: str,
    path: Path,
) -> str:
    if not path.is_file():
        refuse(
            f"missing {name}: {path}"
        )

    observed = sha256_file(path)
    expected = EXPECTED_SHA256[name]

    if observed != expected:
        refuse(
            f"{name} SHA drift: "
            f"{observed} != {expected}"
        )

    return observed


def load_json(path: Path) -> dict:
    return json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )


def verify_inherited_sq12() -> None:
    gate = load_json(SQ12_GATE)

    if (
        gate.get("classification")
        != "TRANSMISSION_GATE_CLOSED_192_FRAMES"
    ):
        refuse(
            "SQ-12 gate classification drift"
        )

    if (
        gate.get(
            "causal_gate",
            {},
        ).get("closed")
        is not True
    ):
        refuse(
            "SQ-12 gate is not closed"
        )

    if (
        gate.get(
            "neural_execution_performed"
        )
        is not False
    ):
        refuse(
            "SQ-12 gate execution boundary drift"
        )

    verification = load_json(
        SQ12_VERIFY
    )

    if (
        verification.get("status")
        != "INDEPENDENT_VERIFICATION_PASS"
    ):
        refuse(
            "SQ-12 independent verification drift"
        )

    if (
        verification.get(
            "verified_classification"
        )
        != "TRANSMISSION_GATE_CLOSED_192_FRAMES"
    ):
        refuse(
            "SQ-12 verified classification drift"
        )

    seal = load_json(SQ12_SEAL)

    if (
        seal.get("status")
        != "SEALED_DEDUCTIVE_CLOSURE"
    ):
        refuse(
            "SQ-12 result seal status drift"
        )

    if (
        seal.get("classification")
        != "TRANSMISSION_GATE_CLOSED_192_FRAMES"
    ):
        refuse(
            "SQ-12 result seal classification drift"
        )

    if (
        seal.get(
            "neural_execution_performed_by_sq12"
        )
        is not False
    ):
        refuse(
            "SQ-12 result seal execution drift"
        )


def verify_threshold() -> float:
    threshold = float(
        VisualTransductionConfig().threshold
    )

    if threshold != THRESHOLD:
        refuse(
            "frozen threshold drift: "
            f"{threshold} != {THRESHOLD}"
        )

    return threshold


def canonicalize_field(
    masks: np.ndarray,
    replicates: np.ndarray,
    values: np.ndarray,
    field_name: str,
) -> dict[str, np.ndarray]:
    result: dict[str, np.ndarray] = {}

    for mask in MASKS:
        hits = np.flatnonzero(
            masks == mask
        )

        if len(hits) != 2:
            refuse(
                f"{field_name}: "
                f"{mask} does not have "
                "exactly two replicates"
            )

        by_rep: dict[
            int,
            np.ndarray,
        ] = {}

        for index in hits:
            rep = int(
                replicates[index]
            )

            if rep in by_rep:
                refuse(
                    f"{field_name}: "
                    f"duplicate {mask} r{rep}"
                )

            by_rep[rep] = np.asarray(
                values[index]
            )

        if set(by_rep) != {1, 2}:
            refuse(
                f"{field_name}: "
                f"{mask} replicate-set drift"
            )

        if not np.array_equal(
            by_rep[1],
            by_rep[2],
        ):
            refuse(
                f"{field_name}: "
                f"{mask} deterministic "
                "replicate mismatch"
            )

        result[mask] = np.array(
            by_rep[1],
            copy=True,
        )

    return result


def load_and_validate_evidence(
    threshold: float,
) -> dict[
    str,
    dict[str, np.ndarray],
]:
    with np.load(
        EVIDENCE,
        allow_pickle=False,
    ) as z:
        required = {
            "condition_id",
            "condition_mask",
            "condition_replicate",
            "source_indices",
            "responder_indices",
            *FIELDS,
        }

        missing = required - set(z.files)

        if missing:
            refuse(
                "SQ-11 evidence missing "
                f"required fields: {sorted(missing)}"
            )

        condition_ids = tuple(
            np.asarray(
                z["condition_id"]
            ).astype(str)
        )

        if (
            condition_ids
            != EXPECTED_CONDITION_IDS
        ):
            refuse(
                "SQ-11 canonical condition "
                "order drift"
            )

        masks = np.asarray(
            z["condition_mask"]
        ).astype(str)

        replicates = np.asarray(
            z["condition_replicate"],
            dtype=np.int64,
        )

        if not np.array_equal(
            np.asarray(
                z["source_indices"],
                dtype=np.int64,
            ),
            BODY_SOURCES,
        ):
            refuse(
                "SQ-11 BODY source identity drift"
            )

        if not np.array_equal(
            np.asarray(
                z["responder_indices"],
                dtype=np.int64,
            ),
            BODY_RESPONDERS,
        ):
            refuse(
                "SQ-11 BODY responder "
                "identity drift"
            )

        voltage = np.asarray(
            z[
                "responder_voltage_pre_threshold"
            ]
        )

        fired = np.asarray(
            z["responder_fired"]
        )

        spikes = np.asarray(
            z[
                "responder_spikes_post_commit"
            ]
        )

        expected_shape = (
            16,
            192,
            3,
        )

        for name, value in (
            (
                "responder_voltage_pre_threshold",
                voltage,
            ),
            (
                "responder_fired",
                fired,
            ),
            (
                "responder_spikes_post_commit",
                spikes,
            ),
        ):
            if value.shape != expected_shape:
                refuse(
                    f"{name} shape drift: "
                    f"{value.shape}"
                )

        if voltage.dtype != np.float32:
            refuse(
                "P5 dtype drift: "
                f"{voltage.dtype}"
            )

        if fired.dtype != np.uint8:
            refuse(
                "P6 dtype drift: "
                f"{fired.dtype}"
            )

        if spikes.dtype != np.uint8:
            refuse(
                "P7 dtype drift: "
                f"{spikes.dtype}"
            )

        if not np.all(
            np.isfinite(voltage)
        ):
            refuse(
                "non-finite P5 evidence"
            )

        if not np.all(
            np.isin(
                fired,
                (0, 1),
            )
        ):
            refuse(
                "P6 is not binary"
            )

        if not np.all(
            np.isin(
                spikes,
                (0, 1),
            )
        ):
            refuse(
                "P7 is not binary"
            )

        expected_fired = (
            voltage
            >= np.float32(threshold)
        ).astype(np.uint8)

        if not np.array_equal(
            fired,
            expected_fired,
        ):
            mismatch = np.argwhere(
                fired
                != expected_fired
            )[0]

            refuse(
                "P5/P6 threshold consistency "
                "failure at "
                f"{tuple(int(x) for x in mismatch)}"
            )

        if not np.array_equal(
            fired,
            spikes,
        ):
            mismatch = np.argwhere(
                fired
                != spikes
            )[0]

            refuse(
                "P6/P7 consistency failure at "
                f"{tuple(int(x) for x in mismatch)}"
            )

        canonical = {
            field: canonicalize_field(
                masks,
                replicates,
                np.asarray(z[field]),
                field,
            )
            for field in FIELDS
        }

    return canonical


def side_of_threshold(
    value: float,
    threshold: float,
) -> str:
    if value < threshold:
        return "BELOW"

    if value > threshold:
        return "ABOVE"

    return "AT"


def analyze_canonical(
    canonical: dict[
        str,
        dict[str, np.ndarray],
    ],
    *,
    threshold: float = THRESHOLD,
) -> dict:
    voltage = canonical[
        "responder_voltage_pre_threshold"
    ]

    fired = canonical[
        "responder_fired"
    ]

    spikes = canonical[
        "responder_spikes_post_commit"
    ]

    contrast_results = []
    contradiction_count = 0
    total_divergent_frames = 0
    candidate_primary = None

    for ordinal, contrast in enumerate(
        CONTRASTS
    ):
        axis = int(
            contrast["body_axis"]
        )

        retained_mask = str(
            contrast["retained"]
        )

        lesioned_mask = str(
            contrast["lesioned"]
        )

        retained_p5 = np.asarray(
            voltage[
                retained_mask
            ][:, axis],
            dtype=np.float32,
        )

        lesioned_p5 = np.asarray(
            voltage[
                lesioned_mask
            ][:, axis],
            dtype=np.float32,
        )

        retained_p6 = np.asarray(
            fired[
                retained_mask
            ][:, axis],
            dtype=np.uint8,
        )

        lesioned_p6 = np.asarray(
            fired[
                lesioned_mask
            ][:, axis],
            dtype=np.uint8,
        )

        retained_p7 = np.asarray(
            spikes[
                retained_mask
            ][:, axis],
            dtype=np.uint8,
        )

        lesioned_p7 = np.asarray(
            spikes[
                lesioned_mask
            ][:, axis],
            dtype=np.uint8,
        )

        p6_mismatch_frames = np.flatnonzero(
            retained_p6
            != lesioned_p6
        )

        p7_mismatch_frames = np.flatnonzero(
            retained_p7
            != lesioned_p7
        )

        if (
            len(p6_mismatch_frames)
            or len(p7_mismatch_frames)
        ):
            contradiction_count += 1

        divergent_frames = np.flatnonzero(
            retained_p5
            != lesioned_p5
        )

        total_divergent_frames += int(
            len(divergent_frames)
        )

        entry = {
            "contrast_ordinal":
                ordinal,
            "body":
                contrast["body"],
            "source":
                int(contrast["source"]),
            "responder":
                int(contrast["responder"]),
            "retained_mask":
                retained_mask,
            "lesioned_mask":
                lesioned_mask,
            "p6_mismatch_count":
                int(
                    len(
                        p6_mismatch_frames
                    )
                ),
            "p7_mismatch_count":
                int(
                    len(
                        p7_mismatch_frames
                    )
                ),
            "p5_divergent_frame_count":
                int(
                    len(
                        divergent_frames
                    )
                ),
            "first_p5_divergent_frame":
                None,
            "last_p5_divergent_frame":
                None,
            "maximum_absolute_p5_difference":
                None,
            "minimum_decision_boundary_distance":
                None,
            "minimum_margin_frame":
                None,
            "minimum_margin_retained_side":
                None,
            "minimum_margin_lesioned_side":
                None,
        }

        if len(divergent_frames):
            first_frame = int(
                divergent_frames[0]
            )

            last_frame = int(
                divergent_frames[-1]
            )

            retained64 = retained_p5[
                divergent_frames
            ].astype(np.float64)

            lesioned64 = lesioned_p5[
                divergent_frames
            ].astype(np.float64)

            differences = np.abs(
                retained64
                - lesioned64
            )

            retained_distance = np.abs(
                retained64
                - float(threshold)
            )

            lesioned_distance = np.abs(
                lesioned64
                - float(threshold)
            )

            margins = np.minimum(
                retained_distance,
                lesioned_distance,
            )

            minimum_local_index = int(
                np.argmin(margins)
            )

            minimum_frame = int(
                divergent_frames[
                    minimum_local_index
                ]
            )

            minimum_margin = float(
                margins[
                    minimum_local_index
                ]
            )

            entry.update(
                {
                    "first_p5_divergent_frame":
                        first_frame,
                    "last_p5_divergent_frame":
                        last_frame,
                    "maximum_absolute_p5_difference":
                        float(
                            np.max(
                                differences
                            )
                        ),
                    "minimum_decision_boundary_distance":
                        minimum_margin,
                    "minimum_margin_frame":
                        minimum_frame,
                    "minimum_margin_retained_side":
                        side_of_threshold(
                            float(
                                retained_p5[
                                    minimum_frame
                                ]
                            ),
                            threshold,
                        ),
                    "minimum_margin_lesioned_side":
                        side_of_threshold(
                            float(
                                lesioned_p5[
                                    minimum_frame
                                ]
                            ),
                            threshold,
                        ),
                }
            )

            candidate = {
                "contrast_ordinal":
                    ordinal,
                "body":
                    contrast["body"],
                "source":
                    int(
                        contrast["source"]
                    ),
                "responder":
                    int(
                        contrast["responder"]
                    ),
                "retained_mask":
                    retained_mask,
                "lesioned_mask":
                    lesioned_mask,
                "frame":
                    minimum_frame,
                "retained_p5":
                    float(
                        retained_p5[
                            minimum_frame
                        ]
                    ),
                "lesioned_p5":
                    float(
                        lesioned_p5[
                            minimum_frame
                        ]
                    ),
                "retained_fired":
                    int(
                        retained_p6[
                            minimum_frame
                        ]
                    ),
                "lesioned_fired":
                    int(
                        lesioned_p6[
                            minimum_frame
                        ]
                    ),
                "absolute_p5_difference":
                    float(
                        abs(
                            float(
                                retained_p5[
                                    minimum_frame
                                ]
                            )
                            - float(
                                lesioned_p5[
                                    minimum_frame
                                ]
                            )
                        )
                    ),
                "decision_boundary_distance":
                    minimum_margin,
                "retained_side":
                    side_of_threshold(
                        float(
                            retained_p5[
                                minimum_frame
                            ]
                        ),
                        threshold,
                    ),
                "lesioned_side":
                    side_of_threshold(
                        float(
                            lesioned_p5[
                                minimum_frame
                            ]
                        ),
                        threshold,
                    ),
            }

            if (
                candidate_primary is None
                or minimum_margin
                < candidate_primary[
                    "decision_boundary_distance"
                ]
            ):
                candidate_primary = candidate

        contrast_results.append(entry)

    body_results = {}

    for body in ("A", "B", "C"):
        members = [
            item
            for item in contrast_results
            if item["body"] == body
        ]

        divergent_members = [
            item
            for item in members
            if (
                item[
                    "p5_divergent_frame_count"
                ]
                > 0
            )
        ]

        if divergent_members:
            min_margin = min(
                float(
                    item[
                        "minimum_decision_boundary_distance"
                    ]
                )
                for item
                in divergent_members
            )

            max_delta = max(
                float(
                    item[
                        "maximum_absolute_p5_difference"
                    ]
                )
                for item
                in divergent_members
            )
        else:
            min_margin = None
            max_delta = None

        body_results[body] = {
            "contrast_count":
                len(members),
            "p5_divergent_frame_count":
                int(
                    sum(
                        item[
                            "p5_divergent_frame_count"
                        ]
                        for item in members
                    )
                ),
            "minimum_decision_boundary_distance":
                min_margin,
            "maximum_absolute_p5_difference":
                max_delta,
        }

    if contradiction_count:
        classification = (
            "TRANSMISSION_GATE_CONTRADICTION"
        )
        primary_endpoint = None
        scale_separation = None

    elif total_divergent_frames == 0:
        classification = (
            "NO_P5_PERTURBATION"
        )
        primary_endpoint = None
        scale_separation = None

    else:
        if candidate_primary is None:
            refuse(
                "internal primary-endpoint failure"
            )

        primary_endpoint = (
            candidate_primary
        )

        margin = float(
            candidate_primary[
                "decision_boundary_distance"
            ]
        )

        if margin == 0.0:
            classification = (
                "GATE_TOUCHES_DECISION_BOUNDARY"
            )
        elif margin > 0.0:
            classification = (
                "GATE_CLOSED_WITH_"
                "POSITIVE_DECISION_MARGIN"
            )
        else:
            refuse(
                "negative decision margin"
            )

        delta = float(
            candidate_primary[
                "absolute_p5_difference"
            ]
        )

        if delta == 0.0:
            refuse(
                "primary endpoint has "
                "zero P5 difference"
            )

        scale_separation = (
            margin / delta
        )

    return {
        "classification":
            classification,
        "threshold":
            float(threshold),
        "matched_contrast_count":
            len(CONTRASTS),
        "contradictory_contrast_count":
            contradiction_count,
        "total_p5_divergent_frames":
            total_divergent_frames,
        "primary_endpoint":
            primary_endpoint,
        "scale_separation":
            scale_separation,
        "by_body":
            body_results,
        "contrasts":
            contrast_results,
    }


def current_git_head() -> str:
    return subprocess.check_output(
        [
            "git",
            "rev-parse",
            "HEAD",
        ],
        cwd=ROOT,
        text=True,
    ).strip()


def main() -> None:
    if OUTPUT.exists():
        refuse(
            "SQ-13 analysis artifact "
            "already exists"
        )

    observed_sha = {
        "preregistration":
            verify_sha(
                "preregistration",
                PREREG,
            ),
        "evidence":
            verify_sha(
                "evidence",
                EVIDENCE,
            ),
        "sq12_gate":
            verify_sha(
                "sq12_gate",
                SQ12_GATE,
            ),
        "sq12_verification":
            verify_sha(
                "sq12_verification",
                SQ12_VERIFY,
            ),
        "sq12_seal":
            verify_sha(
                "sq12_seal",
                SQ12_SEAL,
            ),
        "visual_runtime":
            verify_sha(
                "visual_runtime",
                VISUAL_RUNTIME,
            ),
        "physiology_runtime":
            verify_sha(
                "physiology_runtime",
                PHYSIOLOGY_RUNTIME,
            ),
    }

    verify_inherited_sq12()

    threshold = verify_threshold()

    #
    # Evidence is first opened only after
    # all frozen provenance/runtime gates
    # above have passed.
    #
    canonical = (
        load_and_validate_evidence(
            threshold
        )
    )

    result = analyze_canonical(
        canonical,
        threshold=threshold,
    )

    payload = {
        "schema_version":
            (
                "moscaquant."
                "sq13-surface-tension-analysis/v1"
            ),
        "experiment":
            "SQ-13",
        "codename":
            "SURFACE TENSION",
        "status":
            "ANALYSIS_COMPLETE",
        "analysis_class":
            "SEALED_EVIDENCE_DECISION_BOUNDARY_AUDIT",
        "neural_execution_performed":
            False,
        "binding_commit":
            current_git_head(),
        "analyzer_sha256":
            sha256_file(
                Path(__file__)
            ),
        "provenance_sha256":
            observed_sha,
        "result":
            result,
        "interpretation_boundary": (
            "Observed stored-state distance "
            "to the frozen firing threshold "
            "only. This analysis does not "
            "estimate the intervention needed "
            "to cross that threshold and does "
            "not assume linear scaling."
        ),
        "claim_boundary": (
            "Frozen MoscaQuant computational "
            "model and stored 192-frame SQ-11 "
            "evidence only; no biological, "
            "behavioral, cognitive, market, "
            "prediction, or financial claim."
        ),
    }

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT.write_text(
        json.dumps(
            payload,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    print(
        "SQ-13 SURFACE TENSION "
        "ANALYSIS COMPLETE"
    )

    print(
        "classification:",
        result["classification"],
    )

    print(
        "matched contrasts:",
        result[
            "matched_contrast_count"
        ],
    )

    print(
        "contradictory contrasts:",
        result[
            "contradictory_contrast_count"
        ],
    )

    print(
        "P5-divergent frames:",
        result[
            "total_p5_divergent_frames"
        ],
    )

    primary = result[
        "primary_endpoint"
    ]

    if primary is not None:
        print(
            "primary BODY:",
            primary["body"],
        )
        print(
            "primary contrast:",
            (
                f'{primary["retained_mask"]}'
                " -> "
                f'{primary["lesioned_mask"]}'
            ),
        )
        print(
            "primary frame:",
            primary["frame"],
        )
        print(
            "retained P5:",
            primary["retained_p5"],
        )
        print(
            "lesioned P5:",
            primary["lesioned_p5"],
        )
        print(
            "absolute P5 delta:",
            primary[
                "absolute_p5_difference"
            ],
        )
        print(
            "decision-boundary distance:",
            primary[
                "decision_boundary_distance"
            ],
        )
        print(
            "scale separation:",
            result[
                "scale_separation"
            ],
        )

    print(
        "neural execution:",
        payload[
            "neural_execution_performed"
        ],
    )

    print(
        "output sha256:",
        sha256_file(OUTPUT),
    )


if __name__ == "__main__":
    main()
