from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .events import TelemetryEventV1
from .storage import TelemetryStorage


def _bounded_unit(value: float, name: str) -> float:
    value = float(value)
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"{name} must be between 0.0 and 1.0")
    return value


@dataclass(frozen=True)
class MoodVectorV1:
    """Normalized internal-state indicators for visualization and analysis.

    These are telemetry variables, not claims of subjective human emotion.
    """

    hunger: float
    arousal: float
    courtship_drive: float
    threat: float
    fatigue: float
    reward: float
    punishment: float
    abnormal_state: float = 0.0
    sugar_cube_state: float = 0.0

    def __post_init__(self) -> None:
        for name, value in asdict(self).items():
            _bounded_unit(value, name)

    def to_dict(self) -> dict[str, float]:
        return {name: float(value) for name, value in asdict(self).items()}


def emit_mood_state(
    storage: TelemetryStorage,
    *,
    run_id: str,
    mood: MoodVectorV1,
    experiment_id: str | None = None,
    subject_id: str | None = "MQ-001",
    source_ref: str | None = None,
) -> TelemetryEventV1:
    event = TelemetryEventV1(
        event_type="state.mood",
        run_id=run_id,
        component="behavior",
        experiment_id=experiment_id,
        subject_id=subject_id,
        artifact_ref=source_ref,
        payload={
            "scale": "normalized_unit_interval",
            "indicators": mood.to_dict(),
            "interpretation_boundary": (
                "internal-state telemetry; not evidence of subjective human emotion"
            ),
        },
        lore_surface="HUD",
    )
    storage.append(event)
    return event


def emit_state_transition(
    storage: TelemetryStorage,
    *,
    run_id: str,
    state_name: str,
    before: Any,
    after: Any,
    cause_event_id: str | None = None,
    experiment_id: str | None = None,
    subject_id: str | None = "MQ-001",
) -> TelemetryEventV1:
    event = TelemetryEventV1(
        event_type="state.transition",
        run_id=run_id,
        component="behavior",
        experiment_id=experiment_id,
        subject_id=subject_id,
        payload={
            "state_name": state_name,
            "before": before,
            "after": after,
            "cause_event_id": cause_event_id,
        },
        lore_surface="HUD",
    )
    storage.append(event)
    return event


def emit_decision_trace(
    storage: TelemetryStorage,
    *,
    run_id: str,
    input_ref: str | None,
    encoded_state_ref: str | None,
    oracle_proposal: Any,
    warden_disposition: str,
    final_output: Any,
    experiment_id: str | None = None,
    subject_id: str | None = "MQ-001",
) -> TelemetryEventV1:
    event = TelemetryEventV1(
        event_type="decision.trace",
        run_id=run_id,
        component="decision",
        experiment_id=experiment_id,
        subject_id=subject_id,
        payload={
            "input_ref": input_ref,
            "encoded_state_ref": encoded_state_ref,
            "oracle_proposal": oracle_proposal,
            "warden_disposition": warden_disposition,
            "final_output": final_output,
        },
        lore_surface="HUD",
    )
    storage.append(event)
    return event


def emit_reinforcement(
    storage: TelemetryStorage,
    *,
    run_id: str,
    method: str,
    intensity: float,
    duration_seconds: float | None,
    trigger_reason: str,
    target_ref: str | None = None,
    outcome: str | None = None,
    experiment_id: str | None = None,
    subject_id: str | None = "MQ-001",
) -> TelemetryEventV1:
    intensity = _bounded_unit(intensity, "intensity")

    event = TelemetryEventV1(
        event_type="reinforcement.applied",
        run_id=run_id,
        component="reinforcement",
        experiment_id=experiment_id,
        subject_id=subject_id,
        payload={
            "method": method,
            "intensity": intensity,
            "duration_seconds": duration_seconds,
            "trigger_reason": trigger_reason,
            "target_ref": target_ref,
            "outcome": outcome,
        },
        lore_surface="KILLFEED",
    )
    storage.append(event)
    return event


def emit_lineage(
    storage: TelemetryStorage,
    *,
    run_id: str,
    checkpoint_ref: str,
    parent_checkpoint_ref: str | None,
    generation: int,
    fork_reason: str,
    canonical_codename: str | None = None,
    status: str = "candidate",
    experiment_id: str | None = None,
    subject_id: str | None = "MQ-001",
) -> TelemetryEventV1:
    if generation < 0:
        raise ValueError("generation must be non-negative")

    event = TelemetryEventV1(
        event_type="lineage.checkpoint",
        run_id=run_id,
        component="lineage",
        experiment_id=experiment_id,
        subject_id=subject_id,
        artifact_ref=checkpoint_ref,
        payload={
            "parent_checkpoint_ref": parent_checkpoint_ref,
            "generation": generation,
            "fork_reason": fork_reason,
            "canonical_codename": canonical_codename,
            "status": status,
            "science_boundary": (
                "lineage/promotion labels do not constitute scientific evidence"
            ),
        },
        lore_surface="RESPAWN POINT",
    )
    storage.append(event)
    return event
