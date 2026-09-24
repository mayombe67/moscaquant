from __future__ import annotations

"""Versioned physical-environment manifests for CELL-67 reference physics.

This module freezes provenance for the deterministic public reference resolver.
It does not claim to describe the future production room/collision solver.
"""

from dataclasses import dataclass
import hashlib
import json
from typing import Any

from .environment import (
    CELL67_BIRTHDAY_ID,
    CELL67_STANDARD_ID,
    EnvironmentConfigV1,
    cell67_birthday,
    cell67_standard,
)
from .events import TelemetryEventV1
from .integration import ReferencePhysicsConfigV1
from .physics import CELL67_COORDINATE_FRAME_V1
from .storage import TelemetryStorage


MANIFEST_SCHEMA_ID_V1 = "CELL-67.PHYSICAL-ENVIRONMENT-MANIFEST.v1"
REFERENCE_PHYSICS_PROFILE_ID_V1 = "CELL-67.REFERENCE-PHYSICS.v1"
WORLD_FRAME_ID_V1 = CELL67_COORDINATE_FRAME_V1["frame_id"]

# Constants below are already hard-coded in the deterministic public resolver.
# Freezing them here makes that implementation state hashable and reviewable.
REFERENCE_RESOLVER_CONSTANTS_V1 = {
    "root_lateral_x_m": 0.0,
    "root_height_z_m": 0.08,
    "brace_contact_ids": [
        "reference.front-left-brace",
        "reference.front-right-brace",
    ],
    "brace_body_parts": [
        "leg.front_left.tarsus",
        "leg.front_right.tarsus",
    ],
    "brace_lateral_x_m": [-0.02, 0.02],
    "brace_forward_offset_m": 0.05,
    "brace_height_z_m": 0.75,
    "brace_normal_force_bias_n": 0.05,
    "brace_surface_id": "desk.primary.surface",
}

REFERENCE_SURFACE_IDS_V1 = ("desk.primary.surface",)

UNFROZEN_PRODUCTION_GEOMETRY_V1 = (
    "room_collision_geometry",
    "prop_collision_shapes_and_world_poses",
    "production_joint_contact_geometry",
)


@dataclass(frozen=True)
class PhysicalEnvironmentManifestV1:
    payload: dict[str, Any]

    def canonical_json(self) -> str:
        return json.dumps(
            self.payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )

    def sha256(self) -> str:
        return hashlib.sha256(self.canonical_json().encode("utf-8")).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        return {
            "manifest_sha256": self.sha256(),
            "manifest": self.payload,
        }


def _physical_props(environment: EnvironmentConfigV1) -> list[dict[str, Any]]:
    props: list[dict[str, Any]] = []
    for prop in environment.props:
        if prop.presentation_only:
            continue
        props.append(
            {
                "prop_id": prop.prop_id,
                "kind": prop.kind,
                "interactive": bool(prop.interactive),
                "wearable": bool(prop.wearable),
                "consumable": bool(prop.consumable),
                "attractive": bool(prop.attractive),
                "persistent_after_session": bool(prop.persistent_after_session),
            }
        )
    return sorted(props, key=lambda item: item["prop_id"])


def _reference_physics_parameters(
    physics: ReferencePhysicsConfigV1,
) -> dict[str, Any]:
    return {
        "environment_id": physics.environment_id,
        "tether_enabled": bool(physics.tether_enabled),
        "tether_anchor_m": physics.tether_anchor.to_dict(),
        "tether_length_m": float(physics.tether_length_m),
        "max_root_forward_m": float(physics.max_root_forward_m),
        "forward_gain_m": float(physics.forward_gain_m),
        "tension_gain_n": float(physics.tension_gain_n),
        "pitch_gain_deg": float(physics.pitch_gain_deg),
        "bracing_threshold": float(physics.bracing_threshold),
    }


def build_reference_environment_manifest_v1(
    environment: EnvironmentConfigV1,
    physics: ReferencePhysicsConfigV1,
) -> PhysicalEnvironmentManifestV1:
    if environment.environment_id != physics.environment_id:
        raise ValueError(
            "environment_id mismatch between EnvironmentConfigV1 and "
            "ReferencePhysicsConfigV1"
        )
    if bool(environment.tether_enabled) != bool(physics.tether_enabled):
        raise ValueError(
            "tether_enabled mismatch between EnvironmentConfigV1 and "
            "ReferencePhysicsConfigV1"
        )

    payload = {
        "manifest_schema_id": MANIFEST_SCHEMA_ID_V1,
        "environment_id": environment.environment_id,
        "world_frame_id": WORLD_FRAME_ID_V1,
        "scope": {
            "physics_authority": "deterministic_reference_resolver_only",
            "production_geometry_frozen": False,
        },
        "environment": {
            "base_environment_id": environment.base_environment_id,
            "tether_enabled": bool(environment.tether_enabled),
            "room_roaming_enabled": bool(environment.room_roaming_enabled),
            "temporary": bool(environment.temporary),
            "exploratory_condition": bool(environment.exploratory_condition),
            "restoration_environment_id": environment.restoration_environment_id,
            "physical_props": _physical_props(environment),
        },
        "reference_physics": {
            "profile_id": REFERENCE_PHYSICS_PROFILE_ID_V1,
            "parameters": _reference_physics_parameters(physics),
            "resolver_constants": REFERENCE_RESOLVER_CONSTANTS_V1,
            "surface_ids": list(REFERENCE_SURFACE_IDS_V1),
        },
        "unfrozen_production_geometry": list(
            UNFROZEN_PRODUCTION_GEOMETRY_V1
        ),
    }
    return PhysicalEnvironmentManifestV1(payload)


def cell67_standard_reference_manifest_v1() -> PhysicalEnvironmentManifestV1:
    return build_reference_environment_manifest_v1(
        cell67_standard(),
        ReferencePhysicsConfigV1(
            environment_id=CELL67_STANDARD_ID,
            tether_enabled=True,
        ),
    )


def cell67_birthday_reference_manifest_v1() -> PhysicalEnvironmentManifestV1:
    return build_reference_environment_manifest_v1(
        cell67_birthday(),
        ReferencePhysicsConfigV1(
            environment_id=CELL67_BIRTHDAY_ID,
            tether_enabled=False,
        ),
    )


def emit_environment_manifest_v1(
    storage: TelemetryStorage,
    *,
    run_id: str,
    manifest: PhysicalEnvironmentManifestV1,
    experiment_id: str | None = None,
    subject_id: str | None = "MQ-001",
) -> TelemetryEventV1:
    payload = manifest.to_dict()
    payload.update(
        {
            "manifest_schema_id": MANIFEST_SCHEMA_ID_V1,
            "environment_id": manifest.payload["environment_id"],
            "world_frame_id": manifest.payload["world_frame_id"],
            "scope": manifest.payload["scope"],
        }
    )
    event = TelemetryEventV1(
        event_type="environment.manifest",
        run_id=run_id,
        component="environment",
        experiment_id=experiment_id,
        subject_id=subject_id,
        payload=payload,
        lore_surface="HUD",
    )
    storage.append(event)
    return event
