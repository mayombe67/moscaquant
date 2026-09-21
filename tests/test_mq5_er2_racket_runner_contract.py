from __future__ import annotations

import pytest

from brain import mq5_er2_racket_runner as racket


def test_frozen_experiment_contract():
    assert racket.EXPERIMENT_ID == "mq5-er2-the-racket-v1"
    assert racket.CODENAME == "THE RACKET"
    assert racket.FINANCIAL_SEMANTICS == "NOT ASSIGNED"
    assert racket.EXPECTED_FRAMES == 192


def test_frozen_edges_and_targets():
    assert racket.FOCUSED_EDGE == (116680, 12024)
    assert racket.MATCHED_CONTROL_EDGE == (78481, 16087)
    assert racket.PRIMARY_TARGETS == (92, 656, 137122)
    assert racket.AFFECTED_NEGATIVE_COMPARISONS == (55, 126002)
    assert racket.RETAINED_DEPENDENCY_COMPARISONS == (51, 129, 317, 1273)


def test_known_replay_onsets_are_frozen():
    assert racket.C_BASELINE_ONSETS == {
        51: 148, 55: 145, 92: 141, 129: 148, 317: 153,
        656: 141, 1273: 144, 126002: 151, 137122: 151,
    }
    assert racket.C_LESION13_ONSETS == {
        51: 150, 55: 145, 92: 141, 129: 149, 317: 156,
        656: 141, 1273: 149, 126002: 151, 137122: 151,
    }


def test_dependency_rule_counts_only_later_or_loss():
    baseline = {target: 10 for target in racket.ALL_TARGETS}
    intervention = dict(baseline)
    intervention[92] = 11
    intervention[656] = None
    intervention[137122] = 9

    rows = racket._dependency_rows(baseline, intervention)

    assert rows["92"]["dependency"] is True
    assert rows["656"]["dependency"] is True
    assert rows["137122"]["dependency"] is False


@pytest.mark.parametrize(
    ("count", "expected"),
    [
        (0, "RACKET_CAUSAL_SUPPORT_NOT_OBSERVED"),
        (1, "RACKET_CAUSAL_SUPPORT_PARTIAL"),
        (2, "RACKET_CAUSAL_SUPPORT_PARTIAL"),
        (3, "RACKET_CAUSAL_SUPPORT_COMPLETE"),
    ],
)
def test_primary_classification_contract(count, expected):
    rows = {str(target): {"dependency": False} for target in racket.ALL_TARGETS}
    for target in racket.PRIMARY_TARGETS[:count]:
        rows[str(target)]["dependency"] = True

    classification, observed = racket._primary_classification(rows)

    assert classification == expected
    assert observed == count


def test_target_specificity_is_separate_from_control_specificity():
    rows = {str(target): {"dependency": False} for target in racket.ALL_TARGETS}
    rows["92"]["dependency"] = True

    assert racket._target_specificity(rows) == (
        "AFFECTED_SET_SPECIFIC_WITHIN_TESTED_TARGETS"
    )

    rows["1273"]["dependency"] = True
    assert racket._target_specificity(rows) == (
        "SHARED_WITH_RETAINED_DEPENDENCY_TARGETS"
    )


def test_matched_control_calibration_contract():
    focused = {str(target): {"dependency": False} for target in racket.ALL_TARGETS}
    control = {str(target): {"dependency": False} for target in racket.ALL_TARGETS}

    focused["92"]["dependency"] = True
    report = racket._matched_control_calibration(focused, control)
    assert report["interpretation"] == (
        "FOCUSED_WITHOUT_MATCHED_CONTROL_PRIMARY_DEPENDENCY"
    )

    control["656"]["dependency"] = True
    report = racket._matched_control_calibration(focused, control)
    assert report["interpretation"] == (
        "FOCUSED_AND_MATCHED_CONTROL_PRIMARY_DEPENDENCY"
    )


def test_execution_gate_refuses_while_result_disabled():
    protocol = {
        "experiment_id": racket.EXPERIMENT_ID,
        "codename": racket.CODENAME,
        "financial_semantics": racket.FINANCIAL_SEMANTICS,
        "frames": racket.EXPECTED_FRAMES,
        "result_execution_enabled": False,
        "focused_edge_pre": racket.FOCUSED_EDGE[0],
        "focused_edge_post": racket.FOCUSED_EDGE[1],
        "primary_targets": list(racket.PRIMARY_TARGETS),
        "affected_negative_comparisons": list(
            racket.AFFECTED_NEGATIVE_COMPARISONS
        ),
        "retained_dependency_comparisons": list(
            racket.RETAINED_DEPENDENCY_COMPARISONS
        ),
        "all_targets": list(racket.ALL_TARGETS),
        "matched_control": {
            "presynaptic": racket.MATCHED_CONTROL_EDGE[0],
            "postsynaptic": racket.MATCHED_CONTROL_EDGE[1],
        },
        "matched_control_intervention": {
            "enabled": True,
            "control_only_arm": "CC",
            "control_plus_13_arm": "C13C",
            "primary_control_comparison": "C13C_vs_C13",
        },
    }

    with pytest.raises(RuntimeError, match="result_execution_enabled is false"):
        racket.execution_gate(protocol)
