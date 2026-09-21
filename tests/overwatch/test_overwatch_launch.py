from datetime import datetime, timezone

from overwatch.environment import CELL67_BIRTHDAY_ID, CELL67_STANDARD_ID
from overwatch.launch import (
    BIRTHDAY_PHASE,
    COUNTDOWN_PHASE,
    LAUNCH_TIMESTAMP_UTC,
    emit_birthday_window_closed,
    emit_launch_state,
    emit_launch_transition,
    launch_state_for,
)
from overwatch.storage import LocalJsonlStorage


def test_prelaunch_state_is_beta_countdown():
    state = launch_state_for(datetime(2026, 10, 1, tzinfo=timezone.utc))

    assert state.phase == COUNTDOWN_PHASE
    assert state.environment_id == CELL67_STANDARD_ID
    assert state.beta_label_visible is True
    assert state.countdown_visible is True
    assert state.birthday_privileges_active is False


def test_launch_time_activates_birthday_environment():
    state = launch_state_for(LAUNCH_TIMESTAMP_UTC)

    assert state.phase == BIRTHDAY_PHASE
    assert state.environment_id == CELL67_BIRTHDAY_ID
    assert state.beta_label_visible is False
    assert state.countdown_visible is False
    assert state.birthday_privileges_active is True


def test_launch_state_emits_employee_activation_copy(tmp_path):
    storage = LocalJsonlStorage(tmp_path / "launch.jsonl")
    state = launch_state_for(datetime(2026, 10, 10, tzinfo=timezone.utc))

    event = emit_launch_state(
        storage,
        run_id="launch-run",
        state=state,
        trigger="site_render",
    )

    assert event.event_type == "launch.state"
    assert event.payload["presentation_copy"]["countdown_label"] == (
        "EMPLOYEE ACTIVATION WINDOW"
    )


def test_launch_transition_records_environment_change(tmp_path):
    event = emit_launch_transition(
        LocalJsonlStorage(tmp_path / "launch.jsonl"),
        run_id="launch-run",
        from_phase=COUNTDOWN_PHASE,
        to_phase=BIRTHDAY_PHASE,
        reason="launch_timestamp_reached",
        environment_from=CELL67_STANDARD_ID,
        environment_to=CELL67_BIRTHDAY_ID,
    )

    assert event.event_type == "launch.transition"
    assert event.payload["environment_to"] == CELL67_BIRTHDAY_ID


def test_birthday_window_close_restores_standard_cell(tmp_path):
    event = emit_birthday_window_closed(
        LocalJsonlStorage(tmp_path / "launch.jsonl"),
        run_id="launch-run",
        reason="birthday_session_complete",
    )

    assert event.event_type == "launch.birthday_window_closed"
    assert event.payload["restore_environment_id"] == CELL67_STANDARD_ID
    assert event.payload["clear_temporary_wearables"] is True
