from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, replace
from pathlib import Path

from oracle.audit import canonical_json, sha256_hex
from oracle.reinforcement import ReinforcementCondition, ReinforcementResult


class D6PersistenceError(ValueError):
    pass


@dataclass(frozen=True)
class D6SelectionRecord:
    schema_version: str
    experiment_id: str
    session_id: str
    timestamp: str
    selector_version: str
    seed: int
    selected_index: int
    condition: ReinforcementCondition
    applicable: bool
    status: str
    eligible_conditions: tuple[ReinforcementCondition, ...]
    previous_record_hash: str | None
    record_hash: str


def _record_payload(record: D6SelectionRecord) -> dict:
    payload = asdict(record)
    payload.pop("record_hash")
    return payload


def compute_record_hash(record: D6SelectionRecord) -> str:
    return sha256_hex(_record_payload(record))


def build_selection_record(
    *,
    experiment_id: str,
    session_id: str,
    timestamp: str,
    result: ReinforcementResult,
    previous_record_hash: str | None,
) -> D6SelectionRecord:
    selection = result.selection

    record = D6SelectionRecord(
        schema_version="d6-selection/v1",
        experiment_id=experiment_id,
        session_id=session_id,
        timestamp=timestamp,
        selector_version=selection.selector_version,
        seed=selection.seed,
        selected_index=selection.selected_index,
        condition=selection.condition,
        applicable=result.applicable,
        status=result.status,
        eligible_conditions=selection.eligible_conditions,
        previous_record_hash=previous_record_hash,
        record_hash="",
    )

    return replace(
        record,
        record_hash=compute_record_hash(record),
    )


def verify_record(record: D6SelectionRecord) -> None:
    expected = compute_record_hash(record)

    if record.record_hash != expected:
        raise D6PersistenceError(
            "D6 selection record hash mismatch"
        )


def append_record(
    path: Path,
    record: D6SelectionRecord,
) -> None:
    verify_record(record)

    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("a", encoding="utf-8") as handle:
        handle.write(canonical_json(record) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def load_records(path: Path) -> tuple[D6SelectionRecord, ...]:
    if not path.exists():
        return ()

    records: list[D6SelectionRecord] = []
    previous_hash: str | None = None

    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()

            if not line:
                raise D6PersistenceError(
                    f"blank D6 record at line {line_number}"
                )

            try:
                payload = json.loads(line)

                payload["condition"] = ReinforcementCondition(
                    payload["condition"]
                )

                payload["eligible_conditions"] = tuple(
                    ReinforcementCondition(item)
                    for item in payload["eligible_conditions"]
                )

                record = D6SelectionRecord(**payload)

            except Exception as exc:
                raise D6PersistenceError(
                    f"invalid D6 record at line {line_number}"
                ) from exc

            verify_record(record)

            if record.previous_record_hash != previous_hash:
                raise D6PersistenceError(
                    f"D6 chain mismatch at line {line_number}"
                )

            records.append(record)
            previous_hash = record.record_hash

    return tuple(records)
