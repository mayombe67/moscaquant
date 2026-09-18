from __future__ import annotations

from oracle.d6_darkness import (
    DEFAULT_DURATION_TRANSITIONS,
    DEFAULT_RETAINED_AMPLITUDE,
    apply_darkness,
    build_darkness,
    is_darkness_active,
)
from oracle.models import OracleInput


HASH = "a" * 64


def make_input() -> OracleInput:
    return OracleInput(
        schema_version="oracle-input/v1",
        experiment_id="mq7-darkness",
        session_id="session-001",
        frame_id="frame-001",
        timestamp="2026-09-17T00:00:00+00:00",
        mq001_version="MORTY-test",
        scientific_config_hash=HASH,
        evidence_refs=("evidence-001",),
        derived_features=(
            ("price_signal", 1.0),
            ("momentum", -0.8),
            ("label", "control"),
        ),
        prior_oracle_state_hash=HASH,
        warden_history=(),
    )


def test_darkness_defaults_are_frozen():
    intervention = build_darkness(
        current_generation=5,
    )

    assert (
        intervention.retained_amplitude
        == DEFAULT_RETAINED_AMPLITUDE
        == 0.25
    )

    assert (
        intervention.duration_transitions
        == DEFAULT_DURATION_TRANSITIONS
        == 10
    )


def test_darkness_window_is_exact():
    intervention = build_darkness(
        current_generation=5,
    )

    assert not is_darkness_active(
        intervention,
        generation=4,
    )

    assert is_darkness_active(
        intervention,
        generation=5,
    )

    assert is_darkness_active(
        intervention,
        generation=14,
    )

    assert not is_darkness_active(
        intervention,
        generation=15,
    )


def test_darkness_attenuates_numeric_features_only():
    original = make_input()

    intervention = build_darkness(
        current_generation=0,
    )

    transformed = apply_darkness(
        oracle_input=original,
        intervention=intervention,
        generation=0,
    )

    assert transformed.derived_features == (
        ("price_signal", 0.25),
        ("momentum", -0.2),
        ("label", "control"),
    )


def test_darkness_does_not_modify_original_input():
    original = make_input()

    intervention = build_darkness(
        current_generation=0,
    )

    transformed = apply_darkness(
        oracle_input=original,
        intervention=intervention,
        generation=0,
    )

    assert original.derived_features == (
        ("price_signal", 1.0),
        ("momentum", -0.8),
        ("label", "control"),
    )

    assert transformed is not original


def test_darkness_recovers_immediately_after_window():
    original = make_input()

    intervention = build_darkness(
        current_generation=0,
        duration_transitions=10,
    )

    transformed = apply_darkness(
        oracle_input=original,
        intervention=intervention,
        generation=10,
    )

    assert transformed == original
