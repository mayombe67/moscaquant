from __future__ import annotations

import json
from pathlib import Path


PATH = Path(
    "config/controls/"
    "sq08-three-body-evidence-schema-v1.json"
)


def schema():
    return json.loads(PATH.read_text())


def test_complete_boolean_cube():
    data = schema()

    assert data["condition_masks"] == [
        "000",
        "001",
        "010",
        "011",
        "100",
        "101",
        "110",
        "111",
    ]


def test_body_order_and_identity_are_frozen():
    data = schema()

    assert data["body_order"] == ["A", "B", "C"]

    assert data["body_responders"] == [
        137122,
        317,
        126002,
    ]


def test_frontier_identity_is_frozen():
    data = schema()

    assert data["three_way_direct_frontier"] == [
        7,
        72,
        129,
        411,
        470,
        1472,
        1574,
        1662,
        1919,
        2009,
        2327,
        3712,
        4068,
        14273,
        16349,
        18196,
        130134,
        131527,
    ]


def test_primary_evidence_shapes():
    arrays = schema()["per_episode_arrays"]

    assert arrays["primary_positive_voltage"] == {
        "shape": [192, 1191],
        "dtype": "float32",
        "required": True,
    }

    assert arrays["primary_spikes"] == {
        "shape": [192, 1191],
        "dtype": "uint8",
        "required": True,
    }


def test_mechanistic_readouts_are_preserved():
    arrays = schema()["per_episode_arrays"]

    assert arrays["body_responder_voltage"]["shape"] == [192, 3]
    assert arrays["body_responder_spikes"]["shape"] == [192, 3]

    assert arrays["frontier_voltage"]["shape"] == [192, 18]
    assert arrays["frontier_spikes"]["shape"] == [192, 18]


def test_evidence_fails_closed():
    integrity = schema()["integrity"]

    assert integrity["preserve_every_episode"] is True
    assert integrity["hash_every_episode_artifact"] is True
    assert integrity["fail_on_missing_array"] is True
    assert integrity["fail_on_shape_mismatch"] is True
    assert integrity["fail_on_dtype_mismatch"] is True
    assert integrity["fail_on_duplicate_condition_replicate"] is True


def test_schema_does_not_interpret_science():
    assert (
        schema()["claim_boundary"]
        == "Evidence preservation only; this schema does not interpret mechanism."
    )
