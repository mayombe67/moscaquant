from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

MEASUREMENT = (
    ROOT
    / "config/experiments/"
    "sq11-dark-forest-measurement-contract-v1.json"
)

SCHEMA = (
    ROOT
    / "config/experiments/"
    "sq11-dark-forest-evidence-schema-v1.json"
)


def load(path):
    return json.loads(
        path.read_text()
    )


def test_contracts_are_pre_execution():
    measurement = load(
        MEASUREMENT
    )

    schema = load(
        SCHEMA
    )

    assert (
        measurement["status"]
        == "FROZEN_PRE_EXECUTION"
    )

    assert (
        schema["status"]
        == "FROZEN_PRE_EXECUTION"
    )

    assert (
        measurement[
            "analysis_boundary"
        ][
            "analysis_performed"
        ]
        is False
    )


def test_measurement_contract_binds_qualified_instrument():
    d = load(
        MEASUREMENT
    )

    q = d["provenance"][
        "qualification_result"
    ]

    assert (
        q["sha256"]
        == "84377ef502e7f8e86c6dacb7a476ee06df784a9869383df4ba734de56d9f5231"
    )


def test_geometry_is_frozen():
    d = load(
        MEASUREMENT
    )["coordinates"]

    assert d["row_nnz"] == [
        2830,
        841,
        897,
    ]

    assert d["row_offsets"] == [
        0,
        2830,
        3671,
        4568,
    ]

    assert d["body_positions"] == [
        1908,
        671,
        767,
    ]

    assert d["body_flat_positions"] == [
        1908,
        3501,
        4438,
    ]

    assert (
        d["flat_entry_count"]
        == 4568
    )

    assert (
        d["presynaptic_union_count"]
        == 4393
    )


def test_p2_local_state_has_schema_closure():
    measurement = load(
        MEASUREMENT
    )

    schema = load(
        SCHEMA
    )

    field = (
        "local_effective_activity_pre_synaptic"
    )

    assert (
        measurement[
            "dynamic_measurements"
        ][field]["phase"]
        == "P2"
    )

    assert (
        schema["arrays"][field]
        == {
            "dtype": "float32",
            "shape": [
                16,
                192,
                4393,
            ],
        }
    )


def test_p3_has_schema_closure():
    measurement = load(
        MEASUREMENT
    )

    schema = load(
        SCHEMA
    )

    assert (
        measurement[
            "dynamic_measurements"
        ][
            "responder_synaptic_p3"
        ][
            "phase"
        ]
        == "P3"
    )

    assert (
        schema["arrays"][
            "responder_synaptic_p3"
        ]
        == {
            "dtype": "float32",
            "shape": [
                16,
                192,
                3,
            ],
        }
    )


def test_all_inherited_sophon_measurements_close():
    schema = load(
        SCHEMA
    )

    required = {
        "source_voltage_pre_step",
        "source_spikes_pre_step",
        "source_effective_activity_pre_synaptic",
        "responder_voltage_pre_threshold",
        "responder_fired",
        "responder_voltage_post_reset",
        "responder_spikes_post_commit",
    }

    assert required.issubset(
        schema["arrays"]
    )


def test_replay_geometry_is_self_contained():
    arrays = load(
        SCHEMA
    )["arrays"]

    required = {
        "row_offsets",
        "row_indices",
        "row_weights",
        "body_positions",
        "body_flat_positions",
        "presynaptic_union_indices",
        "row_union_positions",
        "body_edge_weight",
    }

    assert required.issubset(
        arrays
    )


def test_condition_coordinates_are_closed():
    arrays = load(
        SCHEMA
    )["arrays"]

    required = {
        "condition_ordinal",
        "condition_id",
        "condition_mask",
        "condition_replicate",
        "condition_edge_zeroed",
        "source_indices",
        "responder_indices",
    }

    assert required.issubset(
        arrays
    )


def test_schema_freezes_all_16_units():
    d = load(
        SCHEMA
    )

    assert (
        d[
            "canonical_condition_order"
        ]
        == [
            "sq11:000:r1",
            "sq11:000:r2",
            "sq11:001:r1",
            "sq11:001:r2",
            "sq11:010:r1",
            "sq11:010:r2",
            "sq11:011:r1",
            "sq11:011:r2",
            "sq11:100:r1",
            "sq11:100:r2",
            "sq11:101:r1",
            "sq11:101:r2",
            "sq11:110:r1",
            "sq11:110:r2",
            "sq11:111:r1",
            "sq11:111:r2",
        ]
    )


def test_no_post_result_tolerance():
    d = load(
        MEASUREMENT
    )["analysis_boundary"]

    assert (
        d[
            "post_result_tolerance_allowed"
        ]
        is False
    )

    assert (
        d["replay_tolerance"]
        == {
            "absolute": 0.0,
            "relative": 0.0,
        }
    )


def test_verifier_requirements_are_fail_closed():
    d = load(
        SCHEMA
    )[
        "verification_requirements"
    ]

    assert all(
        value is True
        for value in d.values()
    )
