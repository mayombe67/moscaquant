import hashlib
import json

from overwatch.events import TelemetryEventV1
from overwatch.segmented_storage import (
    MANIFEST_SCHEMA,
    SegmentedObjectStorage,
)
from overwatch.storage import ObjectStorageClient


class FakeObjectStorageClient(ObjectStorageClient):
    def __init__(self):
        self.objects = {}
        self.puts = []

    def get_object_bytes(self, *, bucket, key):
        return self.objects.get((bucket, key))

    def put_object_bytes(self, *, bucket, key, body, content_type):
        self.puts.append((bucket, key, content_type))
        self.objects[(bucket, key)] = body


def _event(kind, run_id="run-001"):
    return TelemetryEventV1(
        event_type=kind,
        run_id=run_id,
        component="runtime",
    )


def test_append_many_writes_immutable_segment_then_manifest():
    client = FakeObjectStorageClient()
    storage = SegmentedObjectStorage(
        client=client,
        bucket="private-telemetry",
        prefix="runs/run-001",
    )

    storage.append_many([
        _event("run.started"),
        _event("run.progress"),
    ])

    assert len(client.puts) == 2
    assert "/segments/" in client.puts[0][1]
    assert client.puts[0][2] == "application/x-ndjson"
    assert client.puts[1][1] == "runs/run-001/manifest.json"

    manifest = json.loads(
        client.objects[
            ("private-telemetry", "runs/run-001/manifest.json")
        ].decode("utf-8")
    )

    assert manifest["schema_version"] == MANIFEST_SCHEMA
    assert manifest["event_count"] == 2
    assert manifest["segment_count"] == 1
    assert len(manifest["segments"]) == 1

    record = manifest["segments"][0]
    body = client.objects[("private-telemetry", record["key"])]

    assert record["byte_count"] == len(body)
    assert record["sha256"] == hashlib.sha256(body).hexdigest()
    assert len(body.decode("utf-8").splitlines()) == 2


def test_second_append_creates_new_segment_without_rewriting_first():
    client = FakeObjectStorageClient()
    storage = SegmentedObjectStorage(
        client=client,
        bucket="private-telemetry",
        prefix="runs/run-002",
    )

    storage.append(_event("run.started", "run-002"))

    manifest1 = json.loads(
        client.objects[
            ("private-telemetry", "runs/run-002/manifest.json")
        ].decode("utf-8")
    )
    first_key = manifest1["segments"][0]["key"]
    first_body = client.objects[("private-telemetry", first_key)]

    storage.append(_event("run.completed", "run-002"))

    assert client.objects[("private-telemetry", first_key)] == first_body

    manifest2 = json.loads(
        client.objects[
            ("private-telemetry", "runs/run-002/manifest.json")
        ].decode("utf-8")
    )
    assert manifest2["event_count"] == 2
    assert manifest2["segment_count"] == 2
    assert manifest2["segments"][0]["key"] == first_key


def test_empty_batch_is_noop():
    client = FakeObjectStorageClient()
    storage = SegmentedObjectStorage(
        client=client,
        bucket="private-telemetry",
        prefix="runs/run-003",
    )

    storage.append_many([])

    assert client.puts == []


def test_rejects_unknown_manifest_schema():
    client = FakeObjectStorageClient()
    client.objects[
        ("private-telemetry", "runs/run-004/manifest.json")
    ] = json.dumps({
        "schema_version": "future.v99",
        "segments": [],
    }).encode("utf-8")

    storage = SegmentedObjectStorage(
        client=client,
        bucket="private-telemetry",
        prefix="runs/run-004",
    )

    try:
        storage.append(_event("run.started", "run-004"))
    except RuntimeError as exc:
        assert "manifest schema" in str(exc)
    else:
        raise AssertionError("expected RuntimeError")
