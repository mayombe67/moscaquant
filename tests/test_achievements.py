import pytest

from achievements.models import AchievementDefinition, AchievementOccurrence, Category, EvidenceLevel, Origin, StackPolicy
from achievements.registry import HALF_LIFE_3_CONFIRMED, build_registry, expected_category
from achievements.store import DuplicateOccurrenceError, OccurrenceStore


def make_occurrence(occurrence_id: str, source_event_id: str, stack_index: int):
    return AchievementOccurrence(
        occurrence_id=occurrence_id,
        achievement_id='ACH-065',
        achievement_version='1.0',
        trigger_version='paper-hands/v1',
        subject_id='MQ-001',
        occurred_at=f'2026-09-18T16:00:0{stack_index}Z',
        source_event_id=source_event_id,
        source_event_type='decision',
        origin=Origin.LIVE,
        stack_index=stack_index,
        evidence={'hold_generations': stack_index},
    )


def test_namespace_boundaries():
    assert expected_category('ACH-001') is Category.SCIENCE
    assert expected_category('ACH-033') is Category.ORACLE
    assert expected_category('ACH-049') is Category.CONTAINMENT
    assert expected_category('ACH-065') is Category.BEHAVIOR
    assert expected_category('ACH-089') is Category.LORE
    assert expected_category('ACH-113') is Category.ANOMALOUS_OBSERVANCE
    assert expected_category('ACH-128') is Category.SECRET_ODDITY


def test_half_life_3_is_permanently_locked():
    assert HALF_LIFE_3_CONFIRMED.permanently_locked is True
    assert HALF_LIFE_3_CONFIRMED.public_text == 'Nice try.'


def test_wrong_category_rejected():
    bad = AchievementDefinition('ACH-001', '1.0', 'x/v1', 'WRONG', Category.LORE, EvidenceLevel.E0, StackPolicy.SINGLE, '', '')
    with pytest.raises(ValueError):
        build_registry([bad])


def test_repeatable_occurrences_stack_and_preserve_history():
    store = OccurrenceStore()
    store.append(make_occurrence('one', 'event-1', 1))
    store.append(make_occurrence('two', 'event-2', 2))
    assert store.stack_count('ACH-065') == 2
    assert len(store.occurrences('ACH-065')) == 2
    assert store.first_seen('ACH-065') == '2026-09-18T16:00:01Z'
    assert store.latest_seen('ACH-065') == '2026-09-18T16:00:02Z'


def test_replay_key_is_idempotent():
    store = OccurrenceStore()
    store.append(make_occurrence('one', 'event-1', 1))
    with pytest.raises(DuplicateOccurrenceError):
        store.append(make_occurrence('different-id', 'event-1', 2))


def test_co_occurrence_preserves_shared_source_event():
    store = OccurrenceStore()
    store.append(make_occurrence('a', 'shared', 1))
    store.append(AchievementOccurrence(
        occurrence_id='b', achievement_id='ACH-066', achievement_version='1.0',
        trigger_version='buy-high-sell-low/v1', subject_id='MQ-001',
        occurred_at='2026-09-18T16:00:01Z', source_event_id='shared',
        source_event_type='decision', origin=Origin.LIVE, stack_index=1,
    ))
    assert {x.achievement_id for x in store.co_occurrences('shared')} == {'ACH-065', 'ACH-066'}
