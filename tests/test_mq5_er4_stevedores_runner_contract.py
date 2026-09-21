from __future__ import annotations

import pytest

from brain import mq5_er4_stevedores_runner as stevedores


def test_frozen_contract():
    assert stevedores.EXPERIMENT_ID == "mq5-er4-the-stevedores-v1"
    assert stevedores.CODENAME == "THE STEVEDORES"
    assert stevedores.FINANCIAL_SEMANTICS == "NOT ASSIGNED"
    assert stevedores.AFFECTED_TARGETS == (55, 92, 656, 126002, 137122)
    assert stevedores.RETAINED_TARGETS == (51, 129, 317, 1273)
    assert stevedores.ALL_TARGETS == (
        51, 55, 92, 129, 317, 656, 1273, 126002, 137122
    )


def test_candidate_contract():
    assert stevedores.EXPECTED_CANDIDATES["S1"]["edge"] == (11725, 29921)
    assert stevedores.EXPECTED_CANDIDATES["S2"]["edge"] == (11345, 47350)
    assert stevedores.EXPECTED_CANDIDATES["S3"]["edge"] == (10647, 51642)


def test_control_contract():
    assert stevedores.EXPECTED_CONTROLS["S1"]["edge"] == (19300, 26090)
    assert stevedores.EXPECTED_CONTROLS["S2"]["edge"] == (16922, 34070)
    assert stevedores.EXPECTED_CONTROLS["S3"]["edge"] == (12775, 57635)


def test_dependency_semantics_later_only():
    baseline = {target: 10 for target in stevedores.ALL_TARGETS}
    intervention = dict(baseline)

    intervention[55] = 11
    intervention[92] = 9
    intervention[656] = None

    rows = stevedores.dependency_rows(baseline, intervention)

    assert rows["55"]["dependency"] is True
    assert rows["92"]["dependency"] is False
    assert rows["656"]["dependency"] is True


def test_single_classification():
    rows = {
        str(target): {"dependency": False}
        for target in stevedores.ALL_TARGETS
    }

    label, count = stevedores.classify_single("S1", rows)
    assert label == "SINGLE_EDGE_CAUSAL_SUPPORT_NOT_OBSERVED"
    assert count == 0

    rows["55"]["dependency"] = True
    label, count = stevedores.classify_single("S1", rows)
    assert label == "SINGLE_EDGE_CAUSAL_SUPPORT_PARTIAL"
    assert count == 1

    rows["126002"]["dependency"] = True
    rows["137122"]["dependency"] = True
    label, count = stevedores.classify_single("S1", rows)
    assert label == "SINGLE_EDGE_CAUSAL_SUPPORT_COMPLETE"
    assert count == 3


def test_combined_classification():
    rows = {
        str(target): {"dependency": False}
        for target in stevedores.ALL_TARGETS
    }

    label, count = stevedores.classify_combined(rows)
    assert label == "COMBINED_SET_CAUSAL_SUPPORT_NOT_OBSERVED"
    assert count == 0

    rows["55"]["dependency"] = True
    label, count = stevedores.classify_combined(rows)
    assert label == "COMBINED_SET_CAUSAL_SUPPORT_PARTIAL"
    assert count == 1

    for target in stevedores.AFFECTED_TARGETS:
        rows[str(target)]["dependency"] = True
    label, count = stevedores.classify_combined(rows)
    assert label == "COMBINED_SET_CAUSAL_SUPPORT_COMPLETE"
    assert count == 5


def test_execution_gate_refuses_when_disabled():
    protocol = {
        "experiment_id": stevedores.EXPERIMENT_ID,
        "codename": stevedores.CODENAME,
        "financial_semantics": stevedores.FINANCIAL_SEMANTICS,
        "frames": 192,
        "result_execution_enabled": False,
        "affected_targets": list(stevedores.AFFECTED_TARGETS),
        "retained_dependency_comparisons": list(stevedores.RETAINED_TARGETS),
        "all_targets": list(stevedores.ALL_TARGETS),
        "candidates": [
            {
                "id": cid,
                "presynaptic": row["edge"][0],
                "postsynaptic": row["edge"][1],
                "weight": row["weight"],
                "affected_targets": list(row["associated_targets"]),
            }
            for cid, row in stevedores.EXPECTED_CANDIDATES.items()
        ],
        "matched_control_edges": [
            {
                "candidate_id": cid,
                "presynaptic": row["edge"][0],
                "postsynaptic": row["edge"][1],
                "weight": row["weight"],
            }
            for cid, row in stevedores.EXPECTED_CONTROLS.items()
        ],
    }

    with pytest.raises(
        RuntimeError,
        match="result_execution_enabled is false",
    ):
        stevedores.execution_gate(protocol)
