from __future__ import annotations

import hashlib
import json
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

SQ12_SEAL = (
    ROOT
    / "artifacts/experiments/"
    "sq12-resonance-cascade/"
    "sq12-resonance-cascade-result-seal-v1.json"
)

ANALYSIS = (
    ROOT
    / "artifacts/experiments/"
    "sq13-surface-tension/"
    "sq13-surface-tension-analysis-v1.json"
)

VISUAL_RUNTIME = (
    ROOT
    / "brain/"
    "visual_transduction.py"
)

OUTPUT = (
    ROOT
    / "artifacts/experiments/"
    "sq13-surface-tension/"
    "sq13-surface-tension-verification-v1.json"
)

EXPECTED_SHA256 = {
    "preregistration":
        "21f31896acef9b9b14517ef10e7d7cb1f80719ececeb8c8b7238cb3a5af28813",
    "visual_runtime":
        "015cc699f49e16bb59f6e7e5f04f92cca7bfc1a3c7057e73fe54398c755831f6",
    "evidence":
        (
            "cef49b5e581d6c9b2f21aafc701d06e"
            "8d53b0abc03f8453c9fe6c5d19ede9c37"
        ),
    "sq12_seal":
        (
            "c67db35a6fec7adc5855f9310651caa3"
            "bd731c63647696814c59366cf27b0faf"
        ),
    "analysis":
        (
            "85cf6ec5d47c0571cacc435933e54b8c"
            "c6fcdf8bc54f6959731cd3052565b2d0"
        ),
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

EXPECTED_IDS = tuple(
    f"sq11:{mask}:r{rep}"
    for mask in MASKS
    for rep in (1, 2)
)

SOURCES = np.asarray(
    [65084, 128590, 135589],
    dtype=np.int64,
)

RESPONDERS = np.asarray(
    [137122, 317, 126002],
    dtype=np.int64,
)

#
# Independently restated from the frozen
# SQ-13 preregistration.
#
CONTRASTS = (
    ("A", 0, 65084, 137122, "000", "100"),
    ("A", 0, 65084, 137122, "001", "101"),
    ("A", 0, 65084, 137122, "010", "110"),
    ("A", 0, 65084, 137122, "011", "111"),
    ("B", 1, 128590, 317, "000", "010"),
    ("B", 1, 128590, 317, "001", "011"),
    ("B", 1, 128590, 317, "100", "110"),
    ("B", 1, 128590, 317, "101", "111"),
    ("C", 2, 135589, 126002, "000", "001"),
    ("C", 2, 135589, 126002, "010", "011"),
    ("C", 2, 135589, 126002, "100", "101"),
    ("C", 2, 135589, 126002, "110", "111"),
)


class VerificationError(RuntimeError):
    pass


def refuse(message: str) -> None:
    raise VerificationError(message)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(8 * 1024 * 1024),
            b"",
        ):
            h.update(chunk)

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


def canonical_field(
    masks: np.ndarray,
    reps: np.ndarray,
    array: np.ndarray,
    name: str,
) -> dict[str, np.ndarray]:
    out = {}

    for mask in MASKS:
        positions = np.flatnonzero(
            masks == mask
        )

        if len(positions) != 2:
            refuse(
                f"{name}: {mask} "
                "replicate-count drift"
            )

        found = {}

        for position in positions:
            rep = int(
                reps[position]
            )

            if rep in found:
                refuse(
                    f"{name}: duplicate "
                    f"{mask} r{rep}"
                )

            found[rep] = np.asarray(
                array[position]
            )

        if set(found) != {1, 2}:
            refuse(
                f"{name}: replicate-set drift"
            )

        if not np.array_equal(
            found[1],
            found[2],
        ):
            refuse(
                f"{name}: deterministic "
                f"duplicate mismatch at {mask}"
            )

        out[mask] = np.array(
            found[1],
            copy=True,
        )

    return out


