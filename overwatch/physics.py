from __future__ import annotations

from dataclasses import asdict, dataclass
from math import isfinite
from typing import Any

from .events import TelemetryEventV1
from .storage import TelemetryStorage


CELL67_COORDINATE_FRAME_V1 = {
    "frame_id": "CELL-67.WORLD.v1",
    "units": {
        "distance": "meter",
        "angle": "degree",
        "force": "newton",
        "velocity": "meter_per_second",
    },
    "axes": {
        "+x": "subject_right",
        "+y": "forward_from_desk",
        "+z": "up",
    },
    "origin": "CELL-67 canonical desk-center floor projection",
}


def _finite(value: float, name: str) -> float:
    value = float(value)
    if not isfinite(value):
        raise ValueError(f"{name} must be finite")
    return value


def _nonnegative(value: float, name: str) -> float:
    value = _finite(value, name)
    if value < 0.0:
        raise ValueError(f"{name} must be non-negative")
    return value


@dataclass(frozen=True)
class Vec3V1:
    x: float
    y: float
    z: float

    def __post_init__(self) -> None:
        _finite(self.x, "x")
        _finite(self.y, "y")
        _finite(self.z, "z")

    def to_dict(self) -> dict[str, float]:
        return {
            "x": float(self.x),
            "y": float(self.y),
            "z": float(self.z),
        }


@dataclass(frozen=True)
class ConstraintStateV1:
    environment_id: str
    tether_enabled: bool
    tether_anchor: Vec3V1
    tether_length_m: float
    tether_tension_n: float
    root_position: Vec3V1
    root_displacement_m: float
    constraint_saturated: bool = False

    def __post_init__(self) -> None:
        _nonnegative(self.tether_length_m, "tether_length_m")
        _nonnegative(self.tether_tension_n, "tether_tension_n")
        _nonnegative(self.root_displacement_m, "root_displacement_m")

        if not self.tether_enabled and self.tether_tension_n != 0.0:
            raise ValueError(
                "tether tension must be zero when tether is disabled"
            )

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["tether_anchor"] = self.tether_anchor.to_dict()
        data["root_position"] = self.root_position.to_dict()
        return data


@dataclass(frozen=True)
class ContactPointV1:
    contact_id: str
    body_part: str
    surface_id: str
    position: Vec3V1
    normal_force_n: float
    tangential_force_n: float = 0.0
    slipping: bool = False

    def __post_init__(self) -> None:
        _nonnegative(self.normal_force_n, "normal_force_n")
        _finite(self.tangential_force_n, "tangential_force_n")

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["position"] = self.position.to_dict()
        return data


@dataclass(frozen=True)
class AchievedPoseV1:
    root_position: Vec3V1
    body_pitch_deg: float = 0.0
    body_roll_deg: float = 0.0
    body_yaw_deg: float = 0.0

    def __post_init__(self) -> None:
        _finite(self.body_pitch_deg, "body_pitch_deg")
        _finite(self.body_roll_deg, "body_roll_deg")
        _finite(self.body_yaw_deg, "body_yaw_deg")

    def to_dict(self) -> dict[str, Any]:
        return {
            "root_position": self.root_position.to_dict(),
            "body_pitch_deg": float(self.body_pitch_deg),
            "body_roll_deg": float(self.body_roll_deg),
            "body_yaw_deg": float(self.body_yaw_deg),
        }


def emit_constraint_state(
    storage: TelemetryStorage,
    *,
    run_id: str,
    constraint: ConstraintStateV1,
    source_motor_event_id: str | None = None,
    sample_index: int | None = None,
    experiment_id: str | None = None,
    subject_id: str | None = "MQ-001",
) -> TelemetryEventV1:
    event = TelemetryEventV1(
        event_type="constraint.state",
        run_id=run_id,
        component="physics",
        experiment_id=experiment_id,
        subject_id=subject_id,
        payload={
            "coordinate_frame": CELL67_COORDINATE_FRAME_V1,
            "constraint": constraint.to_dict(),
            "source_motor_event_id": source_motor_event_id,
            "sample_index": sample_index,
        },
        lore_surface="HUD",
    )
    storage.append(event)
    return event


def emit_contact_state(
    storage: TelemetryStorage,
    *,
    run_id: str,
    environment_id: str,
    contacts: tuple[ContactPointV1, ...],
    source_motor_event_id: str | None = None,
    sample_index: int | None = None,
    experiment_id: str | None = None,
    subject_id: str | None = "MQ-001",
) -> TelemetryEventV1:
    event = TelemetryEventV1(
        event_type="contact.state",
        run_id=run_id,
        component="physics",
        experiment_id=experiment_id,
        subject_id=subject_id,
        payload={
            "coordinate_frame": CELL67_COORDINATE_FRAME_V1,
            "environment_id": environment_id,
            "contacts": [contact.to_dict() for contact in contacts],
            "contact_count": len(contacts),
            "source_motor_event_id": source_motor_event_id,
            "sample_index": sample_index,
        },
        lore_surface="HUD",
    )
    storage.append(event)
    return event


def emit_achieved_pose(
    storage: TelemetryStorage,
    *,
    run_id: str,
    pose: AchievedPoseV1,
    source_motor_event_id: str,
    source_constraint_event_id: str | None = None,
    source_contact_event_id: str | None = None,
    sample_index: int | None = None,
    environment_id: str = "CELL-67.v1",
    experiment_id: str | None = None,
    subject_id: str | None = "MQ-001",
) -> TelemetryEventV1:
    event = TelemetryEventV1(
        event_type="physics.pose",
        run_id=run_id,
        component="physics",
        experiment_id=experiment_id,
        subject_id=subject_id,
        payload={
            "coordinate_frame": CELL67_COORDINATE_FRAME_V1,
            "environment_id": environment_id,
            "pose": pose.to_dict(),
            "source_motor_event_id": source_motor_event_id,
            "source_constraint_event_id": source_constraint_event_id,
            "source_contact_event_id": source_contact_event_id,
            "sample_index": sample_index,
            "rendering_boundary": (
                "Panopticon 3D should render achieved pose; motor intent and "
                "physical outcome remain separately inspectable"
            ),
        },
        lore_surface="HUD",
    )
    storage.append(event)
    return event


def emit_physics_transition(
    storage: TelemetryStorage,
    *,
    run_id: str,
    motor_event_id: str,
    constraint_event_id: str | None,
    contact_event_id: str | None,
    pose_event_id: str,
    interpretation: str,
    experiment_id: str | None = None,
    subject_id: str | None = "MQ-001",
) -> TelemetryEventV1:
    event = TelemetryEventV1(
        event_type="physics.transition",
        run_id=run_id,
        component="physics",
        experiment_id=experiment_id,
        subject_id=subject_id,
        payload={
            "motor_event_id": motor_event_id,
            "constraint_event_id": constraint_event_id,
            "contact_event_id": contact_event_id,
            "pose_event_id": pose_event_id,
            "interpretation": interpretation,
            "causal_boundary": (
                "event linkage preserves sequence/provenance and does not by "
                "itself establish scientific causality"
            ),
        },
        lore_surface="HUD",
    )
    storage.append(event)
    return event
