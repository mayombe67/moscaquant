from __future__ import annotations

import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

CONFIG = (
    ROOT
    / "config/controls/"
    "mq5-er6r-the-warrant-v1.toml"
)

PROTOCOL = (
    ROOT
    / "docs/experiments/"
    "mq5-er6r-the-warrant-protocol.md"
)


def load_config() -> dict:
    with CONFIG.open("rb") as handle:
        return tomllib.load(handle)


def test_prereg_identity_and_execution_disabled():
    cfg = load_config()

    assert (
        cfg["experiment_id"]
        == "mq5-er6r-the-warrant-v1"
    )

    assert cfg["codename"] == "THE WARRANT"

    assert (
        cfg["result_execution_enabled"]
        is False
    )

    assert (
        cfg["matched_control_selection_enabled"]
        is False
    )


def test_corrected_parent_is_way_down():
    cfg = load_config()

    assert (
        cfg["scientific_parent_experiment"]
        == "mq5-er5r-way-down-in-the-hole-v1"
    )

    assert (
        cfg["scientific_parent_result_sha256"]
        ==
        "3c56719c4bd87f45206c16326779386e22c55955a189d45ae6ca6f5dddb0ffbc"
    )

    assert (
        cfg["scientific_parent_result_seal_sha256"]
        ==
        "51b46dcce4ffd2c6aeaf3a48190a8b6dfcd04e40b5d66aa10c41742650ada425"
    )


def test_candidate_is_prospectively_frozen_1952():
    cfg = load_config()

    assert cfg["candidate_node"] == 1952

    assert (
        cfg["corrected_candidate_signature"][
            "target_order"
        ]
        == [
            51,
            55,
            92,
            129,
            317,
            656,
            1273,
            126002,
            137122,
        ]
    )

    assert (
        cfg["corrected_candidate_signature"][
            "hop_signature"
        ]
        == [
            2,
            3,
            2,
            3,
            3,
            2,
            2,
            3,
            2,
        ]
    )


def test_orientation_contract_is_corrected():
    cfg = load_config()

    orientation = cfg["orientation"]

    assert (
        orientation["matrix_semantics"]
        == "graph[post, pre] = pre -> post"
    )

    assert (
        orientation["reverse_ancestry_storage"]
        == "csr_rows"
    )

    assert (
        orientation[
            "csc_column_reverse_ancestry_allowed"
        ]
        is False
    )


def test_output_silencing_contract():
    cfg = load_config()

    intervention = cfg["intervention"]

    assert (
        intervention["kind"]
        == "effective_activity_output_silence"
    )

    assert intervention["target_node"] == 1952
    assert intervention["silenced_value"] == 0.0

    assert (
        intervention[
            "preserve_membrane_voltage"
        ]
        is True
    )

    assert (
        intervention[
            "modify_only_target_activity_index"
        ]
        is True
    )


def test_primary_endpoint_and_classification():
    cfg = load_config()

    endpoint = cfg["primary_endpoint"]
    classification = cfg["classification"]

    assert (
        endpoint["kind"]
        == "first_positive_onset_delay_or_absence"
    )

    assert (
        endpoint[
            "earlier_onset_counts_as_dependency"
        ]
        is False
    )

    assert classification["complete_k"] == 5
    assert classification["partial_k_min"] == 1
    assert classification["partial_k_max"] == 4
    assert classification["null_k"] == 0


def test_control_selection_is_prospective_and_fail_closed():
    cfg = load_config()

    control = cfg["matched_control"]

    assert control["selection_enabled"] is False

    assert (
        control[
            "pre_intervention_information_only"
        ]
        is True
    )

    assert (
        control[
            "publish_alternate_control_identities"
        ]
        is False
    )

    assert (
        control[
            "allow_post_selection_relaxation"
        ]
        is False
    )

    assert (
        cfg["stopping_rule"][
            "allow_control_fishing"
        ]
        is False
    )


def test_protocol_records_fresh_warrant_boundary():
    text = PROTOCOL.read_text(
        encoding="utf-8"
    )

    assert (
        "FRESH_CAUSAL_PREREGISTRATION_REQUIRED"
        in text
    )

    assert (
        "does not inherit scientific authority"
        in text
    )

    assert (
        "(2, 3, 2, 3, 3, 2, 2, 3, 2)"
        in text
    )

    assert (
        "does **not**"
        in text
    )

    assert (
        "execute the matched-control selector"
        in text
    )