def load_evidence():
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
            "responder_voltage_pre_threshold",
            "responder_fired",
            "responder_spikes_post_commit",
        }

        missing = required - set(z.files)

        if missing:
            refuse(
                f"missing evidence fields: "
                f"{sorted(missing)}"
            )

        ids = tuple(
            np.asarray(
                z["condition_id"]
            ).astype(str)
        )

        if ids != EXPECTED_IDS:
            refuse(
                "canonical condition-order drift"
            )

        if not np.array_equal(
            np.asarray(
                z["source_indices"],
                dtype=np.int64,
            ),
            SOURCES,
        ):
            refuse(
                "BODY source identity drift"
            )

        if not np.array_equal(
            np.asarray(
                z["responder_indices"],
                dtype=np.int64,
            ),
            RESPONDERS,
        ):
            refuse(
                "BODY responder identity drift"
            )

        masks = np.asarray(
            z["condition_mask"]
        ).astype(str)

        reps = np.asarray(
            z["condition_replicate"],
            dtype=np.int64,
        )

        p5 = np.asarray(
            z[
                "responder_voltage_pre_threshold"
            ]
        )

        p6 = np.asarray(
            z["responder_fired"]
        )

        p7 = np.asarray(
            z[
                "responder_spikes_post_commit"
            ]
        )

        if p5.dtype != np.float32:
            refuse(
                f"P5 dtype drift: {p5.dtype}"
            )

        if p6.dtype != np.uint8:
            refuse(
                f"P6 dtype drift: {p6.dtype}"
            )

        if p7.dtype != np.uint8:
            refuse(
                f"P7 dtype drift: {p7.dtype}"
            )

        if p5.shape != (16, 192, 3):
            refuse(
                f"P5 shape drift: {p5.shape}"
            )

        if p6.shape != (16, 192, 3):
            refuse(
                f"P6 shape drift: {p6.shape}"
            )

        if p7.shape != (16, 192, 3):
            refuse(
                f"P7 shape drift: {p7.shape}"
            )

        if not np.all(
            np.isfinite(p5)
        ):
            refuse(
                "non-finite P5 evidence"
            )

        expected_firing = (
            p5
            >= np.float32(THRESHOLD)
        ).astype(np.uint8)

        if not np.array_equal(
            p6,
            expected_firing,
        ):
            refuse(
                "P5/P6 threshold inconsistency"
            )

        if not np.array_equal(
            p6,
            p7,
        ):
            refuse(
                "P6/P7 inconsistency"
            )

        return {
            "p5": canonical_field(
                masks,
                reps,
                p5,
                "P5",
            ),
            "p6": canonical_field(
                masks,
                reps,
                p6,
                "P6",
            ),
            "p7": canonical_field(
                masks,
                reps,
                p7,
                "P7",
            ),
        }


