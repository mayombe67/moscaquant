from __future__ import annotations
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

SCHEMA_VERSION = "overwatch.telemetry.v1"

@dataclass(frozen=True)
class TelemetryEventV1:
    event_type: str
    run_id: str
    component: str
    payload: dict[str, Any] = field(default_factory=dict)
    event_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    schema_version: str = SCHEMA_VERSION
    experiment_id: str | None = None
    subject_id: str | None = None
    git_commit: str | None = None
    config_hash: str | None = None
    dataset_hash: str | None = None
    artifact_ref: str | None = None
    lore_surface: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
