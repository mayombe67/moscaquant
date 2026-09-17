from __future__ import annotations

from pathlib import Path

import pytest

from oracle.audit import sha256_hex
from oracle.models import OracleInput
from oracle.persistence import (
    OraclePersistenceError,
    append_event,
    write_metadata,
    write_state,
)
from oracle.replay import load_replay
from oracle.state import (
    initial_state,
    transition_with_event,
)


HASH = "a" * 64


def make_input(prior_state_hash: str) -> OracleInput:
    return OracleInput(
        schema_version="oracle-input/v1",
        experiment_id="mq7-persist",
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


def build_history(base: Path):
    state = initial_state(
        oracle_version="ORACLE-01-GLaDOS/0.1.0",
    )

    oracle_input = make_input(state.state_hash)

    next_state, _, event = transition_with_event(
        oracle_input=oracle_input,
        prior_state=state,
        event_id="event-001",
        oracle_artifact_hash=HASH,
        previous_event_hash=None,
    )

    append_event(
        base / "events.jsonl",
        event,
    )

    write_state(
        base / "state.json",
        next_state,
    )

    write_metadata(
        base / "metadata.json",
        oracle_version=next_state.oracle_version,
        oracle_artifact_hash=HASH,
        last_event=event,
        state=next_state,
        event_count=1,
    )

    return next_state, event


def test_valid_history_reloads(tmp_path: Path):
    state, event = build_history(tmp_path)

    replay = load_replay(tmp_path)

    assert replay.state == state
    assert replay.events == (event,)
    assert replay.metadata["event_count"] == 1


def test_tampered_event_is_rejected(tmp_path: Path):
    build_history(tmp_path)

    path = tmp_path / "events.jsonl"

    text = path.read_text(encoding="utf-8")
    path.write_text(
        text.replace(
            "event-001",
            "event-evil",
        ),
        encoding="utf-8",
    )

    with pytest.raises(Exception):
        load_replay(tmp_path)


def test_state_mismatch_is_rejected(tmp_path: Path):
    state, _ = build_history(tmp_path)

    bad = state.__class__(
        **{
            **state.__dict__,
            "state_hash": "b" * 64,
        }
    )

    write_state(
        tmp_path / "state.json",
        bad,
    )

    with pytest.raises(
        OraclePersistenceError,
        match="state snapshot",
    ):
        load_replay(tmp_path)


def test_metadata_mismatch_is_rejected(tmp_path: Path):
    build_history(tmp_path)

    path = tmp_path / "metadata.json"

    text = path.read_text(encoding="utf-8")
    path.write_text(
        text.replace(
            '"event_count":1',
            '"event_count":99',
        ),
        encoding="utf-8",
    )

    with pytest.raises(
        OraclePersistenceError,
        match="event count",
    ):
        load_replay(tmp_path)
