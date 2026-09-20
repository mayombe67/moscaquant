from __future__ import annotations

import re
from typing import Dict, Iterable

from .models import AchievementDefinition, Category, EvidenceLevel, StackPolicy

_ID_RE = re.compile(r'^ACH-(\d{3})$')


def achievement_number(achievement_id: str) -> int:
    match = _ID_RE.match(achievement_id)
    if not match:
        raise ValueError(f'invalid achievement id: {achievement_id}')
    value = int(match.group(1))
    if value < 1 or value > 140:
        raise ValueError(f'achievement id outside canonical namespace: {achievement_id}')
    return value


_EXTENDED_CATEGORY_BY_ID = {
    129: Category.SCIENCE,
    130: Category.SCIENCE,
    131: Category.CONTAINMENT,
    132: Category.BEHAVIOR,
    133: Category.BEHAVIOR,
    134: Category.BEHAVIOR,
    135: Category.ORACLE,
    136: Category.SCIENCE,
    137: Category.ORACLE,
    138: Category.LORE,
    139: Category.LORE,
    140: Category.SECRET_ODDITY,
}


def expected_category(achievement_id: str) -> Category:
    n = achievement_number(achievement_id)
    if n in _EXTENDED_CATEGORY_BY_ID:
        return _EXTENDED_CATEGORY_BY_ID[n]
    if n <= 32:
        return Category.SCIENCE
    if n <= 48:
        return Category.ORACLE
    if n <= 64:
        return Category.CONTAINMENT
    if n <= 88:
        return Category.BEHAVIOR
    if n <= 112:
        return Category.LORE
    if n <= 120:
        return Category.ANOMALOUS_OBSERVANCE
    return Category.SECRET_ODDITY


def validate_definition(definition: AchievementDefinition) -> None:
    expected = expected_category(definition.achievement_id)
    if definition.category != expected:
        raise ValueError(f'{definition.achievement_id} belongs to {expected.value}, not {definition.category.value}')
    if definition.permanently_locked and definition.stack_policy is not StackPolicy.SINGLE:
        raise ValueError('permanently locked achievements must use SINGLE stack policy')


def build_registry(definitions: Iterable[AchievementDefinition]) -> Dict[str, AchievementDefinition]:
    registry: Dict[str, AchievementDefinition] = {}
    for definition in definitions:
        validate_definition(definition)
        if definition.achievement_id in registry:
            raise ValueError(f'duplicate achievement id: {definition.achievement_id}')
        registry[definition.achievement_id] = definition
    return registry


HALF_LIFE_3_CONFIRMED = AchievementDefinition(
    achievement_id='ACH-128',
    version='1.0',
    trigger_version='never/v1',
    title='HALF-LIFE 3 CONFIRMED',
    category=Category.SECRET_ODDITY,
    evidence_level=EvidenceLevel.E0,
    stack_policy=StackPolicy.SINGLE,
    public_text='Nice try.',
    science_text='No valid telemetry condition can unlock this achievement.',
    claim_boundary='Lore-only invariant. Permanently unreachable.',
    permanently_locked=True,
)
