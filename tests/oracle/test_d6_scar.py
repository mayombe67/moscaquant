from __future__ import annotations

from oracle.d6_scar import (
    SCAR_VERSION,
    ScarPhase,
    advance_scar,
    build_scar,
    scar_can_stack,
)
from oracle.reinforcement import ReinforcementCondition


def test_scar_begins_in_origin_session():
    state = build_scar(
        session_id="session-A",
        current_generation=42,
    )

    assert state.schema_version == SCAR_VERSION

    assert (
        state.condition
        is ReinforcementCondition.SC_05_SCAR_TISSUE
    )

    assert state.origin_session_id == "session-A"
    assert state.following_session_id is None
    assert state.activated_generation == 42
    assert state.phase is ScarPhase.CURRENT_SESSION
    assert state.active is True


def test_scar_persists_for_remainder_of_origin_session():
    state = build_scar(
        session_id="session-A",
        current_generation=42,
    )

    later = advance_scar(
        state=state,
        session_id="session-A",
    )

    assert later == state


def test_scar_crosses_into_exactly_one_following_session():
    state = build_scar(
        session_id="session-A",
        current_generation=42,
    )

    following = advance_scar(
        state=state,
        session_id="session-B",
    )

    assert following.origin_session_id == "session-A"
    assert following.following_session_id == "session-B"
    assert following.phase is ScarPhase.FOLLOWING_SESSION
    assert following.active is True


def test_scar_persists_through_following_session():
    state = build_scar(
        session_id="session-A",
        current_generation=42,
    )

    following = advance_scar(
        state=state,
        session_id="session-B",
    )

    later = advance_scar(
        state=following,
        session_id="session-B",
    )

    assert later == following


def test_scar_recovers_after_following_session():
    state = build_scar(
        session_id="session-A",
        current_generation=42,
    )

    following = advance_scar(
        state=state,
        session_id="session-B",
    )

    recovered = advance_scar(
        state=following,
        session_id="session-C",
    )

    assert recovered.phase is ScarPhase.RECOVERED
    assert recovered.active is False


def test_scar_does_not_reactivate_after_recovery():
    state = build_scar(
        session_id="session-A",
        current_generation=42,
    )

    state = advance_scar(
        state=state,
        session_id="session-B",
    )

    state = advance_scar(
        state=state,
        session_id="session-C",
    )

    final = advance_scar(
        state=state,
        session_id="session-D",
    )

    assert final == state
    assert final.active is False


def test_active_scar_cannot_stack():
    state = build_scar(
        session_id="session-A",
        current_generation=42,
    )

    assert scar_can_stack(state) is False


def test_recovered_scar_can_be_replaced_by_future_event():
    state = build_scar(
        session_id="session-A",
        current_generation=42,
    )

    state = advance_scar(
        state=state,
        session_id="session-B",
    )

    state = advance_scar(
        state=state,
        session_id="session-C",
    )

    assert scar_can_stack(state) is True
