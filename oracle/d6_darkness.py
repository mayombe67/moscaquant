from __future__ import annotations

from dataclasses import dataclass, replace

from oracle.models import OracleInput
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


@dataclass(frozen=True)
class DarknessTelemetry:
    intervention_version: str
    original_input_hash: str
    transformed_input_hash: str
    retained_amplitude: float
    active: bool


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
    oracle_input: OracleInput,
    intervention: DarknessIntervention,
    generation: int,
) -> OracleInput:
    if not is_darkness_active(
        intervention,
        generation=generation,
    ):
        return oracle_input

    transformed_features = []

    for key, value in oracle_input.derived_features:
        if isinstance(value, (int, float)):
            transformed_features.append(
                (
                    key,
                    float(value)
                    * intervention.retained_amplitude,
                )
            )
        else:
            transformed_features.append((key, value))

    return replace(
        oracle_input,
        derived_features=tuple(transformed_features),
    )
