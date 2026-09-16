from __future__ import annotations

import hashlib
from pathlib import Path
import tomllib

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
from brain.visual_transduction import (
    VisualTransductionConfig,
    VisualTransductionRuntime,
)


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

CONFIG = Path(
    "config/sensory/"
    "visual-transduction-v1.toml"
)


def digest_array(
    digest,
    array,
):
    digest.update(
        np.ascontiguousarray(
            array
        ).tobytes()
    )


def run_once(
    connectome,
    retinal_indices,
    relay_indices,
    relay_types,
    release_gain,
):
    encoder = MarketVisionTemporalEncoder(
        TERRITORIES
    )

    runtime = VisualTransductionRuntime(
        connectome=connectome,
        retinal_indices=retinal_indices,
        relay_artifact=RELAY,
        config=VisualTransductionConfig(
            release_gain=release_gain,
        ),
    )

    population_size = (
        connectome.shape[0]
    )

    retinal_mask = np.zeros(
        population_size,
        dtype=bool,
    )

    retinal_mask[
        retinal_indices
    ] = True

    relay_mask = np.zeros(
        population_size,
        dtype=bool,
    )

    relay_mask[
        relay_indices
    ] = True

    other_mask = ~(
        retinal_mask
        | relay_mask
    )

    class_masks = {
        cell_type: (
            relay_types
            == cell_type
        )
        for cell_type in (
            "L1",
            "L2",
            "L3",
            "Lai",
        )
    }

    neutral = np.zeros(
        (6, 7),
        dtype=np.float32,
    )

    neural_hash = hashlib.sha256()

    retinal_spikes = 0
    relay_spikes = 0
    other_spikes = 0

    retinal_unique = np.zeros(
        population_size,
        dtype=bool,
    )

    relay_unique = np.zeros(
        population_size,
        dtype=bool,
    )

    other_unique = np.zeros(
        population_size,
        dtype=bool,
    )

    relay_class_spikes = {
        cell_type: 0
        for cell_type in class_masks
    }

    relay_class_unique = {
        cell_type: np.zeros(
            len(relay_indices),
            dtype=bool,
        )
        for cell_type in class_masks
    }

    first_relay_frame = None
    first_other_frame = None

    relay_active_frames = 0
    other_active_frames = 0

    max_relay_spikes_frame = 0
    max_other_spikes_frame = 0

    frame_number = 0

    for _ in range(
        OBSERVATIONS
    ):
        frames = encoder.encode_sequence(
            neutral,
            frame_count=FRAME_COUNT,
        )

        for stimulus in frames:
            spikes = runtime.step(
                stimulus
                * SENSORY_GAIN
            ) > 0

            packed = np.packbits(
                spikes
            )

            digest_array(
                neural_hash,
                packed,
            )

            retinal_fired = (
                spikes
                & retinal_mask
            )

            relay_fired = (
                spikes
                & relay_mask
            )

            other_fired = (
                spikes
                & other_mask
            )

            r_count = int(
                np.count_nonzero(
                    retinal_fired
                )
            )

            relay_count = int(
                np.count_nonzero(
                    relay_fired
                )
            )

            other_count = int(
                np.count_nonzero(
                    other_fired
                )
            )

            retinal_spikes += r_count
            relay_spikes += relay_count
            other_spikes += other_count

            retinal_unique |= (
                retinal_fired
            )

            relay_unique |= (
                relay_fired
            )

            other_unique |= (
                other_fired
            )

            if relay_count:
                relay_active_frames += 1

                max_relay_spikes_frame = max(
                    max_relay_spikes_frame,
                    relay_count,
                )

                if first_relay_frame is None:
                    first_relay_frame = (
                        frame_number
                    )

            if other_count:
                other_active_frames += 1

                max_other_spikes_frame = max(
                    max_other_spikes_frame,
                    other_count,
                )

                if first_other_frame is None:
                    first_other_frame = (
                        frame_number
                    )

            local_relay_spikes = spikes[
                relay_indices
            ]

            for (
                cell_type,
                class_mask,
            ) in class_masks.items():
                class_fired = (
                    local_relay_spikes
                    & class_mask
                )

                relay_class_spikes[
                    cell_type
                ] += int(
                    np.count_nonzero(
                        class_fired
                    )
                )

                relay_class_unique[
                    cell_type
                ] |= class_fired

            frame_number += 1

    result = {
        "frames": frame_number,
        "neural_hash": (
            neural_hash.hexdigest()
        ),
        "final_voltage_hash": (
            hashlib.sha256(
                runtime.voltage.tobytes()
            ).hexdigest()
        ),
        "retinal_spikes": retinal_spikes,
        "relay_spikes": relay_spikes,
        "other_spikes": other_spikes,
        "unique_retinal": int(
            np.count_nonzero(
                retinal_unique
            )
        ),
        "unique_relay": int(
            np.count_nonzero(
                relay_unique
            )
        ),
        "unique_other": int(
            np.count_nonzero(
                other_unique
            )
        ),
        "first_relay_frame": (
            first_relay_frame
        ),
        "first_other_frame": (
            first_other_frame
        ),
        "relay_active_frames": (
            relay_active_frames
        ),
        "other_active_frames": (
            other_active_frames
        ),
        "max_relay_spikes_frame": (
            max_relay_spikes_frame
        ),
        "max_other_spikes_frame": (
            max_other_spikes_frame
        ),
        "class_spikes": (
            relay_class_spikes
        ),
        "class_unique": {
            cell_type: int(
                np.count_nonzero(
                    values
                )
            )
            for (
                cell_type,
                values
            ) in relay_class_unique.items()
        },
    }

    return result


