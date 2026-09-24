from __future__ import annotations

import json

import pytest

from overwatch.environment import cell67_birthday, cell67_standard
from overwatch.environment_manifest import (
    MANIFEST_SCHEMA_ID_V1,
    REFERENCE_PHYSICS_PROFILE_ID_V1,
    REFERENCE_RESOLVER_CONSTANTS_V1,
    build_reference_environment_manifest_v1,
    cell67_birthday_reference_manifest_v1,
    cell67_standard_reference_manifest_v1,
    emit_environment_manifest_v1,
)
from overwatch.integration import ReferencePhysicsConfigV1
from overwatch.storage import LocalJsonlStorage


STANDARD_SHA256 = (
    "302d57c4afba219964cfbe93b9de5ff093c8240ab6acec2a201b8943ef1ebbf8"
)
BIRTHDAY_SHA256 = (
    "b161eb12500ebbcae42703474eeeadaa241d75b4a209eba46faa8caaab1f24c1"
)


def test_standard_reference_manifest_hash_is_frozen() -> None:
    manifest = cell67_standard_reference_manifest_v1()
    assert manifest.sha256() == STANDARD_SHA256
    assert manifest.payload["manifest_schema_id"] == MANIFEST_SCHEMA_ID_V1
    assert manifest.payload["environment_id"] == "CELL-67.v1"
    assert manifest.payload["world_frame_id"] == "CELL-67.WORLD.v1"
    assert manifest.payload["reference_physics"]["profile_id"] == (
        REFERENCE_PHYSICS_PROFILE_ID_V1
    )


def test_birthday_reference_manifest_hash_is_frozen() -> None:
    manifest = cell67_birthday_reference_manifest_v1()
    assert manifest.sha256() == BIRTHDAY_SHA256
    assert manifest.payload["environment_id"] == "CELL-67.BIRTHDAY.v1"
    assert manifest.payload["environment"]["tether_enabled"] is False
    assert manifest.payload["environment"]["room_roaming_enabled"] is True


def test_manifest_hash_uses_canonical_json() -> None:
    manifest = cell67_standard_reference_manifest_v1()
    parsed = json.loads(manifest.canonical_json())
    assert parsed == manifest.payload
    assert "manifest_sha256" not in manifest.payload


def test_presentation_only_props_do_not_enter_physical_manifest() -> None:
    standard = cell67_standard_reference_manifest_v1().payload
    prop_ids = {
        prop["prop_id"]
        for prop in standard["environment"]["physical_props"]
    }
    assert prop_ids == {"desk.primary"}

    birthday = cell67_birthday_reference_manifest_v1().payload
    birthday_prop_ids = {
        prop["prop_id"]
        for prop in birthday["environment"]["physical_props"]
    }
    assert "monitor.primary" not in birthday_prop_ids
    assert "monitor.meme" not in birthday_prop_ids
    assert "birthday.banner" not in birthday_prop_ids
    assert "birthday.appreciation_placard" not in birthday_prop_ids
    assert {
        "desk.primary",
        "birthday.cake",
        "birthday.party_hat",
        "birthday.balloon.cluster_a",
        "birthday.management_card",
    } == birthday_prop_ids


def test_reference_resolver_constants_match_frozen_public_values() -> None:
    assert REFERENCE_RESOLVER_CONSTANTS_V1 == {
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


def test_manifest_rejects_environment_physics_identity_mismatch() -> None:
    with pytest.raises(ValueError, match="environment_id mismatch"):
        build_reference_environment_manifest_v1(
            cell67_standard(),
            ReferencePhysicsConfigV1(
                environment_id="CELL-67.BIRTHDAY.v1",
                tether_enabled=True,
            ),
        )

    with pytest.raises(ValueError, match="tether_enabled mismatch"):
        build_reference_environment_manifest_v1(
            cell67_birthday(),
            ReferencePhysicsConfigV1(
                environment_id="CELL-67.BIRTHDAY.v1",
                tether_enabled=True,
            ),
        )


def test_environment_manifest_event_records_hash_and_payload(tmp_path) -> None:
    storage = LocalJsonlStorage(tmp_path / "environment-manifest.jsonl")
    manifest = cell67_standard_reference_manifest_v1()

    event = emit_environment_manifest_v1(
        storage,
        run_id="run-manifest",
        manifest=manifest,
        experiment_id="exp-manifest",
    )

    assert event.event_type == "environment.manifest"
    assert event.payload["manifest_sha256"] == STANDARD_SHA256
    assert event.payload["environment_id"] == "CELL-67.v1"
    assert event.payload["world_frame_id"] == "CELL-67.WORLD.v1"
    assert event.payload["manifest"] == manifest.payload
