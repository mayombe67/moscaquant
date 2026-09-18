"""MQ-8.5B HR registry validation."""

from __future__ import annotations

from .models import HRRecord


def validate_record(record: HRRecord) -> None:
    record.validate()


def validate_registry(records: list[HRRecord]) -> None:
    seen = set()

    for record in records:
        validate_record(record)

        if record.record_id in seen:
            raise ValueError(f"duplicate HR record_id: {record.record_id}")

        seen.add(record.record_id)
