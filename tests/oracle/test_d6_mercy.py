from __future__ import annotations

import numpy as np

from oracle.d6_mercy import (
    DEFAULT_COOLDOWN_TRANSITIONS,
    DEFAULT_DURATION_TRANSITIONS,
    DEFAULT_GAIN,
    MERCY_TARGET_POOL,
    apply_mercy_activity,
    build_mercy,
    is_mercy_active,
    select_mercy_target,
)
from oracle.reinforcement import ReinforcementCondition


def test_mercy_defaults_are_frozen():
    intervention = build_mercy(
        seed=42,
        experiment_id="mq7-mercy",
        session_id="session-001",
        current_generation=10,
    )

    assert (
        intervention.condition
        is ReinforcementCondition.SC_06_MERCY
    )

    assert intervention.gain == DEFAULT_GAIN == 0.25
    assert intervention.duration_transitions == DEFAULT_DURATION_TRANSITIONS == 1
    assert intervention.cooldown_transitions == DEFAULT_COOLDOWN_TRANSITIONS == 10


def test_mercy_target_is_deterministic():
    first = select_mercy_target(
        seed=42,
        experiment_id="mq7-mercy",
        session_id="session-001",
    )

    second = select_mercy_target(
        seed=42,
        experiment_id="mq7-mercy",
        session_id="session-001",
    )

    assert first == second


def test_mercy_target_comes_from_frozen_pool():
    for seed in range(100):
        pool_index, target = select_mercy_target(
            seed=seed,
            experiment_id="mq7-mercy",
            session_id="session-001",
        )

        assert target == MERCY_TARGET_POOL[pool_index]


def test_mercy_window_is_one_transition():
    intervention = build_mercy(
        seed=42,
        experiment_id="mq7-mercy",
        session_id="session-001",
        current_generation=10,
    )

    assert is_mercy_active(
        intervention,
        generation=10,
    )

    assert not is_mercy_active(
        intervention,
        generation=11,
    )


def test_mercy_boosts_existing_activity_by_25_percent():
    intervention = build_mercy(
        seed=42,
        experiment_id="mq7-mercy",
        session_id="session-001",
        current_generation=0,
    )

    size = max(MERCY_TARGET_POOL) + 1

    activity = np.zeros(
        size,
        dtype=np.float32,
    )

    activity[
        intervention.target_model_index
    ] = 0.40

    result = apply_mercy_activity(
        effective_activity=activity,
        intervention=intervention,
        generation=0,
    )

    assert np.isclose(
        result[intervention.target_model_index],
        0.50,
    )


def test_mercy_caps_activity_at_one():
    intervention = build_mercy(
        seed=42,
        experiment_id="mq7-mercy",
        session_id="session-001",
        current_generation=0,
    )

    size = max(MERCY_TARGET_POOL) + 1

    activity = np.zeros(
        size,
        dtype=np.float32,
    )

    activity[
        intervention.target_model_index
    ] = 0.90

    result = apply_mercy_activity(
        effective_activity=activity,
        intervention=intervention,
        generation=0,
    )

    assert np.isclose(
        result[intervention.target_model_index],
        1.0,
    )


def test_mercy_does_not_create_activity_from_zero():
    intervention = build_mercy(
        seed=42,
        experiment_id="mq7-mercy",
        session_id="session-001",
        current_generation=0,
    )

    size = max(MERCY_TARGET_POOL) + 1

    activity = np.zeros(
        size,
        dtype=np.float32,
    )

    result = apply_mercy_activity(
        effective_activity=activity,
        intervention=intervention,
        generation=0,
    )

    assert np.isclose(
        result[intervention.target_model_index],
        0.0,
    )


def test_mercy_preserves_original_activity():
    intervention = build_mercy(
        seed=42,
        experiment_id="mq7-mercy",
        session_id="session-001",
        current_generation=0,
    )

    size = max(MERCY_TARGET_POOL) + 1

    activity = np.zeros(
        size,
        dtype=np.float32,
    )

    activity[
        intervention.target_model_index
    ] = 0.50

    original = activity.copy()

    apply_mercy_activity(
        effective_activity=activity,
        intervention=intervention,
        generation=0,
    )

    np.testing.assert_array_equal(
        activity,
        original,
    )
