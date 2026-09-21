from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from brain.market_temporal import (
    JITTER_PATTERN,
    MOMENTUM,
    REALIZED_VOLATILITY,
    RETURN_SIGN_ENTROPY,
    MarketVisionTemporalEncoder,
)


ARM_A = "A"
ARM_B = "B"
ARM_C = "C"
ARM_D = "D"
ARM_E = "E"

FIXED_CYCLES_B = 2.5
JITTER_MULTIPLIER_C = 0.0
MOTION_WEIGHT_E = 1.0


@dataclass(frozen=True)
class EncodingVariant:
    arm: str
    asset_mapping: tuple[int, ...] | None = None

    def __post_init__(self) -> None:
        if self.arm not in {ARM_A, ARM_B, ARM_C, ARM_D, ARM_E}:
            raise ValueError(f"unsupported MQ-5.ER arm: {self.arm}")

        if self.arm == ARM_D:
            if self.asset_mapping is None:
                raise ValueError("Arm D requires asset_mapping")
            if sorted(self.asset_mapping) != list(range(6)):
                raise ValueError("Arm D asset_mapping must be a permutation of 0..5")
        elif self.asset_mapping is not None:
            raise ValueError("asset_mapping is only valid for Arm D")


def balanced_asset_territory_mappings() -> tuple[tuple[str, tuple[int, ...]], ...]:
    identity = np.arange(6, dtype=np.int32)
    reversed_order = identity[::-1].copy()

    mappings: list[tuple[str, tuple[int, ...]]] = []

    for shift in range(6):
        mapping = tuple(int(x) for x in np.roll(identity, -shift))
        mappings.append((f"rotation-{shift}", mapping))

    for shift in range(6):
        mapping = tuple(int(x) for x in np.roll(reversed_order, -shift))
        mappings.append((f"reverse-rotation-{shift}", mapping))

    counts = np.zeros((6, 6), dtype=np.int32)

    for _, mapping in mappings:
        if sorted(mapping) != list(range(6)):
            raise RuntimeError("invalid balanced mapping permutation")

        for territory_index, asset_index in enumerate(mapping):
            counts[asset_index, territory_index] += 1

    if not np.all(counts == 2):
        raise RuntimeError("balanced mapping family lost 2x coverage invariant")

    return tuple(mappings)


class MQ5EREncodingVariantEncoder(MarketVisionTemporalEncoder):
    """
    Encoding-only MQ-5.ER implementation.

    This class changes only the preregistered market-to-sensory translation
    component for Arms B-E. It does not contain, call, or modify a neural
    runtime.

    Arm A must remain byte-identical to MarketVisionTemporalEncoder for the
    same spatial encoder state and input feature matrix.
    """

    def __init__(
        self,
        territory_artifact: Path,
        variant: EncodingVariant,
        population_size: int = 166_700,
        base_energy: float = 1.0,
    ):
        super().__init__(
            territory_artifact=territory_artifact,
            population_size=population_size,
            base_energy=base_energy,
        )
        self.variant = variant

    @staticmethod
    def _fixed_jitter(frame_count: int) -> np.ndarray:
        repeats = int(np.ceil(frame_count / len(JITTER_PATTERN)))
        return np.tile(JITTER_PATTERN, repeats)[:frame_count]

    def _mq5_er_temporal_gate(
        self,
        volatility: float,
        entropy: float,
        frame_count: int,
    ) -> np.ndarray:
        volatility_mag = self._to_magnitude(volatility)
        entropy_mag = self._to_magnitude(entropy)

        if self.variant.arm == ARM_B:
            cycles = FIXED_CYCLES_B
        else:
            cycles = 1.0 + 3.0 * volatility_mag

        frame = np.arange(frame_count, dtype=np.float32)

        regular_phase = (
            2.0
            * np.pi
            * cycles
            * frame
            / frame_count
        )

        jitter = self._fixed_jitter(frame_count)

        if self.variant.arm == ARM_C:
            jitter_multiplier = JITTER_MULTIPLIER_C
        else:
            jitter_multiplier = entropy_mag

        irregular_phase = (
            regular_phase
            + jitter_multiplier
            * np.pi
            * jitter
        )

        gate = (
            0.25
            + 0.75
            * (
                0.5
                + 0.5 * np.sin(irregular_phase)
            )
        ).astype(np.float32)

        mean = float(gate.mean())
        if mean <= 0.0:
            raise RuntimeError("temporal gate has zero mean")

        gate /= mean
        return gate

    def encode_sequence(
        self,
        features: np.ndarray,
        frame_count: int = 16,
    ) -> np.ndarray:
        values = self.spatial._validate_features(features)

        if self.variant.arm == ARM_D:
            values = values[
                np.asarray(self.variant.asset_mapping, dtype=np.int32)
            ]

        if frame_count < 2:
            raise ValueError("frame_count must be at least 2")

        base = self.spatial.encode(values)

        sequence = np.zeros(
            (frame_count, self.population_size),
            dtype=np.float32,
        )

        motion_phase = self._motion_phase(frame_count)

        for row_index, territory in enumerate(range(1, 7)):
            geometry = self.spatial.geometries[territory]

            base_weights = base[
                geometry.neuron_index
            ].astype(np.float32, copy=True)

            momentum = float(values[row_index, MOMENTUM])
            volatility = float(values[row_index, REALIZED_VOLATILITY])
            entropy = float(values[row_index, RETURN_SIGN_ENTROPY])

            if self.variant.arm == ARM_A:
                gate = super()._temporal_gate(
                    volatility=volatility,
                    entropy=entropy,
                    frame_count=frame_count,
                )
            else:
                gate = self._mq5_er_temporal_gate(
                    volatility=volatility,
                    entropy=entropy,
                    frame_count=frame_count,
                )

            territory_frames = np.empty(
                (frame_count, len(base_weights)),
                dtype=np.float32,
            )

            for frame_index in range(frame_count):
                if self.variant.arm == ARM_E:
                    motion_weight = np.ones_like(
                        geometry.x,
                        dtype=np.float32,
                    )
                else:
                    motion_weight = (
                        1.0
                        + 0.25
                        * momentum
                        * motion_phase[frame_index]
                        * geometry.x
                    )
                    motion_weight = np.clip(
                        motion_weight,
                        0.0,
                        None,
                    ).astype(np.float32)

                frame_weights = base_weights * motion_weight

                total = float(frame_weights.sum())
                if total <= 0.0:
                    raise RuntimeError("motion frame has zero energy")

                frame_weights *= self.base_energy / total
                frame_weights *= gate[frame_index]

                territory_frames[frame_index] = frame_weights

            frame_energy = territory_frames.sum(axis=1)
            mean_energy = float(frame_energy.mean())

            territory_frames *= self.base_energy / mean_energy

            sequence[
                :,
                geometry.neuron_index,
            ] = territory_frames

        return sequence
