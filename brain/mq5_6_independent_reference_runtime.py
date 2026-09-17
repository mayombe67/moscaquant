from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from scipy import sparse


@dataclass(frozen=True)
class ReferenceRuntimeConfig:
    dt_ms: float = 1.0
    tau_ms: float = 20.0
    threshold: float = 1.0
    reset: float = 0.0
    release_gain: float = 0.9981738484618123

    @property
    def decay(self) -> float:
        return math.exp(
            -self.dt_ms / self.tau_ms
        )


class IndependentReferenceRuntime:
    """
    MQ-5.6 independent full-network reference implementation.

    Deliberately does NOT inherit from or call any existing
    MoscaQuant neural runtime.

    Frozen scientific behavior reproduced independently:
      - full connectome propagation
      - spike-only propagation by default
      - graded Tm2/Tm3/Tm4 propagation
      - frozen R1-R6 -> relay handling
      - release from inhibition
      - membrane decay
      - threshold / spike / reset behavior
      - MQ-5 presynaptic attenuation
    """

    def __init__(
        self,
        connectome: sparse.spmatrix,
        retinal_indices: np.ndarray,
        relay_indices: np.ndarray,
        graded_indices: np.ndarray,
        config: ReferenceRuntimeConfig | None = None,
    ) -> None:
        matrix = connectome.tocsr()

        if matrix.shape[0] != matrix.shape[1]:
            raise ValueError(
                "connectome must be square"
            )

        if matrix.dtype != np.float32:
            raise ValueError(
                "connectome must be float32"
            )

        self.connectome = matrix

        self.population_size = int(
            matrix.shape[0]
        )

        self.retinal_indices = np.asarray(
            retinal_indices,
            dtype=np.int32,
        )

        self.relay_indices = np.asarray(
            relay_indices,
            dtype=np.int32,
        )

        self.graded_indices = np.asarray(
            graded_indices,
            dtype=np.int32,
        )

        self.config = (
            config
            if config is not None
            else ReferenceRuntimeConfig()
        )

        self.decay = self.config.decay

        overlap = np.intersect1d(
            self.retinal_indices,
            self.graded_indices,
        )

        if len(overlap):
            raise ValueError(
                "retinal and graded populations overlap"
            )

        self.relay_from_retina = (
            self.connectome[
                self.relay_indices,
                :
            ][
                :,
                self.retinal_indices,
            ]
            .tocsr()
        )

        if (
            self.relay_from_retina.nnz
            and np.any(
                self.relay_from_retina.data > 0
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

    def reset_state(self) -> None:
        self.voltage.fill(0.0)
        self.spikes.fill(0.0)
        self.relay_inhibition.fill(0.0)
        self.last_release.fill(0.0)

    def effective_activity(
        self,
        attenuation: dict[int, float] | None = None,
    ) -> np.ndarray:
        """
        Frozen MQ-3.2 activity rule.

        Ordinary neurons:
            previous spike only

        Frozen graded Tm2/Tm3/Tm4:
            max(
                previous spike,
                clip(previous voltage, 0, threshold)
                / threshold
            )

        attenuation values are FRACTION REMOVED.
        """

        activity = self.spikes.copy()

        graded_voltage = np.clip(
            self.voltage[
                self.graded_indices
            ],
            np.float32(0.0),
            np.float32(
                self.config.threshold
            ),
        )

        graded_activity = (
            graded_voltage
            / np.float32(
                self.config.threshold
            )
        )

        activity[
            self.graded_indices
        ] = np.maximum(
            self.spikes[
                self.graded_indices
            ],
            graded_activity,
        )

        if attenuation:
            for node, removed in (
                attenuation.items()
            ):
                node = int(node)
                removed = float(removed)

                if not 0.0 <= removed <= 1.0:
                    raise ValueError(
                        "attenuation outside [0,1]"
                    )

                if (
                    node < 0
                    or node >= self.population_size
                ):
                    raise ValueError(
                        f"invalid intervention node: {node}"
                    )

                if np.any(
                    self.retinal_indices == node
                ):
                    raise ValueError(
                        "retinal intervention unsupported"
                    )

                activity[node] *= np.float32(
                    1.0 - removed
                )

        return activity

    def step(
        self,
        stimulus: np.ndarray,
        attenuation: dict[int, float] | None = None,
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

        #
        # Previous-frame retinal spikes.
        #
        retinal_spikes = self.spikes[
            self.retinal_indices
        ]

        #
        # Frozen R1-R6 -> relay current.
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
        # Convert inhibitory retinal current to
        # inhibition magnitude.
        #
        inhibition = np.maximum(
            -direct_retinal_current,
            np.float32(0.0),
        )

        #
        # Release occurs only when inhibition falls.
        #
        release = np.maximum(
            self.relay_inhibition
            - inhibition,
            np.float32(0.0),
        )

        #
        # Independent MQ-3.2 effective activity
        # plus MQ-5 attenuation.
        #
        activity = self.effective_activity(
            attenuation
        )

        #
        # Full ordinary-connectome propagation.
        #
        synaptic = (
            self.connectome
            @ activity
        )

        synaptic = np.asarray(
            synaptic,
            dtype=np.float32,
        ).ravel()

        #
        # Remove the ordinary R1-R6 relay term:
        # that pathway is handled as graded inhibition.
        #
        synaptic[
            self.relay_indices
        ] -= direct_retinal_current

        #
        # Frozen membrane dynamics.
        #
        self.voltage *= self.decay

        self.voltage += synaptic
        self.voltage += stimulus

        self.voltage[
            self.relay_indices
        ] += (
            release
            * np.float32(
                self.config.release_gain
            )
        )

        #
        # Threshold / spike / reset.
        #
        fired = (
            self.voltage
            >= self.config.threshold
        )

        self.spikes.fill(0.0)

        self.spikes[
            fired
        ] = np.float32(1.0)

        self.voltage[
            fired
        ] = np.float32(
            self.config.reset
        )

        #
        # Persist relay state.
        #
        self.relay_inhibition[:] = inhibition
        self.last_release[:] = release

        return self.spikes
