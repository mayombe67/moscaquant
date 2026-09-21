from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from .behavior import emit_state_transition
from .motor import emit_motor_state
from .neural_motor import NeuralMotorAdapterV1
from .physics import (
    AchievedPoseV1,
    ConstraintStateV1,
    ContactPointV1,
    Vec3V1,
    emit_achieved_pose,
    emit_constraint_state,
    emit_contact_state,
    emit_physics_transition,
)
from .storage import TelemetryStorage


@dataclass(frozen=True)
class ReferencePhysicsConfigV1:
    """Deliberately simple deterministic CELL-67 reference physics.

    This proves the integration/provenance path. It is not a production
    neuromechanical solver.
    """

    environment_id: str = "CELL-67.v1"
    tether_enabled: bool = True
    tether_anchor: Vec3V1 = Vec3V1(0.0, 0.0, 0.20)
    tether_length_m: float = 0.35
    max_root_forward_m: float = 0.03
    forward_gain_m: float = 0.10
    tension_gain_n: float = 2.0
    pitch_gain_deg: float = 15.0
    bracing_threshold: float = 0.50


@dataclass(frozen=True)
class IntegrationResultV1:
    motor_event_id: str
    constraint_event_id: str
    contact_event_id: str
    pose_event_id: str
    transition_event_id: str


def _reference_resolve(
    *,
    locomotor_drive: float,
    config: ReferencePhysicsConfigV1,
) -> tuple[ConstraintStateV1, tuple[ContactPointV1, ...], AchievedPoseV1]:
    requested_forward = max(0.0, float(locomotor_drive)) * config.forward_gain_m

    if config.tether_enabled:
        achieved_forward = min(requested_forward, config.max_root_forward_m)
        blocked_forward = max(0.0, requested_forward - achieved_forward)
        tension = blocked_forward * config.tension_gain_n
        saturated = requested_forward > config.max_root_forward_m
    else:
        achieved_forward = requested_forward
        blocked_forward = 0.0
        tension = 0.0
        saturated = False

    root = Vec3V1(0.0, achieved_forward, 0.08)

    constraint = ConstraintStateV1(
        environment_id=config.environment_id,
        tether_enabled=config.tether_enabled,
        tether_anchor=config.tether_anchor,
        tether_length_m=config.tether_length_m,
        tether_tension_n=tension,
        root_position=root,
        root_displacement_m=achieved_forward,
        constraint_saturated=saturated,
    )

    contacts: tuple[ContactPointV1, ...]
    if config.tether_enabled and locomotor_drive >= config.bracing_threshold and saturated:
        contacts = (
            ContactPointV1(
                contact_id="reference.front-left-brace",
                body_part="leg.front_left.tarsus",
                surface_id="desk.primary.surface",
                position=Vec3V1(-0.02, achieved_forward + 0.05, 0.75),
                normal_force_n=0.05 + blocked_forward,
                tangential_force_n=blocked_forward,
                slipping=False,
            ),
            ContactPointV1(
                contact_id="reference.front-right-brace",
                body_part="leg.front_right.tarsus",
                surface_id="desk.primary.surface",
                position=Vec3V1(0.02, achieved_forward + 0.05, 0.75),
                normal_force_n=0.05 + blocked_forward,
                tangential_force_n=blocked_forward,
                slipping=False,
            ),
        )
    else:
        contacts = ()

    pose = AchievedPoseV1(
        root_position=root,
        body_pitch_deg=min(
            config.pitch_gain_deg,
            max(0.0, locomotor_drive) * config.pitch_gain_deg,
        ),
        body_roll_deg=0.0,
        body_yaw_deg=0.0,
    )

    return constraint, contacts, pose


def run_reference_neural_motor_physics_step(
    storage: TelemetryStorage,
    *,
    run_id: str,
    neural_state: Mapping[str, float],
    adapter: NeuralMotorAdapterV1,
    neural_state_ref: str,
    config: ReferencePhysicsConfigV1 | None = None,
    sample_index: int | None = None,
    experiment_id: str | None = None,
    subject_id: str | None = "MQ-001",
) -> IntegrationResultV1:
    """Run one deterministic public reference integration step.

    This function exists to prove the evidence chain. It does not claim to be
    production MORTY physics.
    """

    config = config or ReferencePhysicsConfigV1()

    motor = adapter.map_state(neural_state, sample_index=sample_index)
    motor_event = emit_motor_state(
        storage,
        run_id=run_id,
        motor=motor,
        source_neural_state_ref=neural_state_ref,
        sample_index=sample_index,
        experiment_id=experiment_id,
        subject_id=subject_id,
    )

    constraint, contacts, pose = _reference_resolve(
        locomotor_drive=motor.locomotor_drive,
        config=config,
    )

    constraint_event = emit_constraint_state(
        storage,
        run_id=run_id,
        constraint=constraint,
        source_motor_event_id=motor_event.event_id,
        sample_index=sample_index,
        experiment_id=experiment_id,
        subject_id=subject_id,
    )

    contact_event = emit_contact_state(
        storage,
        run_id=run_id,
        environment_id=config.environment_id,
        contacts=contacts,
        source_motor_event_id=motor_event.event_id,
        sample_index=sample_index,
        experiment_id=experiment_id,
        subject_id=subject_id,
    )

    pose_event = emit_achieved_pose(
        storage,
        run_id=run_id,
        pose=pose,
        source_motor_event_id=motor_event.event_id,
        source_constraint_event_id=constraint_event.event_id,
        source_contact_event_id=contact_event.event_id,
        sample_index=sample_index,
        environment_id=config.environment_id,
        experiment_id=experiment_id,
        subject_id=subject_id,
    )

    transition_event = emit_physics_transition(
        storage,
        run_id=run_id,
        motor_event_id=motor_event.event_id,
        constraint_event_id=constraint_event.event_id,
        contact_event_id=contact_event.event_id,
        pose_event_id=pose_event.event_id,
        interpretation=(
            "reference integration step: neural state mapped to motor intent, "
            "then resolved through deterministic CELL-67 reference constraints"
        ),
        experiment_id=experiment_id,
        subject_id=subject_id,
    )

    return IntegrationResultV1(
        motor_event_id=motor_event.event_id,
        constraint_event_id=constraint_event.event_id,
        contact_event_id=contact_event.event_id,
        pose_event_id=pose_event.event_id,
        transition_event_id=transition_event.event_id,
    )
