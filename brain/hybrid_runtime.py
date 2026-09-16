from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy import sparse


@dataclass(frozen=True)
class HybridRuntimeConfig:
    dt_ms: float = 1.0
    tau_ms: float = 20.0
    threshold: float = 1.0
    reset_voltage: float = 0.0


class HybridRuntime:
    """
    Experimental MQ-3.1 runtime.

    Structural connectome is unchanged.

    Presynaptic drive is:

        max(
            previous_spike,
            clip(previous_voltage, 0, threshold) / threshold
        )

    Therefore:
    - a spike contributes full activity 1.0
    - positive subthreshold voltage contributes proportionally
    - negative presynaptic voltage contributes nothing
    - spike and graded voltage are never added together
    """

    def __init__(
        self,
        connectome: sparse.csr_matrix,
        config: HybridRuntimeConfig | None = None,
    ):
        self.connectome = connectome.tocsr()

        self.config = (
            config
            if config is not None
            else HybridRuntimeConfig()
        )

        self.decay = np.exp(
            -self.config.dt_ms
            / self.config.tau_ms
        )

        neuron_count = (
            self.connectome.shape[0]
        )

        self.voltage = np.zeros(
            neuron_count,
            dtype=np.float32,
        )

        self.spikes = np.zeros(
            neuron_count,
            dtype=np.float32,
        )

    def effective_activity(
        self,
    ) -> np.ndarray:
        graded = np.clip(
            self.voltage,
            0.0,
            self.config.threshold,
        )

        graded = (
            graded
            / self.config.threshold
        )

        return np.maximum(
            self.spikes,
            graded,
        ).astype(
            np.float32,
            copy=False,
        )

    def step(
        self,
        stimulus: np.ndarray | None = None,
    ) -> np.ndarray:
        activity = (
            self.effective_activity()
        )

        synaptic = (
            self.connectome
            @ activity
        )

        self.voltage *= self.decay

        self.voltage += np.asarray(
            synaptic,
            dtype=np.float32,
        )

        if stimulus is not None:
            self.voltage += np.asarray(
                stimulus,
                dtype=np.float32,
            )

        fired = (
            self.voltage
            >= self.config.threshold
        )

        self.spikes.fill(0.0)

        self.spikes[
            fired
        ] = 1.0

        self.voltage[
            fired
        ] = (
            self.config.reset_voltage
        )

        return self.spikes.copy()

    def reset(
        self,
    ) -> None:
        self.voltage.fill(0.0)
        self.spikes.fill(0.0)
