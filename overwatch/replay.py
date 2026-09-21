from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence

from .events import TelemetryEventV1


REPLAY_SCHEMA = "overwatch.replay.v1"


def _canonicalize(value: Any, *, float_digits: int = 12) -> Any:
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite floats are not replay-hashable")
        return round(value, float_digits)
    if isinstance(value, dict):
        return {
            str(k): _canonicalize(v, float_digits=float_digits)
            for k, v in sorted(value.items(), key=lambda item: str(item[0]))
        }
    if isinstance(value, (list, tuple)):
        return [
            _canonicalize(v, float_digits=float_digits)
            for v in value
        ]
    return value


def canonical_json_bytes(
    value: Any,
    *,
    float_digits: int = 12,
) -> bytes:
    canonical = _canonicalize(value, float_digits=float_digits)
    return json.dumps(
        canonical,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def payload_sha256(
    payload: Mapping[str, Any],
    *,
    float_digits: int = 12,
) -> str:
    return hashlib.sha256(
        canonical_json_bytes(payload, float_digits=float_digits)
    ).hexdigest()


def event_state_payload(event: TelemetryEventV1) -> dict[str, Any]:
    """Return replay-relevant event content without volatile identity fields."""
    return {
        "schema_version": event.schema_version,
        "event_type": event.event_type,
        "run_id": event.run_id,
        "component": event.component,
        "experiment_id": event.experiment_id,
        "subject_id": event.subject_id,
        "git_commit": event.git_commit,
        "config_hash": event.config_hash,
        "dataset_hash": event.dataset_hash,
        "artifact_ref": event.artifact_ref,
        "lore_surface": event.lore_surface,
        "payload": event.payload,
    }


def event_state_sha256(
    event: TelemetryEventV1,
    *,
    float_digits: int = 12,
) -> str:
    return hashlib.sha256(
        canonical_json_bytes(
            event_state_payload(event),
            float_digits=float_digits,
        )
    ).hexdigest()


@dataclass(frozen=True)
class ReplayFrameV1:
    run_id: str
    sample_index: int
    event_type: str
    event_state_sha256: str
    source_event_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": REPLAY_SCHEMA,
            "run_id": self.run_id,
            "sample_index": self.sample_index,
            "event_type": self.event_type,
            "event_state_sha256": self.event_state_sha256,
            "source_event_id": self.source_event_id,
        }


@dataclass(frozen=True)
class ReplayDivergenceV1:
    sample_index: int
    expected_hash: str | None
    actual_hash: str | None
    kind: str
    detail: str


@dataclass(frozen=True)
class ReplayVerificationV1:
    ok: bool
    compared_frames: int
    divergences: tuple[ReplayDivergenceV1, ...]


def replay_frame_from_event(
    event: TelemetryEventV1,
    *,
    sample_index: int,
    float_digits: int = 12,
) -> ReplayFrameV1:
    return ReplayFrameV1(
        run_id=event.run_id,
        sample_index=sample_index,
        event_type=event.event_type,
        event_state_sha256=event_state_sha256(
            event,
            float_digits=float_digits,
        ),
        source_event_id=event.event_id,
    )


def build_replay_frames(
    events: Sequence[TelemetryEventV1],
    *,
    start_index: int = 0,
    float_digits: int = 12,
) -> tuple[ReplayFrameV1, ...]:
    return tuple(
        replay_frame_from_event(
            event,
            sample_index=start_index + i,
            float_digits=float_digits,
        )
        for i, event in enumerate(events)
    )


def verify_replay_frames(
    expected: Sequence[ReplayFrameV1],
    actual: Sequence[ReplayFrameV1],
) -> ReplayVerificationV1:
    divergences: list[ReplayDivergenceV1] = []
    max_len = max(len(expected), len(actual))

    for i in range(max_len):
        exp = expected[i] if i < len(expected) else None
        act = actual[i] if i < len(actual) else None

        if exp is None:
            divergences.append(
                ReplayDivergenceV1(
                    sample_index=act.sample_index,
                    expected_hash=None,
                    actual_hash=act.event_state_sha256,
                    kind="unexpected_frame",
                    detail="actual replay contains an extra frame",
                )
            )
            continue

        if act is None:
            divergences.append(
                ReplayDivergenceV1(
                    sample_index=exp.sample_index,
                    expected_hash=exp.event_state_sha256,
                    actual_hash=None,
                    kind="missing_frame",
                    detail="actual replay is missing an expected frame",
                )
            )
            continue

        if exp.sample_index != act.sample_index:
            divergences.append(
                ReplayDivergenceV1(
                    sample_index=exp.sample_index,
                    expected_hash=exp.event_state_sha256,
                    actual_hash=act.event_state_sha256,
                    kind="sample_index",
                    detail=(
                        f"expected sample_index={exp.sample_index}, "
                        f"actual={act.sample_index}"
                    ),
                )
            )

        if exp.event_type != act.event_type:
            divergences.append(
                ReplayDivergenceV1(
                    sample_index=exp.sample_index,
                    expected_hash=exp.event_state_sha256,
                    actual_hash=act.event_state_sha256,
                    kind="event_type",
                    detail=(
                        f"expected event_type={exp.event_type}, "
                        f"actual={act.event_type}"
                    ),
                )
            )

        if exp.event_state_sha256 != act.event_state_sha256:
            divergences.append(
                ReplayDivergenceV1(
                    sample_index=exp.sample_index,
                    expected_hash=exp.event_state_sha256,
                    actual_hash=act.event_state_sha256,
                    kind="state_hash",
                    detail="replayed event state differs from recorded state",
                )
            )

    return ReplayVerificationV1(
        ok=not divergences,
        compared_frames=max_len,
        divergences=tuple(divergences),
    )
