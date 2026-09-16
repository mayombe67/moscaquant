"""Deterministic descriptive market features for MoscaQuant."""

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class MarketWindow:
    close: np.ndarray
    volume: np.ndarray
    bid: float
    ask: float
    bid_size: float
    ask_size: float


@dataclass(frozen=True)
class MarketFeatures:
    return_: float
    momentum: float
    volume_deviation: float
    realized_volatility: float
    spread: float
    order_book_imbalance: float
    return_sign_entropy: float

    def as_array(self) -> np.ndarray:
        return np.asarray(
            [
                self.return_,
                self.momentum,
                self.volume_deviation,
                self.realized_volatility,
                self.spread,
                self.order_book_imbalance,
                self.return_sign_entropy,
            ],
            dtype=np.float32,
        )


def return_sign_entropy(returns: np.ndarray) -> float:
    """
    Binary Shannon entropy of non-zero return direction.

    0.0 = completely one-directional
    1.0 = maximally mixed positive/negative directions

    This is descriptive only. It contains no bullish/bearish
    interpretation and provides no trade recommendation.
    """

    returns = np.asarray(returns, dtype=np.float64)

    nonzero = returns[returns != 0.0]

    if len(nonzero) == 0:
        return 0.0

    p_positive = float(
        np.count_nonzero(nonzero > 0.0) / len(nonzero)
    )

    if p_positive == 0.0 or p_positive == 1.0:
        return 0.0

    p_negative = 1.0 - p_positive

    return float(
        -(
            p_positive * np.log2(p_positive)
            + p_negative * np.log2(p_negative)
        )
    )


def compute_features(window: MarketWindow) -> MarketFeatures:
    """
    Compute deterministic descriptive features from one market window.

    No feature produced here contains BUY/SELL/HOLD semantics.
    """

    close = np.asarray(window.close, dtype=np.float64)
    volume = np.asarray(window.volume, dtype=np.float64)

    if close.ndim != 1:
        raise ValueError("close must be one-dimensional")

    if volume.ndim != 1:
        raise ValueError("volume must be one-dimensional")

    if len(close) < 3:
        raise ValueError(
            "market window requires at least three close values"
        )

    if len(close) != len(volume):
        raise ValueError(
            "close and volume must have equal lengths"
        )

    if np.any(close <= 0.0):
        raise ValueError("close values must be positive")

    if np.any(volume < 0.0):
        raise ValueError("volume values cannot be negative")

    if window.bid <= 0.0 or window.ask <= 0.0:
        raise ValueError("bid and ask must be positive")

    if window.ask < window.bid:
        raise ValueError("ask cannot be below bid")

    if window.bid_size < 0.0 or window.ask_size < 0.0:
        raise ValueError(
            "bid_size and ask_size cannot be negative"
        )

    returns = np.diff(np.log(close))

    one_step_return = float(returns[-1])

    momentum = float(
        np.log(close[-1] / close[0])
    )

    volume_mean = float(volume.mean())

    if volume_mean == 0.0:
        volume_deviation = 0.0
    else:
        volume_deviation = float(
            (volume[-1] - volume_mean) / volume_mean
        )

    realized_volatility = float(
        np.sqrt(np.mean(returns * returns))
    )

    midpoint = (window.bid + window.ask) / 2.0

    spread = float(
        (window.ask - window.bid) / midpoint
    )

    book_total = window.bid_size + window.ask_size

    if book_total == 0.0:
        order_book_imbalance = 0.0
    else:
        order_book_imbalance = float(
            (window.bid_size - window.ask_size)
            / book_total
        )

    entropy = return_sign_entropy(returns)

    return MarketFeatures(
        return_=one_step_return,
        momentum=momentum,
        volume_deviation=volume_deviation,
        realized_volatility=realized_volatility,
        spread=spread,
        order_book_imbalance=order_book_imbalance,
        return_sign_entropy=entropy,
    )
