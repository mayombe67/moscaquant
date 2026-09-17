from __future__ import annotations

from dataclasses import replace

from oracle.audit import build_event, sha256_hex
from oracle.models import (
    OracleEvent,
    OracleInput,
    OracleProposal,
    OracleState,
)
from oracle.protocol import (
    OracleProtocolError,
    validate_input,
    validate_proposal,
    validate_state,
)


def initial_state(
    *,
    oracle_version: str,
) -> OracleState:
    base = OracleState(
        schema_version="oracle-state/v1",
        oracle_version=oracle_version,
        generation=0,
        behavioral_state=(),
        adaptation_state=(),
        intervention_state=(),
        history_digest=sha256_hex(()),
        state_hash="0" * 64,
    )

    state_hash = sha256_hex({
        "schema_version": base.schema_version,
        "oracle_version": base.oracle_version,
        "generation": base.generation,
        "behavioral_state": base.behavioral_state,
        "adaptation_state": base.adaptation_state,
        "intervention_state": base.intervention_state,
        "history_digest": base.history_digest,
    })

    state = replace(
        base,
        state_hash=state_hash,
    )

    validate_state(state)
    return state


def transition(
    *,
    oracle_input: OracleInput,
    prior_state: OracleState,
) -> tuple[OracleState, OracleProposal]:
    validate_input(oracle_input)
    validate_state(prior_state)

    if oracle_input.prior_oracle_state_hash != prior_state.state_hash:
        raise OracleProtocolError(
            "OracleInput prior state hash does not match current state"
        )

    next_generation = prior_state.generation + 1

    history_digest = sha256_hex({
        "previous": prior_state.history_digest,
        "input": oracle_input,
    })

    provisional = OracleState(
        schema_version="oracle-state/v1",
        oracle_version=prior_state.oracle_version,
        generation=next_generation,
        behavioral_state=prior_state.behavioral_state,
        adaptation_state=prior_state.adaptation_state,
        intervention_state=prior_state.intervention_state,
        history_digest=history_digest,
        state_hash="0" * 64,
    )

    next_state_hash = sha256_hex({
        "schema_version": provisional.schema_version,
        "oracle_version": provisional.oracle_version,
        "generation": provisional.generation,
        "behavioral_state": provisional.behavioral_state,
        "adaptation_state": provisional.adaptation_state,
        "intervention_state": provisional.intervention_state,
        "history_digest": provisional.history_digest,
    })

    next_state = replace(
        provisional,
        state_hash=next_state_hash,
    )

    proposal = OracleProposal(
        schema_version="oracle-proposal/v1",
        experiment_id=oracle_input.experiment_id,
        session_id=oracle_input.session_id,
        oracle_version=prior_state.oracle_version,
        proposal_id=sha256_hex({
            "experiment_id": oracle_input.experiment_id,
            "session_id": oracle_input.session_id,
            "frame_id": oracle_input.frame_id,
            "generation": next_generation,
        })[:24],
        proposal_type="ABSTAIN",
        proposal_payload=(),
        confidence=0.0,
        abstain=True,
        evidence_refs=oracle_input.evidence_refs,
        oracle_state_hash=next_state.state_hash,
    )

    validate_state(next_state)
    validate_proposal(proposal)

    return next_state, proposal


def transition_with_event(
    *,
    oracle_input: OracleInput,
    prior_state: OracleState,
    event_id: str,
    oracle_artifact_hash: str,
    previous_event_hash: str | None,
) -> tuple[
    OracleState,
    OracleProposal,
    OracleEvent,
]:
    next_state, proposal = transition(
        oracle_input=oracle_input,
        prior_state=prior_state,
    )

    event = build_event(
        event_id=event_id,
        oracle_input=oracle_input,
        pre_state=prior_state,
        proposal=proposal,
        post_state=next_state,
        oracle_artifact_hash=oracle_artifact_hash,
        previous_event_hash=previous_event_hash,
    )

    return next_state, proposal, event
