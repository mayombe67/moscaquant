from __future__ import annotations

import numpy as np

from oracle.d6_execution import (
    build_d6_execution_plan,
)
from oracle.plasticity_state import (
    apply_plasticity_update,
    build_empty_plasticity_state,
)
from oracle.reinforcement import (
    ReinforcementCondition,
)
from oracle.selector import select_d6


EXPERIMENT = "d6-execution-test"
SESSION = "session-001"


def select_condition(
    condition: ReinforcementCondition,
    *,
    plasticity_active: bool = True,
):
    for seed in range(1000):
        result = select_d6(
            seed=seed,
            experiment_id=EXPERIMENT,
            session_id=SESSION,
            plasticity_active=plasticity_active,
        )

        if result.selection.condition is condition:
            return seed, result

    raise AssertionError(
        f"could not select {condition}"
    )


def test_shock_builds_activity_modifier():
    seed, result = select_condition(
        ReinforcementCondition.SC_01_SHOCK
    )

    plan = build_d6_execution_plan(
        d6_result=result,
        seed=seed,
        experiment_id=EXPERIMENT,
        session_id=SESSION,
        readout_indices=np.array(
            [1, 2],
            dtype=np.int64,
        ),
    )

    assert plan.shock is not None
    assert plan.activity_modifier is not None

    activity = np.zeros(
        140000,
        dtype=np.float32,
    )

    modified = plan.activity_modifier(
        activity,
        0,
    )

    assert (
        modified[
            plan.shock.target_model_index
        ]
        == 0.75
    )


def test_darkness_builds_stimulus_modifier():
    seed, result = select_condition(
        ReinforcementCondition.SC_02_DARKNESS
    )

    plan = build_d6_execution_plan(
        d6_result=result,
        seed=seed,
        experiment_id=EXPERIMENT,
        session_id=SESSION,
        readout_indices=np.array(
            [1],
            dtype=np.int64,
        ),
    )

    stimulus = np.ones(
        8,
        dtype=np.float32,
    )

    modified = plan.stimulus_modifier(
        stimulus,
        0,
    )

    np.testing.assert_allclose(
        modified,
        stimulus * 0.25,
    )


def test_bad_synapse_uses_existing_plasticity():
    seed, result = select_condition(
        ReinforcementCondition.SC_03_BAD_SYNAPSE
    )

    state = build_empty_plasticity_state()

    state = apply_plasticity_update(
        state,
        presynaptic=1,
        postsynaptic=2,
        baseline_artifact_id="baseline",
        baseline_weight=4.0,
        session_id="prior",
        evidence_reference="evidence",
    )

    plan = build_d6_execution_plan(
        d6_result=result,
        seed=seed,
        experiment_id=EXPERIMENT,
        session_id=SESSION,
        readout_indices=np.array(
            [2],
            dtype=np.int64,
        ),
        plasticity_state=state,
    )

    activity = np.array(
        [0.0, 1.0, 0.0],
        dtype=np.float32,
    )

    synaptic = np.array(
        [0.0, 0.0, 4.0],
        dtype=np.float32,
    )

    modified = plan.synaptic_modifier(
        activity,
        synaptic,
    )

    assert np.isclose(
        modified[2],
        3.8,
    )


def test_timeout_builds_readout_modifier():
    seed, result = select_condition(
        ReinforcementCondition.SC_04_TIME_OUT
    )

    plan = build_d6_execution_plan(
        d6_result=result,
        seed=seed,
        experiment_id=EXPERIMENT,
        session_id=SESSION,
        readout_indices=np.array(
            [1, 3],
            dtype=np.int64,
        ),
    )

    voltage = np.ones(
        5,
        dtype=np.float32,
    )

    spikes = np.ones(
        5,
        dtype=np.float32,
    )

    out_voltage, out_spikes = (
        plan.readout_modifier(
            voltage,
            spikes,
            0,
        )
    )

    assert out_voltage[1] == 0.0
    assert out_voltage[3] == 0.0
    assert out_spikes[1] == 0.0
    assert out_spikes[3] == 0.0


def test_scar_carries_into_following_session():
    seed, result = select_condition(
        ReinforcementCondition.SC_05_SCAR_TISSUE
    )

    first = build_d6_execution_plan(
        d6_result=result,
        seed=seed,
        experiment_id=EXPERIMENT,
        session_id=SESSION,
        readout_indices=np.array(
            [1],
            dtype=np.int64,
        ),
    )

    assert first.scar_state is not None
    assert first.scar_state.active

    next_result = select_d6(
        seed=seed,
        experiment_id=EXPERIMENT,
        session_id="session-002",
        plasticity_active=True,
    )

    second = build_d6_execution_plan(
        d6_result=next_result,
        seed=seed,
        experiment_id=EXPERIMENT,
        session_id="session-002",
        readout_indices=np.array(
            [1],
            dtype=np.int64,
        ),
        prior_scar_state=first.scar_state,
        prior_scar_target_model_index=(
            first.scar_target_model_index
        ),
    )

    assert second.scar_state is not None
    assert second.scar_state.active
    assert second.activity_modifier is not None


