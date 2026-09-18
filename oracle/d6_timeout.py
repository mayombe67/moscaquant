from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from oracle.reinforcement import ReinforcementCondition


TIMEOUT_VERSION = "sc-04-time-out/v1"
DEFAULT_DURATION_TRANSITIONS = 10


class TimeOutError(ValueError):
    pass


@dataclass(frozen=True)
class TimeOutIntervention:
    schema_version: str
    condition: ReinforcementCondition
    duration_transitions: int
    started_at_generation: int
    ends_after_generation: int


@dataclass(frozen=True)
class TimeOutReadout:
    voltage: np.ndarray
    spikes: np.ndarray
    active: bool


def build_timeout(
    *,
    current_generation: int,
    duration_transitions: int = DEFAULT_DURATION_TRANSITIONS,
) -> TimeOutIntervention:
    if duration_transitions <= 0:
        raise TimeOutError(
            "duration_transitions must be positive"
        )

    return TimeOutIntervention(
        schema_version=TIMEOUT_VERSION,
        condition=ReinforcementCondition.SC_04_TIME_OUT,
        duration_transitions=duration_transitions,
        started_at_generation=current_generation,
        ends_after_generation=(
            current_generation + duration_transitions
        ),
    )


def is_timeout_active(
    intervention: TimeOutIntervention,
    *,
    generation: int,
) -> bool:
    return (
        intervention.started_at_generation
        <= generation
        < intervention.ends_after_generation
    )


def apply_timeout_readout(
    *,
    voltage: np.ndarray,
    spikes: np.ndarray,
    readout_indices: np.ndarray,
    intervention: TimeOutIntervention,
    generation: int,
) -> TimeOutReadout:
    voltage_copy = np.asarray(
        voltage,
        dtype=np.float32,
    ).copy()

    spikes_copy = np.asarray(
        spikes,
    ).copy()

    indices = np.asarray(
        readout_indices,
        dtype=np.int64,
    )

    if voltage_copy.ndim != 1:
        raise TimeOutError(
            "voltage must be one-dimensional"
        )

    if spikes_copy.ndim != 1:
        raise TimeOutError(
            "spikes must be one-dimensional"
        )

    if len(voltage_copy) != len(spikes_copy):
        raise TimeOutError(
            "voltage and spikes lengths differ"
        )

    if indices.ndim != 1:
        raise TimeOutError(
            "readout_indices must be one-dimensional"
        )

    if np.any(indices < 0) or np.any(
        indices >= len(voltage_copy)
    ):
        raise TimeOutError(
            "readout index outside state vector"
        )

    active = is_timeout_active(
        intervention,
        generation=generation,
    )

    if active:
        voltage_copy[indices] = 0.0
        spikes_copy[indices] = 0

    return TimeOutReadout(
        voltage=voltage_copy,
        spikes=spikes_copy,
        active=active,
    )
