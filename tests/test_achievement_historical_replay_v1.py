import json
from pathlib import Path

from achievements.historical_replay_v1 import historical_replay_occurrences
from achievements.ledger_v1 import load_occurrence_jsonl
from achievements.models import Origin


EXPECTED_IDS = {
    "ACH-001",
    "ACH-002",
    "ACH-003",
    "ACH-004",
    "ACH-005",
    "ACH-006",
    "ACH-007",
    "ACH-008",
    "ACH-009",
    "ACH-019",
    "ACH-020",
}


def test_historical_replay_materializes_expected_11():
    rows = historical_replay_occurrences()
    assert len(rows) == 11
    assert {row.achievement_id for row in rows} == EXPECTED_IDS
    assert all(row.origin is Origin.HISTORICAL_REPLAY for row in rows)
    assert all(row.stack_index == 1 for row in rows)
    assert all(row.source_event_type == "HISTORICAL_EVIDENCE_REPLAY" for row in rows)


def test_historical_replay_hash_chain_is_deterministic():
    first = historical_replay_occurrences()
    second = historical_replay_occurrences()

    assert [row.state_hash for row in first] == [row.state_hash for row in second]
    assert first[0].previous_occurrence_hash == ""
    for previous, current in zip(first, first[1:]):
        assert current.previous_occurrence_hash == previous.state_hash


def test_jsonl_loader_reconstructs_store(tmp_path: Path):
    rows = historical_replay_occurrences()
    path = tmp_path / "occurrences.jsonl"
    path.write_text(
        "".join(
            json.dumps({
                "occurrence_id": row.occurrence_id,
                "achievement_id": row.achievement_id,
                "achievement_version": row.achievement_version,
                "trigger_version": row.trigger_version,
                "subject_id": row.subject_id,
                "occurred_at": row.occurred_at,
                "source_event_id": row.source_event_id,
                "source_event_type": row.source_event_type,
                "origin": row.origin.value,
                "stack_index": row.stack_index,
                "evidence": dict(row.evidence),
                "artifact_refs": list(row.artifact_refs),
                "experiment_id": row.experiment_id,
                "session_id": row.session_id,
                "generation": row.generation,
                "runtime_profile": row.runtime_profile,
                "experiment_seed": row.experiment_seed,
                "state_hash": row.state_hash,
                "previous_occurrence_hash": row.previous_occurrence_hash,
            }, sort_keys=True) + "\n"
            for row in rows
        )
    )

    store = load_occurrence_jsonl(path)
    assert store.stack_count("ACH-001") == 1
    assert store.stack_count("ACH-020") == 1
    assert store.first_seen("ACH-003") == "2026-09-18T00:00:00Z"