def print_result(
    name,
    result,
):
    print()
    print("=" * 72)
    print(name)
    print("=" * 72)

    print(
        "frames:",
        result["frames"],
    )

    print(
        "neural sha256:",
        result["neural_hash"],
    )

    print(
        "final voltage sha256:",
        result[
            "final_voltage_hash"
        ],
    )

    print()
    print(
        "retinal spikes:",
        result[
            "retinal_spikes"
        ],
    )

    print(
        "relay spikes:",
        result[
            "relay_spikes"
        ],
    )

    print(
        "other downstream spikes:",
        result[
            "other_spikes"
        ],
    )

    print()
    print(
        "unique retinal neurons:",
        result[
            "unique_retinal"
        ],
    )

    print(
        "unique relay neurons:",
        result[
            "unique_relay"
        ],
    )

    print(
        "unique other downstream neurons:",
        result[
            "unique_other"
        ],
    )

    print()
    print(
        "first relay spike frame:",
        result[
            "first_relay_frame"
        ],
    )

    print(
        "first other downstream frame:",
        result[
            "first_other_frame"
        ],
    )

    print(
        "relay-active frames:",
        result[
            "relay_active_frames"
        ],
    )

    print(
        "other-active frames:",
        result[
            "other_active_frames"
        ],
    )

    print(
        "max relay spikes/frame:",
        result[
            "max_relay_spikes_frame"
        ],
    )

    print(
        "max other spikes/frame:",
        result[
            "max_other_spikes_frame"
        ],
    )

    print()
    print("relay classes:")

    for cell_type in (
        "L1",
        "L2",
        "L3",
        "Lai",
    ):
        print(
            f"  {cell_type}: "
            f"spikes="
            f"{result['class_spikes'][cell_type]} "
            f"unique="
            f"{result['class_unique'][cell_type]}"
        )


def main():
    with CONFIG.open(
        "rb"
    ) as handle:
        config = tomllib.load(
            handle
        )

    release_gain = float(
        config[
            "transduction"
        ][
            "release_gain"
        ]
    )

    print(
        "frozen release gain:",
        release_gain,
    )

    print(
        "loading frozen connectome..."
    )

    connectome = sparse.load_npz(
        CONNECTOME
    ).tocsr()

    retina = np.load(
        RETINA
    )

    retinal_indices = np.asarray(
        retina[
            "neuron_index"
        ],
        dtype=np.int32,
    )

    relay = np.load(
        RELAY
    )

    relay_indices = np.asarray(
        relay[
            "neuron_index"
        ],
        dtype=np.int32,
    )

    relay_types = np.asarray(
        relay[
            "type"
        ],
    )

    n1 = run_once(
        connectome,
        retinal_indices,
        relay_indices,
        relay_types,
        release_gain,
    )

    n2 = run_once(
        connectome,
        retinal_indices,
        relay_indices,
        relay_types,
        release_gain,
    )

    print_result(
        "NEUTRAL N1",
        n1,
    )

    print_result(
        "NEUTRAL N2",
        n2,
    )

    print()
    print("=" * 72)
    print("REPLAY CHECKS")
    print("=" * 72)

    assert (
        n1["neural_hash"]
        == n2["neural_hash"]
    )

    assert (
        n1["final_voltage_hash"]
        == n2["final_voltage_hash"]
    )

    assert (
        n1["retinal_spikes"]
        == n2["retinal_spikes"]
    )

    assert (
        n1["relay_spikes"]
        == n2["relay_spikes"]
    )

    assert (
        n1["other_spikes"]
        == n2["other_spikes"]
    )

    print(
        "N1 == N2 exact replay: PASS"
    )

    if n1["relay_spikes"] > 0:
        print(
            "retina -> relay propagation: PASS"
        )
    else:
        print(
            "retina -> relay propagation: FAIL"
        )

    if n1["other_spikes"] > 0:
        print(
            "relay -> wider connectome "
            "propagation: OBSERVED"
        )
    else:
        print(
            "relay -> wider connectome "
            "propagation: NOT YET OBSERVED"
        )

    print()
    print(
        "MQ-2.1 NEUTRAL TRANSDUCTION "
        "REPLAY COMPLETE"
    )


if __name__ == "__main__":
    main()
