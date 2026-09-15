from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
from scipy import sparse

from brain.market_temporal import MarketVisionTemporalEncoder
from brain.runtime import LIFRuntime
from market.features import MarketWindow, compute_features
from market.normalization import CausalNormalizer


ASSETS = (
    "BTC",
    "ETH",
    "SOL",
    "XRP",
    "HBAR",
    "DOGE",
)

MARKET_WINDOW = 8
OBSERVATIONS = 12
FRAME_COUNT = 16
SENSORY_GAIN = 12.626497881530927


def synthetic_series(
    condition: str,
    asset_index: int,
):
    """
    Deterministic synthetic market history.

    Conditions A and B share the entire normalizer warm-up history.
    They diverge only after eight completed observations.
    """

    if condition not in {"A", "B"}:
        raise ValueError("condition must be A or B")

    points = OBSERVATIONS + MARKET_WINDOW - 1

    # Observation 8 ends at source index 15.
    # Everything before index 15 is identical between A and B.
    branch_index = MARKET_WINDOW + 8 - 1

    scale = 1.0 + 0.08 * asset_index

    base_prices = (
        60000.0,
        3000.0,
        150.0,
        0.60,
        0.20,
        0.15,
    )

    close = np.empty(
        points,
        dtype=np.float64,
    )

    volume = np.empty(
        points,
        dtype=np.float64,
    )

    spread_fraction = np.empty(
        points,
        dtype=np.float64,
    )

    imbalance = np.empty(
        points,
        dtype=np.float64,
    )

    close[0] = base_prices[
        asset_index
    ]

    volume[0] = 1000.0 * scale

    spread_fraction[0] = 0.001
    imbalance[0] = 0.0

    for i in range(1, points):

        if i < branch_index:
            # Shared baseline history.
            r = (
                0.00035 * np.sin(i * 0.7)
                + 0.00015
                * (-1.0 if i % 2 else 1.0)
            )

            volume_factor = (
                1.0
                + 0.04 * np.sin(i * 0.5)
            )

            spread = (
                0.001
                + 0.00008 * np.sin(i * 0.4)
            )

            book_imbalance = (
                0.08 * np.sin(i * 0.6)
            )

        elif condition == "A":
            # Persistent directional regime.
            j = i - branch_index

            r = (
                0.0010
                + 0.00025 * j
            ) * scale

            volume_factor = (
                1.15
                + 0.10 * j
            )

            spread = (
                0.0009
                + 0.00003 * j
            )

            book_imbalance = (
                0.18
                + 0.04 * j
            )

        else:
            # Choppy / directionally disordered regime.
            j = i - branch_index

            direction = (
                1.0
                if j % 2 == 0
                else -1.0
            )

            r = (
                direction
                * (
                    0.0015
                    + 0.00035 * j
                )
                * scale
            )

            volume_factor = (
                1.35
                if j % 2 == 0
                else 0.82
            )

            spread = (
                0.0014
                + 0.00020 * (j % 3)
            )

            book_imbalance = (
                direction
                * (
                    0.28
                    + 0.04 * j
                )
            )

        close[i] = (
            close[i - 1]
            * np.exp(r)
        )

        volume[i] = (
            1000.0
            * scale
            * volume_factor
        )

        spread_fraction[i] = spread

        imbalance[i] = np.clip(
            book_imbalance,
            -0.95,
            0.95,
        )

    return (
        close,
        volume,
        spread_fraction,
        imbalance,
    )


def market_window_at(
    series,
    observation: int,
):
    close, volume, spread_fraction, imbalance = series

    start = observation
    end = observation + MARKET_WINDOW

    close_window = close[start:end]
    volume_window = volume[start:end]

    last_index = end - 1
    last = float(
        close[last_index]
    )

    spread = float(
        spread_fraction[
            last_index
        ]
    )

    bid = last * (
        1.0 - spread / 2.0
    )

    ask = last * (
        1.0 + spread / 2.0
    )

    book = float(
        imbalance[last_index]
    )

    bid_size = 100.0 * (
        1.0 + book
    )

    ask_size = 100.0 * (
        1.0 - book
    )

    return MarketWindow(
        close=close_window,
        volume=volume_window,
        bid=bid,
        ask=ask,
        bid_size=bid_size,
        ask_size=ask_size,
    )


def digest_array(
    digest,
    array: np.ndarray,
):
    digest.update(
        np.ascontiguousarray(
            array
        ).tobytes()
    )


