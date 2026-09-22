from __future__ import annotations

import pytest

from brain import mq5_er5_the_greek_runner as greek


def test_frozen_contract():
    assert greek.EXPERIMENT_ID == "mq5-er5-the-greek-v1"
    assert greek.CODENAME == "THE GREEK"
    assert greek.FINANCIAL_SEMANTICS == "NOT ASSIGNED"
    assert greek.MAX_BACKWARD_HOPS == 3
    assert greek.TOP_K == 5
    assert greek.FOCUSED_MIN_AFFECTED_COVERAGE == 4


def test_target_sets():
    assert greek.AFFECTED_TARGETS == (55, 92, 656, 126002, 137122)
    assert greek.RETAINED_TARGETS == (51, 129, 317, 1273)


def test_classify_focused():
    rows = [
        {
            "affected_coverage": 4,
            "affected_targets": [55, 92, 656, 126002],
        }
    ]
    assert greek.classify(rows) == "GREEK_FOCUSED_COORDINATOR_CANDIDATE"


def test_classify_distributed():
    rows = [
        {
            "affected_coverage": 3,
            "affected_targets": [55, 92, 656],
        },
        {
            "affected_coverage": 2,
            "affected_targets": [126002, 137122],
        },
    ]
    assert greek.classify(rows) == "GREEK_DISTRIBUTED_COORDINATOR_PATTERN"


def test_classify_none():
    rows = [
        {
            "affected_coverage": 2,
            "affected_targets": [55, 92],
        }
    ]
    assert greek.classify(rows) == "NO_CLEAR_GREEK_COORDINATOR"


def test_execution_gate_refuses_when_disabled():
    protocol = {
        "experiment_id": greek.EXPERIMENT_ID,
        "codename": greek.CODENAME,
        "financial_semantics": greek.FINANCIAL_SEMANTICS,
        "frames": 192,
        "result_execution_enabled": False,
        "affected_targets": list(greek.AFFECTED_TARGETS),
        "retained_dependency_comparisons": list(greek.RETAINED_TARGETS),
        "all_targets": list(greek.ALL_TARGETS),
        "max_backward_hops": 3,
        "top_k": 5,
        "focused_min_affected_coverage": 4,
    }

    with pytest.raises(
        RuntimeError,
        match="result_execution_enabled is false",
    ):
        greek.execution_gate(protocol)
