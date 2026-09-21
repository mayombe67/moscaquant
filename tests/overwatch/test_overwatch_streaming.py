import pytest

from overwatch.events import TelemetryEventV1
from overwatch.streaming import (
    StreamSampleV1,
    build_render_frame,
    deterministic_downsample,
    validate_authoritative_order,
    verify_frame_source_hashes,
)


def _sample(sequence, payload, event_type="motor.state"):
    return StreamSampleV1(
        sequence=sequence,
        event=TelemetryEventV1(
            event_type=event_type,
            run_id="run-1",
            component="test",
            subject_id="MQ-001",
            payload=payload,
        ),
    )


def test_authoritative_sequence_must_be_contiguous():
    with pytest.raises(ValueError):
        validate_authoritative_order(
            (
                _sample(10, {"n": 1}),
                _sample(12, {"n": 2}),
            )
        )


def test_render_frame_links_back_to_source_events():
    samples = (
        _sample(20, {"n": 1}),
        _sample(21, {"n": 2}),
    )

    frame = build_render_frame(samples, frame_index=3)

    assert frame.frame_index == 3
    assert frame.source_sequence_start == 20
    assert frame.source_sequence_end == 21
    assert len(frame.source_event_ids) == 2
    assert len(frame.source_state_hashes) == 2
    assert len(frame.public_events) == 2
    assert len(frame.frame_sha256) == 64


def test_downsampling_is_deterministic_by_fixed_chunk_size():
    samples = tuple(
        _sample(i, {"n": i})
        for i in range(7)
    )

    frames = deterministic_downsample(
        samples,
        max_events_per_frame=3,
    )

    assert len(frames) == 3
    assert [
        (f.source_sequence_start, f.source_sequence_end)
        for f in frames
    ] == [(0, 2), (3, 5), (6, 6)]


def test_same_samples_produce_same_frame_hash():
    samples = (
        _sample(1, {"x": 1.0}),
        _sample(2, {"x": 2.0}),
    )

    first = build_render_frame(samples, frame_index=0)
    second = build_render_frame(samples, frame_index=0)

    assert first.frame_sha256 == second.frame_sha256


def test_frame_source_hashes_verify_against_authoritative_samples():
    samples = (
        _sample(100, {"root_y": 0.01}, "physics.pose"),
        _sample(101, {"root_y": 0.02}, "physics.pose"),
    )

    frame = build_render_frame(samples, frame_index=8)

    assert verify_frame_source_hashes(frame, samples) is True


def test_frame_source_verification_detects_mutated_state():
    source = (
        _sample(200, {"root_y": 0.01}, "physics.pose"),
    )
    frame = build_render_frame(source, frame_index=9)

    mutated = (
        _sample(200, {"root_y": 0.02}, "physics.pose"),
    )

    assert verify_frame_source_hashes(frame, mutated) is False
