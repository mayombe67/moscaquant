import json

from overwatch.events import TelemetryEventV1
from overwatch.integrity import ObjectLister, verify_segmented_receipts
from overwatch.segmented_storage import SegmentedObjectStorage
from overwatch.storage import ObjectStorageClient


class FakeClient(ObjectStorageClient, ObjectLister):
    def __init__(self):
        self.objects = {}

    def get_object_bytes(self, *, bucket, key):
        return self.objects.get((bucket, key))

    def put_object_bytes(self, *, bucket, key, body, content_type):
        self.objects[(bucket, key)] = body

    def list_object_keys(self, *, bucket, prefix):
        return sorted(
            key
            for (b, key), _ in self.objects.items()
            if b == bucket and key.startswith(prefix)
        )


def _event(kind):
    return TelemetryEventV1(
        event_type=kind,
        run_id="run-001",
        component="runtime",
    )


def _storage(client):
    return SegmentedObjectStorage(
        client=client,
        bucket="telemetry",
        prefix="runs/run-001",
    )


def test_integrity_report_is_clean_for_valid_receipts():
    client = FakeClient()
    storage = _storage(client)
    storage.append_many([_event("run.started"), _event("run.completed")])

    report = verify_segmented_receipts(
        client=client,
        lister=client,
        bucket="telemetry",
        prefix="runs/run-001",
    )

    assert report.ok is True
    assert report.expected_segments == 1
    assert report.verified_segments == 1
    assert report.expected_events == 2
    assert report.verified_events == 2
    assert report.issues == ()


def test_integrity_detects_corrupt_segment():
    client = FakeClient()
    storage = _storage(client)
    storage.append(_event("run.started"))

    manifest = json.loads(
        client.objects[("telemetry", "runs/run-001/manifest.json")].decode()
    )
    key = manifest["segments"][0]["key"]
    client.objects[("telemetry", key)] = b"tampered\n"

    report = verify_segmented_receipts(
        client=client,
        lister=client,
        bucket="telemetry",
        prefix="runs/run-001",
    )

    kinds = {issue.kind for issue in report.issues}
    assert report.ok is False
    assert "segment.sha256" in kinds
    assert "manifest.event_total" in kinds


def test_integrity_detects_missing_segment():
    client = FakeClient()
    storage = _storage(client)
    storage.append(_event("run.started"))

    manifest = json.loads(
        client.objects[("telemetry", "runs/run-001/manifest.json")].decode()
    )
    key = manifest["segments"][0]["key"]
    del client.objects[("telemetry", key)]

    report = verify_segmented_receipts(
        client=client,
        lister=client,
        bucket="telemetry",
        prefix="runs/run-001",
    )

    assert any(issue.kind == "segment.missing" for issue in report.issues)


def test_integrity_detects_orphan_segment():
    client = FakeClient()
    storage = _storage(client)
    storage.append(_event("run.started"))

    orphan = "runs/run-001/segments/99999999-orphan.ndjson"
    client.objects[("telemetry", orphan)] = b'{"event":"orphan"}\n'

    report = verify_segmented_receipts(
        client=client,
        lister=client,
        bucket="telemetry",
        prefix="runs/run-001",
    )

    assert orphan in report.orphan_segments
    assert any(issue.kind == "segment.orphan" for issue in report.issues)


def test_integrity_detects_missing_manifest():
    client = FakeClient()
    orphan = "runs/run-001/segments/00000001-orphan.ndjson"
    client.objects[("telemetry", orphan)] = b'{"event":"orphan"}\n'

    report = verify_segmented_receipts(
        client=client,
        lister=client,
        bucket="telemetry",
        prefix="runs/run-001",
    )

    assert report.manifest_present is False
    assert report.ok is False
    assert orphan in report.orphan_segments
    assert report.issues[0].kind == "manifest.missing"
