from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from oracle.reinforcement import ReinforcementCondition


DARKNESS_VERSION = "sc-02-darkness/v1"
DEFAULT_RETAINED_AMPLITUDE = 0.25
DEFAULT_DURATION_TRANSITIONS = 10


class DarknessError(ValueError):
    pass


@dataclass(frozen=True)
class DarknessIntervention:
    schema_version: str
    condition: ReinforcementCondition
    retained_amplitude: float
    duration_transitions: int
    started_at_generation: int
    ends_after_generation: int


def build_darkness(
    *,
    current_generation: int,
    retained_amplitude: float = DEFAULT_RETAINED_AMPLITUDE,
    duration_transitions: int = DEFAULT_DURATION_TRANSITIONS,
) -> DarknessIntervention:
    if not 0.0 <= retained_amplitude <= 1.0:
        raise DarknessError(
            "retained_amplitude must be between 0.0 and 1.0"
        )

    if duration_transitions <= 0:
        raise DarknessError(
            "duration_transitions must be positive"
        )

    return DarknessIntervention(
        schema_version=DARKNESS_VERSION,
        condition=ReinforcementCondition.SC_02_DARKNESS,
        retained_amplitude=retained_amplitude,
        duration_transitions=duration_transitions,
        started_at_generation=current_generation,
        ends_after_generation=(
            current_generation + duration_transitions
        ),
    )


def is_darkness_active(
    intervention: DarknessIntervention,
    *,
    generation: int,
) -> bool:
    return (
        intervention.started_at_generation
        <= generation
        < intervention.ends_after_generation
    )


def apply_darkness(
    *,
    stimulus: np.ndarray,
    intervention: DarknessIntervention,
    generation: int,
) -> np.ndarray:
    original = np.asarray(
        stimulus,
        dtype=np.float32,
    )

    if not np.all(np.isfinite(original)):
        raise DarknessError(
            "stimulus contains non-finite values"
        )

    if not is_darkness_active(
        intervention,
        generation=generation,
    ):
        return original.copy()

    return (
        original
        * intervention.retained_amplitude
    ).astype(
        np.float32,
        copy=False,
    )
