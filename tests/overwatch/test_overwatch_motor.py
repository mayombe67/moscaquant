import pytest

from overwatch.motor import (
    MotorStateV1,
    emit_motor_activity,
    emit_motor_state,
    emit_motor_transition,
)
from overwatch.storage import LocalJsonlStorage


def test_motor_state_emits_model_derived_pose(tmp_path):
    storage = LocalJsonlStorage(tmp_path / "motor.jsonl")
    state = MotorStateV1(
        left_wing_deg=18.0,
        right_wing_deg=11.0,
        left_wing_velocity=2.5,
        right_wing_velocity=1.5,
        body_roll_deg=3.0,
        escape_drive=0.8,
        left_foreleg=(10.0, 20.0, 30.0),
    )

    event = emit_motor_state(
        storage,
        run_id="run-001",
        motor=state,
        source_neural_state_ref="state://neural-42",
        sample_index=42,
    )

    assert event.event_type == "motor.state"
    assert event.payload["motor"]["left_wing_deg"] == 18.0
    assert event.payload["motor"]["left_foreleg"] == [10.0, 20.0, 30.0]
    assert event.payload["source_neural_state_ref"] == "state://neural-42"
    assert "rather than substitute canned action animations" in (
        event.payload["interpretation_boundary"]
    )


def test_motor_drives_must_be_normalized():
    with pytest.raises(ValueError):
        MotorStateV1(escape_drive=1.2)


def test_motor_transition_links_state_refs(tmp_path):
    event = emit_motor_transition(
        LocalJsonlStorage(tmp_path / "motor.jsonl"),
        run_id="run-002",
        before_ref="motor://41",
        after_ref="motor://42",
        changed_channels=["left_wing_deg", "body_roll_deg"],
        source_event_id="evt-d6",
    )

    assert event.event_type == "motor.transition"
    assert event.payload["changed_channels"] == [
        "left_wing_deg",
        "body_roll_deg",
    ]
    assert event.payload["source_event_id"] == "evt-d6"


def test_motor_activity_is_channelized_and_normalized(tmp_path):
    event = emit_motor_activity(
        LocalJsonlStorage(tmp_path / "motor.jsonl"),
        run_id="run-003",
        channel_activity={
            "left_wing_drive": 0.75,
            "right_wing_drive": 0.25,
            "escape_drive": 0.9,
        },
        source_neural_state_ref="state://neural-99",
    )

    assert event.event_type == "motor.activity"
    assert event.payload["channels"]["escape_drive"] == 0.9
    assert event.payload["source_neural_state_ref"] == "state://neural-99"
