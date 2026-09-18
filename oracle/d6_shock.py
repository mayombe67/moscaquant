from __future__ import annotations

import hashlib
from dataclasses import dataclass

import numpy as np

from oracle.reinforcement import ReinforcementCondition


SHOCK_VERSION = "sc-01-shock/v1"
TARGET_SELECTOR_VERSION = "sc-01-target-sha256/v1"

DEFAULT_INTENSITY = 0.75
DEFAULT_DURATION_TRANSITIONS = 1
DEFAULT_COOLDOWN_TRANSITIONS = 10


SHOCK_TARGET_POOL = (
    43417,
    44274,
    55548,
    55925,
    56393,
    64717,
    65084,
    68045,
    87441,
    92657,
    93484,
    128590,
    135589,
)


class ShockError(ValueError):
    pass


@dataclass(frozen=True)
class ShockIntervention:
    schema_version: str
    condition: ReinforcementCondition
    selector_version: str
    target_model_index: int
    target_pool_index: int
    intensity: float
    duration_transitions: int
    cooldown_transitions: int
    started_at_generation: int
    ends_after_generation: int


def select_shock_target(
    *,
    seed: int,
    experiment_id: str,
    session_id: str,
) -> tuple[int, int]:
    payload = (
        f"{TARGET_SELECTOR_VERSION}\0"
        f"{seed}\0"
        f"{experiment_id}\0"
        f"{session_id}"
    ).encode("utf-8")

    digest = hashlib.sha256(payload).digest()

    index = (
        int.from_bytes(
            digest[:8],
            byteorder="big",
            signed=False,
        )
        % len(SHOCK_TARGET_POOL)
    )

    return index, SHOCK_TARGET_POOL[index]


def build_shock(
    *,
    seed: int,
    experiment_id: str,
    session_id: str,
    current_generation: int,
    intensity: float = DEFAULT_INTENSITY,
) -> ShockIntervention:
    if not 0.0 <= intensity <= 1.0:
        raise ShockError(
            "intensity must be between 0.0 and 1.0"
        )

    pool_index, target = select_shock_target(
        seed=seed,
        experiment_id=experiment_id,
        session_id=session_id,
    )

    return ShockIntervention(
        schema_version=SHOCK_VERSION,
        condition=ReinforcementCondition.SC_01_SHOCK,
        selector_version=TARGET_SELECTOR_VERSION,
        target_model_index=target,
        target_pool_index=pool_index,
        intensity=intensity,
        duration_transitions=DEFAULT_DURATION_TRANSITIONS,
        cooldown_transitions=DEFAULT_COOLDOWN_TRANSITIONS,
        started_at_generation=current_generation,
        ends_after_generation=current_generation + 1,
    )


def is_shock_active(
    intervention: ShockIntervention,
    *,
    generation: int,
) -> bool:
    return (
        intervention.started_at_generation
        <= generation
        < intervention.ends_after_generation
    )


def apply_shock_activity(
    *,
    effective_activity: np.ndarray,
    intervention: ShockIntervention,
    generation: int,
) -> np.ndarray:
    activity = np.asarray(
        effective_activity,
        dtype=np.float32,
    ).copy()

    target = intervention.target_model_index

    if target < 0 or target >= len(activity):
        raise ShockError(
            "shock target outside activity vector"
        )

    if is_shock_active(
        intervention,
        generation=generation,
    ):
        activity[target] = max(
            float(activity[target]),
            intervention.intensity,
        )

    return activity
