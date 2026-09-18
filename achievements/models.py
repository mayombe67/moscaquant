from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Tuple


class Category(str, Enum):
    SCIENCE = 'SCIENCE'
    ORACLE = 'ORACLE'
    CONTAINMENT = 'CONTAINMENT'
    BEHAVIOR = 'BEHAVIOR'
    LORE = 'LORE'
    ANOMALOUS_OBSERVANCE = 'ANOMALOUS_OBSERVANCE'
    SECRET_ODDITY = 'SECRET_ODDITY'


class EvidenceLevel(str, Enum):
    E0 = 'E0'
    E1 = 'E1'
    E2 = 'E2'
    E3 = 'E3'
    E4 = 'E4'


class StackPolicy(str, Enum):
    SINGLE = 'SINGLE'
    REPEATABLE = 'REPEATABLE'
    PROGRESSIVE = 'PROGRESSIVE'


class Origin(str, Enum):
    LIVE = 'LIVE'
    HISTORICAL_REPLAY = 'HISTORICAL_REPLAY'
    MANUAL_CANON = 'MANUAL_CANON'


class ScienceEffect(str, Enum):
    NONE = 'NONE'
    PRESENTATION_ONLY = 'PRESENTATION_ONLY'
    EXPERIMENTAL = 'EXPERIMENTAL'


@dataclass(frozen=True)
class AchievementDefinition:
    achievement_id: str
    version: str
    trigger_version: str
    title: str
    category: Category
    evidence_level: EvidenceLevel
    stack_policy: StackPolicy
    public_text: str
    science_text: str
    claim_boundary: str = ''
    evidence_refs: Tuple[str, ...] = ()
    permanently_locked: bool = False


@dataclass(frozen=True)
class AchievementOccurrence:
    occurrence_id: str
    achievement_id: str
    achievement_version: str
    trigger_version: str
    subject_id: str
    occurred_at: str
    source_event_id: str
    source_event_type: str
    origin: Origin
    stack_index: int
    evidence: Mapping[str, Any] = field(default_factory=dict)
    artifact_refs: Tuple[str, ...] = ()
    experiment_id: str | None = None
    session_id: str | None = None
    generation: int | None = None
    runtime_profile: str | None = None
    experiment_seed: int | None = None
    state_hash: str = ''
    previous_occurrence_hash: str = ''

    def replay_key(self) -> str:
        return '|'.join((self.achievement_id, self.source_event_id, self.trigger_version, self.origin.value))
