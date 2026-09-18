from __future__ import annotations

import hashlib

import numpy as np

from oracle.d6_scar import ScarTissueState


SCAR_EFFECT_VERSION = "sc-05-scar-effect/v1"
SCAR_TARGET_SELECTOR_VERSION = "sc-05-target-sha256/v1"

DEFAULT_ATTENUATION = 0.25

SCAR_TARGET_POOL = (
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


class ScarEffectError(ValueError):
    pass


def select_scar_target(
    *,
    seed: int,
    experiment_id: str,
    origin_session_id: str,
) -> tuple[int, int]:
    payload = (
        f"{SCAR_TARGET_SELECTOR_VERSION}\0"
        f"{seed}\0"
        f"{experiment_id}\0"
        f"{origin_session_id}"
    ).encode("utf-8")

    digest = hashlib.sha256(payload).digest()

    pool_index = (
        int.from_bytes(
            digest[:8],
            byteorder="big",
            signed=False,
        )
        % len(SCAR_TARGET_POOL)
    )

    return (
        pool_index,
        SCAR_TARGET_POOL[pool_index],
    )


def apply_scar_effect(
    *,
    effective_activity: np.ndarray,
    scar_state: ScarTissueState,
    target_model_index: int,
    attenuation: float = DEFAULT_ATTENUATION,
) -> np.ndarray:
    if not 0.0 <= attenuation <= 1.0:
        raise ScarEffectError(
            "attenuation must be between 0.0 and 1.0"
        )

    activity = np.asarray(
        effective_activity,
        dtype=np.float32,
    ).copy()

    if (
        target_model_index < 0
        or target_model_index >= len(activity)
    ):
        raise ScarEffectError(
            "scar target outside activity vector"
        )

    if not scar_state.active:
        return activity

    retained_fraction = 1.0 - attenuation

    activity[target_model_index] *= np.float32(
        retained_fraction
    )

    return activity
