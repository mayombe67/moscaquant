from achievements.longitudinal_v1 import (
    build_dossier,
    build_longitudinal_projection,
    co_occurring_achievement_ids,
    deterministic_streak_days,
)
from achievements.models import (
    AchievementDefinition,
    AchievementOccurrence,
    Category,
    EvidenceLevel,
    Origin,
    StackPolicy,
)
from achievements.store import OccurrenceStore


def definition(achievement_id="ACH-065"):
    return AchievementDefinition(
        achievement_id=achievement_id,
        version="1.0",
        trigger_version="paper-hands/v1",
        title="TEST ACHIEVEMENT",
        category=Category.BEHAVIOR,
        evidence_level=EvidenceLevel.E1,
        stack_policy=StackPolicy.REPEATABLE,
        public_text="public",
        science_text="science",
        claim_boundary="boundary",
        evidence_refs=("docs/evidence.md",),
    )


def occurrence(
    occurrence_id,
    achievement_id,
    when,
    source_event_id,
    stack_index,
    *,
    trigger_version="paper-hands/v1",
):
    return AchievementOccurrence(
        occurrence_id=occurrence_id,
        achievement_id=achievement_id,
        achievement_version="1.0",
        trigger_version=trigger_version,
        subject_id="MQ-001",
        occurred_at=when,
        source_event_id=source_event_id,
        source_event_type="decision",
        origin=Origin.LIVE,
        stack_index=stack_index,
        evidence={"example": stack_index},
        artifact_refs=(f"artifact-{occurrence_id}.json",),
        experiment_id="mq-test",
        session_id="session-1",
        generation=stack_index,
        runtime_profile="habitat",
        experiment_seed=5,
    )


def test_dossier_is_derived_from_immutable_occurrences():
    store = OccurrenceStore()
    store.append(occurrence("a", "ACH-065", "2026-09-18T23:55:00Z", "event-1", 1))
    store.append(occurrence("b", "ACH-065", "2026-09-19T00:05:00Z", "event-2", 2))
    store.append(occurrence("c", "ACH-065", "2026-09-20T12:00:00Z", "event-3", 3))

    dossier = build_dossier(
        definition=definition(),
        store=store,
        semantics={
            "family": "BEHAVIOR",
            "tags": ["test"],
            "related_achievement_ids": ["ACH-066"],
        },
    )

    assert dossier["stack_count"] == 3
    assert dossier["first_recorded_at"] == "2026-09-18T23:55:00Z"
    assert dossier["latest_recorded_at"] == "2026-09-20T12:00:00Z"
    assert dossier["longest_daily_streak"] == 3
    assert len(dossier["occurrence_history"]) == 3
    assert dossier["derived_only"] is True


def test_co_occurrence_uses_shared_source_event():
    store = OccurrenceStore()
    store.append(occurrence("a", "ACH-065", "2026-09-19T12:00:00Z", "shared", 1))
    store.append(occurrence("b", "ACH-066", "2026-09-19T12:00:00Z", "shared", 1))

    assert co_occurring_achievement_ids(store, "ACH-065") == ("ACH-066",)


def test_streak_deduplicates_multiple_occurrences_same_day():
    rows = [
        occurrence("a", "ACH-065", "2026-09-18T01:00:00Z", "e1", 1),
        occurrence("b", "ACH-065", "2026-09-18T02:00:00Z", "e2", 2),
        occurrence("c", "ACH-065", "2026-09-19T02:00:00Z", "e3", 3),
    ]
    assert deterministic_streak_days(rows) == 2


def test_projection_contains_family_summary_without_replacing_history():
    store = OccurrenceStore()
    store.append(occurrence("a", "ACH-065", "2026-09-18T01:00:00Z", "e1", 1))

    projection = build_longitudinal_projection(
        definitions=[definition()],
        store=store,
        semantics_by_id={"ACH-065": {"family": "BEHAVIOR"}},
    )

    assert projection["schema"] == "moscaquant-achievement-longitudinal-projection/v1"
    assert projection["achievement_count"] == 1
    assert projection["families"][0]["family"] == "BEHAVIOR"
    assert projection["families"][0]["total_occurrences"] == 1
    assert projection["derivation"]["presentation_is_authoritative"] is False
    assert projection["achievements"][0]["occurrence_history"][0]["occurrence_id"] == "a"
