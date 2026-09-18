from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ReinforcementCondition(StrEnum):
    SC_01_SHOCK = "SC-01"
    SC_02_DARKNESS = "SC-02"
    SC_03_BAD_SYNAPSE = "SC-03"
    SC_04_TIME_OUT = "SC-04"
    SC_05_SCAR_TISSUE = "SC-05"
    SC_06_MERCY = "SC-06"


@dataclass(frozen=True)
class ReinforcementSelection:
    schema_version: str
    selector_version: str
    condition: ReinforcementCondition
    selected_index: int
    seed: int
    eligible_conditions: tuple[ReinforcementCondition, ...]


@dataclass(frozen=True)
class ReinforcementResult:
    selection: ReinforcementSelection
    applicable: bool
    status: str
