from __future__ import annotations

from collections import defaultdict
from typing import Dict, List, Set

from .models import AchievementOccurrence


class DuplicateOccurrenceError(ValueError):
    pass


class OccurrenceStore:
    def __init__(self) -> None:
        self._occurrences: List[AchievementOccurrence] = []
        self._replay_keys: Set[str] = set()
        self._by_achievement: Dict[str, List[AchievementOccurrence]] = defaultdict(list)
        self._by_source_event: Dict[str, List[AchievementOccurrence]] = defaultdict(list)

    def append(self, occurrence: AchievementOccurrence) -> None:
        key = occurrence.replay_key()
        if key in self._replay_keys:
            raise DuplicateOccurrenceError(key)
        expected_stack = len(self._by_achievement[occurrence.achievement_id]) + 1
        if occurrence.stack_index != expected_stack:
            raise ValueError(f'invalid stack_index {occurrence.stack_index}; expected {expected_stack}')
        self._occurrences.append(occurrence)
        self._replay_keys.add(key)
        self._by_achievement[occurrence.achievement_id].append(occurrence)
        self._by_source_event[occurrence.source_event_id].append(occurrence)

    def occurrences(self, achievement_id: str) -> tuple[AchievementOccurrence, ...]:
        return tuple(self._by_achievement.get(achievement_id, ()))

    def co_occurrences(self, source_event_id: str) -> tuple[AchievementOccurrence, ...]:
        return tuple(self._by_source_event.get(source_event_id, ()))

    def stack_count(self, achievement_id: str) -> int:
        return len(self._by_achievement.get(achievement_id, ()))

    def first_seen(self, achievement_id: str) -> str | None:
        rows = self._by_achievement.get(achievement_id, ())
        return rows[0].occurred_at if rows else None

    def latest_seen(self, achievement_id: str) -> str | None:
        rows = self._by_achievement.get(achievement_id, ())
        return rows[-1].occurred_at if rows else None
