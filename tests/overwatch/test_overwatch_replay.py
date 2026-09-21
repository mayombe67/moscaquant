from overwatch.events import TelemetryEventV1
from overwatch.replay import (
    build_replay_frames,
    canonical_json_bytes,
    event_state_sha256,
    payload_sha256,
    replay_frame_from_event,
    verify_replay_frames,
)


def _event(payload, *, event_type="motor.state"):
    return TelemetryEventV1(
        event_type=event_type,
        run_id="run-1",
        component="test",
        payload=payload,
        subject_id="MQ-001",
    )


def test_canonical_json_ignores_mapping_insertion_order():
    left = {"b": 2, "a": 1}
    right = {"a": 1, "b": 2}

    assert canonical_json_bytes(left) == canonical_json_bytes(right)
    assert payload_sha256(left) == payload_sha256(right)


def test_canonical_json_rounds_float_noise():
    left = {"x": 0.12345678901234}
    right = {"x": 0.12345678901235}

    assert payload_sha256(left, float_digits=12) == payload_sha256(
        right,
        float_digits=12,
    )


def test_event_state_hash_excludes_event_uuid_and_timestamp():
    first = _event({"x": 1.0})
    second = _event({"x": 1.0})

    assert first.event_id != second.event_id
    assert event_state_sha256(first) == event_state_sha256(second)


def test_replay_frame_uses_stable_event_state_hash():
    event = _event({"pose": {"x": 1.0}})

    frame = replay_frame_from_event(event, sample_index=42)

    assert frame.sample_index == 42
    assert frame.event_type == "motor.state"
    assert frame.event_state_sha256 == event_state_sha256(event)
    assert frame.source_event_id == event.event_id


def test_build_replay_frames_preserves_order():
    events = (
        _event({"n": 1}, event_type="motor.state"),
        _event({"n": 2}, event_type="constraint.state"),
        _event({"n": 3}, event_type="physics.pose"),
    )

    frames = build_replay_frames(events, start_index=10)

    assert [f.sample_index for f in frames] == [10, 11, 12]
    assert [f.event_type for f in frames] == [
        "motor.state",
        "constraint.state",
        "physics.pose",
    ]


def test_verify_replay_frames_accepts_identical_state():
    events = (
        _event({"n": 1}),
        _event({"n": 2}),
    )

    expected = build_replay_frames(events)
    actual = build_replay_frames(events)

    report = verify_replay_frames(expected, actual)

    assert report.ok is True
    assert report.divergences == ()


def test_verify_replay_frames_detects_state_divergence():
    expected = build_replay_frames(
        (_event({"root_y": 0.03}, event_type="physics.pose"),)
    )
    actual = build_replay_frames(
        (_event({"root_y": 0.04}, event_type="physics.pose"),)
    )

    report = verify_replay_frames(expected, actual)

    assert report.ok is False
    assert report.divergences[0].kind == "state_hash"


def test_verify_replay_frames_detects_missing_frame():
    expected = build_replay_frames(
        (
            _event({"n": 1}),
            _event({"n": 2}),
        )
    )
    actual = build_replay_frames((_event({"n": 1}),))

    report = verify_replay_frames(expected, actual)

    assert report.ok is False
    assert any(d.kind == "missing_frame" for d in report.divergences)
