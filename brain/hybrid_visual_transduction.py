from __future__ import annotations

from pathlib import Path

import numpy as np

from brain.visual_transduction import (
    VisualTransductionConfig,
    VisualTransductionRuntime,
)


class HybridVisualTransductionRuntime(
    VisualTransductionRuntime
):
    """
    MQ-3.1 experimental propagation runtime.

    Preserves the frozen MQ-2.1 visual-transduction mechanism exactly.

    The only experimental change is the presynaptic activity used by
    ordinary non-retinal connectome edges:

        effective_activity =
            max(
                previous_spike,
                clip(previous_voltage, 0, threshold) / threshold
            )

    Frozen R1-R6 neurons remain spike-only so that:
      * R1-R6 -> relay histaminergic current is unchanged
      * the MQ-2.1 release-from-inhibition mechanism is unchanged
      * retinal contribution removal remains exact
      * sensory gain and release gain remain unchanged

    Negative presynaptic voltage does not transmit.
    Spike and graded activity are not added together.
    """

    def __init__(
        self,
        connectome,
        retinal_indices: np.ndarray,
        relay_artifact: Path,
        config: VisualTransductionConfig | None = None,
    ):
        super().__init__(
            connectome=connectome,
            retinal_indices=retinal_indices,
            relay_artifact=relay_artifact,
            config=config,
        )

    def effective_activity(
        self,
    ) -> np.ndarray:
        #
        # Positive membrane potential is expressed
        # proportionally up to the existing LIF threshold.
        #
        graded = np.clip(
            self.voltage,
            0.0,
            self.config.threshold,
        )

        graded = (
            graded
            / self.config.threshold
        )

        activity = np.maximum(
            self.spikes,
            graded,
        ).astype(
            np.float32,
            copy=False,
        )

        #
        # CRITICAL EXPERIMENTAL CONTROL:
        #
        # R1-R6 remain exactly spike-only.
        #
        # Otherwise the ordinary connectome calculation
        # would introduce graded retinal transmission that
        # is not part of the frozen MQ-2.1 model.
        #
        activity[
            self.retinal_indices
        ] = self.spikes[
            self.retinal_indices
        ]

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
        # Frozen MQ-2.1 retinal pathway remains
        # based on retinal SPIKES, not graded voltage.
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
        # MQ-3.1 EXPERIMENTAL CHANGE:
        #
        # Ordinary non-retinal synapses receive either
        # full spike activity or proportional positive
        # subthreshold membrane activity.
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

        #
        # Frozen MQ-2.1 rule.
        #
        # Because retinal effective activity was explicitly
        # forced back to prior_spikes above, this subtraction
        # exactly removes the same R1-R6 contribution used to
        # calculate direct_retinal_current.
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
