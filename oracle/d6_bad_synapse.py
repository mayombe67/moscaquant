from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy import sparse

from oracle.reinforcement import ReinforcementCondition


BAD_SYNAPSE_VERSION = "sc-03-bad-synapse/v1"
DEFAULT_MULTIPLIER = 0.95


class BadSynapseError(ValueError):
    pass


@dataclass(frozen=True)
class BadSynapseOverlay:
    schema_version: str
    condition: ReinforcementCondition
    presynaptic: int
    postsynaptic: int
    multiplier: float


def build_bad_synapse_overlay(
    *,
    presynaptic: int,
    postsynaptic: int,
    multiplier: float = DEFAULT_MULTIPLIER,
) -> BadSynapseOverlay:
    if not 0.0 <= multiplier <= 1.0:
        raise BadSynapseError(
            "multiplier must be between 0.0 and 1.0"
        )

    return BadSynapseOverlay(
        schema_version=BAD_SYNAPSE_VERSION,
        condition=ReinforcementCondition.SC_03_BAD_SYNAPSE,
        presynaptic=presynaptic,
        postsynaptic=postsynaptic,
        multiplier=multiplier,
    )


def apply_bad_synapse_overlay(
    *,
    connectome: sparse.spmatrix,
    effective_activity: np.ndarray,
    overlay: BadSynapseOverlay,
) -> np.ndarray:
    matrix = connectome.tocsr(copy=False)

    activity = np.asarray(
        effective_activity,
        dtype=np.float32,
    )

    if activity.ndim != 1:
        raise BadSynapseError(
            "effective_activity must be one-dimensional"
        )

    rows, cols = matrix.shape

    if len(activity) != cols:
        raise BadSynapseError(
            "activity length does not match connectome"
        )

    source = overlay.presynaptic
    target = overlay.postsynaptic

    if source < 0 or source >= cols:
        raise BadSynapseError(
            "presynaptic index outside connectome"
        )

    if target < 0 or target >= rows:
        raise BadSynapseError(
            "postsynaptic index outside connectome"
        )

    weight = float(
        matrix[target, source]
    )

    if weight == 0.0:
        raise BadSynapseError(
            "selected edge does not exist"
        )

    baseline = np.asarray(
        matrix @ activity,
        dtype=np.float32,
    ).ravel()

    result = baseline.copy()

    adjustment = (
        weight
        * float(activity[source])
        * (overlay.multiplier - 1.0)
    )

    result[target] += np.float32(
        adjustment
    )

    return result
