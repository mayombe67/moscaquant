from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any, Mapping

from .streaming import RENDER_FRAME_SCHEMA


class PublicFeedError(ValueError):
    pass


def validate_public_render_frame(frame: Mapping[str, Any]) -> None:
    if frame.get("schema") != RENDER_FRAME_SCHEMA:
        raise PublicFeedError(
            f"expected schema {RENDER_FRAME_SCHEMA!r}"
        )

    required = (
        "frame_index",
        "source_sequence_start",
        "source_sequence_end",
        "source_event_ids",
        "source_state_hashes",
        "public_events",
        "frame_sha256",
    )
    missing = [key for key in required if key not in frame]
    if missing:
        raise PublicFeedError(
            "render frame missing required fields: " + ", ".join(missing)
        )

    if not isinstance(frame["public_events"], list):
        raise PublicFeedError("public_events must be a list")

    if len(frame["source_event_ids"]) != len(frame["source_state_hashes"]):
        raise PublicFeedError(
            "source_event_ids and source_state_hashes must have equal length"
        )


def write_latest_render_frame(
    frame: Mapping[str, Any],
    destination: str | Path,
) -> Path:
    """Atomically publish one sanitized Panopticon render frame.

    The caller is responsible for supplying a frame produced by the public
    projection/render-frame path. This function never accepts raw telemetry.
    """
    validate_public_render_frame(frame)

    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)

    payload = json.dumps(
        dict(frame),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ) + "\n"

    fd, temp_name = tempfile.mkstemp(
        prefix=destination.name + ".",
        suffix=".tmp",
        dir=destination.parent,
        text=True,
    )

    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())

        os.replace(temp_name, destination)
        os.chmod(destination, 0o640)
    except Exception:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise

    return destination