def test_mercy_builds_activity_modifier():
    seed, result = select_condition(
        ReinforcementCondition.SC_06_MERCY
    )

    plan = build_d6_execution_plan(
        d6_result=result,
        seed=seed,
        experiment_id=EXPERIMENT,
        session_id=SESSION,
        readout_indices=np.array(
            [1],
            dtype=np.int64,
        ),
    )

    target = (
        plan.mercy.target_model_index
    )

    activity = np.zeros(
        140000,
        dtype=np.float32,
    )

    activity[target] = 0.4

    modified = plan.activity_modifier(
        activity,
        0,
    )

    assert np.isclose(
        modified[target],
        0.5,
    )


def test_non_applicable_sc03_has_no_new_intervention():
    seed, result = select_condition(
        ReinforcementCondition.SC_03_BAD_SYNAPSE,
        plasticity_active=False,
    )

    plan = build_d6_execution_plan(
        d6_result=result,
        seed=seed,
        experiment_id=EXPERIMENT,
        session_id=SESSION,
        readout_indices=np.array(
            [1],
            dtype=np.int64,
        ),
    )

    assert not plan.applicable
    assert plan.shock is None
    assert plan.darkness is None
    assert plan.timeout is None
    assert plan.mercy is None
def test_scar_origin_session_starts_at_activation_generation():
    seed, result = select_condition(
        ReinforcementCondition.SC_05_SCAR_TISSUE
    )

    plan = build_d6_execution_plan(
        d6_result=result,
        seed=seed,
        experiment_id=EXPERIMENT,
        session_id=SESSION,
        readout_indices=np.array(
            [1],
            dtype=np.int64,
        ),
        intervention_generation=5,
    )

    target = plan.scar_target_model_index

    activity = np.zeros(
        140000,
        dtype=np.float32,
    )

    activity[target] = 1.0

    before = plan.activity_modifier(
        activity,
        4,
    )

    active = plan.activity_modifier(
        activity,
        5,
    )

    assert np.isclose(
        before[target],
        1.0,
    )

    assert np.isclose(
        active[target],
        0.75,
    )


def test_scar_following_session_active_from_generation_zero():
    seed, result = select_condition(
        ReinforcementCondition.SC_05_SCAR_TISSUE
    )

    first = build_d6_execution_plan(
        d6_result=result,
        seed=seed,
        experiment_id=EXPERIMENT,
        session_id=SESSION,
        readout_indices=np.array(
            [1],
            dtype=np.int64,
        ),
        intervention_generation=5,
    )

    next_result = select_d6(
        seed=seed,
        experiment_id=EXPERIMENT,
        session_id="session-002",
        plasticity_active=True,
    )

    second = build_d6_execution_plan(
        d6_result=next_result,
        seed=seed,
        experiment_id=EXPERIMENT,
        session_id="session-002",
        readout_indices=np.array(
            [1],
            dtype=np.int64,
        ),
        prior_scar_state=first.scar_state,
        prior_scar_target_model_index=(
            first.scar_target_model_index
        ),
    )

    target = second.scar_target_model_index

    activity = np.zeros(
        140000,
        dtype=np.float32,
    )

    activity[target] = 1.0

    modified = second.activity_modifier(
        activity,
        0,
    )

    assert np.isclose(
        modified[target],
        0.75,
    )


def test_scar_target_is_identical_in_following_session():
    seed, result = select_condition(
        ReinforcementCondition.SC_05_SCAR_TISSUE
    )

    first = build_d6_execution_plan(
        d6_result=result,
        seed=seed,
        experiment_id=EXPERIMENT,
        session_id=SESSION,
        readout_indices=np.array(
            [1],
            dtype=np.int64,
        ),
        intervention_generation=5,
    )

    next_result = select_d6(
        seed=seed + 999,
        experiment_id=EXPERIMENT,
        session_id="session-002",
        plasticity_active=True,
    )

    second = build_d6_execution_plan(
        d6_result=next_result,
        seed=seed + 999,
        experiment_id=EXPERIMENT,
        session_id="session-002",
        readout_indices=np.array(
            [1],
            dtype=np.int64,
        ),
        prior_scar_state=first.scar_state,
        prior_scar_target_model_index=(
            first.scar_target_model_index
        ),
    )

    assert (
        second.scar_target_model_index
        == first.scar_target_model_index
    )
