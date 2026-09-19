from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import asdict
from datetime import datetime, timezone
from typing import Iterable, Mapping, Sequence

from .models import AchievementDefinition, AchievementOccurrence
from .store import OccurrenceStore


def _parse_time(value: str) -> datetime:
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _date(value: str | None) -> str | None:
    return value[:10] if value else None


def deterministic_streak_days(rows: Sequence[AchievementOccurrence]) -> int:
    """Longest run of consecutive UTC calendar days with >=1 occurrence."""
    if not rows:
        return 0
    days = sorted({_parse_time(row.occurred_at).date() for row in rows})
    best = run = 1
    for previous, current in zip(days, days[1:]):
        delta = (current - previous).days
        if delta == 1:
            run += 1
            best = max(best, run)
        elif delta > 1:
            run = 1
    return best


def co_occurring_achievement_ids(
    store: OccurrenceStore,
    achievement_id: str,
) -> tuple[str, ...]:
    related: set[str] = set()
    for row in store.occurrences(achievement_id):
        for peer in store.co_occurrences(row.source_event_id):
            if peer.achievement_id != achievement_id:
                related.add(peer.achievement_id)
    return tuple(sorted(related))


def occurrence_history(
    store: OccurrenceStore,
    achievement_id: str,
) -> list[dict]:
    history = []
    for row in store.occurrences(achievement_id):
        history.append({
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
        })
    return history


def build_dossier(
    *,
    definition: AchievementDefinition,
    store: OccurrenceStore,
    semantics: Mapping[str, object] | None = None,
) -> dict:
    """Derive a dossier view without mutating occurrence history."""
    semantics = dict(semantics or {})
    rows = store.occurrences(definition.achievement_id)
    first_seen = store.first_seen(definition.achievement_id)
    latest_seen = store.latest_seen(definition.achievement_id)

    trigger_versions = sorted({row.trigger_version for row in rows})
    origins = sorted({row.origin.value for row in rows})
    source_event_types = sorted({row.source_event_type for row in rows})
    public_artifacts = sorted({
        ref
        for row in rows
        for ref in row.artifact_refs
    })

    return {
        "achievement_id": definition.achievement_id,
        "title": definition.title,
        "category": definition.category.value,
        "family": semantics.get("family", "UNCLASSIFIED"),
        "tags": list(semantics.get("tags", [])),
        "related_achievement_ids": list(
            semantics.get("related_achievement_ids", [])
        ),
        "co_occurring_achievement_ids": list(
            co_occurring_achievement_ids(store, definition.achievement_id)
        ),
        "achievement_version": definition.version,
        "definition_trigger_version": definition.trigger_version,
        "observed_trigger_versions": trigger_versions,
        "evidence_level": definition.evidence_level.value,
        "stack_policy": definition.stack_policy.value,
        "stack_count": store.stack_count(definition.achievement_id),
        "first_recorded_at": first_seen,
        "first_recorded_date": _date(first_seen),
        "latest_recorded_at": latest_seen,
        "latest_recorded_date": _date(latest_seen),
        "longest_daily_streak": deterministic_streak_days(rows),
        "origins": origins,
        "source_event_types": source_event_types,
        "public_text": definition.public_text,
        "science_text": definition.science_text,
        "claim_boundary": definition.claim_boundary,
        "public_evidence_refs": sorted(set(definition.evidence_refs) | set(public_artifacts)),
        "occurrence_history": occurrence_history(store, definition.achievement_id),
        "derived_only": True,
    }


def family_summary(dossiers: Iterable[Mapping[str, object]]) -> list[dict]:
    grouped: dict[str, list[Mapping[str, object]]] = defaultdict(list)
    for dossier in dossiers:
        grouped[str(dossier.get("family") or "UNCLASSIFIED")].append(dossier)

    rows = []
    for family in sorted(grouped):
        members = grouped[family]
        rows.append({
            "family": family,
            "achievement_count": len(members),
            "total_occurrences": sum(int(x.get("stack_count", 0)) for x in members),
            "achievement_ids": sorted(str(x["achievement_id"]) for x in members),
            "evidence_levels": dict(sorted(Counter(
                str(x.get("evidence_level", "E0")) for x in members
            ).items())),
        })
    return rows


def build_longitudinal_projection(
    *,
    definitions: Iterable[AchievementDefinition],
    store: OccurrenceStore,
    semantics_by_id: Mapping[str, Mapping[str, object]] | None = None,
) -> dict:
    semantics_by_id = semantics_by_id or {}
    dossiers = [
        build_dossier(
            definition=definition,
            store=store,
            semantics=semantics_by_id.get(definition.achievement_id, {}),
        )
        for definition in definitions
        if store.stack_count(definition.achievement_id) > 0
    ]
    dossiers.sort(key=lambda row: row["achievement_id"])
    return {
        "schema": "moscaquant-achievement-longitudinal-projection/v1",
        "achievement_count": len(dossiers),
        "achievements": dossiers,
        "families": family_summary(dossiers),
        "derivation": {
            "authoritative_source": "AchievementOccurrence history",
            "presentation_is_authoritative": False,
        },
    }