def derive_scalar(canonical):
    total_divergent = 0
    contradictory = 0

    per_body = {
        "A": {
            "divergent": 0,
            "min_margin": None,
            "max_delta": None,
        },
        "B": {
            "divergent": 0,
            "min_margin": None,
            "max_delta": None,
        },
        "C": {
            "divergent": 0,
            "min_margin": None,
            "max_delta": None,
        },
    }

    primary = None

    for ordinal, (
        body,
        axis,
        source,
        responder,
        retained_mask,
        lesioned_mask,
    ) in enumerate(CONTRASTS):

        local_contradiction = False

        for frame in range(192):
            retained_fired = int(
                canonical["p6"][
                    retained_mask
                ][frame, axis]
            )

            lesioned_fired = int(
                canonical["p6"][
                    lesioned_mask
                ][frame, axis]
            )

            retained_spike = int(
                canonical["p7"][
                    retained_mask
                ][frame, axis]
            )

            lesioned_spike = int(
                canonical["p7"][
                    lesioned_mask
                ][frame, axis]
            )

            if (
                retained_fired
                != lesioned_fired
                or retained_spike
                != lesioned_spike
            ):
                local_contradiction = True

            retained_value = float(
                canonical["p5"][
                    retained_mask
                ][frame, axis]
            )

            lesioned_value = float(
                canonical["p5"][
                    lesioned_mask
                ][frame, axis]
            )

            if (
                retained_value
                == lesioned_value
            ):
                continue

            total_divergent += 1

            per_body[body][
                "divergent"
            ] += 1

            delta = abs(
                retained_value
                - lesioned_value
            )

            margin = min(
                abs(
                    retained_value
                    - THRESHOLD
                ),
                abs(
                    lesioned_value
                    - THRESHOLD
                ),
            )

            current_min = per_body[
                body
            ]["min_margin"]

            if (
                current_min is None
                or margin < current_min
            ):
                per_body[
                    body
                ]["min_margin"] = margin

            current_max = per_body[
                body
            ]["max_delta"]

            if (
                current_max is None
                or delta > current_max
            ):
                per_body[
                    body
                ]["max_delta"] = delta

            candidate = (
                margin,
                ordinal,
                frame,
                body,
                source,
                responder,
                retained_mask,
                lesioned_mask,
                retained_value,
                lesioned_value,
                retained_fired,
                lesioned_fired,
                delta,
            )

            if (
                primary is None
                or candidate[:3]
                < primary[:3]
            ):
                primary = candidate

        if local_contradiction:
            contradictory += 1

    if contradictory:
        classification = (
            "TRANSMISSION_GATE_CONTRADICTION"
        )

    elif total_divergent == 0:
        classification = (
            "NO_P5_PERTURBATION"
        )

    elif primary[0] == 0.0:
        classification = (
            "GATE_TOUCHES_DECISION_BOUNDARY"
        )

    else:
        classification = (
            "GATE_CLOSED_WITH_"
            "POSITIVE_DECISION_MARGIN"
        )

    if primary is None:
        endpoint = None
        scale = None

    else:
        (
            margin,
            ordinal,
            frame,
            body,
            source,
            responder,
            retained_mask,
            lesioned_mask,
            retained_value,
            lesioned_value,
            retained_fired,
            lesioned_fired,
            delta,
        ) = primary

        endpoint = {
            "absolute_p5_difference":
                delta,
            "body":
                body,
            "contrast_ordinal":
                ordinal,
            "decision_boundary_distance":
                margin,
            "frame":
                frame,
            "lesioned_fired":
                lesioned_fired,
            "lesioned_mask":
                lesioned_mask,
            "lesioned_p5":
                lesioned_value,
            "lesioned_side":
                (
                    "BELOW"
                    if lesioned_value < THRESHOLD
                    else (
                        "ABOVE"
                        if lesioned_value > THRESHOLD
                        else "AT"
                    )
                ),
            "responder":
                responder,
            "retained_fired":
                retained_fired,
            "retained_mask":
                retained_mask,
            "retained_p5":
                retained_value,
            "retained_side":
                (
                    "BELOW"
                    if retained_value < THRESHOLD
                    else (
                        "ABOVE"
                        if retained_value > THRESHOLD
                        else "AT"
                    )
                ),
            "source":
                source,
        }

        scale = (
            margin / delta
        )

    by_body = {}

    for body in ("A", "B", "C"):
        item = per_body[body]

        by_body[body] = {
            "p5_divergent_frame_count":
                item["divergent"],
            "minimum_decision_boundary_distance":
                item["min_margin"],
            "maximum_absolute_p5_difference":
                item["max_delta"],
        }

    return {
        "classification":
            classification,
        "contradictory_contrast_count":
            contradictory,
        "total_p5_divergent_frames":
            total_divergent,
        "primary_endpoint":
            endpoint,
        "scale_separation":
            scale,
        "by_body":
            by_body,
    }


