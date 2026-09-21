from overwatch.storage import LocalJsonlStorage
from overwatch.transport import (
    BoundedTransportQueueV1,
    emit_transport_backpressure,
    emit_transport_batch,
)


def test_bounded_queue_preserves_fifo_order():
    queue = BoundedTransportQueueV1[int](capacity=3)

    assert queue.put(10) is True
    assert queue.put(11) is True
    assert queue.put(12) is True

    assert queue.drain(2) == (10, 11)
    assert queue.drain(2) == (12,)


def test_bounded_queue_rejects_when_full_without_dropping_existing_items():
    queue = BoundedTransportQueueV1[int](capacity=2)

    assert queue.put(1) is True
    assert queue.put(2) is True
    assert queue.put(3) is False

    assert queue.drain(10) == (1, 2)

    stats = queue.stats()
    assert stats.accepted == 2
    assert stats.rejected == 1


def test_put_many_stops_at_first_backpressure():
    queue = BoundedTransportQueueV1[int](capacity=2)

    accepted = queue.put_many((1, 2, 3, 4))

    assert accepted == 2
    assert queue.drain(10) == (1, 2)


def test_transport_backpressure_is_killfeed_event(tmp_path):
    event = emit_transport_backpressure(
        LocalJsonlStorage(tmp_path / "transport.jsonl"),
        run_id="run-1",
        queue_name="panopticon-public",
        capacity=128,
        queued=128,
        rejected_total=1,
    )

    assert event.event_type == "transport.backpressure"
    assert event.lore_surface == "KILLFEED"
    assert event.payload["handling"] == (
        "caller_must_retry_or_stop_no_silent_drop"
    )


def test_transport_batch_records_sequence_bounds(tmp_path):
    event = emit_transport_batch(
        LocalJsonlStorage(tmp_path / "transport.jsonl"),
        run_id="run-2",
        queue_name="panopticon-public",
        batch_size=32,
        first_sequence=100,
        last_sequence=131,
    )

    assert event.event_type == "transport.batch"
    assert event.payload["batch_size"] == 32
    assert event.payload["first_sequence"] == 100
    assert event.payload["last_sequence"] == 131
