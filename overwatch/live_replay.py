from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .events import TelemetryEventV1
from .storage import TelemetryStorage
from .replay import ReplayDivergenceV1


@dataclass(frozen=True)
class StreamCursorV1:
    run_id: str
    sequence: int
    mode: str  # live | replay
    frame_index: int | None = None

    def __post_init__(self) -> None:
        if self.sequence < 0:
            raise ValueError("sequence must be non-negative")
        if self.mode not in {"live", "replay"}:
            raise ValueError("mode must be live or replay")
        if self.frame_index is not None and self.frame_index < 0:
            raise ValueError("frame_index must be non-negative")

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "sequence": self.sequence,
            "mode": self.mode,
            "frame_index": self.frame_index,
        }


def handoff_cursor(
    cursor: StreamCursorV1,
    *,
    to_mode: str,
) -> StreamCursorV1:
    if to_mode not in {"live", "replay"}:
        raise ValueError("to_mode must be live or replay")

    return StreamCursorV1(
        run_id=cursor.run_id,
        sequence=cursor.sequence,
        mode=to_mode,
        frame_index=cursor.frame_index,
    )


def emit_stream_handoff(
    storage: TelemetryStorage,
    *,
    run_id: str,
    from_cursor: StreamCursorV1,
    to_cursor: StreamCursorV1,
    reason: str,
    subject_id: str | None = "MQ-001",
) -> TelemetryEventV1:
    if from_cursor.run_id != to_cursor.run_id:
        raise ValueError("cursor handoff cannot change run_id")
    if from_cursor.sequence != to_cursor.sequence:
        raise ValueError("cursor handoff cannot silently change sequence")

    event = TelemetryEventV1(
        event_type="stream.handoff",
        run_id=run_id,
        component="stream",
        subject_id=subject_id,
        payload={
            "from": from_cursor.to_dict(),
            "to": to_cursor.to_dict(),
            "reason": reason,
            "boundary": (
                "handoff changes viewer mode, not scientific state or authoritative ordering"
            ),
        },
        lore_surface="HUD",
    )
    storage.append(event)
    return event


def emit_replay_divergence(
    storage: TelemetryStorage,
    *,
    run_id: str,
    divergence: ReplayDivergenceV1,
    source_frame_index: int | None = None,
    subject_id: str | None = "MQ-001",
) -> TelemetryEventV1:
    event = TelemetryEventV1(
        event_type="replay.divergence",
        run_id=run_id,
        component="replay",
        subject_id=subject_id,
        payload={
            "sample_index": divergence.sample_index,
            "expected_hash": divergence.expected_hash,
            "actual_hash": divergence.actual_hash,
            "kind": divergence.kind,
            "detail": divergence.detail,
            "source_frame_index": source_frame_index,
            "handling": "report_only_no_silent_repair",
        },
        lore_surface="KILLFEED",
    )
    storage.append(event)
    return event


def emit_stream_gap(
    storage: TelemetryStorage,
    *,
    run_id: str,
    expected_sequence: int,
    actual_sequence: int,
    subject_id: str | None = "MQ-001",
) -> TelemetryEventV1:
    if expected_sequence < 0 or actual_sequence < 0:
        raise ValueError("sequence values must be non-negative")

    event = TelemetryEventV1(
        event_type="stream.gap",
        run_id=run_id,
        component="stream",
        subject_id=subject_id,
        payload={
            "expected_sequence": expected_sequence,
            "actual_sequence": actual_sequence,
            "missing_count": max(0, actual_sequence - expected_sequence),
            "handling": "report_and_stop_frame_assembly",
        },
        lore_surface="KILLFEED",
    )
    storage.append(event)
    return event
