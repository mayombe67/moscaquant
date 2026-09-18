from __future__ import annotations

import numpy as np
import pytest

from oracle.d6_shock import (
    DEFAULT_COOLDOWN_TRANSITIONS,
    DEFAULT_DURATION_TRANSITIONS,
    DEFAULT_INTENSITY,
    SHOCK_TARGET_POOL,
    SHOCK_VERSION,
    ShockError,
    apply_shock_activity,
    build_shock,
    is_shock_active,
    select_shock_target,
)
from oracle.reinforcement import ReinforcementCondition


def test_shock_defaults_are_frozen():
    intervention = build_shock(
        seed=42,
        experiment_id="mq7-shock",
        session_id="session-001",
        current_generation=10,
    )

    assert intervention.schema_version == SHOCK_VERSION

    assert (
        intervention.condition
        is ReinforcementCondition.SC_01_SHOCK
    )

    assert intervention.intensity == DEFAULT_INTENSITY == 0.75
    assert intervention.duration_transitions == DEFAULT_DURATION_TRANSITIONS == 1
    assert intervention.cooldown_transitions == DEFAULT_COOLDOWN_TRANSITIONS == 10


def test_shock_target_selection_is_deterministic():
    first = select_shock_target(
        seed=123,
        experiment_id="mq7-shock",
        session_id="session-001",
    )

    second = select_shock_target(
        seed=123,
        experiment_id="mq7-shock",
        session_id="session-001",
    )

    assert first == second


def test_shock_target_always_comes_from_frozen_pool():
    for seed in range(100):
        pool_index, target = select_shock_target(
            seed=seed,
            experiment_id="mq7-shock",
            session_id="session-001",
        )

        assert 0 <= pool_index < len(SHOCK_TARGET_POOL)
        assert target == SHOCK_TARGET_POOL[pool_index]


def test_shock_window_is_exactly_one_transition():
    intervention = build_shock(
        seed=42,
        experiment_id="mq7-shock",
        session_id="session-001",
        current_generation=10,
    )

    assert not is_shock_active(
        intervention,
        generation=9,
    )

    assert is_shock_active(
        intervention,
        generation=10,
    )

    assert not is_shock_active(
        intervention,
        generation=11,
    )


def test_shock_raises_target_activity_to_intensity_floor():
    intervention = build_shock(
        seed=42,
        experiment_id="mq7-shock",
        session_id="session-001",
        current_generation=0,
    )

    size = max(SHOCK_TARGET_POOL) + 1

    activity = np.zeros(
        size,
        dtype=np.float32,
    )

    result = apply_shock_activity(
        effective_activity=activity,
        intervention=intervention,
        generation=0,
    )

    assert np.isclose(
        result[intervention.target_model_index],
        0.75,
    )


def test_shock_never_reduces_existing_activity():
    intervention = build_shock(
        seed=42,
        experiment_id="mq7-shock",
        session_id="session-001",
        current_generation=0,
    )

    size = max(SHOCK_TARGET_POOL) + 1

    activity = np.zeros(
        size,
        dtype=np.float32,
    )

    activity[
        intervention.target_model_index
    ] = 0.90

    result = apply_shock_activity(
        effective_activity=activity,
        intervention=intervention,
        generation=0,
    )

    assert np.isclose(
        result[intervention.target_model_index],
        0.90,
    )


def test_shock_preserves_original_activity():
    intervention = build_shock(
        seed=42,
        experiment_id="mq7-shock",
        session_id="session-001",
        current_generation=0,
    )

    size = max(SHOCK_TARGET_POOL) + 1

    activity = np.zeros(
        size,
        dtype=np.float32,
    )

    original = activity.copy()

    apply_shock_activity(
        effective_activity=activity,
        intervention=intervention,
        generation=0,
    )

    np.testing.assert_array_equal(
        activity,
        original,
    )


def test_shock_has_no_effect_outside_window():
    intervention = build_shock(
        seed=42,
        experiment_id="mq7-shock",
        session_id="session-001",
        current_generation=0,
    )

    size = max(SHOCK_TARGET_POOL) + 1

    activity = np.zeros(
        size,
        dtype=np.float32,
    )

    result = apply_shock_activity(
        effective_activity=activity,
        intervention=intervention,
        generation=1,
    )

    np.testing.assert_array_equal(
        result,
        activity,
    )


def test_shock_rejects_out_of_range_target():
    intervention = build_shock(
        seed=42,
        experiment_id="mq7-shock",
        session_id="session-001",
        current_generation=0,
    )

    activity = np.zeros(
        10,
        dtype=np.float32,
    )

    with pytest.raises(
        ShockError,
        match="outside",
    ):
        apply_shock_activity(
            effective_activity=activity,
            intervention=intervention,
            generation=0,
        )
