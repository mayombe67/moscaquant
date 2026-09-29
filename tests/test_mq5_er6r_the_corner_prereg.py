from __future__ import annotations

import hashlib
import json
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config/controls/mq5-er6r-the-corner-v1.toml"
CONTROL = ROOT / "artifacts/mq5-er6r-the-warrant-matched-control-v1.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load() -> dict:
    return tomllib.loads(CONFIG.read_text(encoding="utf-8"))


def test_execution_stage_is_disabled_and_bound_to_frozen_science():
    stage = load()
    control = json.loads(CONTROL.read_text(encoding="utf-8"))

    assert stage["stage_id"] == "mq5-er6r-the-corner-v1"
    assert stage["parent_experiment"] == "mq5-er6r-the-warrant-v1"
    assert stage["frames"] == 192
    assert stage["neural_execution_enabled"] is False
    assert stage["result_execution_enabled"] is False
    assert stage["candidate_node"] == control["candidate"]["node"] == 1952
    assert stage["matched_control_node"] == control["selected_control"]["node"] == 3056
    assert stage["matched_control_artifact_sha256"] == sha256(CONTROL)
    assert stage["warrant_protocol_sha256"] == sha256(
        ROOT / "docs/experiments/mq5-er6r-the-warrant-protocol.md"
    )
    assert stage["warrant_config_sha256"] == sha256(
        ROOT / "config/controls/mq5-er6r-the-warrant-v1.toml"
    )


def test_three_arm_operator_and_endpoint_are_prospectively_fixed():
    stage = load()
    arms = stage["arms"]
    intervention = stage["intervention"]
    endpoint = stage["primary_endpoint"]
    integrity = stage["integrity"]

    assert arms == {
        "baseline": "P0", "candidate": "P1952", "matched_control": "PCONTROL"
    }
    assert stage["all_targets"] == [51, 55, 92, 129, 317, 656, 1273, 126002, 137122]
    assert stage["affected_targets"] == [55, 92, 656, 126002, 137122]
    assert stage["retained_targets"] == [51, 129, 317, 1273]
    assert intervention["silenced_value"] == 0.0
    assert (intervention["start_frame"], intervention["end_frame"]) == (0, 191)
    assert intervention["identical_candidate_control_operator"] is True
    assert intervention["baseline_unmodified"] is True
    assert intervention["preserve_membrane_and_internal_state"] is True
    assert intervention["preserve_connectome_and_stimulus"] is True
    assert endpoint["kind"] == "first_positive_onset_delay_or_absence"
    assert endpoint["earlier_onset_counts_as_dependency"] is False
    assert endpoint["retained_are_specificity_diagnostics_only"] is True
    assert endpoint["secondary_can_override_primary"] is False
    assert (endpoint["affected_k_null"], endpoint["affected_k_partial_min"],
            endpoint["affected_k_partial_max"], endpoint["affected_k_complete"]) == (0, 1, 4, 5)
    assert integrity["require_separate_neural_execution_authorization"] is True
    assert integrity["require_runtime_input_and_write_path_checks"] is True
    assert integrity["allow_control_reselection"] is False
    assert integrity["allow_candidate_replacement"] is False
