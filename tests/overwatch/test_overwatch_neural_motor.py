import pytest

from overwatch.neural_motor import (
    AdapterProvenanceV1,
    ReferenceNeuralMotorAdapterV1,
    reference_adapter_provenance,
)


def test_reference_adapter_maps_basic_drives():
    adapter = ReferenceNeuralMotorAdapterV1()

    motor = adapter.map_state(
        {
            "locomotor": 0.8,
            "grooming": 0.2,
            "courtship": 0.6,
            "escape": 0.4,
        }
    )

    assert motor.locomotor_drive == 0.8
    assert motor.grooming_drive == 0.2
    assert motor.courtship_drive == 0.6
    assert motor.escape_drive == 0.4


def test_reference_adapter_clamps_normalized_drives():
    adapter = ReferenceNeuralMotorAdapterV1()

    motor = adapter.map_state(
        {
            "locomotor": 2.0,
            "escape": -1.0,
        }
    )

    assert motor.locomotor_drive == 1.0
    assert motor.escape_drive == 0.0


def test_reference_adapter_preserves_signed_wing_velocity():
    adapter = ReferenceNeuralMotorAdapterV1()

    motor = adapter.map_state(
        {
            "left_wing": -3.5,
            "right_wing": 4.25,
        }
    )

    assert motor.left_wing_velocity == -3.5
    assert motor.right_wing_velocity == 4.25


def test_adapter_provenance_requires_known_visibility():
    with pytest.raises(ValueError):
        AdapterProvenanceV1(
            adapter_id="x",
            adapter_version="v1",
            implementation_visibility="classified",
        )


def test_reference_adapter_provenance_is_public():
    provenance = reference_adapter_provenance()

    assert provenance.adapter_id == "reference.linear-neural-motor"
    assert provenance.implementation_visibility == "public"
    assert provenance.methodology_ref == "docs/NEURAL_MOTOR_ADAPTER_V1.md"
