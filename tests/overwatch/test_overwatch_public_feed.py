import json

import pytest

from overwatch.public_feed import (
    PublicFeedError,
    validate_public_render_frame,
    write_latest_render_frame,
)


def _frame():
    return {
        "schema": "overwatch.render-frame.v1",
        "frame_index": 7,
        "source_sequence_start": 100,
        "source_sequence_end": 101,
        "source_event_ids": ["evt-1", "evt-2"],
        "source_state_hashes": ["a" * 64, "b" * 64],
        "public_events": [
            {
                "event_type": "motor.state",
                "payload": {"motor": {"locomotor_drive": 0.8}},
            }
        ],
        "frame_sha256": "c" * 64,
    }


def test_valid_public_render_frame_is_accepted():
    validate_public_render_frame(_frame())


def test_wrong_schema_is_rejected():
    frame = _frame()
    frame["schema"] = "private.raw.telemetry"

    with pytest.raises(PublicFeedError):
        validate_public_render_frame(frame)


def test_missing_required_field_is_rejected():
    frame = _frame()
    del frame["frame_sha256"]

    with pytest.raises(PublicFeedError):
        validate_public_render_frame(frame)


def test_mismatched_source_identity_lists_are_rejected():
    frame = _frame()
    frame["source_state_hashes"] = ["a" * 64]

    with pytest.raises(PublicFeedError):
        validate_public_render_frame(frame)


def test_latest_frame_is_written_atomically_as_json(tmp_path):
    destination = tmp_path / "latest-render-frame.json"

    result = write_latest_render_frame(_frame(), destination)

    assert result == destination
    loaded = json.loads(destination.read_text(encoding="utf-8"))
    assert loaded["frame_index"] == 7
    assert loaded["schema"] == "overwatch.render-frame.v1"
