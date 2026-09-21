import pytest

from overwatch.live_replay import (
    StreamCursorV1,
    emit_replay_divergence,
    emit_stream_gap,
    emit_stream_handoff,
    handoff_cursor,
)
from overwatch.replay import ReplayDivergenceV1
from overwatch.storage import LocalJsonlStorage


def test_cursor_handoff_preserves_run_and_sequence():
    live = StreamCursorV1(
        run_id="run-1",
        sequence=120,
        mode="live",
        frame_index=10,
    )

    replay = handoff_cursor(live, to_mode="replay")

    assert replay.run_id == live.run_id
    assert replay.sequence == live.sequence
    assert replay.mode == "replay"
    assert replay.frame_index == 10


def test_invalid_cursor_mode_rejected():
    with pytest.raises(ValueError):
        StreamCursorV1(
            run_id="run-1",
            sequence=0,
            mode="banana",
        )


def test_stream_handoff_cannot_change_sequence(tmp_path):
    storage = LocalJsonlStorage(tmp_path / "handoff.jsonl")

    with pytest.raises(ValueError):
        emit_stream_handoff(
            storage,
            run_id="run-1",
            from_cursor=StreamCursorV1("run-1", 10, "live"),
            to_cursor=StreamCursorV1("run-1", 11, "replay"),
            reason="viewer_scrub",
        )


def test_replay_divergence_emits_killfeed_event(tmp_path):
    storage = LocalJsonlStorage(tmp_path / "handoff.jsonl")
    divergence = ReplayDivergenceV1(
        sample_index=42,
        expected_hash="abc",
        actual_hash="def",
        kind="state_hash",
        detail="replayed state differs",
    )

    event = emit_replay_divergence(
        storage,
        run_id="run-2",
        divergence=divergence,
        source_frame_index=7,
    )

    assert event.event_type == "replay.divergence"
    assert event.lore_surface == "KILLFEED"
    assert event.payload["handling"] == "report_only_no_silent_repair"
    assert event.payload["source_frame_index"] == 7


def test_stream_gap_reports_expected_and_actual_sequence(tmp_path):
    event = emit_stream_gap(
        LocalJsonlStorage(tmp_path / "handoff.jsonl"),
        run_id="run-3",
        expected_sequence=100,
        actual_sequence=104,
    )

    assert event.event_type == "stream.gap"
    assert event.payload["missing_count"] == 4
    assert event.payload["handling"] == "report_and_stop_frame_assembly"
