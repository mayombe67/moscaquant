from __future__ import annotations

import numpy as np

from oracle.d6_scar import (
    advance_scar,
    build_scar,
)
from oracle.d6_scar_effect import (
    DEFAULT_ATTENUATION,
    SCAR_TARGET_POOL,
    apply_scar_effect,
    select_scar_target,
)


def test_scar_target_selection_is_deterministic():
    first = select_scar_target(
        seed=42,
        experiment_id="mq7-scar",
        origin_session_id="session-A",
    )

    second = select_scar_target(
        seed=42,
        experiment_id="mq7-scar",
        origin_session_id="session-A",
    )

    assert first == second


def test_scar_target_is_from_frozen_pool():
    for seed in range(100):
        pool_index, target = select_scar_target(
            seed=seed,
            experiment_id="mq7-scar",
            origin_session_id="session-A",
        )

        assert (
            target
            == SCAR_TARGET_POOL[pool_index]
        )


def test_active_scar_retains_75_percent_activity():
    state = build_scar(
        session_id="session-A",
        current_generation=0,
    )

    target = SCAR_TARGET_POOL[0]

    activity = np.zeros(
        max(SCAR_TARGET_POOL) + 1,
        dtype=np.float32,
    )

    activity[target] = 0.8

    result = apply_scar_effect(
        effective_activity=activity,
        scar_state=state,
        target_model_index=target,
    )

    assert DEFAULT_ATTENUATION == 0.25

    assert np.isclose(
        result[target],
        0.6,
    )


def test_scar_effect_persists_into_following_session():
    state = build_scar(
        session_id="session-A",
        current_generation=0,
    )

    state = advance_scar(
        state=state,
        session_id="session-B",
    )

    target = SCAR_TARGET_POOL[0]

    activity = np.zeros(
        max(SCAR_TARGET_POOL) + 1,
        dtype=np.float32,
    )

    activity[target] = 1.0

    result = apply_scar_effect(
        effective_activity=activity,
        scar_state=state,
        target_model_index=target,
    )

    assert np.isclose(
        result[target],
        0.75,
    )


def test_scar_effect_disappears_after_recovery():
    state = build_scar(
        session_id="session-A",
        current_generation=0,
    )

    state = advance_scar(
        state=state,
        session_id="session-B",
    )

    state = advance_scar(
        state=state,
        session_id="session-C",
    )

    target = SCAR_TARGET_POOL[0]

    activity = np.zeros(
        max(SCAR_TARGET_POOL) + 1,
        dtype=np.float32,
    )

    activity[target] = 1.0

    result = apply_scar_effect(
        effective_activity=activity,
        scar_state=state,
        target_model_index=target,
    )

    assert np.isclose(
        result[target],
        1.0,
    )


def test_scar_does_not_modify_original_activity():
    state = build_scar(
        session_id="session-A",
        current_generation=0,
    )

    target = SCAR_TARGET_POOL[0]

    activity = np.zeros(
        max(SCAR_TARGET_POOL) + 1,
        dtype=np.float32,
    )

    activity[target] = 1.0
    original = activity.copy()

    apply_scar_effect(
        effective_activity=activity,
        scar_state=state,
        target_model_index=target,
    )

    np.testing.assert_array_equal(
        activity,
        original,
    )
