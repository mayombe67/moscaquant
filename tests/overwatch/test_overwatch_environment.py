import pytest

from overwatch.environment import (
    CELL67_BIRTHDAY_ID,
    CELL67_STANDARD_ID,
    cell67_birthday,
    cell67_standard,
    emit_environment_activated,
    emit_environment_restored,
    emit_prop_interaction,
    emit_wearable_state,
)
from overwatch.storage import LocalJsonlStorage


def test_standard_cell67_is_tethered():
    env = cell67_standard()
    assert env.environment_id == CELL67_STANDARD_ID
    assert env.tether_enabled is True
    assert env.room_roaming_enabled is False


def test_birthday_cell67_removes_tether_and_is_exploratory():
    env = cell67_birthday()
    assert env.environment_id == CELL67_BIRTHDAY_ID
    assert env.tether_enabled is False
    assert env.room_roaming_enabled is True
    assert env.temporary is True
    assert env.exploratory_condition is True
    assert env.restoration_environment_id == CELL67_STANDARD_ID


def test_birthday_cake_is_attractive_but_not_consumable():
    cake = cell67_birthday().prop("birthday.cake")
    assert cake.attractive is True
    assert cake.consumable is False
    assert cake.metadata["cake_is_a_lie"] is True


def test_cake_consumption_attempt_is_recorded_and_denied(tmp_path):
    storage = LocalJsonlStorage(tmp_path / "env.jsonl")
    event = emit_prop_interaction(
        storage,
        run_id="run-birthday",
        environment=cell67_birthday(),
        prop_id="birthday.cake",
        interaction="consume",
        source_motor_event_id="evt-motor-42",
        distance_m=0.01,
    )

    assert event.event_type == "environment.prop_interaction"
    assert event.payload["allowed"] is False
    assert event.payload["denied_reason"] == "prop_not_consumable"
    assert event.payload["source_motor_event_id"] == "evt-motor-42"


def test_party_hat_requires_real_interaction_before_equip(tmp_path):
    storage = LocalJsonlStorage(tmp_path / "env.jsonl")
    env = cell67_birthday()

    with pytest.raises(ValueError):
        emit_wearable_state(
            storage,
            run_id="run-birthday",
            environment=env,
            prop_id="birthday.party_hat",
            equipped=True,
            interaction_event_id=None,
        )

    interaction = emit_prop_interaction(
        storage,
        run_id="run-birthday",
        environment=env,
        prop_id="birthday.party_hat",
        interaction="contact",
        source_motor_event_id="evt-motor-99",
    )

    equipped = emit_wearable_state(
        storage,
        run_id="run-birthday",
        environment=env,
        prop_id="birthday.party_hat",
        equipped=True,
        interaction_event_id=interaction.event_id,
    )

    assert equipped.payload["equipped"] is True
    assert equipped.payload["temporary"] is True
    assert equipped.payload["interaction_event_id"] == interaction.event_id


def test_birthday_environment_emits_activation(tmp_path):
    event = emit_environment_activated(
        LocalJsonlStorage(tmp_path / "env.jsonl"),
        run_id="run-birthday",
        environment=cell67_birthday(),
        activation_reason="launch_day_birthday",
    )

    assert event.event_type == "environment.activated"
    assert event.payload["environment"]["tether_enabled"] is False


def test_birthday_restoration_clears_temporary_wearables(tmp_path):
    event = emit_environment_restored(
        LocalJsonlStorage(tmp_path / "env.jsonl"),
        run_id="run-birthday",
        from_environment=cell67_birthday(),
        reason="birthday_window_complete",
    )

    assert event.payload["to_environment_id"] == CELL67_STANDARD_ID
    assert event.payload["clear_temporary_wearables"] is True
