from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import numpy as np

from brain.visual_transduction import (
    VisualTransductionConfig,
    VisualTransductionRuntime,
)


class PhysiologyConstrainedVisualTransductionRuntime(
    VisualTransductionRuntime
):
    """
    MQ-3.2 experimental runtime.

    Preserves the frozen MQ-2.1 R1-R6 visual-transduction mechanism.

    Only neurons in the frozen MQ-3.2 graded-type artifact
    (Tm2, Tm3, Tm4) may transmit positive subthreshold voltage.

    All other neurons retain spike-only propagation.

    Graded neurons use:

        max(
            previous_spike,
            clip(previous_voltage, 0, threshold) / threshold
        )

    No gain coefficient is introduced.
    """

    def __init__(
        self,
        connectome,
        retinal_indices: np.ndarray,
        relay_artifact: Path,
        graded_artifact: Path,
        config: VisualTransductionConfig | None = None,
        synaptic_modifier: Callable[
            [np.ndarray, np.ndarray],
            np.ndarray,
        ] | None = None,
    ):
        super().__init__(
            connectome=connectome,
            retinal_indices=retinal_indices,
            relay_artifact=relay_artifact,
            config=config,
        )
        self.synaptic_modifier = (
            synaptic_modifier
        )

        graded = np.load(
            graded_artifact
        )

        self.graded_indices = np.asarray(
            graded["neuron_index"],
            dtype=np.int32,
        )

        self.graded_types = np.asarray(
            graded["type"],
        ).astype(str)

        if len(self.graded_indices) != 5490:
            raise ValueError(
                "unexpected MQ-3.2 graded population size"
            )

        observed_types = set(
            np.unique(
                self.graded_types
            )
        )

        if observed_types != {
            "Tm2",
            "Tm3",
            "Tm4",
        }:
            raise ValueError(
                "unexpected graded cell types: "
                f"{sorted(observed_types)}"
            )

        #
        # MQ-2.1 retinal neurons must never be included
        # in this experimental graded population.
        #
        overlap = np.intersect1d(
            self.retinal_indices,
            self.graded_indices,
        )

        if len(overlap):
            raise ValueError(
                "graded population overlaps frozen R1-R6 retina"
            )

    def effective_activity(
        self,
    ) -> np.ndarray:
        #
        # Baseline behavior everywhere.
        #
        activity = self.spikes.copy()

        #
        # MQ-3.2 change only for the frozen
        # Tm2/Tm3/Tm4 population.
        #
        graded_voltage = np.clip(
            self.voltage[
                self.graded_indices
            ],
            0.0,
            self.config.threshold,
        )

        graded_activity = (
            graded_voltage
            / self.config.threshold
        )

        activity[
            self.graded_indices
        ] = np.maximum(
            self.spikes[
                self.graded_indices
            ],
            graded_activity,
        )

        return activity

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

        #
        # Frozen MQ-2.1 retinal processing.
        #
        retinal_spikes = prior_spikes[
            self.retinal_indices
        ]

        direct_retinal_current = (
            self.relay_from_retina
            @ retinal_spikes
        )

        direct_retinal_current = np.asarray(
            direct_retinal_current,
            dtype=np.float32,
        ).ravel()

        inhibition = np.maximum(
            -direct_retinal_current,
            0.0,
        )

        release = np.maximum(
            self.relay_inhibition
            - inhibition,
            0.0,
        )

        #
        # MQ-3.2 experimental propagation.
        #
        effective_activity = (
            self.effective_activity()
        )

        synaptic = (
            self.connectome
            @ effective_activity
        )

        synaptic = np.asarray(
            synaptic,
            dtype=np.float32,
        ).ravel()

        if self.synaptic_modifier is not None:
            modified = self.synaptic_modifier(
                effective_activity,
                synaptic,
            )

            modified = np.asarray(
                modified,
                dtype=np.float32,
            )

            if modified.shape != synaptic.shape:
                raise ValueError(
                    "synaptic modifier shape mismatch"
                )

            if not np.all(
                np.isfinite(modified)
            ):
                raise ValueError(
                    "synaptic modifier produced non-finite values"
                )

            synaptic = modified.copy()

        #
        # Frozen MQ-2.1 retinal double-count removal.
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

        self.relay_inhibition[:] = inhibition
        self.last_release[:] = release

        return self.spikes
