from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .events import TelemetryEventV1
from .storage import TelemetryStorage


def _finite(value: float, name: str) -> float:
    value = float(value)
    if value != value or value in (float("inf"), float("-inf")):
        raise ValueError(f"{name} must be finite")
    return value


def _unit(value: float, name: str) -> float:
    value = _finite(value, name)
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"{name} must be between 0.0 and 1.0")
    return value


@dataclass(frozen=True)
class MotorStateV1:
    """Continuous model-derived motor state for Panopticon 3D.

    Angles are degrees. Drives are normalized [0, 1].
    """

    head_yaw_deg: float = 0.0
    head_pitch_deg: float = 0.0

    left_antenna_deg: float = 0.0
    right_antenna_deg: float = 0.0

    left_wing_deg: float = 0.0
    right_wing_deg: float = 0.0
    left_wing_velocity: float = 0.0
    right_wing_velocity: float = 0.0

    body_pitch_deg: float = 0.0
    body_roll_deg: float = 0.0
    body_yaw_deg: float = 0.0

    locomotor_drive: float = 0.0
    grooming_drive: float = 0.0
    courtship_drive: float = 0.0
    escape_drive: float = 0.0

    left_foreleg: tuple[float, ...] = ()
    right_foreleg: tuple[float, ...] = ()
    left_midleg: tuple[float, ...] = ()
    right_midleg: tuple[float, ...] = ()
    left_hindleg: tuple[float, ...] = ()
    right_hindleg: tuple[float, ...] = ()

    def __post_init__(self) -> None:
        scalar_fields = {
            "head_yaw_deg": self.head_yaw_deg,
            "head_pitch_deg": self.head_pitch_deg,
            "left_antenna_deg": self.left_antenna_deg,
            "right_antenna_deg": self.right_antenna_deg,
            "left_wing_deg": self.left_wing_deg,
            "right_wing_deg": self.right_wing_deg,
            "left_wing_velocity": self.left_wing_velocity,
            "right_wing_velocity": self.right_wing_velocity,
            "body_pitch_deg": self.body_pitch_deg,
            "body_roll_deg": self.body_roll_deg,
            "body_yaw_deg": self.body_yaw_deg,
        }
        for name, value in scalar_fields.items():
            _finite(value, name)

        drives = {
            "locomotor_drive": self.locomotor_drive,
            "grooming_drive": self.grooming_drive,
            "courtship_drive": self.courtship_drive,
            "escape_drive": self.escape_drive,
        }
        for name, value in drives.items():
            _unit(value, name)

        for name in (
            "left_foreleg",
            "right_foreleg",
            "left_midleg",
            "right_midleg",
            "left_hindleg",
            "right_hindleg",
        ):
            values = getattr(self, name)
            for i, value in enumerate(values):
                _finite(value, f"{name}[{i}]")

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        for key in (
            "left_foreleg",
            "right_foreleg",
            "left_midleg",
            "right_midleg",
            "left_hindleg",
            "right_hindleg",
        ):
            data[key] = list(data[key])
        return data


def emit_motor_state(
    storage: TelemetryStorage,
    *,
    run_id: str,
    motor: MotorStateV1,
    source_neural_state_ref: str | None = None,
    source_event_id: str | None = None,
    sample_index: int | None = None,
    experiment_id: str | None = None,
    subject_id: str | None = "MQ-001",
) -> TelemetryEventV1:
    event = TelemetryEventV1(
        event_type="motor.state",
        run_id=run_id,
        component="motor",
        experiment_id=experiment_id,
        subject_id=subject_id,
        payload={
            "motor": motor.to_dict(),
            "source_neural_state_ref": source_neural_state_ref,
            "source_event_id": source_event_id,
            "sample_index": sample_index,
            "interpretation_boundary": (
                "model-derived motor telemetry; Panopticon should render this "
                "state rather than substitute canned action animations"
            ),
        },
        lore_surface="HUD",
    )
    storage.append(event)
    return event


def emit_motor_transition(
    storage: TelemetryStorage,
    *,
    run_id: str,
    before_ref: str | None,
    after_ref: str | None,
    changed_channels: list[str],
    source_event_id: str | None = None,
    experiment_id: str | None = None,
    subject_id: str | None = "MQ-001",
) -> TelemetryEventV1:
    event = TelemetryEventV1(
        event_type="motor.transition",
        run_id=run_id,
        component="motor",
        experiment_id=experiment_id,
        subject_id=subject_id,
        payload={
            "before_ref": before_ref,
            "after_ref": after_ref,
            "changed_channels": list(changed_channels),
            "source_event_id": source_event_id,
        },
        lore_surface="HUD",
    )
    storage.append(event)
    return event


def emit_motor_activity(
    storage: TelemetryStorage,
    *,
    run_id: str,
    channel_activity: dict[str, float],
    source_neural_state_ref: str | None = None,
    experiment_id: str | None = None,
    subject_id: str | None = "MQ-001",
) -> TelemetryEventV1:
    normalized = {
        str(name): _unit(value, str(name))
        for name, value in channel_activity.items()
    }

    event = TelemetryEventV1(
        event_type="motor.activity",
        run_id=run_id,
        component="motor",
        experiment_id=experiment_id,
        subject_id=subject_id,
        payload={
            "channels": normalized,
            "source_neural_state_ref": source_neural_state_ref,
        },
        lore_surface="HUD",
    )
    storage.append(event)
    return event
