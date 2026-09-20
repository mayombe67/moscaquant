from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Iterable

from .events import TelemetryEventV1
from .storage import ObjectStorageClient, TelemetryStorage


MANIFEST_SCHEMA = "overwatch.segment-manifest.v1"


@dataclass(frozen=True)
class SegmentRecord:
    key: str
    event_count: int
    sha256: str
    byte_count: int

    def to_dict(self) -> dict[str, object]:
        return {
            "key": self.key,
            "event_count": self.event_count,
            "sha256": self.sha256,
            "byte_count": self.byte_count,
        }


class SegmentedObjectStorage(TelemetryStorage):
    """Immutable object-segment storage for OVERWATCH telemetry.

    Segment objects are written once and never rewritten. A small manifest is
    updated after each successful segment write.

    v1 assumes a single writer for a given run prefix. Deployment code must
    enforce that ownership boundary.
    """

    def __init__(
        self,
        *,
        client: ObjectStorageClient,
        bucket: str,
        prefix: str,
    ):
        if not bucket:
            raise ValueError("bucket is required")
        if not prefix:
            raise ValueError("prefix is required")

        self.client = client
        self.bucket = bucket
        self.prefix = prefix.rstrip("/")
        self.manifest_key = f"{self.prefix}/manifest.json"

    def append(self, event: TelemetryEventV1) -> None:
        self.append_many([event])

    def append_many(self, events: Iterable[TelemetryEventV1]) -> None:
        batch = list(events)
        if not batch:
            return

        manifest = self._load_manifest()
        sequence = len(manifest["segments"]) + 1

        body = self._encode_events(batch)
        digest = hashlib.sha256(body).hexdigest()
        segment_key = f"{self.prefix}/segments/{sequence:08d}-{digest[:12]}.ndjson"

        # Immutable evidence first.
        existing = self.client.get_object_bytes(
            bucket=self.bucket,
            key=segment_key,
        )
        if existing is not None and existing != body:
            raise RuntimeError(
                f"segment collision at {segment_key}; refusing to overwrite evidence"
            )
        if existing is None:
            self.client.put_object_bytes(
                bucket=self.bucket,
                key=segment_key,
                body=body,
                content_type="application/x-ndjson",
            )

        record = SegmentRecord(
            key=segment_key,
            event_count=len(batch),
            sha256=digest,
            byte_count=len(body),
        )

        manifest["segments"].append(record.to_dict())
        manifest["event_count"] += len(batch)
        manifest["segment_count"] = len(manifest["segments"])

        manifest_body = (
            json.dumps(
                manifest,
                sort_keys=True,
                indent=2,
                ensure_ascii=False,
            )
            + "\n"
        ).encode("utf-8")

        # Small mutable index written only after immutable evidence exists.
        self.client.put_object_bytes(
            bucket=self.bucket,
            key=self.manifest_key,
            body=manifest_body,
            content_type="application/json",
        )

    def _encode_events(self, events: list[TelemetryEventV1]) -> bytes:
        rows = [
            json.dumps(
                event.to_dict(),
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            )
            for event in events
        ]
        return ("\n".join(rows) + "\n").encode("utf-8")

    def _load_manifest(self) -> dict[str, object]:
        raw = self.client.get_object_bytes(
            bucket=self.bucket,
            key=self.manifest_key,
        )
        if raw is None:
            return {
                "schema_version": MANIFEST_SCHEMA,
                "event_count": 0,
                "segment_count": 0,
                "segments": [],
            }

        manifest = json.loads(raw.decode("utf-8"))
        if manifest.get("schema_version") != MANIFEST_SCHEMA:
            raise RuntimeError("unsupported OVERWATCH manifest schema")
        if not isinstance(manifest.get("segments"), list):
            raise RuntimeError("invalid OVERWATCH manifest")
        return manifest
