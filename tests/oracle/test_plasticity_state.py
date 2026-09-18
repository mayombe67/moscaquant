from __future__ import annotations

import math

import pytest

from oracle.plasticity_state import (
    MIN_MULTIPLIER,
    UPDATE_MULTIPLIER,
    PlasticityStateError,
    apply_plasticity_update,
    build_empty_plasticity_state,
    complete_trading_session,
    get_edge_state,
)


ARTIFACT = "connectome-baseline-v1.npz"


def apply(
    state,
    *,
    session="session-A",
    evidence="credit-event-001",
):
    return apply_plasticity_update(
        state,
        presynaptic=56393,
        postsynaptic=68045,
        baseline_artifact_id=ARTIFACT,
        baseline_weight=2.0,
        session_id=session,
        evidence_reference=evidence,
    )


def test_empty_state_is_hashed():
    state = build_empty_plasticity_state()

    assert state.edges == ()
    assert state.previous_state_hash is None
    assert len(state.state_hash) == 64


def test_first_update_applies_five_percent_reduction():
    state = apply(
        build_empty_plasticity_state()
    )

    edge = get_edge_state(
        state,
        presynaptic=56393,
        postsynaptic=68045,
    )

    assert edge is not None
    assert edge.multiplier == UPDATE_MULTIPLIER == 0.95
    assert edge.update_count == 1


def test_repeated_updates_stack_multiplicatively():
    state = build_empty_plasticity_state()

    state = apply(
        state,
        session="session-A",
        evidence="e1",
    )

    state = apply(
        state,
        session="session-B",
        evidence="e2",
    )

    edge = get_edge_state(
        state,
        presynaptic=56393,
        postsynaptic=68045,
    )

    assert edge is not None

    assert math.isclose(
        edge.multiplier,
        0.95 * 0.95,
    )

    assert edge.update_count == 2


def test_cumulative_reduction_is_clamped_at_twenty_percent():
    state = build_empty_plasticity_state()

    for index in range(20):
        state = apply(
            state,
            session=f"session-{index}",
            evidence=f"e-{index}",
        )

    edge = get_edge_state(
        state,
        presynaptic=56393,
        postsynaptic=68045,
    )

    assert edge is not None
    assert edge.multiplier == MIN_MULTIPLIER == 0.80


def test_update_resets_inactive_session_counter():
    state = apply(
        build_empty_plasticity_state(),
        session="session-A",
    )

    for index in range(3):
        state = complete_trading_session(
            state,
            session_id=f"inactive-{index}",
        )

    edge = get_edge_state(
        state,
        presynaptic=56393,
        postsynaptic=68045,
    )

    assert edge is not None
    assert edge.inactive_completed_sessions == 3

    state = apply(
        state,
        session="session-B",
        evidence="new-credit",
    )

    edge = get_edge_state(
        state,
        presynaptic=56393,
        postsynaptic=68045,
    )

    assert edge is not None
    assert edge.inactive_completed_sessions == 0


def test_no_recovery_before_five_completed_inactive_sessions():
    state = apply(
        build_empty_plasticity_state(),
        session="session-A",
    )

    for index in range(4):
        state = complete_trading_session(
            state,
            session_id=f"inactive-{index}",
        )

    edge = get_edge_state(
        state,
        presynaptic=56393,
        postsynaptic=68045,
    )

    assert edge is not None
    assert edge.multiplier == 0.95
    assert edge.inactive_completed_sessions == 4


def test_recovery_occurs_after_five_completed_inactive_sessions():
    state = apply(
        build_empty_plasticity_state(),
        session="session-A",
    )

    for index in range(5):
        state = complete_trading_session(
            state,
            session_id=f"inactive-{index}",
        )

    edge = get_edge_state(
        state,
        presynaptic=56393,
        postsynaptic=68045,
    )

    assert edge is not None

    assert math.isclose(
        edge.multiplier,
        1.0,
    )

    assert edge.inactive_completed_sessions == 0


def test_update_session_itself_does_not_count_as_inactive():
    state = apply(
        build_empty_plasticity_state(),
        session="session-A",
    )

    state = complete_trading_session(
        state,
        session_id="session-A",
    )

    edge = get_edge_state(
        state,
        presynaptic=56393,
        postsynaptic=68045,
    )

    assert edge is not None
    assert edge.multiplier == 0.95
    assert edge.inactive_completed_sessions == 0


def test_state_hash_chain_advances():
    first = build_empty_plasticity_state()

    second = apply(first)

    third = complete_trading_session(
        second,
        session_id="session-A",
    )

    assert second.previous_state_hash == first.state_hash
    assert third.previous_state_hash == second.state_hash

    assert first.state_hash != second.state_hash
    assert second.state_hash != third.state_hash


def test_duplicate_session_completion_is_rejected():
    state = apply(
        build_empty_plasticity_state()
    )

    state = complete_trading_session(
        state,
        session_id="session-A",
    )

    with pytest.raises(
        PlasticityStateError,
        match="already completed",
    ):
        complete_trading_session(
            state,
            session_id="session-A",
        )
