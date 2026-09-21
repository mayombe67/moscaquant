import pytest

from overwatch.physics import (
    AchievedPoseV1,
    ConstraintStateV1,
    ContactPointV1,
    Vec3V1,
    emit_achieved_pose,
    emit_constraint_state,
    emit_contact_state,
    emit_physics_transition,
)
from overwatch.storage import LocalJsonlStorage


def test_tethered_constraint_state_records_tension(tmp_path):
    state = ConstraintStateV1(
        environment_id="CELL-67.v1",
        tether_enabled=True,
        tether_anchor=Vec3V1(0.0, 0.0, 0.2),
        tether_length_m=0.35,
        tether_tension_n=0.42,
        root_position=Vec3V1(0.0, 0.20, 0.08),
        root_displacement_m=0.20,
        constraint_saturated=True,
    )

    event = emit_constraint_state(
        LocalJsonlStorage(tmp_path / "physics.jsonl"),
        run_id="run-1",
        constraint=state,
        source_motor_event_id="motor-42",
        sample_index=42,
    )

    assert event.event_type == "constraint.state"
    assert event.payload["constraint"]["tether_tension_n"] == 0.42
    assert event.payload["constraint"]["constraint_saturated"] is True
    assert event.payload["coordinate_frame"]["frame_id"] == "CELL-67.WORLD.v1"


def test_untethered_birthday_state_cannot_have_tension():
    with pytest.raises(ValueError):
        ConstraintStateV1(
            environment_id="CELL-67.BIRTHDAY.v1",
            tether_enabled=False,
            tether_anchor=Vec3V1(0, 0, 0),
            tether_length_m=0.35,
            tether_tension_n=0.01,
            root_position=Vec3V1(0, 0, 0),
            root_displacement_m=0.0,
        )


def test_contact_state_records_body_surface_force(tmp_path):
    contact = ContactPointV1(
        contact_id="contact-left-foreleg-desk",
        body_part="leg.front_left.tarsus",
        surface_id="desk.primary.surface",
        position=Vec3V1(-0.02, 0.10, 0.75),
        normal_force_n=0.08,
        tangential_force_n=0.01,
        slipping=False,
    )

    event = emit_contact_state(
        LocalJsonlStorage(tmp_path / "physics.jsonl"),
        run_id="run-2",
        environment_id="CELL-67.v1",
        contacts=(contact,),
        source_motor_event_id="motor-100",
    )

    assert event.event_type == "contact.state"
    assert event.payload["contact_count"] == 1
    assert event.payload["contacts"][0]["body_part"] == "leg.front_left.tarsus"


def test_achieved_pose_stays_separate_from_motor_intent(tmp_path):
    event = emit_achieved_pose(
        LocalJsonlStorage(tmp_path / "physics.jsonl"),
        run_id="run-3",
        pose=AchievedPoseV1(
            root_position=Vec3V1(0.0, 0.03, 0.08),
            body_pitch_deg=12.0,
        ),
        source_motor_event_id="motor-command-forward",
        source_constraint_event_id="constraint-blocked",
        source_contact_event_id="contact-bracing",
    )

    assert event.event_type == "physics.pose"
    assert event.payload["source_motor_event_id"] == "motor-command-forward"
    assert event.payload["pose"]["root_position"]["y"] == 0.03
    assert "motor intent and physical outcome remain separately inspectable" in (
        event.payload["rendering_boundary"]
    )


def test_physics_transition_links_full_chain(tmp_path):
    event = emit_physics_transition(
        LocalJsonlStorage(tmp_path / "physics.jsonl"),
        run_id="run-4",
        motor_event_id="motor-1",
        constraint_event_id="constraint-1",
        contact_event_id="contact-1",
        pose_event_id="pose-1",
        interpretation="forward drive produced tether tension and foreleg bracing",
    )

    assert event.event_type == "physics.transition"
    assert event.payload["motor_event_id"] == "motor-1"
    assert event.payload["pose_event_id"] == "pose-1"
    assert "does not by itself establish scientific causality" in (
        event.payload["causal_boundary"]
    )
