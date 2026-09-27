from __future__ import annotations

import numpy as np


BODY_RESPONDERS = np.asarray(
    [
        137122,
        317,
        126002,
    ],
    dtype=np.int32,
)

FRONTIER_INDICES = np.asarray(
    [
        7,
        72,
        129,
        411,
        470,
        1472,
        1574,
        1662,
        1919,
        2009,
        2327,
        3712,
        4068,
        14273,
        16349,
        18196,
        130134,
        131527,
    ],
    dtype=np.int32,
)


class ReadoutRefusal(RuntimeError):
    pass


def validate_readout_indices(population_size: int) -> None:
    if not isinstance(population_size, int):
        raise TypeError("population_size must be int")

    if population_size <= 0:
        raise ValueError("population_size must be positive")

    if BODY_RESPONDERS.shape != (3,):
        raise ReadoutRefusal("BODY responder coordinate drift")

    if FRONTIER_INDICES.shape != (18,):
        raise ReadoutRefusal("frontier coordinate drift")

    all_indices = np.concatenate(
        (
            BODY_RESPONDERS,
            FRONTIER_INDICES,
        )
    )

    if len(np.unique(all_indices)) != 21:
        raise ReadoutRefusal(
            "SQ-08 mechanistic readout contains duplicate model indices"
        )

    if np.any(all_indices < 0):
        raise ReadoutRefusal(
            "SQ-08 mechanistic readout contains negative index"
        )

    if np.any(all_indices >= population_size):
        raise ReadoutRefusal(
            "SQ-08 mechanistic readout index exceeds runtime population"
        )


def capture_mechanistic_state(
    *,
    voltage: np.ndarray,
    spikes: np.ndarray,
) -> dict[str, np.ndarray]:
    voltage = np.asarray(voltage)
    spikes = np.asarray(spikes)

    if voltage.ndim != 1:
        raise ReadoutRefusal(
            "runtime voltage must be one-dimensional"
        )

    if spikes.ndim != 1:
        raise ReadoutRefusal(
            "runtime spikes must be one-dimensional"
        )

    if voltage.shape != spikes.shape:
        raise ReadoutRefusal(
            "runtime voltage/spike population shape mismatch"
        )

    validate_readout_indices(int(voltage.shape[0]))

    if not np.all(np.isfinite(voltage)):
        raise ReadoutRefusal(
            "runtime voltage contains non-finite state"
        )

    if not np.all(np.isfinite(spikes)):
        raise ReadoutRefusal(
            "runtime spikes contains non-finite state"
        )

    body_voltage = np.asarray(
        voltage[BODY_RESPONDERS],
        dtype=np.float32,
    ).copy()

    body_spikes = np.asarray(
        spikes[BODY_RESPONDERS] > 0,
        dtype=np.uint8,
    ).copy()

    frontier_voltage = np.asarray(
        voltage[FRONTIER_INDICES],
        dtype=np.float32,
    ).copy()

    frontier_spikes = np.asarray(
        spikes[FRONTIER_INDICES] > 0,
        dtype=np.uint8,
    ).copy()

    expected = {
        "body_responder_voltage": (
            body_voltage,
            (3,),
            np.dtype(np.float32),
        ),
        "body_responder_spikes": (
            body_spikes,
            (3,),
            np.dtype(np.uint8),
        ),
        "frontier_voltage": (
            frontier_voltage,
            (18,),
            np.dtype(np.float32),
        ),
        "frontier_spikes": (
            frontier_spikes,
            (18,),
            np.dtype(np.uint8),
        ),
    }

    result = {}

    for key, (value, shape, dtype) in expected.items():
        if value.shape != shape:
            raise ReadoutRefusal(
                f"SQ-08 mechanistic shape drift: {key}"
            )

        if value.dtype != dtype:
            raise ReadoutRefusal(
                f"SQ-08 mechanistic dtype drift: {key}"
            )

        result[key] = value

    return result
