"""Minimal deterministic neural runtime for MQ-001."""

from dataclasses import dataclass

import numpy as np
from scipy import sparse


@dataclass(frozen=True)
class LIFConfig:
    dt_ms: float = 1.0
    tau_ms: float = 20.0
    threshold: float = 1.0
    reset: float = 0.0


class LIFRuntime:
    """Minimal leaky integrate-and-fire runtime over the frozen MQ-001 graph."""

    def __init__(
        self,
        connectome: sparse.csr_matrix,
        config: LIFConfig | None = None,
    ):
        self.connectome = connectome
        self.config = config or LIFConfig()

        self.n = connectome.shape[0]

        if connectome.shape != (self.n, self.n):
            raise ValueError("Connectome must be square")

        self.voltage = np.zeros(self.n, dtype=np.float32)
        self.spikes = np.zeros(self.n, dtype=np.float32)
        self.step_number = 0

        self.decay = np.float32(
            np.exp(-self.config.dt_ms / self.config.tau_ms)
        )

    def step(self, stimulus: np.ndarray | None = None) -> np.ndarray:
        """Advance MQ-001 by one simulation step."""

        synaptic = self.connectome @ self.spikes

        self.voltage *= self.decay
        self.voltage += synaptic

        if stimulus is not None:
            if stimulus.shape != (self.n,):
                raise ValueError(
                    f"Stimulus shape {stimulus.shape} != {(self.n,)}"
                )

            self.voltage += stimulus

        fired = self.voltage >= self.config.threshold

        self.spikes.fill(0.0)
        self.spikes[fired] = 1.0

        self.voltage[fired] = self.config.reset

        self.step_number += 1

        return self.spikes
