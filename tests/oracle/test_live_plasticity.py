from __future__ import annotations

from oracle.credit_assignment import (
    classify_credit,
    score_edge,
)
from oracle.live_plasticity import (
    apply_live_bad_synapse,
)
from oracle.plasticity_adapter import (
    get_plasticity_state,
)
from oracle.selector import select_d6
from oracle.state import initial_state


ARTIFACT = "connectome-baseline-v1.npz"

SOURCE = 56393
TARGET = 68045
WEIGHT = 2.0


def find_sc03_seed(
    *,
    plasticity_active: bool,
):
    for seed in range(10000):
        result = select_d6(
            seed=seed,
            experiment_id="mq7-live",
            session_id="session-A",
            plasticity_active=plasticity_active,
        )

        if (
            result.selection.condition.value
            == "SC-03"
        ):
            return result

    raise AssertionError(
        "could not select SC-03"
    )


def eligible_credit():
    edge = score_edge(
        presynaptic=SOURCE,
        postsynaptic=TARGET,
        weight=WEIGHT,
        activity_history=[1.0],
    )

    return classify_credit([edge])


def test_sc03_remains_not_applicable_when_plasticity_off():
    oracle = initial_state(
        oracle_version="oracle-test-v1",
    )

    d6 = find_sc03_seed(
        plasticity_active=False,
    )

    result = apply_live_bad_synapse(
        oracle_state=oracle,
        d6_result=d6,
        credit_result=eligible_credit(),
        baseline_artifact_id=ARTIFACT,
        session_id="session-A",
        evidence_reference="credit-001",
    )

    assert result.status == "NOT_APPLICABLE"
    assert result.oracle_state == oracle
    assert result.plasticity_state is None


def test_ambiguous_credit_blocks_update():
    oracle = initial_state(
        oracle_version="oracle-test-v1",
    )

    d6 = find_sc03_seed(
        plasticity_active=True,
    )

    first = score_edge(
        presynaptic=SOURCE,
        postsynaptic=TARGET,
        weight=1.0,
        activity_history=[1.0],
    )

    second = score_edge(
        presynaptic=68045,
        postsynaptic=1273,
        weight=1.0,
        activity_history=[1.0],
    )

    credit = classify_credit(
        [first, second]
    )

    assert credit.status == "AMBIGUOUS_CREDIT"

    result = apply_live_bad_synapse(
        oracle_state=oracle,
        d6_result=d6,
        credit_result=credit,
        baseline_artifact_id=ARTIFACT,
        session_id="session-A",
        evidence_reference="credit-001",
    )

    assert (
        result.status
        == "NO_UPDATE_AMBIGUOUS_CREDIT"
    )

    assert result.oracle_state == oracle


def test_no_eligible_pathway_blocks_update():
    oracle = initial_state(
        oracle_version="oracle-test-v1",
    )

    d6 = find_sc03_seed(
        plasticity_active=True,
    )

    edge = score_edge(
        presynaptic=SOURCE,
        postsynaptic=TARGET,
        weight=WEIGHT,
        activity_history=[0.0] * 10,
    )

    credit = classify_credit([edge])

    result = apply_live_bad_synapse(
        oracle_state=oracle,
        d6_result=d6,
        credit_result=credit,
        baseline_artifact_id=ARTIFACT,
        session_id="session-A",
        evidence_reference="credit-001",
    )

    assert (
        result.status
        == "NO_UPDATE_NO_ELIGIBLE_PATHWAY"
    )

    assert result.oracle_state == oracle


def test_unique_eligible_edge_updates_persistent_state():
    oracle = initial_state(
        oracle_version="oracle-test-v1",
    )

    d6 = find_sc03_seed(
        plasticity_active=True,
    )

    result = apply_live_bad_synapse(
        oracle_state=oracle,
        d6_result=d6,
        credit_result=eligible_credit(),
        baseline_artifact_id=ARTIFACT,
        session_id="session-A",
        evidence_reference="credit-001",
    )

    assert result.status == "UPDATED"

    restored = get_plasticity_state(
        result.oracle_state
    )

    assert restored is not None
    assert len(restored.edges) == 1

    edge = restored.edges[0]

    assert edge.presynaptic == SOURCE
    assert edge.postsynaptic == TARGET
    assert edge.multiplier == 0.95


def test_second_valid_update_stacks():
    oracle = initial_state(
        oracle_version="oracle-test-v1",
    )

    d6 = find_sc03_seed(
        plasticity_active=True,
    )

    first = apply_live_bad_synapse(
        oracle_state=oracle,
        d6_result=d6,
        credit_result=eligible_credit(),
        baseline_artifact_id=ARTIFACT,
        session_id="session-A",
        evidence_reference="credit-001",
    )

    second = apply_live_bad_synapse(
        oracle_state=first.oracle_state,
        d6_result=d6,
        credit_result=eligible_credit(),
        baseline_artifact_id=ARTIFACT,
        session_id="session-B",
        evidence_reference="credit-002",
    )

    restored = get_plasticity_state(
        second.oracle_state
    )

    assert restored is not None

    edge = restored.edges[0]

    assert edge.multiplier == 0.95 * 0.95
    assert edge.update_count == 2
