from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, is_dataclass, replace
from typing import Any
from datetime import datetime, timezone

from oracle.models import OracleEvent, OracleInput, OracleProposal, OracleState


class OracleAuditError(ValueError):
    pass


def _canonicalize(value: Any) -> Any:
    if is_dataclass(value):
        return _canonicalize(asdict(value))

    if isinstance(value, dict):
        return {
            str(key): _canonicalize(val)
            for key, val in sorted(
                value.items(),
                key=lambda item: str(item[0]),
            )
        }

    if isinstance(value, (list, tuple)):
        return [_canonicalize(item) for item in value]

    if isinstance(value, (str, int, float, bool)) or value is None:
        return value

    raise OracleAuditError(
        f"unsupported canonical value type: {type(value).__name__}"
    )


def canonical_json(value: Any) -> str:
    normalized = _canonicalize(value)

    return json.dumps(
        normalized,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def sha256_hex(value: Any) -> str:
    payload = canonical_json(value).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def event_payload(event: OracleEvent) -> dict[str, Any]:
    payload = asdict(event)

    # event_hash cannot participate in its own digest.
    payload.pop("event_hash")

    return payload


def compute_event_hash(event: OracleEvent) -> str:
    return sha256_hex(event_payload(event))


def verify_event_hash(event: OracleEvent) -> None:
    expected = compute_event_hash(event)

    if event.event_hash != expected:
        raise OracleAuditError(
            "OracleEvent hash mismatch"
        )


def verify_chain(
    previous: OracleEvent | None,
    current: OracleEvent,
) -> None:
    verify_event_hash(current)

    if previous is None:
        if current.previous_event_hash is not None:
            raise OracleAuditError(
                "genesis event must not reference a predecessor"
            )
        return

    verify_event_hash(previous)

    if current.previous_event_hash != previous.event_hash:
        raise OracleAuditError(
            "OracleEvent chain link mismatch"
        )


def verify_chain_sequence(
    events: tuple[OracleEvent, ...],
) -> None:
    previous: OracleEvent | None = None

    for event in events:
        verify_chain(previous, event)
        previous = event


def build_event(
    *,
    event_id: str,
    oracle_input: OracleInput,
    pre_state: OracleState,
    proposal: OracleProposal,
    post_state: OracleState,
    oracle_artifact_hash: str,
    previous_event_hash: str | None,
    intervention_id: str | None = None,
    entropy_commitment: str | None = None,
    warden_disposition: str | None = None,
    notes: str | None = None,
) -> OracleEvent:
    event = OracleEvent(
        schema_version="oracle-event/v1",
        event_id=event_id,
        timestamp=datetime.now(timezone.utc).isoformat(),
        experiment_id=oracle_input.experiment_id,
        session_id=oracle_input.session_id,
        oracle_version=proposal.oracle_version,
        oracle_artifact_hash=oracle_artifact_hash,
        input_hash=sha256_hex(oracle_input),
        pre_state_hash=pre_state.state_hash,
        proposal_hash=sha256_hex(proposal),
        post_state_hash=post_state.state_hash,
        previous_event_hash=previous_event_hash,
        event_hash="",
        intervention_id=intervention_id,
        entropy_commitment=entropy_commitment,
        warden_disposition=warden_disposition,
        notes=notes,
    )

    return replace(
        event,
        event_hash=compute_event_hash(event),
    )
