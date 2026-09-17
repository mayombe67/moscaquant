from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, is_dataclass
from typing import Any

from oracle.models import OracleEvent


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
