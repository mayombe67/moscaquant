from __future__ import annotations

from collections.abc import Callable

import numpy as np

from oracle.plasticity_state import PlasticityState


class PlasticityModifierError(ValueError):
    pass


def build_synaptic_modifier(
    plasticity: PlasticityState,
) -> Callable[
    [np.ndarray, np.ndarray],
    np.ndarray,
]:
    edges = plasticity.edges

    def modifier(
        effective_activity: np.ndarray,
        baseline_synaptic: np.ndarray,
    ) -> np.ndarray:
        activity = np.asarray(
            effective_activity,
            dtype=np.float32,
        )

        synaptic = np.asarray(
            baseline_synaptic,
            dtype=np.float32,
        ).copy()

        if activity.ndim != 1:
            raise PlasticityModifierError(
                "effective activity must be one-dimensional"
            )

        if synaptic.ndim != 1:
            raise PlasticityModifierError(
                "synaptic vector must be one-dimensional"
            )

        for edge in edges:
            source = edge.presynaptic
            target = edge.postsynaptic

            if source < 0 or source >= len(activity):
                raise PlasticityModifierError(
                    "plasticity source outside activity vector"
                )

            if target < 0 or target >= len(synaptic):
                raise PlasticityModifierError(
                    "plasticity target outside synaptic vector"
                )

            if not 0.0 < edge.multiplier <= 1.0:
                raise PlasticityModifierError(
                    "invalid plasticity multiplier"
                )

            adjustment = (
                edge.baseline_weight
                * float(activity[source])
                * (edge.multiplier - 1.0)
            )

            synaptic[target] += np.float32(
                adjustment
            )

        if not np.all(
            np.isfinite(synaptic)
        ):
            raise PlasticityModifierError(
                "plasticity produced non-finite synaptic values"
            )

        return synaptic

    return modifier
