import json

from overwatch.runtime import (
    emit_checkpoint,
    emit_progress,
    emit_runtime_snapshot,
    emit_worker_failure,
    emit_worker_recovered,
)
from overwatch.writer import JsonlTelemetryWriter


def _read_events(path):
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
    ]


def test_runtime_snapshot_emits_hud_event(tmp_path):
    out = tmp_path / "ow.jsonl"
    writer = JsonlTelemetryWriter(out)

    event = emit_runtime_snapshot(
        writer,
        run_id="run-001",
        experiment_id="MQ-TEST",
        disk_path=tmp_path,
    )

    assert event.event_type == "runtime.snapshot"
    assert event.lore_surface == "HUD"

    stored = _read_events(out)
    assert stored[0]["event_type"] == "runtime.snapshot"
    assert "memory" in stored[0]["payload"]
    assert "disk" in stored[0]["payload"]


def test_progress_emits_payload_surface(tmp_path):
    out = tmp_path / "ow.jsonl"
    event = emit_progress(
        JsonlTelemetryWriter(out),
        run_id="run-002",
        completed_units=25,
        total_units=100,
        units_per_second=12.5,
    )

    assert event.lore_surface == "PAYLOAD"
    assert event.payload["completed_units"] == 25


def test_checkpoint_emits_respawn_point(tmp_path):
    out = tmp_path / "ow.jsonl"
    event = emit_checkpoint(
        JsonlTelemetryWriter(out),
        run_id="run-003",
        checkpoint_ref="checkpoint://cp-1",
        duration_seconds=1.25,
    )

    assert event.lore_surface == "RESPAWN POINT"
    assert event.artifact_ref == "checkpoint://cp-1"


def test_failure_and_recovery_emit_killfeed_and_respawn(tmp_path):
    out = tmp_path / "ow.jsonl"
    writer = JsonlTelemetryWriter(out)

    failed = emit_worker_failure(
        writer,
        run_id="run-004",
        reason="synthetic failure",
        worker_id="worker-7",
    )
    recovered = emit_worker_recovered(
        writer,
        run_id="run-004",
        worker_id="worker-7",
        recovery_ref="checkpoint://cp-7",
    )

    assert failed.lore_surface == "KILLFEED"
    assert recovered.lore_surface == "RESPAWN"

    events = _read_events(out)
    assert [e["event_type"] for e in events] == [
        "worker.failed",
        "worker.recovered",
    ]
