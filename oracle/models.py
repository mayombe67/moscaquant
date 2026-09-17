from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class OracleInput:
    schema_version: str
    experiment_id: str
    session_id: str
    frame_id: str
    timestamp: str
    mq001_version: str
    scientific_config_hash: str
    evidence_refs: tuple[str, ...]
    derived_features: tuple[tuple[str, Any], ...]
    prior_oracle_state_hash: str | None
    warden_history: tuple[str, ...]


@dataclass(frozen=True)
class OracleState:
    schema_version: str
    oracle_version: str
    generation: int
    behavioral_state: tuple[tuple[str, Any], ...]
    adaptation_state: tuple[tuple[str, Any], ...]
    intervention_state: tuple[tuple[str, Any], ...]
    history_digest: str
    state_hash: str


@dataclass(frozen=True)
class OracleProposal:
    schema_version: str
    experiment_id: str
    session_id: str
    oracle_version: str
    proposal_id: str
    proposal_type: str
    proposal_payload: tuple[tuple[str, Any], ...]
    confidence: float
    abstain: bool
    evidence_refs: tuple[str, ...]
    oracle_state_hash: str


@dataclass(frozen=True)
class OracleEvent:
    schema_version: str
    event_id: str
    timestamp: str
    experiment_id: str
    session_id: str
    oracle_version: str
    oracle_artifact_hash: str
    input_hash: str
    pre_state_hash: str
    proposal_hash: str
    post_state_hash: str
    previous_event_hash: str | None
    event_hash: str
    intervention_id: str | None = None
    entropy_commitment: str | None = None
    warden_disposition: str | None = None
    notes: str | None = None
