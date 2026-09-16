from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from scipy import sparse

from brain.market_replay import (
    FRAME_COUNT,
    OBSERVATIONS,
    SENSORY_GAIN,
)
from brain.market_temporal import (
    MarketVisionTemporalEncoder,
)
from brain.runtime import LIFRuntime


CONNECTOME = Path(
    "/home/wil/moscaquant-data/processed/"
    "connectome-baseline-v1.npz"
)

RETINA = Path(
    "/home/wil/moscaquant-data/processed/"
    "visual-r1-r6-map-v1.npz"
)

TERRITORIES = Path(
    "/home/wil/moscaquant-data/processed/"
    "market-retinal-territories-v1.npz"
)

RELAY = Path(
    "/home/wil/moscaquant-data/processed/"
    "visual-relay-map-v1.npz"
)


DT_MS = 1.0
TAU_MS = 20.0
THRESHOLD = 1.0


def main():
    print(
        "loading frozen MQ-001 connectome..."
    )

    connectome = sparse.load_npz(
        CONNECTOME
    ).tocsr()

    retina = np.load(
        RETINA
    )

    retinal_indices = np.asarray(
        retina["neuron_index"],
        dtype=np.int32,
    )

    relay = np.load(
        RELAY
    )

    relay_indices = np.asarray(
        relay["neuron_index"],
        dtype=np.int32,
    )

    relay_body_ids = np.asarray(
        relay["body_id"],
        dtype=np.int64,
    )

    relay_types = np.asarray(
        relay["type"],
    )

    relay_from_retina = (
        connectome[
            relay_indices,
            :
        ][
            :,
            retinal_indices
        ].tocsr()
    )

    if (
        relay_from_retina.nnz
        and np.any(
            relay_from_retina.data > 0
        )
    ):
        raise RuntimeError(
            "positive retinal relay edge"
        )

    encoder = (
        MarketVisionTemporalEncoder(
            TERRITORIES
        )
    )

    #
    # Baseline MQ-001 is used only to generate the
    # frozen neutral R1-R6 spike sequence.
    #
    runtime = LIFRuntime(
        connectome
    )

    decay = math.exp(
        -DT_MS / TAU_MS
    )

    previous_inhibition = np.zeros(
        len(relay_indices),
        dtype=np.float32,
    )

    #
    # Passive relay membrane state with gain = 1.
    #
    passive_voltage = np.zeros(
        len(relay_indices),
        dtype=np.float64,
    )

    peak_voltage = 0.0
    peak_frame = None
    peak_local_index = None

    frame_number = 0
    total_release = 0.0
    release_frames = 0

    neutral = np.zeros(
        (6, 7),
        dtype=np.float32,
    )

    for _ in range(
        OBSERVATIONS
    ):
        retinal_frames = (
            encoder.encode_sequence(
                neutral,
                frame_count=FRAME_COUNT,
            )
        )

        for stimulus in retinal_frames:
            retinal_spikes = (
                runtime.spikes[
                    retinal_indices
                ]
            )

            direct_current = (
                relay_from_retina
                @ retinal_spikes
            )

            direct_current = np.asarray(
                direct_current,
                dtype=np.float32,
            ).ravel()

            inhibition = np.maximum(
                -direct_current,
                0.0,
            )

            release = np.maximum(
                previous_inhibition
                - inhibition,
                0.0,
            )

            release_sum = float(
                release.sum()
            )

            total_release += (
                release_sum
            )

            if release_sum > 0:
                release_frames += 1

            passive_voltage *= decay

            passive_voltage += release

            local_index = int(
                np.argmax(
                    passive_voltage
                )
            )

            frame_peak = float(
                passive_voltage[
                    local_index
                ]
            )

            if frame_peak > peak_voltage:
                peak_voltage = frame_peak
                peak_frame = frame_number
                peak_local_index = (
                    local_index
                )

            runtime.step(
                stimulus
                * SENSORY_GAIN
            )

            previous_inhibition = (
                inhibition
            )

            frame_number += 1

    if peak_voltage <= 0:
        raise RuntimeError(
            "neutral sequence produced no "
            "release-from-inhibition signal"
        )

    release_gain = (
        THRESHOLD
        / peak_voltage
    )

    global_index = int(
        relay_indices[
            peak_local_index
        ]
    )

    body_id = int(
        relay_body_ids[
            peak_local_index
        ]
    )

    cell_type = str(
        relay_types[
            peak_local_index
        ]
    )

    print()
    print("=" * 72)
    print(
        "MQ-2.1 NEUTRAL RELEASE CALIBRATION"
    )
    print("=" * 72)

    print(
        "frames:",
        frame_number,
    )

    print(
        "release-active frames:",
        release_frames,
    )

    print(
        "integrated release:",
        total_release,
    )

    print()
    print(
        "passive unscaled peak:",
        peak_voltage,
    )

    print(
        "peak frame:",
        peak_frame,
    )

    print(
        "peak relay population index:",
        global_index,
    )

    print(
        "peak body_id:",
        body_id,
    )

    print(
        "peak type:",
        cell_type,
    )

    print()
    print(
        "LIF threshold:",
        THRESHOLD,
    )

    print(
        "derived release_gain_v1:",
        release_gain,
    )

    print()
    print(
        "Calibration rule:"
    )

    print(
        "minimum gain such that the strongest "
        "neutral release-integrating relay reaches "
        "the existing +1 LIF threshold"
    )

    print()
    print(
        "No A/B market response used."
    )

    print(
        "No P&L or decoder used."
    )

    print()
    print(
        "MQ-2.1 NEUTRAL CALIBRATION PASS"
    )


if __name__ == "__main__":
    main()
