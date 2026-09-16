"""Causal normalization for MoscaQuant market features."""

from collections import deque
from dataclasses import dataclass, field

import numpy as np

from market.features import MarketFeatures


FEATURE_NAMES = (
    "return",
    "momentum",
    "volume_deviation",
    "realized_volatility",
    "spread",
    "order_book_imbalance",
    "return_sign_entropy",
)

# Metadata for the future sensory encoder.
#
# True:
#   sign itself carries descriptive information.
#
# False:
#   feature is magnitude-only and must not acquire an artificial
#   bullish/bearish interpretation.
SIGNED = np.asarray(
    [
        True,   # return
        True,   # momentum
        True,   # volume deviation
        False,  # realized volatility
        False,  # spread
        True,   # order-book imbalance
        False,  # return-sign entropy
    ],
    dtype=bool,
)


@dataclass
class CausalNormalizer:
    """
    Normalize market features using past observations only.

    The current observation is transformed against existing history
    before being added to that history.

    No future observations are used.
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

        self.history = deque(
            self.history,
            maxlen=self.window_size,
        )

    def transform(
        self,
        features: MarketFeatures,
    ) -> np.ndarray:
        """
        Transform one feature vector and then update history.

        During warm-up, zeros are emitted so an insufficient
        normalization history cannot create arbitrary sensory input.
        """

        current = features.as_array().astype(
            np.float64,
            copy=False,
        )

        if current.shape != (len(FEATURE_NAMES),):
            raise ValueError(
                "market feature vector does not match "
                "normalization schema"
            )

        if not np.all(np.isfinite(current)):
            raise ValueError(
                "market features must all be finite"
            )

        if len(self.history) < self.min_history:
            normalized = np.zeros(
                len(FEATURE_NAMES),
                dtype=np.float32,
            )
        else:
            past = np.asarray(
                self.history,
                dtype=np.float64,
            )

            mean = past.mean(axis=0)
            std = past.std(axis=0)

            scale = np.maximum(
                std,
                self.epsilon,
            )

            z = (current - mean) / scale

            normalized = np.tanh(z).astype(
                np.float32
            )

        self.history.append(
            current.copy()
        )

        return normalized
