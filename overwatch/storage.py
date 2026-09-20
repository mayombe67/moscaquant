from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterable

from .events import TelemetryEventV1
from .writer import JsonlTelemetryWriter


class TelemetryStorage(ABC):
    """Storage boundary for OVERWATCH telemetry.

    Storage backends persist evidence. They do not alter experiment behavior.
    """

    @abstractmethod
    def append(self, event: TelemetryEventV1) -> None:
        raise NotImplementedError

    def append_many(self, events: Iterable[TelemetryEventV1]) -> None:
        for event in events:
            self.append(event)


class LocalJsonlStorage(TelemetryStorage):
    """Reference append-only local storage backend."""

    def __init__(self, path: str | Path):
        self.writer = JsonlTelemetryWriter(path)

    def append(self, event: TelemetryEventV1) -> None:
        self.writer.emit(event)


class ObjectStorageClient(ABC):
    """Minimal client contract required by S3-compatible storage."""

    @abstractmethod
    def get_object_bytes(self, *, bucket: str, key: str) -> bytes | None:
        raise NotImplementedError

    @abstractmethod
    def put_object_bytes(
        self,
        *,
        bucket: str,
        key: str,
        body: bytes,
        content_type: str,
    ) -> None:
        raise NotImplementedError


class S3CompatibleJsonlStorage(TelemetryStorage):
    """Dependency-injected S3-compatible JSONL storage.

    This module intentionally does not import boto3 or load credentials.
    Deployment/ops code supplies an ObjectStorageClient implementation.
    """

    def __init__(
        self,
        *,
        client: ObjectStorageClient,
        bucket: str,
        key: str,
    ):
        if not bucket:
            raise ValueError("bucket is required")
        if not key:
            raise ValueError("key is required")

        self.client = client
        self.bucket = bucket
        self.key = key

    def append(self, event: TelemetryEventV1) -> None:
        import json

        existing = self.client.get_object_bytes(
            bucket=self.bucket,
            key=self.key,
        ) or b""

        line = (
            json.dumps(
                event.to_dict(),
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            )
            + "\n"
        ).encode("utf-8")

        self.client.put_object_bytes(
            bucket=self.bucket,
            key=self.key,
            body=existing + line,
            content_type="application/x-ndjson",
        )
