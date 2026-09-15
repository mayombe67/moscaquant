from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import math

import numpy as np
from scipy import sparse


@dataclass(frozen=True)
class VisualTransductionConfig:
    dt_ms: float = 1.0
    tau_ms: float = 20.0
    threshold: float = 1.0
    reset: float = 0.0
    release_gain: float = 0.0


class VisualTransductionRuntime:
    """
    MQ-2.1 visual-specific extension of the baseline LIF runtime.

    The frozen R1-R6 -> relay synaptic contribution is intercepted for the
    frozen L1/L2/L3/Lai relay population.

    That direct retinal contribution is represented as graded inhibition.
    A decrease in inhibition produces a positive release-from-inhibition
    drive into the existing LIF membrane state.

    All other connectome edges retain baseline behavior.
    """

    def __init__(
        self,
        connectome,
        retinal_indices: np.ndarray,
        relay_artifact: Path,
        config: VisualTransductionConfig | None = None,
    ):
        self.connectome = connectome.tocsr()

        self.config = (
            config
            if config is not None
            else VisualTransductionConfig()
        )

        self.population_size = (
            self.connectome.shape[0]
        )

        if self.connectome.shape != (
            self.population_size,
            self.population_size,
        ):
            raise ValueError(
                "connectome must be square"
            )

        self.retinal_indices = np.asarray(
            retinal_indices,
            dtype=np.int32,
        )

        relay = np.load(
            relay_artifact
        )

        self.relay_indices = np.asarray(
            relay["neuron_index"],
            dtype=np.int32,
        )

        self.relay_body_ids = np.asarray(
            relay["body_id"],
            dtype=np.int64,
        )

        self.relay_types = np.asarray(
            relay["type"],
        )

        if len(self.relay_indices) != 2430:
            raise ValueError(
                "unexpected MQ-2.1 relay population"
            )

        self.relay_from_retina = (
            self.connectome[
                self.relay_indices,
                :
            ][
                :,
                self.retinal_indices
            ].tocsr()
        )

        #
        # The frozen R1-R6 first-hop signal should be
        # exclusively inhibitory.
        #
        if (
            self.relay_from_retina.nnz
            and np.any(
                self.relay_from_retina.data
                > 0
            )
        ):
            raise ValueError(
                "positive R1-R6 -> relay edge found"
            )

        self.voltage = np.zeros(
            self.population_size,
            dtype=np.float32,
        )

        self.spikes = np.zeros(
            self.population_size,
            dtype=np.float32,
        )

        self.relay_inhibition = np.zeros(
            len(self.relay_indices),
            dtype=np.float32,
        )

        self.last_release = np.zeros(
            len(self.relay_indices),
            dtype=np.float32,
        )

        self.decay = math.exp(
            -self.config.dt_ms
            / self.config.tau_ms
        )

    def reset_state(self):
        self.voltage.fill(0.0)
        self.spikes.fill(0.0)
        self.relay_inhibition.fill(0.0)
        self.last_release.fill(0.0)

    def step(
        self,
        stimulus: np.ndarray,
    ) -> np.ndarray:
        stimulus = np.asarray(
            stimulus,
            dtype=np.float32,
        )

        if stimulus.shape != (
            self.population_size,
        ):
            raise ValueError(
                "stimulus shape mismatch"
            )

        prior_spikes = self.spikes

        retinal_spikes = prior_spikes[
            self.retinal_indices
        ]

        #
        # Frozen biological R1-R6 direct current.
        #
        direct_retinal_current = (
            self.relay_from_retina
            @ retinal_spikes
        )

        direct_retinal_current = np.asarray(
            direct_retinal_current,
            dtype=np.float32,
        ).ravel()

        #
        # Convert negative histaminergic current into
        # a positive graded inhibition magnitude.
        #
        inhibition = np.maximum(
            -direct_retinal_current,
            0.0,
        )

        #
        # Release from inhibition exists only when
        # inhibition becomes weaker than the prior frame.
        #
        release = np.maximum(
            self.relay_inhibition
            - inhibition,
            0.0,
        )

        synaptic = (
            self.connectome
            @ prior_spikes
        )

        synaptic = np.asarray(
            synaptic,
            dtype=np.float32,
        ).ravel()

        #
        # Critical MQ-2.1 rule:
        #
        # Remove the ordinary R1-R6 -> relay contribution
        # from baseline LIF processing so histamine is not
        # counted twice.
        #
        synaptic[
            self.relay_indices
        ] -= direct_retinal_current

        self.voltage *= self.decay

        self.voltage += synaptic

        self.voltage += stimulus

        self.voltage[
            self.relay_indices
        ] += (
            release
            * self.config.release_gain
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
        ] = self.config.reset

        self.relay_inhibition[:] = (
            inhibition
        )

        self.last_release[:] = (
            release
        )

        return self.spikes
