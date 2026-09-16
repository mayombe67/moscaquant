from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np

from brain.physiology_constrained_visual_transduction import (
    PhysiologyConstrainedVisualTransductionRuntime,
)
from brain.visual_transduction import (
    VisualTransductionConfig,
)


@dataclass(frozen=True)
class InterventionSpec:
    """
    MQ-5 runtime intervention.

    attenuation is the FRACTION REMOVED:

        0.00 -> sham / no attenuation
        0.25 -> retain 75% contribution
        0.50 -> retain 50% contribution
        0.75 -> retain 25% contribution
        1.00 -> full silencing

    start_frame and end_frame are inclusive.
    """

    experiment_id: str
    target_model_index: int
    attenuation: float
    start_frame: int
    end_frame: int
    mode: str = "attenuate"

    def __post_init__(self) -> None:
        if not self.experiment_id:
            raise ValueError(
                "experiment_id must be non-empty"
            )

        if self.target_model_index < 0:
            raise ValueError(
                "target_model_index must be >= 0"
            )

        if not 0.0 <= self.attenuation <= 1.0:
            raise ValueError(
                "attenuation must be between 0 and 1"
            )

        if self.start_frame < 0:
            raise ValueError(
                "start_frame must be >= 0"
            )

        if self.end_frame < self.start_frame:
            raise ValueError(
                "end_frame must be >= start_frame"
            )

        allowed_modes = {
            "sham",
            "attenuate",
            "silence",
        }

        if self.mode not in allowed_modes:
            raise ValueError(
                f"unsupported intervention mode: {self.mode}"
            )

        if (
            self.mode == "sham"
            and self.attenuation != 0.0
        ):
            raise ValueError(
                "sham intervention must use attenuation=0"
            )

        if (
            self.mode == "silence"
            and self.attenuation != 1.0
        ):
            raise ValueError(
                "silence intervention must use attenuation=1"
            )

    @property
    def retained_fraction(self) -> float:
        return 1.0 - self.attenuation

    def active_at(
        self,
        frame: int,
    ) -> bool:
        return (
            self.start_frame
            <= frame
            <= self.end_frame
        )


class MQ5InterventionRuntime(
    PhysiologyConstrainedVisualTransductionRuntime
):
    """
    MQ-5 intervention overlay.

    The frozen structural connectome is never modified.

    Intervention is applied to presynaptic effective activity
    immediately before the inherited runtime performs:

        connectome @ effective_activity

    Therefore attenuation changes the selected neuron's
    outgoing ordinary-connectome contribution while preserving
    all frozen weight values.

    Retinal targets are rejected because the frozen R1-R6
    direct retinal pathway is handled separately from ordinary
    effective-activity propagation.
    """

    def __init__(
        self,
        connectome,
        retinal_indices: np.ndarray,
        relay_artifact: Path,
        graded_artifact: Path,
        config: VisualTransductionConfig | None = None,
        interventions: Iterable[
            InterventionSpec
        ] = (),
    ):
        super().__init__(
            connectome=connectome,
            retinal_indices=retinal_indices,
            relay_artifact=relay_artifact,
            graded_artifact=graded_artifact,
            config=config,
        )

        self.interventions = tuple(
            interventions
        )

        self.intervention_frame = 0

        self._validate_interventions()

    def _validate_interventions(
        self,
    ) -> None:
        population_size = int(
            self.population_size
        )

        retinal = set(
            int(x)
            for x in self.retinal_indices
        )

        for spec in self.interventions:
            if (
                spec.target_model_index
                >= population_size
            ):
                raise ValueError(
                    "intervention target outside "
                    f"population: "
                    f"{spec.target_model_index}"
                )

            if (
                spec.target_model_index
                in retinal
            ):
                raise ValueError(
                    "MQ-5 source attenuation currently "
                    "does not support retinal targets: "
                    f"{spec.target_model_index}"
                )

        #
        # Avoid ambiguous compound attenuation.
        # Combined-input experiments use different targets,
        # not two simultaneous specs on one target.
        #
        specs = list(
            self.interventions
        )

        for i, left in enumerate(specs):
            for right in specs[i + 1:]:
                if (
                    left.target_model_index
                    != right.target_model_index
                ):
                    continue

                overlap = not (
                    left.end_frame
                    < right.start_frame
                    or right.end_frame
                    < left.start_frame
                )

                if overlap:
                    raise ValueError(
                        "overlapping interventions on "
                        "the same target are ambiguous: "
                        f"{left.target_model_index}"
                    )

    def set_intervention_frame(
        self,
        frame: int,
    ) -> None:
        frame = int(frame)

        if frame < 0:
            raise ValueError(
                "intervention frame must be >= 0"
            )

        self.intervention_frame = frame

    def active_interventions(
        self,
    ) -> tuple[InterventionSpec, ...]:
        return tuple(
            spec
            for spec in self.interventions
            if spec.active_at(
                self.intervention_frame
            )
        )

    def effective_activity(
        self,
    ) -> np.ndarray:
        activity = (
            super()
            .effective_activity()
            .copy()
        )

        for spec in (
            self.active_interventions()
        ):
            activity[
                spec.target_model_index
            ] *= np.float32(
                spec.retained_fraction
            )

        return activity

    def intervention_metadata(
        self,
    ) -> list[dict]:
        return [
            {
                "experiment_id":
                    spec.experiment_id,

                "target_model_index":
                    spec.target_model_index,

                "mode":
                    spec.mode,

                "attenuation":
                    spec.attenuation,

                "retained_fraction":
                    spec.retained_fraction,

                "start_frame":
                    spec.start_frame,

                "end_frame":
                    spec.end_frame,
            }
            for spec in self.interventions
        ]
