"""Robust causal normalization for MoscaQuant encoding-robustness tests."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field

import numpy as np

from market.features import MarketFeatures
from market.normalization import FEATURE_NAMES


MAD_CONSISTENCY_FACTOR = 1.4826


@dataclass
class RobustCausalNormalizer:
    """
    Normalize market features using past observations only.

    Location:
        rolling median

    Scale:
        1.4826 * rolling median absolute deviation

    The current observation is transformed before it is appended to
    history.

    During warm-up, zeros are emitted exactly as in the existing causal
    normalizer.
    """

    window_size: int = 64
    min_history: int = 8
    epsilon: float = 1e-8
    history: deque = field(default_factory=deque)

    def __post_init__(self) -> None:
        if self.window_size < 2:
            raise ValueError(
                "window_size must be at least 2"
            )

        if self.min_history < 2:
            raise ValueError(
                "min_history must be at least 2"
            )

        if self.min_history > self.window_size:
            raise ValueError(
                "min_history cannot exceed window_size"
            )

        if self.epsilon <= 0.0:
            raise ValueError(
                "epsilon must be positive"
            )

        self.history = deque(
            self.history,
            maxlen=self.window_size,
        )

    def transform(
        self,
        features: MarketFeatures,
    ) -> np.ndarray:
        current = features.as_array().astype(
            np.float64,
            copy=False,
        )

        if current.shape != (
            len(FEATURE_NAMES),
        ):
            raise ValueError(
                "market feature vector does not match "
                "normalization schema"
            )

        if not np.all(
            np.isfinite(current)
        ):
            raise ValueError(
                "market features must all be finite"
            )

        if (
            len(self.history)
            < self.min_history
        ):
            normalized = np.zeros(
                len(FEATURE_NAMES),
                dtype=np.float32,
            )

        else:
            past = np.asarray(
                self.history,
                dtype=np.float64,
            )

            median = np.median(
                past,
                axis=0,
            )

            absolute_deviation = np.abs(
                past - median
            )

            mad = np.median(
                absolute_deviation,
                axis=0,
            )

            scale = np.maximum(
                MAD_CONSISTENCY_FACTOR
                * mad,
                self.epsilon,
            )

            robust_z = (
                current - median
            ) / scale

            normalized = np.tanh(
                robust_z
            ).astype(
                np.float32
            )

        self.history.append(
            current.copy()
        )

        return normalized
