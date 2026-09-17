from __future__ import annotations

import json
import os
from dataclasses import asdict
from pathlib import Path
from typing import Any

from oracle.audit import canonical_json, verify_chain_sequence
from oracle.models import OracleEvent, OracleState


class OraclePersistenceError(ValueError):
    pass


def _atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    temp = path.with_suffix(path.suffix + ".tmp")

    with temp.open("w", encoding="utf-8") as handle:
        handle.write(text)
        handle.flush()
        os.fsync(handle.fileno())

    os.replace(temp, path)


def append_event(path: Path, event: OracleEvent) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    line = canonical_json(event) + "\n"

    with path.open("a", encoding="utf-8") as handle:
        handle.write(line)
        handle.flush()
        os.fsync(handle.fileno())


def write_state(path: Path, state: OracleState) -> None:
    _atomic_write_text(
        path,
        canonical_json(state) + "\n",
    )


def write_metadata(
    path: Path,
    *,
    oracle_version: str,
    oracle_artifact_hash: str,
    last_event: OracleEvent,
    state: OracleState,
    event_count: int,
) -> None:
    payload = {
        "schema_version": "oracle-persistence/v1",
        "oracle_version": oracle_version,
        "oracle_artifact_hash": oracle_artifact_hash,
        "last_verified_event_id": last_event.event_id,
        "last_verified_event_hash": last_event.event_hash,
        "state_hash": state.state_hash,
        "event_count": event_count,
    }

    _atomic_write_text(
        path,
        canonical_json(payload) + "\n",
    )


def load_events(path: Path) -> tuple[OracleEvent, ...]:
    if not path.exists():
        return ()

    events: list[OracleEvent] = []

    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()

            if not line:
                raise OraclePersistenceError(
                    f"blank event record at line {line_number}"
                )

            try:
                payload = json.loads(line)
                events.append(OracleEvent(**payload))
            except Exception as exc:
                raise OraclePersistenceError(
                    f"invalid event record at line {line_number}"
                ) from exc

    verify_chain_sequence(tuple(events))
    return tuple(events)


def load_state(path: Path) -> OracleState:
    if not path.exists():
        raise OraclePersistenceError(
            "state snapshot missing"
        )

    try:
        payload = json.loads(
            path.read_text(encoding="utf-8")
        )

        for field in (
            "behavioral_state",
            "adaptation_state",
            "intervention_state",
        ):
            payload[field] = tuple(
                tuple(item)
                for item in payload[field]
            )

        return OracleState(**payload)

    except Exception as exc:
        raise OraclePersistenceError(
            "invalid state snapshot"
        ) from exc


def load_metadata(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise OraclePersistenceError(
            "metadata missing"
        )

    try:
        payload = json.loads(
            path.read_text(encoding="utf-8")
        )
    except Exception as exc:
        raise OraclePersistenceError(
            "invalid metadata"
        ) from exc

    if not isinstance(payload, dict):
        raise OraclePersistenceError(
            "metadata must be a JSON object"
        )

    return payload


def verify_persisted_state(
    *,
    events: tuple[OracleEvent, ...],
    state: OracleState,
    metadata: dict[str, Any],
) -> None:
    if not events:
        raise OraclePersistenceError(
            "cannot verify state without events"
        )

    last = events[-1]

    if state.state_hash != last.post_state_hash:
        raise OraclePersistenceError(
            "state snapshot does not match final event"
        )

    if metadata.get("last_verified_event_hash") != last.event_hash:
        raise OraclePersistenceError(
            "metadata event hash mismatch"
        )

    if metadata.get("last_verified_event_id") != last.event_id:
        raise OraclePersistenceError(
            "metadata event id mismatch"
        )

    if metadata.get("state_hash") != state.state_hash:
        raise OraclePersistenceError(
            "metadata state hash mismatch"
        )

    if metadata.get("event_count") != len(events):
        raise OraclePersistenceError(
            "metadata event count mismatch"
        )
