from __future__ import annotations

from oracle.reinforcement import ReinforcementCondition
from oracle.selector import D6_CONDITIONS, select_d6


def test_d6_has_exactly_six_conditions():
    assert len(D6_CONDITIONS) == 6

    assert D6_CONDITIONS == (
        ReinforcementCondition.SC_01_SHOCK,
        ReinforcementCondition.SC_02_DARKNESS,
        ReinforcementCondition.SC_03_BAD_SYNAPSE,
        ReinforcementCondition.SC_04_TIME_OUT,
        ReinforcementCondition.SC_05_SCAR_TISSUE,
        ReinforcementCondition.SC_06_MERCY,
    )


def test_d6_selection_is_deterministic():
    first = select_d6(
        seed=42,
        experiment_id="mq7-d6",
        session_id="session-001",
        plasticity_active=False,
    )

    second = select_d6(
        seed=42,
        experiment_id="mq7-d6",
        session_id="session-001",
        plasticity_active=False,
    )

    assert first == second


def test_d6_index_is_valid():
    result = select_d6(
        seed=123,
        experiment_id="mq7-d6",
        session_id="session-001",
        plasticity_active=True,
    )

    assert 0 <= result.selection.selected_index < 6
    assert result.selection.condition in D6_CONDITIONS


def test_bad_synapse_is_not_rerolled_when_inapplicable():
    found = None

    for seed in range(10000):
        result = select_d6(
            seed=seed,
            experiment_id="mq7-d6",
            session_id="session-001",
            plasticity_active=False,
        )

        if (
            result.selection.condition
            is ReinforcementCondition.SC_03_BAD_SYNAPSE
        ):
            found = result
            break

    assert found is not None
    assert found.applicable is False
    assert found.status == "NOT_APPLICABLE"
    assert (
        found.selection.condition
        is ReinforcementCondition.SC_03_BAD_SYNAPSE
    )


def test_bad_synapse_is_applicable_with_plasticity():
    for seed in range(10000):
        result = select_d6(
            seed=seed,
            experiment_id="mq7-d6",
            session_id="session-001",
            plasticity_active=True,
        )

        if (
            result.selection.condition
            is ReinforcementCondition.SC_03_BAD_SYNAPSE
        ):
            assert result.applicable is True
            assert result.status == "SELECTED"
            return

    raise AssertionError("SC-03 was not selected in search range")