def run_replay(
    condition: str,
    connectome,
    territory_artifact: Path,
):
    # Six independent causal histories.
    normalizers = [
        CausalNormalizer(
            window_size=64,
            min_history=8,
        )
        for _ in ASSETS
    ]

    series = [
        synthetic_series(
            condition,
            asset_index,
        )
        for asset_index in range(
            len(ASSETS)
        )
    ]

    encoder = (
        MarketVisionTemporalEncoder(
            territory_artifact
        )
    )

    # Fresh brain state every replay.
    runtime = LIFRuntime(
        connectome
    )

    normalized_hash = hashlib.sha256()
    retinal_hash = hashlib.sha256()
    neural_hash = hashlib.sha256()

    spike_counts = []

    for observation in range(
        OBSERVATIONS
    ):
        normalized = np.empty(
            (6, 7),
            dtype=np.float32,
        )

        for asset_index in range(6):
            window = market_window_at(
                series[asset_index],
                observation,
            )

            features = compute_features(
                window
            )

            normalized[
                asset_index
            ] = normalizers[
                asset_index
            ].transform(
                features
            )

        digest_array(
            normalized_hash,
            normalized,
        )

        retinal = (
            encoder.encode_sequence(
                normalized,
                frame_count=FRAME_COUNT,
            )
        )

        digest_array(
            retinal_hash,
            retinal,
        )

        for frame in retinal:
            spikes = runtime.step(
                frame * SENSORY_GAIN
            )

            packed = np.packbits(
                spikes.astype(
                    np.bool_
                )
            )

            digest_array(
                neural_hash,
                packed,
            )

            spike_counts.append(
                int(
                    np.count_nonzero(
                        spikes
                    )
                )
            )

    return {
        "condition": condition,
        "normalized_hash": (
            normalized_hash.hexdigest()
        ),
        "retinal_hash": (
            retinal_hash.hexdigest()
        ),
        "neural_hash": (
            neural_hash.hexdigest()
        ),
        "spike_counts": spike_counts,
        "total_spikes": int(
            sum(spike_counts)
        ),
        "active_frames": int(
            np.count_nonzero(
                np.asarray(
                    spike_counts
                )
            )
        ),
        "final_voltage_hash": (
            hashlib.sha256(
                runtime.voltage.tobytes()
            ).hexdigest()
        ),
        "final_voltage_max": float(
            runtime.voltage.max()
        ),
    }


def summarize(result):
    print(
        "condition:",
        result["condition"],
    )

    print(
        "normalized sha256:",
        result[
            "normalized_hash"
        ],
    )

    print(
        "retinal sha256:",
        result[
            "retinal_hash"
        ],
    )

    print(
        "neural sha256:",
        result[
            "neural_hash"
        ],
    )

    print(
        "final voltage sha256:",
        result[
            "final_voltage_hash"
        ],
    )

    print(
        "total spikes:",
        result[
            "total_spikes"
        ],
    )

    print(
        "active frames:",
        result[
            "active_frames"
        ],
    )

    print(
        "final max voltage:",
        result[
            "final_voltage_max"
        ],
    )


def main():
    connectome_path = Path(
        "/home/wil/moscaquant-data/"
        "processed/"
        "connectome-baseline-v1.npz"
    )

    territory_path = Path(
        "/home/wil/moscaquant-data/"
        "processed/"
        "market-retinal-territories-v1.npz"
    )

    print(
        "loading frozen connectome..."
    )

    connectome = sparse.load_npz(
        connectome_path
    )

    print(
        "shape:",
        connectome.shape,
        "nnz:",
        connectome.nnz,
    )

    print()
    print("RUN A1")

    a1 = run_replay(
        "A",
        connectome,
        territory_path,
    )

    summarize(a1)

    print()
    print("RUN A2")

    a2 = run_replay(
        "A",
        connectome,
        territory_path,
    )

    summarize(a2)

    print()
    print("RUN B")

    b = run_replay(
        "B",
        connectome,
        territory_path,
    )

    summarize(b)

    print()
    print("=" * 72)
    print("REPLAY CHECKS")
    print("=" * 72)

    assert (
        a1["normalized_hash"]
        == a2["normalized_hash"]
    )

    assert (
        a1["retinal_hash"]
        == a2["retinal_hash"]
    )

    assert (
        a1["neural_hash"]
        == a2["neural_hash"]
    )

    assert (
        a1["final_voltage_hash"]
        == a2["final_voltage_hash"]
    )

    assert (
        a1["spike_counts"]
        == a2["spike_counts"]
    )

    print(
        "A1 == A2 exact replay: PASS"
    )

    assert (
        a1["normalized_hash"]
        != b["normalized_hash"]
    )

    print(
        "A != B normalized percept: PASS"
    )

    assert (
        a1["retinal_hash"]
        != b["retinal_hash"]
    )

    print(
        "A != B retinal stream: PASS"
    )

    if (
        a1["neural_hash"]
        != b["neural_hash"]
        or
        a1["final_voltage_hash"]
        != b["final_voltage_hash"]
    ):
        print(
            "A != B neural trajectory: PASS"
        )
    else:
        raise AssertionError(
            "different retinal histories "
            "produced identical MQ-001 "
            "neural state"
        )

    different_frames = int(
        np.count_nonzero(
            np.asarray(
                a1["spike_counts"]
            )
            != np.asarray(
                b["spike_counts"]
            )
        )
    )

    print(
        "frames with different "
        "spike counts:",
        different_frames,
    )

    print()
    print(
        "MQ-2 SYNTHETIC MARKET "
        "AWARENESS PASS"
    )


if __name__ == "__main__":
    main()
