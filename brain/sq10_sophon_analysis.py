from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from brain.sq10_sophon_independent_verify import (
    verify_evidence_arrays,
)


ROOT = Path(__file__).resolve().parents[1]

ANALYSIS_CONTRACT = (
    ROOT
    / "config/experiments/"
    "sq10-sophon-analysis-contract-draft-v1.json"
)

BODY_ORDER = ("A", "B", "C")


class AnalysisRefusal(RuntimeError):
    pass


def refuse(message: str) -> None:
    raise AnalysisRefusal(message)


def load_contract() -> dict:
    return json.loads(
        ANALYSIS_CONTRACT.read_text()
    )


def first_exact_divergence(
    retained: np.ndarray,
    lesioned: np.ndarray,
) -> int | None:
    retained = np.asarray(retained)
    lesioned = np.asarray(lesioned)

    if retained.shape != lesioned.shape:
        refuse(
            "divergence comparison shape mismatch"
        )

    if retained.ndim != 1:
        refuse(
            "divergence comparison must be 1D"
        )

    diff = np.flatnonzero(
        retained != lesioned
    )

    if len(diff) == 0:
        return None

    return int(diff[0])


def canonical_r1_index_by_mask(
    arrays: dict[str, np.ndarray],
) -> dict[str, int]:
    masks = arrays[
        "condition_mask"
    ]

    replicates = arrays[
        "condition_replicate"
    ]

    result = {}

    for i, (mask, replicate) in enumerate(
        zip(masks, replicates)
    ):
        if int(replicate) != 1:
            continue

        mask = str(mask)

        if mask in result:
            refuse(
                f"duplicate canonical r1 mask: {mask}"
            )

        result[mask] = int(i)

    expected = {
        "000",
        "001",
        "010",
        "011",
        "100",
        "101",
        "110",
        "111",
    }

    if set(result) != expected:
        refuse(
            "canonical r1 mask universe mismatch"
        )

    return result


def validate_frozen_analysis_contract(
    contract: dict,
) -> None:
    if (
        contract[
            "neural_execution_authorized"
        ]
        is not False
    ):
        refuse(
            "analysis contract unexpectedly "
            "authorizes neural execution"
        )

    if (
        contract["status"]
        != "FROZEN_ANALYSIS_PRE_NEURAL_EXECUTION"
    ):
        refuse(
            "SQ-10 analysis contract "
            "is not frozen"
        )

    numerical = (
        contract["primary_test"]
        ["numerical_acceptance"]
    )

    if (
        numerical["status"]
        != "FROZEN_FROM_SYNTHETIC_FLOAT32_CALIBRATION"
    ):
        refuse(
            "numerical calibration "
            "is not frozen"
        )

    if (
        numerical[
            "absolute_tolerance"
        ]
        != 3.814697265625e-06
    ):
        refuse(
            "SQ-10 absolute tolerance drift"
        )

    if (
        numerical[
            "relative_tolerance"
        ]
        != 0.0
    ):
        refuse(
            "SQ-10 relative tolerance drift"
        )

    contrasts = contract[
        "matched_contrasts"
    ]

    if len(contrasts) != 12:
        refuse(
            "SQ-10 matched-contrast "
            "universe drift"
        )


