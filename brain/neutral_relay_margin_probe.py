from __future__ import annotations

from pathlib import Path
import math
import tomllib

import numpy as np
from scipy import sparse

from brain.market_replay import (
    FRAME_COUNT,
    OBSERVATIONS,
    SENSORY_GAIN,
)
from brain.market_temporal import MarketVisionTemporalEncoder
from brain.runtime import LIFRuntime


CONNECTOME = Path(
    "/home/wil/moscaquant-data/processed/connectome-baseline-v1.npz"
)

RETINA = Path(
    "/home/wil/moscaquant-data/processed/visual-r1-r6-map-v1.npz"
)

TERRITORIES = Path(
    "/home/wil/moscaquant-data/processed/market-retinal-territories-v1.npz"
)

RELAY = Path(
    "/home/wil/moscaquant-data/processed/visual-relay-map-v1.npz"
)

CONFIG = Path(
    "config/sensory/visual-transduction-v1.toml"
)


def main():
    with CONFIG.open("rb") as handle:
        config = tomllib.load(handle)

    gain = float(
        config["transduction"]["release_gain"]
    )

    connectome = sparse.load_npz(
        CONNECTOME
    ).tocsr()

    retina = np.load(RETINA)

    retinal_indices = np.asarray(
        retina["neuron_index"],
        dtype=np.int32,
    )

    relay = np.load(RELAY)

    relay_indices = np.asarray(
        relay["neuron_index"],
        dtype=np.int32,
    )

    relay_types = np.asarray(
        relay["type"],
    )

    relay_body_ids = np.asarray(
        relay["body_id"],
        dtype=np.int64,
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

    runtime = LIFRuntime(
        connectome
    )

    encoder = MarketVisionTemporalEncoder(
        TERRITORIES
    )

    decay = math.exp(
        -1.0 / 20.0
    )

    prior_inhibition = np.zeros(
        len(relay_indices),
        dtype=np.float32,
    )

    #
    # Passive release-driven membrane state.
    # No threshold/reset here: we want peak margin.
    #
    voltage = np.zeros(
        len(relay_indices),
        dtype=np.float64,
    )

    peak = np.zeros(
        len(relay_indices),
        dtype=np.float64,
    )

    peak_frame = np.full(
        len(relay_indices),
        -1,
        dtype=np.int32,
    )

    neutral = np.zeros(
        (6, 7),
        dtype=np.float32,
    )

    frame_number = 0

    for _ in range(OBSERVATIONS):
        frames = encoder.encode_sequence(
            neutral,
            frame_count=FRAME_COUNT,
        )

        for stimulus in frames:
            retinal_spikes = runtime.spikes[
                retinal_indices
            ]

            current = (
                relay_from_retina
                @ retinal_spikes
            )

            current = np.asarray(
                current,
                dtype=np.float32,
            ).ravel()

            inhibition = np.maximum(
                -current,
                0.0,
            )

            release = np.maximum(
                prior_inhibition
                - inhibition,
                0.0,
            )

            voltage *= decay
            voltage += (
                release * gain
            )

            improved = voltage > peak

            peak[improved] = voltage[
                improved
            ]

            peak_frame[improved] = (
                frame_number
            )

            runtime.step(
                stimulus * SENSORY_GAIN
            )

            prior_inhibition = inhibition
            frame_number += 1

    print(
        "frozen release gain:",
        gain,
    )

    print()
    print("=" * 72)
    print("NEUTRAL RELAY MARGIN CENSUS")
    print("=" * 72)

    for cell_type in (
        "L1",
        "L2",
        "L3",
        "Lai",
    ):
        mask = (
            relay_types
            == cell_type
        )

        values = peak[
            mask
        ]

        local_indices = np.flatnonzero(
            mask
        )

        best_local = local_indices[
            int(
                np.argmax(values)
            )
        ]

        print()
        print(cell_type)
        print(
            "  neurons:",
            len(values),
        )
        print(
            "  maximum passive voltage:",
            float(
                values.max()
            ),
        )
        print(
            "  median peak voltage:",
            float(
                np.median(values)
            ),
        )
        print(
            "  >= 1.00:",
            int(
                np.count_nonzero(
                    values >= 1.0
                )
            ),
        )
        print(
            "  >= 0.75:",
            int(
                np.count_nonzero(
                    values >= 0.75
                )
            ),
        )
        print(
            "  >= 0.50:",
            int(
                np.count_nonzero(
                    values >= 0.50
                )
            ),
        )
        print(
            "  >= 0.25:",
            int(
                np.count_nonzero(
                    values >= 0.25
                )
            ),
        )
        print(
            "  strongest index:",
            int(
                relay_indices[
                    best_local
                ]
            ),
        )
        print(
            "  strongest body_id:",
            int(
                relay_body_ids[
                    best_local
                ]
            ),
        )
        print(
            "  strongest frame:",
            int(
                peak_frame[
                    best_local
                ]
            ),
        )

    excitatory_mask = np.isin(
        relay_types,
        (
            "L2",
            "L3",
        ),
    )

    excitatory_peak = peak[
        excitatory_mask
    ]

    print()
    print("=" * 72)
    print("EXCITATORY RELAY SUMMARY")
    print("=" * 72)

    print(
        "L2/L3 neurons:",
        len(excitatory_peak),
    )

    print(
        "strongest excitatory peak:",
        float(
            excitatory_peak.max()
        ),
    )

    print(
        "distance to threshold:",
        float(
            1.0
            - excitatory_peak.max()
        ),
    )

    print(
        "excitatory neurons >= 0.75:",
        int(
            np.count_nonzero(
                excitatory_peak
                >= 0.75
            )
        ),
    )

    print(
        "excitatory neurons >= 0.50:",
        int(
            np.count_nonzero(
                excitatory_peak
                >= 0.50
            )
        ),
    )

    print()
    print(
        "NEUTRAL RELAY MARGIN PROBE PASS"
    )


if __name__ == "__main__":
    main()
