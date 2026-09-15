from __future__ import annotations

from pathlib import Path

import numpy as np

from brain.market_sensory import (
    MarketVisionSpatialEncoder,
)


MOMENTUM = 1
REALIZED_VOLATILITY = 3
RETURN_SIGN_ENTROPY = 6


# Fixed deterministic timing perturbation.
#
# This is deliberately not random. It simply provides a reproducible
# irregular sequence that entropy can progressively expose.
JITTER_PATTERN = np.array(
    [
        0.00,
        0.37,
        -0.21,
        0.14,
        -0.43,
        0.29,
        -0.08,
        0.46,
        -0.31,
        0.11,
        -0.39,
        0.24,
        -0.16,
        0.41,
        -0.27,
        0.06,
    ],
    dtype=np.float32,
)


class MarketVisionTemporalEncoder:
    """
    Deterministic temporal wrapper around the frozen spatial encoder.

    Temporal features alter motion and timing while preserving mean
    integrated sensory energy per territory across the observation window.
    """

    def __init__(
        self,
        territory_artifact: Path,
        population_size: int = 166_700,
        base_energy: float = 1.0,
    ):
        self.spatial = MarketVisionSpatialEncoder(
            territory_artifact=territory_artifact,
            population_size=population_size,
            base_energy=base_energy,
        )

        self.population_size = population_size
        self.base_energy = float(base_energy)

    @staticmethod
    def _to_magnitude(value: float) -> float:
        """
        Convert causal normalized deviation [-1, 1] to magnitude [0, 1].

        -1 = unusually low
         0 = recent baseline
        +1 = unusually high
        """
        return (float(value) + 1.0) / 2.0

    @staticmethod
    def _motion_phase(frame_count: int) -> np.ndarray:
        """
        Centered temporal trajectory in [-1, 1].

        Mean is approximately zero, so motion direction does not create
        systematic energy bias.
        """
        if frame_count < 2:
            raise ValueError(
                "frame_count must be at least 2"
            )

        return np.linspace(
            -1.0,
            1.0,
            frame_count,
            dtype=np.float32,
        )

    @staticmethod
    def _jitter(frame_count: int) -> np.ndarray:
        repeats = int(
            np.ceil(
                frame_count / len(JITTER_PATTERN)
            )
        )

        tiled = np.tile(
            JITTER_PATTERN,
            repeats,
        )

        return tiled[:frame_count]

    def _temporal_gate(
        self,
        volatility: float,
        entropy: float,
        frame_count: int,
    ) -> np.ndarray:
        """
        Build deterministic pulse timing.

        Volatility controls cadence.
        Entropy controls irregularity.

        The final gate always has mean 1.0.
        """

        volatility_mag = self._to_magnitude(
            volatility
        )

        entropy_mag = self._to_magnitude(
            entropy
        )

        # 1 to 4 pulse cycles across the observation window.
        cycles = 1.0 + 3.0 * volatility_mag

        frame = np.arange(
            frame_count,
            dtype=np.float32,
        )

        regular_phase = (
            2.0
            * np.pi
            * cycles
            * frame
            / frame_count
        )

        jitter = self._jitter(
            frame_count
        )

        irregular_phase = (
            regular_phase
            + entropy_mag
            * np.pi
            * jitter
        )

        # Positive gate: never turns the sensory territory fully off.
        gate = (
            0.25
            + 0.75
            * (
                0.5
                + 0.5
                * np.sin(
                    irregular_phase
                )
            )
        ).astype(
            np.float32
        )

        mean = float(
            gate.mean()
        )

        if mean <= 0.0:
            raise RuntimeError(
                "temporal gate has zero mean"
            )

        # Critical fairness rule.
        gate /= mean

        return gate

    def encode_sequence(
        self,
        features: np.ndarray,
        frame_count: int = 16,
    ) -> np.ndarray:
        values = self.spatial._validate_features(
            features
        )

        if frame_count < 2:
            raise ValueError(
                "frame_count must be at least 2"
            )

        base = self.spatial.encode(
            values
        )

        sequence = np.zeros(
            (
                frame_count,
                self.population_size,
            ),
            dtype=np.float32,
        )

        motion_phase = self._motion_phase(
            frame_count
        )

        for row_index, territory in enumerate(
            range(1, 7)
        ):
            geometry = self.spatial.geometries[
                territory
            ]

            base_weights = base[
                geometry.neuron_index
            ].astype(
                np.float32,
                copy=True,
            )

            momentum = float(
                values[
                    row_index,
                    MOMENTUM,
                ]
            )

            volatility = float(
                values[
                    row_index,
                    REALIZED_VOLATILITY,
                ]
            )

            entropy = float(
                values[
                    row_index,
                    RETURN_SIGN_ENTROPY,
                ]
            )

            gate = self._temporal_gate(
                volatility=volatility,
                entropy=entropy,
                frame_count=frame_count,
            )

            territory_frames = np.empty(
                (
                    frame_count,
                    len(base_weights),
                ),
                dtype=np.float32,
            )

            for frame_index in range(
                frame_count
            ):
                # Momentum produces coherent horizontal movement.
                #
                # Positive and negative values push the distribution in
                # opposite directions over time.
                motion_weight = (
                    1.0
                    + 0.25
                    * momentum
                    * motion_phase[
                        frame_index
                    ]
                    * geometry.x
                )

                motion_weight = np.clip(
                    motion_weight,
                    0.0,
                    None,
                ).astype(
                    np.float32
                )

                frame_weights = (
                    base_weights
                    * motion_weight
                )

                total = float(
                    frame_weights.sum()
                )

                if total <= 0.0:
                    raise RuntimeError(
                        "motion frame has zero energy"
                    )

                # Preserve spatial energy before pulse modulation.
                frame_weights *= (
                    self.base_energy
                    / total
                )

                frame_weights *= gate[
                    frame_index
                ]

                territory_frames[
                    frame_index
                ] = frame_weights

            # Final numerical correction:
            # mean territory energy across the whole window must equal
            # base_energy exactly within float tolerance.
            frame_energy = territory_frames.sum(
                axis=1
            )

            mean_energy = float(
                frame_energy.mean()
            )

            territory_frames *= (
                self.base_energy
                / mean_energy
            )

            sequence[
                :,
                geometry.neuron_index,
            ] = territory_frames

        return sequence
