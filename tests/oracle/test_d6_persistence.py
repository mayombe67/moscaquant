from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from oracle.d6_persistence import (
    D6PersistenceError,
    append_record,
    build_selection_record,
    load_records,
)
from oracle.selector import select_d6


def test_d6_selection_round_trip(tmp_path: Path):
    result = select_d6(
        seed=42,
        experiment_id="mq7-d6",
        session_id="session-001",
        plasticity_active=False,
    )

    record = build_selection_record(
        experiment_id="mq7-d6",
        session_id="session-001",
        timestamp="2026-09-17T00:00:00+00:00",
        result=result,
        previous_record_hash=None,
    )

    path = tmp_path / "d6-selections.jsonl"
    append_record(path, record)

    loaded = load_records(path)

    assert loaded == (record,)


def test_d6_selection_chain_round_trip(tmp_path: Path):
    first_result = select_d6(
        seed=42,
        experiment_id="mq7-d6",
        session_id="session-001",
        plasticity_active=False,
    )

    first = build_selection_record(
        experiment_id="mq7-d6",
        session_id="session-001",
        timestamp="2026-09-17T00:00:00+00:00",
        result=first_result,
        previous_record_hash=None,
    )

    second_result = select_d6(
        seed=43,
        experiment_id="mq7-d6",
        session_id="session-001",
        plasticity_active=False,
    )

    second = build_selection_record(
        experiment_id="mq7-d6",
        session_id="session-001",
        timestamp="2026-09-17T00:01:00+00:00",
        result=second_result,
        previous_record_hash=first.record_hash,
    )

    path = tmp_path / "d6-selections.jsonl"

    append_record(path, first)
    append_record(path, second)

    assert load_records(path) == (first, second)


def test_d6_record_tampering_is_rejected(tmp_path: Path):
    result = select_d6(
        seed=42,
        experiment_id="mq7-d6",
        session_id="session-001",
        plasticity_active=False,
    )

    record = build_selection_record(
        experiment_id="mq7-d6",
        session_id="session-001",
        timestamp="2026-09-17T00:00:00+00:00",
        result=result,
        previous_record_hash=None,
    )

    path = tmp_path / "d6-selections.jsonl"
    append_record(path, record)

    text = path.read_text(encoding="utf-8")
    path.write_text(
        text.replace(
            '"status":"SELECTED"',
            '"status":"CHEATED"',
        ),
        encoding="utf-8",
    )

    with pytest.raises(
        D6PersistenceError,
        match="hash mismatch",
    ):
        load_records(path)


def test_d6_chain_tampering_is_rejected(tmp_path: Path):
    first_result = select_d6(
        seed=42,
        experiment_id="mq7-d6",
        session_id="session-001",
        plasticity_active=False,
    )

    first = build_selection_record(
        experiment_id="mq7-d6",
        session_id="session-001",
        timestamp="2026-09-17T00:00:00+00:00",
        result=first_result,
        previous_record_hash=None,
    )

    second_result = select_d6(
        seed=43,
        experiment_id="mq7-d6",
        session_id="session-001",
        plasticity_active=False,
    )

    second = build_selection_record(
        experiment_id="mq7-d6",
        session_id="session-001",
        timestamp="2026-09-17T00:01:00+00:00",
        result=second_result,
        previous_record_hash=first.record_hash,
    )

    bad_second = replace(
        second,
        previous_record_hash="b" * 64,
        record_hash="",
    )

    bad_second = replace(
        bad_second,
        record_hash=__import__(
            "oracle.d6_persistence",
            fromlist=["compute_record_hash"],
        ).compute_record_hash(bad_second),
    )

    path = tmp_path / "d6-selections.jsonl"

    append_record(path, first)
    append_record(path, bad_second)

    with pytest.raises(
        D6PersistenceError,
        match="chain mismatch",
    ):
        load_records(path)
