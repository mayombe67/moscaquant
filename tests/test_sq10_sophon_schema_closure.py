import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

CONTRACT = (
    ROOT
    / "config/experiments/"
    "sq10-sophon-measurement-contract-draft-v1.json"
)

SCHEMA = (
    ROOT
    / "config/experiments/"
    "sq10-sophon-evidence-schema-draft-v1.json"
)


def load(path: Path) -> dict:
    return json.loads(path.read_text())


def test_sq10_execution_remains_unauthorized():
    contract = load(CONTRACT)
    schema = load(SCHEMA)

    assert contract["neural_execution_authorized"] is False
    assert schema["neural_execution_authorized"] is False


def test_all_required_measurements_have_schema_closure():
    contract = load(CONTRACT)
    schema = load(SCHEMA)

    required = set()

    for group in (
        "source",
        "responder",
        "edge",
        "derived",
    ):
        required |= set(
            contract[
                "required_measurements"
            ][group]
        )

    closure = schema[
        "required_measurement_closure"
    ]

    assert set(closure) == required

def test_stored_measurements_reference_real_fields():
    schema = load(SCHEMA)

    arrays = schema["arrays"]
    closure = schema["required_measurement_closure"]

    for measurement, mapping in closure.items():
        if mapping["mode"] != "stored":
            continue

        assert mapping["field"] in arrays, measurement


def test_derived_measurements_reference_real_derivations():
    schema = load(SCHEMA)

    derivations = schema["derivations"]
    closure = schema["required_measurement_closure"]

    for measurement, mapping in closure.items():
        if mapping["mode"] != "derived":
            continue

        assert mapping["derivation"] in derivations, measurement


def test_edge_derivation_inputs_are_closed():
    schema = load(SCHEMA)

    arrays = schema["arrays"]
    derivations = schema["derivations"]

    assert (
        derivations[
            "potential_direct_edge_drive"
        ]["inputs"]
        == [
            "source_effective_activity_pre_synaptic",
            "body_edge_weight",
        ]
    )

    assert (
        "source_effective_activity_pre_synaptic"
        in arrays
    )
    assert "body_edge_weight" in arrays

    assert (
        derivations[
            "actual_direct_edge_contribution"
        ]["inputs"]
        == [
            "potential_direct_edge_drive",
            "condition_edge_zeroed",
        ]
    )

    assert (
        derivations[
            "removed_direct_edge_contribution"
        ]["inputs"]
        == [
            "potential_direct_edge_drive",
            "condition_edge_zeroed",
        ]
    )

    assert "condition_edge_zeroed" in arrays


def test_phase_assignments_match_runtime_clock_audit():
    schema = load(SCHEMA)

    arrays = schema["arrays"]

    assert arrays["source_voltage_pre_step"]["phase"] == "P0"
    assert arrays["source_spikes_pre_step"]["phase"] == "P0"
    assert (
        arrays["source_effective_activity_pre_synaptic"]["phase"]
        == "P2"
    )

    assert (
        arrays["responder_voltage_pre_threshold"]["phase"]
        == "P5"
    )
    assert arrays["responder_fired"]["phase"] == "P6"
    assert (
        arrays["responder_voltage_post_reset"]["phase"]
        == "P7"
    )
    assert (
        arrays["responder_spikes_post_commit"]["phase"]
        == "P7"
    )


def test_body_coordinates_are_exact():
    schema = load(SCHEMA)

    assert schema["coordinates"]["sources"] == [
        65084,
        128590,
        135589,
    ]

    assert schema["coordinates"]["responders"] == [
        137122,
        317,
        126002,
    ]


def test_complete_cube_is_exact():
    schema = load(SCHEMA)

    assert schema["coordinates"]["condition_masks"] == [
        "000",
        "001",
        "010",
        "011",
        "100",
        "101",
        "110",
        "111",
    ]

    assert (
        schema["coordinates"]["mask_semantics"]
        == "0=retained,1=zeroed"
    )
