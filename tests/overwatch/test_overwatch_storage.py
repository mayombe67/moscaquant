import json

from overwatch.events import TelemetryEventV1
from overwatch.storage import (
    LocalJsonlStorage,
    ObjectStorageClient,
    S3CompatibleJsonlStorage,
)


class FakeObjectStorageClient(ObjectStorageClient):
    def __init__(self):
        self.objects = {}

    def get_object_bytes(self, *, bucket, key):
        return self.objects.get((bucket, key))

    def put_object_bytes(self, *, bucket, key, body, content_type):
        assert content_type == "application/x-ndjson"
        self.objects[(bucket, key)] = body


def test_local_storage_appends_jsonl(tmp_path):
    path = tmp_path / "receipts.jsonl"
    storage = LocalJsonlStorage(path)

    storage.append(
        TelemetryEventV1(
            event_type="run.started",
            run_id="run-local",
            component="runtime",
        )
    )

    rows = path.read_text(encoding="utf-8").splitlines()
    assert len(rows) == 1
    assert json.loads(rows[0])["run_id"] == "run-local"


def test_s3_compatible_storage_appends_without_sdk_dependency():
    client = FakeObjectStorageClient()
    storage = S3CompatibleJsonlStorage(
        client=client,
        bucket="telemetry",
        key="runs/run-001/receipts.jsonl",
    )

    storage.append(
        TelemetryEventV1(
            event_type="run.started",
            run_id="run-001",
            component="runtime",
        )
    )
    storage.append(
        TelemetryEventV1(
            event_type="run.completed",
            run_id="run-001",
            component="runtime",
        )
    )

    body = client.objects[
        ("telemetry", "runs/run-001/receipts.jsonl")
    ].decode("utf-8")

    events = [json.loads(line) for line in body.splitlines()]
    assert [e["event_type"] for e in events] == [
        "run.started",
        "run.completed",
    ]


def test_s3_storage_requires_bucket_and_key():
    client = FakeObjectStorageClient()

    try:
        S3CompatibleJsonlStorage(client=client, bucket="", key="x")
    except ValueError as exc:
        assert "bucket" in str(exc)
    else:
        raise AssertionError("expected ValueError")

    try:
        S3CompatibleJsonlStorage(client=client, bucket="b", key="")
    except ValueError as exc:
        assert "key" in str(exc)
    else:
        raise AssertionError("expected ValueError")