def main():
    if OUTPUT.exists():
        refuse(
            "verification artifact "
            "already exists"
        )

    observed = {
        "preregistration":
            verify_sha(
                "preregistration",
                PREREG,
            ),
        "visual_runtime":
            verify_sha(
                "visual_runtime",
                VISUAL_RUNTIME,
            ),
        "evidence":
            verify_sha(
                "evidence",
                EVIDENCE,
            ),
        "sq12_seal":
            verify_sha(
                "sq12_seal",
                SQ12_SEAL,
            ),
        "analysis":
            verify_sha(
                "analysis",
                ANALYSIS,
            ),
    }

    if (
        float(
            VisualTransductionConfig()
            .threshold
        )
        != THRESHOLD
    ):
        refuse(
            "runtime threshold drift"
        )

    seal = json.loads(
        SQ12_SEAL.read_text()
    )

    if (
        seal.get("classification")
        != "TRANSMISSION_GATE_CLOSED_192_FRAMES"
    ):
        refuse(
            "inherited SQ-12 classification drift"
        )

    artifact = json.loads(
        ANALYSIS.read_text()
    )

    if (
        artifact.get(
            "neural_execution_performed"
        )
        is not False
    ):
        refuse(
            "SQ-13 execution boundary drift"
        )

    canonical = load_evidence()
    derived = derive_scalar(canonical)

    result = artifact["result"]

    if (
        result["classification"]
        != derived["classification"]
    ):
        refuse(
            "classification mismatch"
        )

    if (
        result[
            "contradictory_contrast_count"
        ]
        != derived[
            "contradictory_contrast_count"
        ]
    ):
        refuse(
            "contradiction-count mismatch"
        )

    if (
        result[
            "total_p5_divergent_frames"
        ]
        != derived[
            "total_p5_divergent_frames"
        ]
    ):
        refuse(
            "divergent-frame mismatch"
        )

    if (
        result["primary_endpoint"]
        != derived["primary_endpoint"]
    ):
        refuse(
            "primary-endpoint mismatch"
        )

    if (
        result["scale_separation"]
        != derived["scale_separation"]
    ):
        refuse(
            "scale-separation mismatch"
        )

    for body in ("A", "B", "C"):
        observed_body = (
            result["by_body"][body]
        )

        derived_body = (
            derived["by_body"][body]
        )

        for key in (
            "p5_divergent_frame_count",
            "minimum_decision_boundary_distance",
            "maximum_absolute_p5_difference",
        ):
            if (
                observed_body[key]
                != derived_body[key]
            ):
                refuse(
                    f"{body} {key} mismatch"
                )

    payload = {
        "schema_version":
            (
                "moscaquant."
                "sq13-surface-tension-"
                "verification/v1"
            ),
        "experiment":
            "SQ-13",
        "codename":
            "SURFACE TENSION",
        "status":
            "INDEPENDENT_VERIFICATION_PASS",
        "verification_method":
            (
                "independent scalar "
                "frame-by-frame reconstruction"
            ),
        "imports_primary_analyzer":
            False,
        "neural_execution_performed":
            False,
        "verified_classification":
            derived["classification"],
        "verified_primary_endpoint":
            derived["primary_endpoint"],
        "verified_scale_separation":
            derived["scale_separation"],
        "verified_total_p5_divergent_frames":
            derived[
                "total_p5_divergent_frames"
            ],
        "verified_by_body":
            derived["by_body"],
        "provenance_sha256":
            observed,
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
        + "\n"
    )

    print(
        "SQ-13 SURFACE TENSION "
        "INDEPENDENT VERIFICATION PASS"
    )

    print(
        "classification:",
        payload[
            "verified_classification"
        ],
    )

    print(
        "P5-divergent frames:",
        payload[
            "verified_total_p5_divergent_frames"
        ],
    )

    endpoint = payload[
        "verified_primary_endpoint"
    ]

    print(
        "primary BODY:",
        endpoint["body"],
    )

    print(
        "primary frame:",
        endpoint["frame"],
    )

    print(
        "decision-boundary distance:",
        endpoint[
            "decision_boundary_distance"
        ],
    )

    print(
        "absolute P5 delta:",
        endpoint[
            "absolute_p5_difference"
        ],
    )

    print(
        "scale separation:",
        payload[
            "verified_scale_separation"
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
