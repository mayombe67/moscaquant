from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Iterable

from achievements.catalog_v1 import STATUS_BY_ID, V1_REGISTRY
from achievements.models import AchievementOccurrence, Origin


HISTORICAL_REPLAY_TIMESTAMP = "2026-09-18T00:00:00Z"


def _canonical_json(payload: dict) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def _state_hash(payload: dict) -> str:
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


def historical_replay_occurrences() -> tuple[AchievementOccurrence, ...]:
    """Materialize canonical replay occurrences from frozen eligible definitions.

    These are replay records, not claims about the original wall-clock time of
    the historical scientific event. The timestamp is the canonical replay
    materialization time used by the existing MQ-8 historical projection.
    """
    rows = []
    previous_hash = ""

    for achievement_id in sorted(V1_REGISTRY):
        if STATUS_BY_ID.get(achievement_id) != "HISTORICAL_REPLAY_ELIGIBLE":
            continue

        definition = V1_REGISTRY[achievement_id]
        source_event_id = f"historical-replay:{achievement_id}:v1"
        occurrence_id = f"{achievement_id}-HISTORICAL-REPLAY-001"

        hash_payload = {
            "occurrence_id": occurrence_id,
            "achievement_id": achievement_id,
            "achievement_version": definition.version,
            "trigger_version": definition.trigger_version,
            "subject_id": "MQ-001",
            "occurred_at": HISTORICAL_REPLAY_TIMESTAMP,
            "source_event_id": source_event_id,
            "source_event_type": "HISTORICAL_EVIDENCE_REPLAY",
            "origin": Origin.HISTORICAL_REPLAY.value,
            "stack_index": 1,
            "artifact_refs": list(definition.evidence_refs),
            "previous_occurrence_hash": previous_hash,
        }
        current_hash = _state_hash(hash_payload)

        row = AchievementOccurrence(
            occurrence_id=occurrence_id,
            achievement_id=achievement_id,
            achievement_version=definition.version,
            trigger_version=definition.trigger_version,
            subject_id="MQ-001",
            occurred_at=HISTORICAL_REPLAY_TIMESTAMP,
            source_event_id=source_event_id,
            source_event_type="HISTORICAL_EVIDENCE_REPLAY",
            origin=Origin.HISTORICAL_REPLAY,
            stack_index=1,
            evidence={
                "historical_replay": True,
                "claim_boundary": definition.claim_boundary,
            },
            artifact_refs=tuple(definition.evidence_refs),
            state_hash=current_hash,
            previous_occurrence_hash=previous_hash,
        )
        rows.append(row)
        previous_hash = current_hash

    return tuple(rows)


def occurrence_to_dict(row: AchievementOccurrence) -> dict:
    return {
        "occurrence_id": row.occurrence_id,
        "achievement_id": row.achievement_id,
        "achievement_version": row.achievement_version,
        "trigger_version": row.trigger_version,
        "subject_id": row.subject_id,
        "occurred_at": row.occurred_at,
        "source_event_id": row.source_event_id,
        "source_event_type": row.source_event_type,
        "origin": row.origin.value,
        "stack_index": row.stack_index,
        "evidence": dict(row.evidence),
        "artifact_refs": list(row.artifact_refs),
        "experiment_id": row.experiment_id,
        "session_id": row.session_id,
        "generation": row.generation,
        "runtime_profile": row.runtime_profile,
        "experiment_seed": row.experiment_seed,
        "state_hash": row.state_hash,
        "previous_occurrence_hash": row.previous_occurrence_hash,
    }
