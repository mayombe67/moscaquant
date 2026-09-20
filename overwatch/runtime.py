from __future__ import annotations

from pathlib import Path
from typing import Any

from .collectors import runtime_snapshot
from .events import TelemetryEventV1
from .writer import JsonlTelemetryWriter


def emit_runtime_snapshot(
    writer: JsonlTelemetryWriter,
    *,
    run_id: str,
    component: str = "runtime",
    experiment_id: str | None = None,
    subject_id: str | None = None,
    git_commit: str | None = None,
    config_hash: str | None = None,
    dataset_hash: str | None = None,
    disk_path: str | Path = ".",
    extra_payload: dict[str, Any] | None = None,
) -> TelemetryEventV1:
    """Collect and emit a best-effort runtime snapshot.

    This function observes and records only. It does not alter experiment state.
    """
    payload = runtime_snapshot(disk_path=disk_path)
    if extra_payload:
        payload["context"] = dict(extra_payload)

    event = TelemetryEventV1(
        event_type="runtime.snapshot",
        run_id=run_id,
        component=component,
        experiment_id=experiment_id,
        subject_id=subject_id,
        git_commit=git_commit,
        config_hash=config_hash,
        dataset_hash=dataset_hash,
        payload=payload,
        lore_surface="HUD",
    )
    writer.emit(event)
    return event


def emit_progress(
    writer: JsonlTelemetryWriter,
    *,
    run_id: str,
    completed_units: int,
    total_units: int | None = None,
    units_per_second: float | None = None,
    experiment_id: str | None = None,
) -> TelemetryEventV1:
    payload: dict[str, Any] = {
        "completed_units": completed_units,
        "total_units": total_units,
        "units_per_second": units_per_second,
    }

    event = TelemetryEventV1(
        event_type="run.progress",
        run_id=run_id,
        component="runtime",
        experiment_id=experiment_id,
        payload=payload,
        lore_surface="PAYLOAD",
    )
    writer.emit(event)
    return event


def emit_checkpoint(
    writer: JsonlTelemetryWriter,
    *,
    run_id: str,
    checkpoint_ref: str,
    duration_seconds: float | None = None,
    experiment_id: str | None = None,
) -> TelemetryEventV1:
    event = TelemetryEventV1(
        event_type="checkpoint.saved",
        run_id=run_id,
        component="runtime",
        experiment_id=experiment_id,
        artifact_ref=checkpoint_ref,
        payload={"duration_seconds": duration_seconds},
        lore_surface="RESPAWN POINT",
    )
    writer.emit(event)
    return event


def emit_worker_failure(
    writer: JsonlTelemetryWriter,
    *,
    run_id: str,
    reason: str,
    worker_id: str | None = None,
    experiment_id: str | None = None,
) -> TelemetryEventV1:
    event = TelemetryEventV1(
        event_type="worker.failed",
        run_id=run_id,
        component="runtime",
        experiment_id=experiment_id,
        payload={
            "reason": reason,
            "worker_id": worker_id,
        },
        lore_surface="KILLFEED",
    )
    writer.emit(event)
    return event


def emit_worker_recovered(
    writer: JsonlTelemetryWriter,
    *,
    run_id: str,
    worker_id: str | None = None,
    recovery_ref: str | None = None,
    experiment_id: str | None = None,
) -> TelemetryEventV1:
    event = TelemetryEventV1(
        event_type="worker.recovered",
        run_id=run_id,
        component="runtime",
        experiment_id=experiment_id,
        artifact_ref=recovery_ref,
        payload={"worker_id": worker_id},
        lore_surface="RESPAWN",
    )
    writer.emit(event)
    return event