def analyze_contrast(
    *,
    arrays: dict[str, np.ndarray],
    retained_index: int,
    lesioned_index: int,
    body: str,
    tolerance: float,
) -> dict:
    if body not in BODY_ORDER:
        refuse(
            f"invalid BODY label: {body}"
        )

    body_index = BODY_ORDER.index(
        body
    )

    retained_p5 = arrays[
        "responder_voltage_pre_threshold"
    ][
        retained_index,
        :,
        body_index,
    ]

    lesioned_p5 = arrays[
        "responder_voltage_pre_threshold"
    ][
        lesioned_index,
        :,
        body_index,
    ]

    responder_frame = first_exact_divergence(
        retained_p5,
        lesioned_p5,
    )

    source_retained = arrays[
        "source_effective_activity_pre_synaptic"
    ][
        retained_index,
        :,
        body_index,
    ]

    source_lesioned = arrays[
        "source_effective_activity_pre_synaptic"
    ][
        lesioned_index,
        :,
        body_index,
    ]

    target_source_frame = first_exact_divergence(
        source_retained,
        source_lesioned,
    )

    off_target_source_frames = {}
    off_target_responder_frames = {}

    for other_index, other_body in enumerate(
        BODY_ORDER
    ):
        if other_body == body:
            continue

        off_target_source_frames[
            other_body
        ] = first_exact_divergence(
            arrays[
                "source_effective_activity_pre_synaptic"
            ][
                retained_index,
                :,
                other_index,
            ],
            arrays[
                "source_effective_activity_pre_synaptic"
            ][
                lesioned_index,
                :,
                other_index,
            ],
        )

        off_target_responder_frames[
            other_body
        ] = first_exact_divergence(
            arrays[
                "responder_voltage_pre_threshold"
            ][
                retained_index,
                :,
                other_index,
            ],
            arrays[
                "responder_voltage_pre_threshold"
            ][
                lesioned_index,
                :,
                other_index,
            ],
        )

    result = {
        "body": body,
        "body_index": body_index,
        "retained_episode_index":
            int(retained_index),
        "lesioned_episode_index":
            int(lesioned_index),

        "first_responder_divergence_frame":
            responder_frame,

        "target_source_first_divergence_frame":
            target_source_frame,

        "off_target_source_first_divergence_frames":
            off_target_source_frames,

        "off_target_responder_first_divergence_frames":
            off_target_responder_frames,

        "absolute_tolerance":
            float(tolerance),

        "retained_p5":
            None,
        "lesioned_p5":
            None,
        "observed_signed_delta":
            None,
        "retained_source_activity":
            None,
        "edge_weight":
            None,
        "predicted_direct_delta":
            None,
        "residual":
            None,
        "absolute_residual":
            None,
        "classification":
            None,
    }

    if responder_frame is None:
        result["classification"] = (
            "NO_RESPONDER_DIVERGENCE"
        )
        return result

    if (
        target_source_frame is not None
        and target_source_frame
        <= responder_frame
    ):
        result["classification"] = (
            "SOURCE_STATE_DIVERGES_"
            "BEFORE_OR_AT_RESPONDER"
        )
        return result

    frame = responder_frame

    retained_value = np.float64(
        retained_p5[frame]
    )

    lesioned_value = np.float64(
        lesioned_p5[frame]
    )

    observed_delta = float(
        retained_value
        - lesioned_value
    )

    source_activity = float(
        np.float64(
            source_retained[frame]
        )
    )

    edge_weight = float(
        np.float64(
            arrays[
                "body_edge_weight"
            ][body_index]
        )
    )

    predicted_delta = float(
        np.float64(source_activity)
        * np.float64(edge_weight)
    )

    residual = float(
        observed_delta
        - predicted_delta
    )

    absolute_residual = abs(
        residual
    )

    result.update(
        {
            "retained_p5":
                float(retained_value),
            "lesioned_p5":
                float(lesioned_value),
            "observed_signed_delta":
                observed_delta,
            "retained_source_activity":
                source_activity,
            "edge_weight":
                edge_weight,
            "predicted_direct_delta":
                predicted_delta,
            "residual":
                residual,
            "absolute_residual":
                absolute_residual,
        }
    )

    if absolute_residual > tolerance:
        result["classification"] = (
            "DIRECT_PREDICTION_RESIDUAL_"
            "EXCEEDS_TOLERANCE"
        )

    elif abs(predicted_delta) <= tolerance:
        result["classification"] = (
            "DIRECT_EFFECT_BELOW_"
            "CALIBRATED_RESOLUTION"
        )

    else:
        result["classification"] = (
            "DIRECT_LOCAL_AT_FIRST_DIVERGENCE"
        )

    return result


def analyze(
    arrays: dict[str, np.ndarray],
) -> dict:
    verification = verify_evidence_arrays(
        arrays
    )

    contract = load_contract()

    validate_frozen_analysis_contract(
        contract
    )

    numerical = (
        contract["primary_test"]
        ["numerical_acceptance"]
    )

    tolerance = float(
        numerical[
            "absolute_tolerance"
        ]
    )

    index_by_mask = (
        canonical_r1_index_by_mask(
            arrays
        )
    )

    contrast_results = []

    for contrast in contract[
        "matched_contrasts"
    ]:
        body = contrast["body"]
        retained_mask = contrast[
            "retained"
        ]
        lesioned_mask = contrast[
            "lesioned"
        ]

        result = analyze_contrast(
            arrays=arrays,
            retained_index=(
                index_by_mask[
                    retained_mask
                ]
            ),
            lesioned_index=(
                index_by_mask[
                    lesioned_mask
                ]
            ),
            body=body,
            tolerance=tolerance,
        )

        result[
            "retained_mask"
        ] = retained_mask

        result[
            "lesioned_mask"
        ] = lesioned_mask

        contrast_results.append(
            result
        )

    if len(contrast_results) != 12:
        refuse(
            "SQ-10 analysis did not "
            "produce 12 contrasts"
        )

    counts = {}

    for result in contrast_results:
        classification = result[
            "classification"
        ]

        counts[classification] = (
            counts.get(
                classification,
                0,
            )
            + 1
        )

    return {
        "schema_version":
            "moscaquant."
            "sq10-sophon-analysis/v1",

        "experiment": "SQ-10",
        "codename": "SOPHON",

        "status":
            "ANALYSIS_COMPLETE",

        "verification":
            verification,

        "numerical_acceptance": {
            "absolute_tolerance":
                tolerance,
            "relative_tolerance":
                0.0,
        },

        "contrast_count":
            len(contrast_results),

        "classification_counts":
            counts,

        "contrasts":
            contrast_results,
    }
