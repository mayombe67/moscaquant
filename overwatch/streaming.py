from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any, Iterable, Sequence

from .events import TelemetryEventV1
from .projection import public_projection
from .replay import canonical_json_bytes, event_state_sha256


STREAM_SCHEMA = "overwatch.stream.v1"
RENDER_FRAME_SCHEMA = "overwatch.render-frame.v1"


@dataclass(frozen=True)
class StreamSampleV1:
    sequence: int
    event: TelemetryEventV1

    def __post_init__(self) -> None:
        if self.sequence < 0:
            raise ValueError("sequence must be non-negative")


@dataclass(frozen=True)
class RenderFrameV1:
    frame_index: int
    source_sequence_start: int
    source_sequence_end: int
    source_event_ids: tuple[str, ...]
    source_state_hashes: tuple[str, ...]
    public_events: tuple[dict[str, Any], ...]
    frame_sha256: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": RENDER_FRAME_SCHEMA,
            "frame_index": self.frame_index,
            "source_sequence_start": self.source_sequence_start,
            "source_sequence_end": self.source_sequence_end,
            "source_event_ids": list(self.source_event_ids),
            "source_state_hashes": list(self.source_state_hashes),
            "public_events": list(self.public_events),
            "frame_sha256": self.frame_sha256,
        }


def validate_authoritative_order(samples: Sequence[StreamSampleV1]) -> None:
    if not samples:
        return

    expected = samples[0].sequence
    for sample in samples:
        if sample.sequence != expected:
            raise ValueError(
                f"non-contiguous authoritative sequence: "
                f"expected {expected}, got {sample.sequence}"
            )
        expected += 1


def _frame_hash(payload: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json_bytes(payload)).hexdigest()


def build_render_frame(
    samples: Sequence[StreamSampleV1],
    *,
    frame_index: int,
) -> RenderFrameV1:
    if not samples:
        raise ValueError("render frame requires at least one sample")
    if frame_index < 0:
        raise ValueError("frame_index must be non-negative")

    validate_authoritative_order(samples)

    event_ids = tuple(sample.event.event_id for sample in samples)
    state_hashes = tuple(event_state_sha256(sample.event) for sample in samples)
    projected = tuple(public_projection(sample.event) for sample in samples)

    body = {
        "schema": RENDER_FRAME_SCHEMA,
        "frame_index": frame_index,
        "source_sequence_start": samples[0].sequence,
        "source_sequence_end": samples[-1].sequence,
        "source_event_ids": list(event_ids),
        "source_state_hashes": list(state_hashes),
        "public_events": list(projected),
    }

    return RenderFrameV1(
        frame_index=frame_index,
        source_sequence_start=samples[0].sequence,
        source_sequence_end=samples[-1].sequence,
        source_event_ids=event_ids,
        source_state_hashes=state_hashes,
        public_events=projected,
        frame_sha256=_frame_hash(body),
    )


def deterministic_downsample(
    samples: Sequence[StreamSampleV1],
    *,
    max_events_per_frame: int,
) -> tuple[RenderFrameV1, ...]:
    if max_events_per_frame <= 0:
        raise ValueError("max_events_per_frame must be positive")

    validate_authoritative_order(samples)

    frames: list[RenderFrameV1] = []
    for frame_index, start in enumerate(
        range(0, len(samples), max_events_per_frame)
    ):
        chunk = samples[start:start + max_events_per_frame]
        frames.append(
            build_render_frame(
                chunk,
                frame_index=frame_index,
            )
        )
    return tuple(frames)


def verify_frame_source_hashes(
    frame: RenderFrameV1,
    samples: Sequence[StreamSampleV1],
) -> bool:
    if not samples:
        return False
    validate_authoritative_order(samples)

    if samples[0].sequence != frame.source_sequence_start:
        return False
    if samples[-1].sequence != frame.source_sequence_end:
        return False

    actual_ids = tuple(sample.event.event_id for sample in samples)
    actual_hashes = tuple(event_state_sha256(sample.event) for sample in samples)

    return (
        actual_ids == frame.source_event_ids
        and actual_hashes == frame.source_state_hashes
    )
