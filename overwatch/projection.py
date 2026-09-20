from __future__ import annotations

from typing import Any

from .events import TelemetryEventV1

_PUBLIC_TOP_LEVEL = {
    "schema_version",
    "event_id",
    "timestamp_utc",
    "event_type",
    "run_id",
    "component",
    "experiment_id",
    "subject_id",
    "git_commit",
    "config_hash",
    "dataset_hash",
    "artifact_ref",
    "lore_surface",
}

_PRIVATE_PAYLOAD_KEYS = {
    "hostname",
    "private_ip",
    "public_ip",
    "username",
    "home_dir",
    "working_dir",
    "aws_account_id",
    "bucket",
    "bucket_name",
    "iam_role",
    "endpoint",
    "broker_account_id",
    "broker_endpoint",
    "token",
    "secret",
    "password",
    "credential",
}

def _sanitize_payload(value: Any) -> Any:
    if isinstance(value, dict):
        out = {}
        for key, item in value.items():
            if str(key).lower() in _PRIVATE_PAYLOAD_KEYS:
                continue
            out[key] = _sanitize_payload(item)
        return out
    if isinstance(value, list):
        return [_sanitize_payload(item) for item in value]
    return value

def public_projection(event: TelemetryEventV1) -> dict[str, Any]:
    raw = event.to_dict()
    projected = {
        key: raw[key]
        for key in _PUBLIC_TOP_LEVEL
        if key in raw and raw[key] is not None
    }
    projected["payload"] = _sanitize_payload(raw.get("payload", {}))
    return projected
