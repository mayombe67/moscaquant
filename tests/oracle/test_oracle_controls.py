from __future__ import annotations

import pytest

from oracle.controls import (
    OracleControl,
    OracleControlError,
    apply_control,
    parse_control,
)
from oracle.models import OracleInput
from oracle.state import initial_state


HASH = "a" * 64


def make_input(
    prior_state_hash: str,
    *,
    evidence_refs: tuple[str, ...] = (
        "evidence-a",
        "evidence-b",
        "evidence-c",
        "evidence-d",
    ),
) -> OracleInput:
    return OracleInput(
        schema_version="oracle-input/v1",
        experiment_id="mq7-controls",
        session_id="session-001",
        frame_id="frame-001",
        timestamp="2026-09-17T00:00:00+00:00",
        mq001_version="mq001-test",
        scientific_config_hash=HASH,
        evidence_refs=evidence_refs,
        derived_features=(("signal", 1.0),),
        prior_oracle_state_hash=prior_state_hash,
        warden_history=(),
    )


def test_unknown_control_is_rejected():
    with pytest.raises(
        OracleControlError,
        match="unknown Oracle control",
    ):
        parse_control("O9_CHAOS")


def test_o0_bypasses_oracle_and_is_not_abstention():
    state = initial_state(
        oracle_version="ORACLE-01-GLaDOS/0.1.0",
    )

    oracle_input = make_input(state.state_hash)

    result = apply_control(
        control=OracleControl.O0_NO_ORACLE,
        oracle_input=oracle_input,
        prior_state=state,
    )

    assert result.state == state
    assert result.proposal is None
    assert result.control is OracleControl.O0_NO_ORACLE


def test_o1_is_deterministic():
    state = initial_state(
        oracle_version="ORACLE-01-GLaDOS/0.1.0",
    )

    oracle_input = make_input(state.state_hash)

    first = apply_control(
        control=OracleControl.O1_STATIC_ORACLE,
        oracle_input=oracle_input,
        prior_state=state,
    )

    second = apply_control(
        control=OracleControl.O1_STATIC_ORACLE,
        oracle_input=oracle_input,
        prior_state=state,
    )

    assert first.state == second.state
    assert first.proposal == second.proposal


def test_o2_is_currently_non_adaptive():
    state = initial_state(
        oracle_version="ORACLE-01-GLaDOS/0.1.0",
    )

    oracle_input = make_input(state.state_hash)

    static = apply_control(
        control=OracleControl.O1_STATIC_ORACLE,
        oracle_input=oracle_input,
        prior_state=state,
    )

    adaptive = apply_control(
        control=OracleControl.O2_ADAPTIVE_ORACLE,
        oracle_input=oracle_input,
        prior_state=state,
    )

    assert static.state == adaptive.state
    assert static.proposal == adaptive.proposal
    assert adaptive.control is OracleControl.O2_ADAPTIVE_ORACLE


def test_o3_requires_explicit_seed():
    state = initial_state(
        oracle_version="ORACLE-01-GLaDOS/0.1.0",
    )

    oracle_input = make_input(state.state_hash)

    with pytest.raises(
        OracleControlError,
        match="explicit shuffle seed",
    ):
        apply_control(
            control=OracleControl.O3_SHUFFLED_ORACLE,
            oracle_input=oracle_input,
            prior_state=state,
        )


def test_o3_shuffle_is_deterministic_and_preserves_original():
    state = initial_state(
        oracle_version="ORACLE-01-GLaDOS/0.1.0",
    )

    original = (
        "evidence-a",
        "evidence-b",
        "evidence-c",
        "evidence-d",
    )

    oracle_input = make_input(
        state.state_hash,
        evidence_refs=original,
    )

    first = apply_control(
        control=OracleControl.O3_SHUFFLED_ORACLE,
        oracle_input=oracle_input,
        prior_state=state,
        shuffle_seed=42,
    )

    second = apply_control(
        control=OracleControl.O3_SHUFFLED_ORACLE,
        oracle_input=oracle_input,
        prior_state=state,
        shuffle_seed=42,
    )

    assert first.oracle_input.evidence_refs == second.oracle_input.evidence_refs
    assert set(first.oracle_input.evidence_refs) == set(original)
    assert oracle_input.evidence_refs == original

    assert first.provenance.original_evidence_refs == original
    assert (
        first.provenance.transformed_evidence_refs
        == first.oracle_input.evidence_refs
    )
    assert first.provenance.shuffle_seed == 42
