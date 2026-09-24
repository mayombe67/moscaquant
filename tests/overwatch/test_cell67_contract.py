from __future__ import annotations

from dataclasses import fields

import pytest

from overwatch.cell67_contract import (
    ANGLE_FIELDS_V1,
    BODY_ROTATION_AXES_V1,
    CONTRACT_ID,
    ENVIRONMENT_IDS_V1,
    HEAD_ROTATION_AXES_V1,
    LEG_VECTOR_ELEMENT_UNIT_V1,
    LEG_VECTOR_FIELDS_V1,
    LEG_VECTOR_INDEX_SEMANTICS_V1,
    MOTOR_FIELD_CHANNEL_MAP_V1,
    NORMALIZED_DRIVE_FIELDS_V1,
    REFERENCE_SURFACE_IDS_V1,
    SEMANTIC_RIG_IDS_V1,
    WING_VELOCITY_FIELDS_V1,
    WING_VELOCITY_UNIT_V1,
    WORLD_HANDEDNESS_V1,
    semantic_channel_for_motor_field,
)
from overwatch.environment import CELL67_BIRTHDAY_ID, CELL67_STANDARD_ID
from overwatch.motor import MotorStateV1
from overwatch.physics import CELL67_COORDINATE_FRAME_V1


def test_world_frame_is_frozen_v1() -> None:
    assert CONTRACT_ID == "CELL-67.COORDINATE-RIG.v1"
    assert CELL67_COORDINATE_FRAME_V1 == {
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
    assert WORLD_HANDEDNESS_V1 == "right-handed"


def test_body_and_head_rotation_axes_are_explicit() -> None:
    assert BODY_ROTATION_AXES_V1 == {
        "body_pitch_deg": "+x",
        "body_roll_deg": "+y",
        "body_yaw_deg": "+z",
    }
    assert HEAD_ROTATION_AXES_V1 == {
        "head_pitch_deg": "local +x",
        "head_yaw_deg": "local +z",
    }


def test_semantic_rig_ids_are_unique_and_use_front_mid_hind() -> None:
    assert len(SEMANTIC_RIG_IDS_V1) == len(set(SEMANTIC_RIG_IDS_V1))
    assert "leg.front_left" in SEMANTIC_RIG_IDS_V1
    assert "leg.mid_left" in SEMANTIC_RIG_IDS_V1
    assert "leg.hind_left" in SEMANTIC_RIG_IDS_V1
    assert not any(".middle_" in value for value in SEMANTIC_RIG_IDS_V1)
    assert not any(".rear_" in value for value in SEMANTIC_RIG_IDS_V1)


def test_all_current_motor_fields_have_frozen_semantic_aliases() -> None:
    actual_fields = {field.name for field in fields(MotorStateV1)}
    assert actual_fields == set(MOTOR_FIELD_CHANNEL_MAP_V1)


def test_leg_vector_mapping_preserves_existing_serialized_fields() -> None:
    assert LEG_VECTOR_FIELDS_V1 == {
        "left_foreleg": "leg.front_left",
        "right_foreleg": "leg.front_right",
        "left_midleg": "leg.mid_left",
        "right_midleg": "leg.mid_right",
        "left_hindleg": "leg.hind_left",
        "right_hindleg": "leg.hind_right",
    }
    assert LEG_VECTOR_ELEMENT_UNIT_V1 == "degree"
    assert LEG_VECTOR_INDEX_SEMANTICS_V1 == "opaque_until_versioned_joint_mapping"


def test_unfrozen_units_stay_unfrozen() -> None:
    assert set(ANGLE_FIELDS_V1) <= set(MOTOR_FIELD_CHANNEL_MAP_V1)
    assert set(NORMALIZED_DRIVE_FIELDS_V1) <= set(MOTOR_FIELD_CHANNEL_MAP_V1)
    assert set(WING_VELOCITY_FIELDS_V1) <= set(MOTOR_FIELD_CHANNEL_MAP_V1)
    assert WING_VELOCITY_UNIT_V1 == "unfrozen_model_value"


def test_environment_identity_is_stable() -> None:
    assert ENVIRONMENT_IDS_V1 == (CELL67_STANDARD_ID, CELL67_BIRTHDAY_ID)
    assert ENVIRONMENT_IDS_V1 == ("CELL-67.v1", "CELL-67.BIRTHDAY.v1")


def test_reference_surface_id_is_stable() -> None:
    assert REFERENCE_SURFACE_IDS_V1 == ("desk.primary.surface",)


def test_semantic_lookup_fails_closed_for_unfrozen_fields() -> None:
    assert semantic_channel_for_motor_field("left_foreleg") == "leg.front_left.joints"
    with pytest.raises(KeyError, match="unfrozen MotorStateV1 field"):
        semantic_channel_for_motor_field("totally_new_motor_thing")
