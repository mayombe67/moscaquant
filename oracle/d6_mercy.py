from __future__ import annotations

import hashlib
from dataclasses import dataclass

import numpy as np

from oracle.reinforcement import ReinforcementCondition


MERCY_VERSION = "sc-06-mercy/v1"
TARGET_SELECTOR_VERSION = "sc-06-target-sha256/v1"

DEFAULT_GAIN = 0.25
DEFAULT_DURATION_TRANSITIONS = 1
DEFAULT_COOLDOWN_TRANSITIONS = 10


MERCY_TARGET_POOL = (
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


class MercyError(ValueError):
    pass


@dataclass(frozen=True)
class MercyIntervention:
    schema_version: str
    condition: ReinforcementCondition
    selector_version: str
    target_model_index: int
    target_pool_index: int
    gain: float
    duration_transitions: int
    cooldown_transitions: int
    started_at_generation: int
    ends_after_generation: int


def select_mercy_target(
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
        % len(MERCY_TARGET_POOL)
    )

    return index, MERCY_TARGET_POOL[index]


def build_mercy(
    *,
    seed: int,
    experiment_id: str,
    session_id: str,
    current_generation: int,
    gain: float = DEFAULT_GAIN,
) -> MercyIntervention:
    if not 0.0 <= gain <= 1.0:
        raise MercyError(
            "gain must be between 0.0 and 1.0"
        )

    pool_index, target = select_mercy_target(
        seed=seed,
        experiment_id=experiment_id,
        session_id=session_id,
    )

    return MercyIntervention(
        schema_version=MERCY_VERSION,
        condition=ReinforcementCondition.SC_06_MERCY,
        selector_version=TARGET_SELECTOR_VERSION,
        target_model_index=target,
        target_pool_index=pool_index,
        gain=gain,
        duration_transitions=DEFAULT_DURATION_TRANSITIONS,
        cooldown_transitions=DEFAULT_COOLDOWN_TRANSITIONS,
        started_at_generation=current_generation,
        ends_after_generation=current_generation + 1,
    )


def is_mercy_active(
    intervention: MercyIntervention,
    *,
    generation: int,
) -> bool:
    return (
        intervention.started_at_generation
        <= generation
        < intervention.ends_after_generation
    )


def apply_mercy_activity(
    *,
    effective_activity: np.ndarray,
    intervention: MercyIntervention,
    generation: int,
) -> np.ndarray:
    activity = np.asarray(
        effective_activity,
        dtype=np.float32,
    ).copy()

    target = intervention.target_model_index

    if target < 0 or target >= len(activity):
        raise MercyError(
            "mercy target outside activity vector"
        )

    if not is_mercy_active(
        intervention,
        generation=generation,
    ):
        return activity

    existing = float(activity[target])

    if existing <= 0.0:
        return activity

    activity[target] = np.float32(
        min(
            1.0,
            existing * (1.0 + intervention.gain),
        )
    )

    return activity
