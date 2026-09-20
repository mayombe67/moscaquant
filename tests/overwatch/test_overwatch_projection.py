from overwatch.events import TelemetryEventV1
from overwatch.projection import public_projection

def test_public_projection_preserves_scientific_identity():
    event = TelemetryEventV1(
        event_type="run.progress",
        run_id="run-001",
        component="science",
        experiment_id="SQ-03F.6",
        git_commit="abc123",
        config_hash="cfg",
        dataset_hash="data",
        payload={"completed": 42, "total": 100},
    )
    projected = public_projection(event)
    assert projected["event_type"] == "run.progress"
    assert projected["run_id"] == "run-001"
    assert projected["experiment_id"] == "SQ-03F.6"
    assert projected["git_commit"] == "abc123"
    assert projected["payload"] == {"completed": 42, "total": 100}

def test_public_projection_strips_private_ops_fields_recursively():
    event = TelemetryEventV1(
        event_type="worker.failed",
        run_id="run-002",
        component="runtime",
        payload={
            "reason": "spot interruption",
            "hostname": "private-host",
            "private_ip": "10.0.0.5",
            "nested": {
                "bucket_name": "private-bucket",
                "endpoint": "https://internal.example",
                "safe": "kept",
            },
        },
    )
    projected = public_projection(event)
    assert projected["payload"] == {
        "reason": "spot interruption",
        "nested": {"safe": "kept"},
    }
