import json

from overwatch.integration import (
    ReferencePhysicsConfigV1,
    run_reference_neural_motor_physics_step,
)
from overwatch.neural_motor import ReferenceNeuralMotorAdapterV1
from overwatch.storage import LocalJsonlStorage


def _rows(path):
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
    ]


def test_reference_integration_emits_full_event_chain(tmp_path):
    path = tmp_path / "integration.jsonl"
    result = run_reference_neural_motor_physics_step(
        LocalJsonlStorage(path),
        run_id="run-1",
        neural_state={"locomotor": 0.8},
        adapter=ReferenceNeuralMotorAdapterV1(),
        neural_state_ref="neural://sample-42",
        sample_index=42,
    )

    rows = _rows(path)
    types = [row["event_type"] for row in rows]

    assert types == [
        "motor.state",
        "constraint.state",
        "contact.state",
        "physics.pose",
        "physics.transition",
    ]
    assert result.motor_event_id == rows[0]["event_id"]
    assert result.pose_event_id == rows[3]["event_id"]


def test_reference_integration_preserves_provenance_links(tmp_path):
    path = tmp_path / "integration.jsonl"
    run_reference_neural_motor_physics_step(
        LocalJsonlStorage(path),
        run_id="run-2",
        neural_state={"locomotor": 0.9},
        adapter=ReferenceNeuralMotorAdapterV1(),
        neural_state_ref="neural://sample-99",
        sample_index=99,
    )

    motor, constraint, contact, pose, transition = _rows(path)

    assert motor["payload"]["source_neural_state_ref"] == "neural://sample-99"
    assert constraint["payload"]["source_motor_event_id"] == motor["event_id"]
    assert contact["payload"]["source_motor_event_id"] == motor["event_id"]
    assert pose["payload"]["source_motor_event_id"] == motor["event_id"]
    assert pose["payload"]["source_constraint_event_id"] == constraint["event_id"]
    assert pose["payload"]["source_contact_event_id"] == contact["event_id"]
    assert transition["payload"]["pose_event_id"] == pose["event_id"]


def test_reference_tether_limits_forward_motion_and_creates_tension(tmp_path):
    path = tmp_path / "integration.jsonl"
    run_reference_neural_motor_physics_step(
        LocalJsonlStorage(path),
        run_id="run-3",
        neural_state={"locomotor": 1.0},
        adapter=ReferenceNeuralMotorAdapterV1(),
        neural_state_ref="neural://max-drive",
    )

    rows = _rows(path)
    constraint = rows[1]
    pose = rows[3]

    assert constraint["payload"]["constraint"]["constraint_saturated"] is True
    assert constraint["payload"]["constraint"]["tether_tension_n"] > 0.0
    assert pose["payload"]["pose"]["root_position"]["y"] == 0.03


def test_reference_tethered_drive_can_create_bracing_contacts(tmp_path):
    path = tmp_path / "integration.jsonl"
    run_reference_neural_motor_physics_step(
        LocalJsonlStorage(path),
        run_id="run-4",
        neural_state={"locomotor": 1.0},
        adapter=ReferenceNeuralMotorAdapterV1(),
        neural_state_ref="neural://brace",
    )

    contact = _rows(path)[2]

    assert contact["payload"]["contact_count"] == 2
    body_parts = {
        c["body_part"]
        for c in contact["payload"]["contacts"]
    }
    assert body_parts == {
        "leg.front_left.tarsus",
        "leg.front_right.tarsus",
    }


def test_birthday_reference_config_allows_untethered_forward_motion(tmp_path):
    path = tmp_path / "integration.jsonl"
    config = ReferencePhysicsConfigV1(
        environment_id="CELL-67.BIRTHDAY.v1",
        tether_enabled=False,
    )

    run_reference_neural_motor_physics_step(
        LocalJsonlStorage(path),
        run_id="run-birthday",
        neural_state={"locomotor": 1.0},
        adapter=ReferenceNeuralMotorAdapterV1(),
        neural_state_ref="neural://birthday-roam",
        config=config,
    )

    constraint = _rows(path)[1]["payload"]["constraint"]
    pose = _rows(path)[3]["payload"]["pose"]

    assert constraint["tether_enabled"] is False
    assert constraint["tether_tension_n"] == 0.0
    assert pose["root_position"]["y"] == 0.1
