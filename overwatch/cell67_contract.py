from __future__ import annotations

"""Canonical CELL-67 coordinate, semantic-rig, and channel contract v1."""

from .environment import CELL67_BIRTHDAY_ID, CELL67_STANDARD_ID
from .physics import CELL67_COORDINATE_FRAME_V1

CONTRACT_ID = "CELL-67.COORDINATE-RIG.v1"
CELL67_WORLD_FRAME_V1 = CELL67_COORDINATE_FRAME_V1
WORLD_HANDEDNESS_V1 = "right-handed"

BODY_ROTATION_AXES_V1 = {
    "body_pitch_deg": "+x",
    "body_roll_deg": "+y",
    "body_yaw_deg": "+z",
}
HEAD_ROTATION_AXES_V1 = {
    "head_pitch_deg": "local +x",
    "head_yaw_deg": "local +z",
}

SEMANTIC_RIG_IDS_V1 = (
    "body.root",
    "body.head",
    "antenna.left",
    "antenna.right",
    "wing.left",
    "wing.right",
    "leg.front_left",
    "leg.front_right",
    "leg.mid_left",
    "leg.mid_right",
    "leg.hind_left",
    "leg.hind_right",
)

MOTOR_FIELD_CHANNEL_MAP_V1 = {
    "head_yaw_deg": "body.head.yaw",
    "head_pitch_deg": "body.head.pitch",
    "left_antenna_deg": "antenna.left.angle",
    "right_antenna_deg": "antenna.right.angle",
    "left_wing_deg": "wing.left.angle",
    "right_wing_deg": "wing.right.angle",
    "left_wing_velocity": "wing.left.velocity",
    "right_wing_velocity": "wing.right.velocity",
    "body_pitch_deg": "body.root.pitch",
    "body_roll_deg": "body.root.roll",
    "body_yaw_deg": "body.root.yaw",
    "locomotor_drive": "drive.locomotor",
    "grooming_drive": "drive.grooming",
    "courtship_drive": "drive.courtship",
    "escape_drive": "drive.escape",
    "left_foreleg": "leg.front_left.joints",
    "right_foreleg": "leg.front_right.joints",
    "left_midleg": "leg.mid_left.joints",
    "right_midleg": "leg.mid_right.joints",
    "left_hindleg": "leg.hind_left.joints",
    "right_hindleg": "leg.hind_right.joints",
}

LEG_VECTOR_FIELDS_V1 = {
    "left_foreleg": "leg.front_left",
    "right_foreleg": "leg.front_right",
    "left_midleg": "leg.mid_left",
    "right_midleg": "leg.mid_right",
    "left_hindleg": "leg.hind_left",
    "right_hindleg": "leg.hind_right",
}
LEG_VECTOR_ELEMENT_UNIT_V1 = "degree"
LEG_VECTOR_INDEX_SEMANTICS_V1 = "opaque_until_versioned_joint_mapping"

ANGLE_FIELDS_V1 = (
    "head_yaw_deg",
    "head_pitch_deg",
    "left_antenna_deg",
    "right_antenna_deg",
    "left_wing_deg",
    "right_wing_deg",
    "body_pitch_deg",
    "body_roll_deg",
    "body_yaw_deg",
)

NORMALIZED_DRIVE_FIELDS_V1 = (
    "locomotor_drive",
    "grooming_drive",
    "courtship_drive",
    "escape_drive",
)

WING_VELOCITY_FIELDS_V1 = (
    "left_wing_velocity",
    "right_wing_velocity",
)
WING_VELOCITY_UNIT_V1 = "unfrozen_model_value"

ENVIRONMENT_IDS_V1 = (
    CELL67_STANDARD_ID,
    CELL67_BIRTHDAY_ID,
)

REFERENCE_SURFACE_IDS_V1 = (
    "desk.primary.surface",
)


def semantic_channel_for_motor_field(field_name: str) -> str:
    try:
        return MOTOR_FIELD_CHANNEL_MAP_V1[field_name]
    except KeyError as exc:
        raise KeyError(f"unfrozen MotorStateV1 field: {field_name}") from exc


def contract_summary_v1() -> dict[str, object]:
    return {
        "contract_id": CONTRACT_ID,
        "world_frame": CELL67_WORLD_FRAME_V1,
        "world_handedness": WORLD_HANDEDNESS_V1,
        "body_rotation_axes": dict(BODY_ROTATION_AXES_V1),
        "head_rotation_axes": dict(HEAD_ROTATION_AXES_V1),
        "semantic_rig_ids": list(SEMANTIC_RIG_IDS_V1),
        "motor_field_channel_map": dict(MOTOR_FIELD_CHANNEL_MAP_V1),
        "leg_vector_fields": dict(LEG_VECTOR_FIELDS_V1),
        "leg_vector_element_unit": LEG_VECTOR_ELEMENT_UNIT_V1,
        "leg_vector_index_semantics": LEG_VECTOR_INDEX_SEMANTICS_V1,
        "angle_fields": list(ANGLE_FIELDS_V1),
        "normalized_drive_fields": list(NORMALIZED_DRIVE_FIELDS_V1),
        "wing_velocity_fields": list(WING_VELOCITY_FIELDS_V1),
        "wing_velocity_unit": WING_VELOCITY_UNIT_V1,
        "environment_ids": list(ENVIRONMENT_IDS_V1),
        "reference_surface_ids": list(REFERENCE_SURFACE_IDS_V1),
    }
