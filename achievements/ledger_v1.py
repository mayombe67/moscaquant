from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from .models import AchievementOccurrence, Origin
from .store import OccurrenceStore


def occurrence_from_dict(payload: dict) -> AchievementOccurrence:
    return AchievementOccurrence(
        occurrence_id=payload["occurrence_id"],
        achievement_id=payload["achievement_id"],
        achievement_version=payload["achievement_version"],
        trigger_version=payload["trigger_version"],
        subject_id=payload["subject_id"],
        occurred_at=payload["occurred_at"],
        source_event_id=payload["source_event_id"],
        source_event_type=payload["source_event_type"],
        origin=Origin(payload["origin"]),
        stack_index=int(payload["stack_index"]),
        evidence=dict(payload.get("evidence", {})),
        artifact_refs=tuple(payload.get("artifact_refs", [])),
        experiment_id=payload.get("experiment_id"),
        session_id=payload.get("session_id"),
        generation=payload.get("generation"),
        runtime_profile=payload.get("runtime_profile"),
        experiment_seed=payload.get("experiment_seed"),
        state_hash=payload.get("state_hash", ""),
        previous_occurrence_hash=payload.get("previous_occurrence_hash", ""),
    )


def load_occurrence_jsonl(path: Path) -> OccurrenceStore:
    store = OccurrenceStore()
    if not path.exists():
        return store

    for lineno, line in enumerate(path.read_text().splitlines(), 1):
        if not line.strip():
            continue
        payload = json.loads(line)
        try:
            store.append(occurrence_from_dict(payload))
        except Exception as exc:
            raise ValueError(f"{path}:{lineno}: {exc}") from exc

    return store
