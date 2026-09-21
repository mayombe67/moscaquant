from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Deque, Generic, Iterable, TypeVar

from .events import TelemetryEventV1
from .storage import TelemetryStorage


T = TypeVar("T")


@dataclass(frozen=True)
class TransportStatsV1:
    capacity: int
    queued: int
    accepted: int
    rejected: int
    batches_emitted: int

    def to_dict(self) -> dict[str, int]:
        return {
            "capacity": self.capacity,
            "queued": self.queued,
            "accepted": self.accepted,
            "rejected": self.rejected,
            "batches_emitted": self.batches_emitted,
        }


class BoundedTransportQueueV1(Generic[T]):
    """Deterministic bounded FIFO queue.

    Version 1 never silently drops queued items. When full, `put` returns False
    and the caller must surface backpressure explicitly.
    """

    def __init__(self, capacity: int) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self.capacity = int(capacity)
        self._queue: Deque[T] = deque()
        self._accepted = 0
        self._rejected = 0
        self._batches_emitted = 0

    def __len__(self) -> int:
        return len(self._queue)

    def put(self, item: T) -> bool:
        if len(self._queue) >= self.capacity:
            self._rejected += 1
            return False

        self._queue.append(item)
        self._accepted += 1
        return True

    def put_many(self, items: Iterable[T]) -> int:
        accepted = 0
        for item in items:
            if not self.put(item):
                break
            accepted += 1
        return accepted

    def drain(self, max_items: int) -> tuple[T, ...]:
        if max_items <= 0:
            raise ValueError("max_items must be positive")

        items: list[T] = []
        while self._queue and len(items) < max_items:
            items.append(self._queue.popleft())

        if items:
            self._batches_emitted += 1

        return tuple(items)

    def stats(self) -> TransportStatsV1:
        return TransportStatsV1(
            capacity=self.capacity,
            queued=len(self._queue),
            accepted=self._accepted,
            rejected=self._rejected,
            batches_emitted=self._batches_emitted,
        )


def emit_transport_backpressure(
    storage: TelemetryStorage,
    *,
    run_id: str,
    queue_name: str,
    capacity: int,
    queued: int,
    rejected_total: int,
    subject_id: str | None = "MQ-001",
) -> TelemetryEventV1:
    event = TelemetryEventV1(
        event_type="transport.backpressure",
        run_id=run_id,
        component="transport",
        subject_id=subject_id,
        payload={
            "queue_name": queue_name,
            "capacity": int(capacity),
            "queued": int(queued),
            "rejected_total": int(rejected_total),
            "handling": "caller_must_retry_or_stop_no_silent_drop",
        },
        lore_surface="KILLFEED",
    )
    storage.append(event)
    return event


def emit_transport_batch(
    storage: TelemetryStorage,
    *,
    run_id: str,
    queue_name: str,
    batch_size: int,
    first_sequence: int | None,
    last_sequence: int | None,
    subject_id: str | None = "MQ-001",
) -> TelemetryEventV1:
    if batch_size < 0:
        raise ValueError("batch_size must be non-negative")
    if batch_size == 0 and (
        first_sequence is not None or last_sequence is not None
    ):
        raise ValueError(
            "empty batch cannot have sequence boundaries"
        )
    if batch_size > 0 and (
        first_sequence is None or last_sequence is None
    ):
        raise ValueError(
            "non-empty batch requires sequence boundaries"
        )

    event = TelemetryEventV1(
        event_type="transport.batch",
        run_id=run_id,
        component="transport",
        subject_id=subject_id,
        payload={
            "queue_name": queue_name,
            "batch_size": int(batch_size),
            "first_sequence": first_sequence,
            "last_sequence": last_sequence,
        },
        lore_surface="HUD",
    )
    storage.append(event)
    return event
