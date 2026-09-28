from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

SCHEMA = (
    ROOT
    / "config/experiments/"
    "sq11-dark-forest-evidence-schema-v2.json"
)


def load():
    return json.loads(
        SCHEMA.read_text()
    )


def test_schema_is_pre_execution():
    schema = load()

    assert (
        schema["status"]
        == "FROZEN_PRE_EXECUTION"
    )


def test_schema_binds_replay_v2():
    schema = load()

    replay = schema[
        "provenance"
    ][
        "execution_authoritative_replay"
    ]

    assert replay["version"] == 2

    assert (
        replay["qualification_mismatches"]
        == 0
    )

    assert (
        replay["qualification_comparisons"]
        == 2304
    )


def test_required_structural_arrays_exist():
    arrays = load()["arrays"]

    required = {
        "condition_edge_zeroed",
        "body_positions",
        "body_flat_positions",
        "presynaptic_union_indices",
        "row_union_positions",
        "row_offsets",
        "row_indices",
        "row_weights",
        "body_edge_weight",
        "local_effective_activity_pre_synaptic",
        "responder_synaptic_p3",
    }

    assert required.issubset(
        arrays.keys()
    )


def test_condition_edge_zeroed_semantics_are_frozen():
    field = load()["arrays"][
        "condition_edge_zeroed"
    ]

    assert (
        field["dtype"]
        == "uint8"
    )

    assert (
        "structurally omits"
        in field["semantics"]
    )


def test_no_zero_multiplier_semantics():
    replay = load()[
        "replay_semantics"
    ]

    assert (
        replay[
            "zero_multiplication_equivalent"
        ]
        is False
    )

    assert (
        replay[
            "lesioned_body_entry_operation"
        ]
        == "skip"
    )


def test_exact_float32_boundary():
    replay = load()[
        "replay_semantics"
    ]

    assert (
        replay["absolute_tolerance"]
        == 0.0
    )

    assert (
        replay["relative_tolerance"]
        == 0.0
    )

    assert (
        replay["equality_rule"]
        == "exact float32 equality"
    )


def test_analysis_is_locked_out():
    requirements = load()[
        "verification_requirements"
    ]

    assert (
        requirements[
            "exact_runtime_p3_replay"
        ]
        is True
    )
