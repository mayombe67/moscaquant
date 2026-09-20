from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from .segmented_storage import MANIFEST_SCHEMA
from .storage import ObjectStorageClient


@dataclass(frozen=True)
class IntegrityIssue:
    kind: str
    key: str | None
    detail: str

    def to_dict(self) -> dict[str, str | None]:
        return {
            "kind": self.kind,
            "key": self.key,
            "detail": self.detail,
        }


@dataclass(frozen=True)
class IntegrityReport:
    ok: bool
    manifest_present: bool
    manifest_schema: str | None
    expected_segments: int
    verified_segments: int
    expected_events: int
    verified_events: int
    orphan_segments: tuple[str, ...]
    issues: tuple[IntegrityIssue, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "manifest_present": self.manifest_present,
            "manifest_schema": self.manifest_schema,
            "expected_segments": self.expected_segments,
            "verified_segments": self.verified_segments,
            "expected_events": self.expected_events,
            "verified_events": self.verified_events,
            "orphan_segments": list(self.orphan_segments),
            "issues": [issue.to_dict() for issue in self.issues],
        }


class ObjectLister:
    """Optional listing capability used for orphan detection."""

    def list_object_keys(self, *, bucket: str, prefix: str) -> list[str]:
        raise NotImplementedError


def verify_segmented_receipts(
    *,
    client: ObjectStorageClient,
    bucket: str,
    prefix: str,
    lister: ObjectLister | None = None,
) -> IntegrityReport:
    prefix = prefix.rstrip("/")
    manifest_key = f"{prefix}/manifest.json"
    issues: list[IntegrityIssue] = []

    raw_manifest = client.get_object_bytes(bucket=bucket, key=manifest_key)
    if raw_manifest is None:
        return IntegrityReport(
            ok=False,
            manifest_present=False,
            manifest_schema=None,
            expected_segments=0,
            verified_segments=0,
            expected_events=0,
            verified_events=0,
            orphan_segments=tuple(
                _find_orphans(
                    lister=lister,
                    bucket=bucket,
                    prefix=prefix,
                    referenced=set(),
                )
            ),
            issues=(
                IntegrityIssue(
                    kind="manifest.missing",
                    key=manifest_key,
                    detail="manifest object is missing",
                ),
            ),
        )

    try:
        manifest = json.loads(raw_manifest.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        return IntegrityReport(
            ok=False,
            manifest_present=True,
            manifest_schema=None,
            expected_segments=0,
            verified_segments=0,
            expected_events=0,
            verified_events=0,
            orphan_segments=(),
            issues=(
                IntegrityIssue(
                    kind="manifest.invalid",
                    key=manifest_key,
                    detail=str(exc),
                ),
            ),
        )

    schema = manifest.get("schema_version")
    if schema != MANIFEST_SCHEMA:
        issues.append(
            IntegrityIssue(
                kind="manifest.schema",
                key=manifest_key,
                detail=f"expected {MANIFEST_SCHEMA!r}, found {schema!r}",
            )
        )

    segments = manifest.get("segments")
    if not isinstance(segments, list):
        segments = []
        issues.append(
            IntegrityIssue(
                kind="manifest.segments",
                key=manifest_key,
                detail="segments must be a list",
            )
        )

    expected_events = manifest.get("event_count")
    if not isinstance(expected_events, int):
        expected_events = 0
        issues.append(
            IntegrityIssue(
                kind="manifest.event_count",
                key=manifest_key,
                detail="event_count must be an integer",
            )
        )

    verified_segments = 0
    verified_events = 0
    referenced: set[str] = set()

    for record in segments:
        if not isinstance(record, dict):
            issues.append(
                IntegrityIssue(
                    kind="segment.record",
                    key=None,
                    detail="segment record must be an object",
                )
            )
            continue

        key = record.get("key")
        digest = record.get("sha256")
        byte_count = record.get("byte_count")
        event_count = record.get("event_count")

        if not isinstance(key, str):
            issues.append(
                IntegrityIssue(
                    kind="segment.key",
                    key=None,
                    detail="segment key must be a string",
                )
            )
            continue

        referenced.add(key)
        body = client.get_object_bytes(bucket=bucket, key=key)
        if body is None:
            issues.append(
                IntegrityIssue(
                    kind="segment.missing",
                    key=key,
                    detail="referenced segment object is missing",
                )
            )
            continue

        actual_digest = hashlib.sha256(body).hexdigest()
        if digest != actual_digest:
            issues.append(
                IntegrityIssue(
                    kind="segment.sha256",
                    key=key,
                    detail=f"expected {digest!r}, found {actual_digest!r}",
                )
            )
            continue

        if byte_count != len(body):
            issues.append(
                IntegrityIssue(
                    kind="segment.byte_count",
                    key=key,
                    detail=f"expected {byte_count!r}, found {len(body)!r}",
                )
            )
            continue

        try:
            lines = [line for line in body.decode("utf-8").splitlines() if line]
            for line in lines:
                json.loads(line)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            issues.append(
                IntegrityIssue(
                    kind="segment.ndjson",
                    key=key,
                    detail=str(exc),
                )
            )
            continue

        if event_count != len(lines):
            issues.append(
                IntegrityIssue(
                    kind="segment.event_count",
                    key=key,
                    detail=f"expected {event_count!r}, found {len(lines)!r}",
                )
            )
            continue

        verified_segments += 1
        verified_events += len(lines)

    if verified_events != expected_events:
        issues.append(
            IntegrityIssue(
                kind="manifest.event_total",
                key=manifest_key,
                detail=f"expected {expected_events}, verified {verified_events}",
            )
        )

    orphans = tuple(
        _find_orphans(
            lister=lister,
            bucket=bucket,
            prefix=prefix,
            referenced=referenced,
        )
    )
    for key in orphans:
        issues.append(
            IntegrityIssue(
                kind="segment.orphan",
                key=key,
                detail="segment exists but is not referenced by manifest",
            )
        )

    return IntegrityReport(
        ok=not issues,
        manifest_present=True,
        manifest_schema=schema if isinstance(schema, str) else None,
        expected_segments=len(segments),
        verified_segments=verified_segments,
        expected_events=expected_events,
        verified_events=verified_events,
        orphan_segments=orphans,
        issues=tuple(issues),
    )


def _find_orphans(
    *,
    lister: ObjectLister | None,
    bucket: str,
    prefix: str,
    referenced: set[str],
) -> list[str]:
    if lister is None:
        return []

    segment_prefix = f"{prefix}/segments/"
    keys = lister.list_object_keys(bucket=bucket, prefix=segment_prefix)
    return sorted(
        key
        for key in keys
        if key.startswith(segment_prefix) and key not in referenced
    )
