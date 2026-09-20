import json

import pytest

from overwatch.behavior import (
    MoodVectorV1,
    emit_decision_trace,
    emit_lineage,
    emit_mood_state,
    emit_reinforcement,
    emit_state_transition,
)
from overwatch.storage import LocalJsonlStorage


def _read(path):
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
    ]


def test_mood_vector_is_normalized_and_emits_hud_state(tmp_path):
    path = tmp_path / "behavior.jsonl"
    storage = LocalJsonlStorage(path)

    mood = MoodVectorV1(
        hunger=0.3,
        arousal=0.7,
        courtship_drive=0.6,
        threat=0.2,
        fatigue=0.4,
        reward=0.8,
        punishment=0.1,
        abnormal_state=0.0,
        sugar_cube_state=0.0,
    )

    event = emit_mood_state(
        storage,
        run_id="run-001",
        mood=mood,
        experiment_id="MQ-TEST",
    )

    assert event.event_type == "state.mood"
    assert event.lore_surface == "HUD"
    assert event.payload["indicators"]["arousal"] == 0.7
    assert "not evidence of subjective human emotion" in (
        event.payload["interpretation_boundary"]
    )


def test_mood_vector_rejects_out_of_range_values():
    with pytest.raises(ValueError):
        MoodVectorV1(
            hunger=1.1,
            arousal=0.0,
            courtship_drive=0.0,
            threat=0.0,
            fatigue=0.0,
            reward=0.0,
            punishment=0.0,
        )


def test_state_transition_records_before_after_and_cause(tmp_path):
    path = tmp_path / "behavior.jsonl"
    event = emit_state_transition(
        LocalJsonlStorage(path),
        run_id="run-002",
        state_name="threat",
        before=0.2,
        after=0.8,
        cause_event_id="evt-parent",
    )

    assert event.event_type == "state.transition"
    assert event.payload["before"] == 0.2
    assert event.payload["after"] == 0.8
    assert event.payload["cause_event_id"] == "evt-parent"


def test_decision_trace_preserves_oracle_warden_final_chain(tmp_path):
    path = tmp_path / "behavior.jsonl"
    event = emit_decision_trace(
        LocalJsonlStorage(path),
        run_id="run-003",
        input_ref="market://snapshot-42",
        encoded_state_ref="state://encoded-42",
        oracle_proposal={"action": "A"},
        warden_disposition="allowed",
        final_output={"action": "A"},
    )

    assert event.event_type == "decision.trace"
    assert event.payload["oracle_proposal"] == {"action": "A"}
    assert event.payload["warden_disposition"] == "allowed"
    assert event.payload["final_output"] == {"action": "A"}


def test_reinforcement_records_method_and_intensity(tmp_path):
    path = tmp_path / "behavior.jsonl"
    event = emit_reinforcement(
        LocalJsonlStorage(path),
        run_id="run-004",
        method="timeout",
        intensity=0.5,
        duration_seconds=2.0,
        trigger_reason="synthetic-test",
        outcome="applied",
    )

    assert event.event_type == "reinforcement.applied"
    assert event.lore_surface == "KILLFEED"
    assert event.payload["method"] == "timeout"
    assert event.payload["intensity"] == 0.5


def test_lineage_checkpoint_records_parent_generation_and_boundary(tmp_path):
    path = tmp_path / "behavior.jsonl"
    emit_lineage(
        LocalJsonlStorage(path),
        run_id="run-005",
        checkpoint_ref="checkpoint://child",
        parent_checkpoint_ref="checkpoint://parent",
        generation=3,
        fork_reason="frozen-experiment-branch",
        canonical_codename="MORTY",
        status="candidate",
    )

    row = _read(path)[0]

    assert row["event_type"] == "lineage.checkpoint"
    assert row["payload"]["generation"] == 3
    assert row["payload"]["canonical_codename"] == "MORTY"
    assert "do not constitute scientific evidence" in (
        row["payload"]["science_boundary"]
    )
