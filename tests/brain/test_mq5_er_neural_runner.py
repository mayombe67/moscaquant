from __future__ import annotations

from types import SimpleNamespace

import pytest

from brain.mq5_er_neural_runner import (
    causal_expression_report,
    classify_arm_d_family,
    classify_encoding,
    execution_gate,
)


TARGETS = (51, 55, 92)


def _result(onsets, fingerprint):
    return SimpleNamespace(
        first_positive_onsets=onsets,
        positive_voltage_fingerprint=fingerprint,
    )


def test_causal_expression_requires_strict_delay_or_loss():
    baseline = _result(
        {51: 10, 55: 11, 92: 12},
        [1.0, 2.0, 3.0],
    )
    lesion = _result(
        {51: 11, 55: None, 92: 12},
        [1.0, 2.0, 3.0],
    )

    report = causal_expression_report(
        baseline,
        lesion,
        TARGETS,
    )

    assert report["targets"]["51"]["expressed"] is True
    assert report["targets"]["55"]["expressed"] is True
    assert report["targets"]["92"]["expressed"] is False
    assert report["all_targets_expressed"] is False


def test_preserved_requires_exact_onset_fingerprint_and_causal_expression():
    arm_a = _result(
        {51: 10, 55: 11, 92: 12},
        [1.0, 2.0, 3.0],
    )
    lesion = _result(
        {51: 11, 55: 12, 92: 13},
        [1.0, 2.0, 3.0],
    )

    report = classify_encoding(
        arm_a,
        arm_a,
        lesion,
        targets=TARGETS,
        fingerprint_tolerance=1e-9,
    )

    assert report["classification"] == "RESPONSE PATTERN PRESERVED"


def test_altered_when_targets_and_causality_retained_but_onset_changes():
    arm_a = _result(
        {51: 10, 55: 11, 92: 12},
        [1.0, 2.0, 3.0],
    )
    baseline = _result(
        {51: 10, 55: 12, 92: 12},
        [1.0, 2.0, 3.0],
    )
    lesion = _result(
        {51: 11, 55: 13, 92: 14},
        [1.0, 2.0, 3.0],
    )

    report = classify_encoding(
        arm_a,
        baseline,
        lesion,
        targets=TARGETS,
        fingerprint_tolerance=1e-9,
    )

    assert (
        report["classification"]
        == "RESPONSE RETAINED WITH ALTERED EXPRESSION"
    )


def test_not_retained_when_target_missing():
    arm_a = _result(
        {51: 10, 55: 11, 92: 12},
        [1.0, 2.0, 3.0],
    )
    baseline = _result(
        {51: 10, 55: None, 92: 12},
        [1.0, 2.0, 3.0],
    )
    lesion = _result(
        {51: 11, 55: None, 92: 13},
        [1.0, 2.0, 3.0],
    )

    report = classify_encoding(
        arm_a,
        baseline,
        lesion,
        targets=TARGETS,
        fingerprint_tolerance=1e-9,
    )

    assert report["classification"] == "RESPONSE PATTERN NOT RETAINED"


def test_arm_d_family_four_way_labels():
    preserved = "RESPONSE PATTERN PRESERVED"
    altered = "RESPONSE RETAINED WITH ALTERED EXPRESSION"
    failed = "RESPONSE PATTERN NOT RETAINED"

    assert classify_arm_d_family([preserved] * 11) == (
        "ASSET-TERRITORY ROBUST ACROSS TESTED REMAPS"
    )

    assert classify_arm_d_family(
        [preserved] * 10 + [altered]
    ) == (
        "ASSET-TERRITORY RETAINED BUT ALTERED "
        "ACROSS TESTED REMAPS"
    )

    assert classify_arm_d_family(
        [preserved] * 5 + [failed] * 6
    ) == "MIXED ASSET-TERRITORY DEPENDENCE"

    assert classify_arm_d_family(
        [failed] * 11
    ) == "ASSET-TERRITORY ASSIGNMENT DEPENDENCE SUPPORTED"


def test_execution_gate_refuses_when_disabled():
    protocol = {
        "execution": {
            "result_execution_enabled": False,
        },
        "classification": {
            "preservation_tolerances_frozen": True,
        },
    }

    with pytest.raises(
        RuntimeError,
        match="result_execution_enabled is false",
    ):
        execution_gate(protocol)
