import json
from overwatch.events import SCHEMA_VERSION, TelemetryEventV1
from overwatch.lore import LORE_SURFACES
from overwatch.writer import JsonlTelemetryWriter

def test_event_envelope_is_stable():
    event = TelemetryEventV1(
        event_type="run.started",
        run_id="run-001",
        component="science",
        experiment_id="MQ-001",
        payload={"phase": "test"},
    )
    data = event.to_dict()
    assert data["schema_version"] == SCHEMA_VERSION
    assert data["event_type"] == "run.started"
    assert data["run_id"] == "run-001"
    assert data["payload"] == {"phase": "test"}
    assert data["event_id"]
    assert data["timestamp_utc"]

def test_writer_appends_one_json_object_per_line(tmp_path):
    out = tmp_path / "telemetry.jsonl"
    JsonlTelemetryWriter(out).emit(
        TelemetryEventV1(
            event_type="checkpoint.saved",
            run_id="run-001",
            component="runtime",
            payload={"checkpoint": "cp-001"},
        )
    )
    lines = out.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    data = json.loads(lines[0])
    assert data["event_type"] == "checkpoint.saved"

def test_lore_is_downstream_of_event_type():
    assert LORE_SURFACES["run.started"] == "SPAWN"
    assert LORE_SURFACES["worker.failed"] == "KILLFEED"
    assert LORE_SURFACES["run.highlight_candidate"] == "PLAY OF THE GAME"
