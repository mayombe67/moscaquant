from __future__ import annotations

from dataclasses import replace

import pytest

from oracle.audit import (
    OracleAuditError,
    sha256_hex,
    compute_event_hash,
    verify_chain,
)
from oracle.models import (
    OracleEvent,
    OracleInput,
    OracleProposal,
)
from oracle.protocol import (
    OracleProtocolError,
    validate_proposal,
)
from oracle.state import (
    initial_state,
    transition_with_event,
    transition,
)


HASH = "a" * 64


def make_input(prior_state_hash: str) -> OracleInput:
    return OracleInput(
        schema_version="oracle-input/v1",
        experiment_id="mq7-test",
        session_id="session-001",
        frame_id="frame-001",
        timestamp="2026-09-17T00:00:00+00:00",
        mq001_version="mq001-test",
        scientific_config_hash=HASH,
        evidence_refs=("evidence-001",),
        derived_features=(("signal", 1.0),),
        prior_oracle_state_hash=prior_state_hash,
        warden_history=(),
    )


def test_initial_state_is_valid_and_deterministic():
    first = initial_state(
        oracle_version="ORACLE-01-GLaDOS/0.1.0",
    )
    second = initial_state(
        oracle_version="ORACLE-01-GLaDOS/0.1.0",
    )

    assert first == second
    assert first.generation == 0
    assert len(first.state_hash) == 64


def test_transition_advances_generation_and_abstains():
    state = initial_state(
        oracle_version="ORACLE-01-GLaDOS/0.1.0",
    )

    oracle_input = make_input(state.state_hash)

    next_state, proposal = transition(
        oracle_input=oracle_input,
        prior_state=state,
    )

    assert next_state.generation == 1
    assert proposal.abstain is True
    assert proposal.proposal_type == "ABSTAIN"
    assert proposal.confidence == 0.0
    assert proposal.oracle_state_hash == next_state.state_hash


def test_transition_rejects_wrong_prior_state_hash():
    state = initial_state(
        oracle_version="ORACLE-01-GLaDOS/0.1.0",
    )

    oracle_input = make_input("b" * 64)

    with pytest.raises(
        OracleProtocolError,
        match="prior state hash",
    ):
        transition(
            oracle_input=oracle_input,
            prior_state=state,
        )


def test_non_abstaining_proposal_requires_evidence():
    proposal = OracleProposal(
        schema_version="oracle-proposal/v1",
        experiment_id="mq7-test",
        session_id="session-001",
        oracle_version="ORACLE-01-GLaDOS/0.1.0",
        proposal_id="proposal-001",
        proposal_type="TEST",
        proposal_payload=(),
        confidence=0.5,
        abstain=False,
        evidence_refs=(),
        oracle_state_hash=HASH,
    )

    with pytest.raises(
        OracleProtocolError,
        match="require evidence",
    ):
        validate_proposal(proposal)


def test_proposal_rejects_authority_field():
    proposal = OracleProposal(
        schema_version="oracle-proposal/v1",
        experiment_id="mq7-test",
        session_id="session-001",
        oracle_version="ORACLE-01-GLaDOS/0.1.0",
        proposal_id="proposal-001",
        proposal_type="TEST",
        proposal_payload=(("execute", True),),
        confidence=0.5,
        abstain=False,
        evidence_refs=("evidence-001",),
        oracle_state_hash=HASH,
    )

    with pytest.raises(
        OracleProtocolError,
        match="forbidden proposal field",
    ):
        validate_proposal(proposal)


def make_event(
    *,
    event_id: str,
    previous_event_hash: str | None,
) -> OracleEvent:
    event = OracleEvent(
        schema_version="oracle-event/v1",
        event_id=event_id,
        timestamp="2026-09-17T00:00:00+00:00",
        experiment_id="mq7-test",
        session_id="session-001",
        oracle_version="ORACLE-01-GLaDOS/0.1.0",
        oracle_artifact_hash=HASH,
        input_hash=HASH,
        pre_state_hash=HASH,
        proposal_hash=HASH,
        post_state_hash=HASH,
        previous_event_hash=previous_event_hash,
        event_hash="",
    )

    return replace(
        event,
        event_hash=compute_event_hash(event),
    )


def test_event_chain_accepts_valid_link():
    first = make_event(
        event_id="event-001",
        previous_event_hash=None,
    )

    second = make_event(
        event_id="event-002",
        previous_event_hash=first.event_hash,
    )

    verify_chain(first, second)


def test_event_chain_detects_tampering():
    first = make_event(
        event_id="event-001",
        previous_event_hash=None,
    )

    second = make_event(
        event_id="event-002",
        previous_event_hash=first.event_hash,
    )

    tampered = replace(
        second,
        notes="tampered",
    )

    with pytest.raises(
        OracleAuditError,
        match="hash mismatch",
    ):
        verify_chain(first, tampered)


def test_transition_with_event_builds_valid_audit_record():
    state = initial_state(
        oracle_version="ORACLE-01-GLaDOS/0.1.0",
    )

    oracle_input = make_input(state.state_hash)

    next_state, proposal, event = transition_with_event(
        oracle_input=oracle_input,
        prior_state=state,
        event_id="event-001",
        oracle_artifact_hash=HASH,
        previous_event_hash=None,
    )

    assert event.pre_state_hash == state.state_hash
    assert event.post_state_hash == next_state.state_hash
    assert event.proposal_hash == sha256_hex(proposal)
    assert event.previous_event_hash is None

    verify_chain(None, event)


def test_transition_events_chain_cleanly():
    state = initial_state(
        oracle_version="ORACLE-01-GLaDOS/0.1.0",
    )

    input_one = make_input(state.state_hash)

    state_one, _, event_one = transition_with_event(
        oracle_input=input_one,
        prior_state=state,
        event_id="event-001",
        oracle_artifact_hash=HASH,
        previous_event_hash=None,
    )

    input_two = make_input(state_one.state_hash)

    _, _, event_two = transition_with_event(
        oracle_input=input_two,
        prior_state=state_one,
        event_id="event-002",
        oracle_artifact_hash=HASH,
        previous_event_hash=event_one.event_hash,
    )

    verify_chain(event_one, event_two)
