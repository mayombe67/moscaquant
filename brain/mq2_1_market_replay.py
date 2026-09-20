from __future__ import annotations
from config.paths import data_path

import hashlib
from pathlib import Path
import tomllib

import numpy as np
from scipy import sparse

from brain.market_replay import (
    ASSETS,
    FRAME_COUNT,
    OBSERVATIONS,
    SENSORY_GAIN,
    synthetic_series,
    market_window_at,
)
from brain.market_temporal import MarketVisionTemporalEncoder
from brain.visual_transduction import (
    VisualTransductionConfig,
    VisualTransductionRuntime,
)
from market.features import compute_features
from market.normalization import CausalNormalizer


CONNECTOME = data_path('processed', 'connectome-baseline-v1.npz')

RETINA = data_path('processed', 'visual-r1-r6-map-v1.npz')

RELAY = data_path('processed', 'visual-relay-map-v1.npz')

TERRITORIES = data_path('processed', 'market-retinal-territories-v1.npz')

CONFIG = Path(
    "config/sensory/visual-transduction-v1.toml"
)


def digest_array(digest, array):
    digest.update(
        np.ascontiguousarray(
            array
        ).tobytes()
    )


def run_replay(
    condition,
    connectome,
    retinal_indices,
    relay_indices,
    relay_types,
    release_gain,
):
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

    n = connectome.shape[0]

    retinal_mask = np.zeros(
        n,
        dtype=bool,
    )
    retinal_mask[retinal_indices] = True

    relay_mask = np.zeros(
        n,
        dtype=bool,
    )
    relay_mask[relay_indices] = True

    wider_mask = ~(
        retinal_mask
        | relay_mask
    )

    class_masks = {
        cell_type: (
            relay_types == cell_type
        )
        for cell_type in (
            "L1",
            "L2",
            "L3",
            "Lai",
        )
    }

    normalized_hash = hashlib.sha256()
    retinal_hash = hashlib.sha256()
    neural_hash = hashlib.sha256()
    relay_hash = hashlib.sha256()
    wider_hash = hashlib.sha256()

    retinal_spikes = 0
    relay_spikes = 0
    wider_spikes = 0

    class_spikes = {
        cell_type: 0
        for cell_type in class_masks
    }

    class_unique = {
        cell_type: np.zeros(
            len(relay_indices),
            dtype=bool,
        )
        for cell_type in class_masks
    }

    unique_retinal = np.zeros(
        n,
        dtype=bool,
    )

    unique_relay = np.zeros(
        n,
        dtype=bool,
    )

    unique_wider = np.zeros(
        n,
        dtype=bool,
    )

    frame_spike_counts = []
    relay_frame_counts = []
    wider_frame_counts = []

    first_relay_frame = None
    first_excitatory_relay_frame = None
    first_wider_frame = None

    frame_number = 0

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

        retinal_frames = (
            encoder.encode_sequence(
                normalized,
                frame_count=FRAME_COUNT,
            )
        )

        digest_array(
            retinal_hash,
            retinal_frames,
        )

        for stimulus in retinal_frames:
            spikes = (
                runtime.step(
                    stimulus * SENSORY_GAIN
                ) > 0
            )

            retinal_fired = (
                spikes
                & retinal_mask
            )

            relay_fired = (
                spikes
                & relay_mask
            )

            wider_fired = (
                spikes
                & wider_mask
            )

            local_relay = spikes[
                relay_indices
            ]

            excitatory_relay = (
                local_relay
                & np.isin(
                    relay_types,
                    (
                        "L2",
                        "L3",
                    ),
                )
            )

            digest_array(
                neural_hash,
                np.packbits(spikes),
            )

            digest_array(
                relay_hash,
                np.packbits(
                    local_relay
                ),
            )

            digest_array(
                wider_hash,
                np.packbits(
                    wider_fired
                ),
            )

            total_count = int(
                np.count_nonzero(
                    spikes
                )
            )

            relay_count = int(
                np.count_nonzero(
                    relay_fired
                )
            )

            wider_count = int(
                np.count_nonzero(
                    wider_fired
                )
            )

            retinal_count = int(
                np.count_nonzero(
                    retinal_fired
                )
            )

            retinal_spikes += (
                retinal_count
            )

            relay_spikes += (
                relay_count
            )

            wider_spikes += (
                wider_count
            )

            frame_spike_counts.append(
                total_count
            )

            relay_frame_counts.append(
                relay_count
            )

            wider_frame_counts.append(
                wider_count
            )

            unique_retinal |= (
                retinal_fired
            )

            unique_relay |= (
                relay_fired
            )

            unique_wider |= (
                wider_fired
            )

            if (
                relay_count > 0
                and first_relay_frame is None
            ):
                first_relay_frame = (
                    frame_number
                )

            if (
                np.any(
                    excitatory_relay
                )
                and
                first_excitatory_relay_frame
                is None
            ):
                first_excitatory_relay_frame = (
                    frame_number
                )

            if (
                wider_count > 0
                and first_wider_frame is None
            ):
                first_wider_frame = (
                    frame_number
                )

            for (
                cell_type,
                mask,
            ) in class_masks.items():
                fired = (
                    local_relay
                    & mask
                )

                class_spikes[
                    cell_type
                ] += int(
                    np.count_nonzero(
                        fired
                    )
                )

                class_unique[
                    cell_type
                ] |= fired

            frame_number += 1

    return {
        "condition": condition,

        "normalized_hash":
            normalized_hash.hexdigest(),

        "retinal_hash":
            retinal_hash.hexdigest(),

        "neural_hash":
            neural_hash.hexdigest(),

        "relay_hash":
            relay_hash.hexdigest(),

        "wider_hash":
            wider_hash.hexdigest(),

        "final_voltage_hash":
            hashlib.sha256(
                runtime.voltage.tobytes()
            ).hexdigest(),

        "retinal_spikes":
            retinal_spikes,

        "relay_spikes":
            relay_spikes,

        "wider_spikes":
            wider_spikes,

        "unique_retinal":
            int(
                np.count_nonzero(
                    unique_retinal
                )
            ),

        "unique_relay":
            int(
                np.count_nonzero(
                    unique_relay
                )
            ),

        "unique_wider":
            int(
                np.count_nonzero(
                    unique_wider
                )
            ),

        "class_spikes":
            class_spikes,

        "class_unique": {
            cell_type: int(
                np.count_nonzero(
                    values
                )
            )
            for (
                cell_type,
                values
            ) in class_unique.items()
        },

        "first_relay_frame":
            first_relay_frame,

        "first_excitatory_relay_frame":
            first_excitatory_relay_frame,

        "first_wider_frame":
            first_wider_frame,

        "frame_spike_counts":
            frame_spike_counts,

        "relay_frame_counts":
            relay_frame_counts,

        "wider_frame_counts":
            wider_frame_counts,

        "final_voltage_max":
            float(
                runtime.voltage.max()
            ),

        "final_voltage_min":
            float(
                runtime.voltage.min()
            ),
    }


def summarize(name, result):
    print()
    print("=" * 72)
    print(name)
    print("=" * 72)

    print(
        "condition:",
        result["condition"],
    )

    print(
        "normalized sha256:",
        result["normalized_hash"],
    )

    print(
        "retinal sha256:",
        result["retinal_hash"],
    )

    print(
        "neural sha256:",
        result["neural_hash"],
    )

    print(
        "relay sha256:",
        result["relay_hash"],
    )

    print(
        "wider sha256:",
        result["wider_hash"],
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
        result["retinal_spikes"],
    )

    print(
        "relay spikes:",
        result["relay_spikes"],
    )

    print(
        "wider-connectome spikes:",
        result["wider_spikes"],
    )

    print()
    print(
        "unique retinal neurons:",
        result["unique_retinal"],
    )

    print(
        "unique relay neurons:",
        result["unique_relay"],
    )

    print(
        "unique wider neurons:",
        result["unique_wider"],
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

    print()
    print(
        "first relay frame:",
        result["first_relay_frame"],
    )

    print(
        "first excitatory relay frame:",
        result[
            "first_excitatory_relay_frame"
        ],
    )

    print(
        "first wider frame:",
        result["first_wider_frame"],
    )

    print()
    print(
        "final max voltage:",
        result["final_voltage_max"],
    )

    print(
        "final min voltage:",
        result["final_voltage_min"],
    )


def count_different_frames(
    first,
    second,
):
    return int(
        np.count_nonzero(
            np.asarray(first)
            != np.asarray(second)
        )
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
        "frozen MQ-2.1 release gain:",
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

    relay_types = np.asarray(
        relay["type"],
    )

    print()
    print("RUN A1")

    a1 = run_replay(
        "A",
        connectome,
        retinal_indices,
        relay_indices,
        relay_types,
        release_gain,
    )

    summarize(
        "A1",
        a1,
    )

    print()
    print("RUN A2")

    a2 = run_replay(
        "A",
        connectome,
        retinal_indices,
        relay_indices,
        relay_types,
        release_gain,
    )

    summarize(
        "A2",
        a2,
    )

    print()
    print("RUN B")

    b = run_replay(
        "B",
        connectome,
        retinal_indices,
        relay_indices,
        relay_types,
        release_gain,
    )

    summarize(
        "B",
        b,
    )

    print()
    print("=" * 72)
    print("DETERMINISM")
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
        a1["relay_hash"]
        == a2["relay_hash"]
    )

    assert (
        a1["wider_hash"]
        == a2["wider_hash"]
    )

    assert (
        a1["final_voltage_hash"]
        == a2["final_voltage_hash"]
    )

    assert (
        a1["frame_spike_counts"]
        == a2["frame_spike_counts"]
    )

    assert (
        a1["relay_frame_counts"]
        == a2["relay_frame_counts"]
    )

    assert (
        a1["wider_frame_counts"]
        == a2["wider_frame_counts"]
    )

    print(
        "A1 == A2 exact replay: PASS"
    )

    print()
    print("=" * 72)
    print("A/B DISCRIMINATION")
    print("=" * 72)

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
        a1["relay_hash"]
        != b["relay_hash"]
    ):
        print(
            "A != B relay spike trajectory: PASS"
        )
    else:
        print(
            "A != B relay spike trajectory: NO"
        )

    if (
        a1["wider_hash"]
        != b["wider_hash"]
    ):
        print(
            "A != B wider-connectome "
            "spike trajectory: PASS"
        )
    else:
        print(
            "A != B wider-connectome "
            "spike trajectory: NO"
        )

    print()
    print(
        "frames with different total "
        "spike counts:",
        count_different_frames(
            a1["frame_spike_counts"],
            b["frame_spike_counts"],
        ),
    )

    print(
        "frames with different relay "
        "spike counts:",
        count_different_frames(
            a1["relay_frame_counts"],
            b["relay_frame_counts"],
        ),
    )

    print(
        "frames with different wider "
        "spike counts:",
        count_different_frames(
            a1["wider_frame_counts"],
            b["wider_frame_counts"],
        ),
    )

    print()
    print("=" * 72)
    print("MQ-2.1 PROPAGATION GATE")
    print("=" * 72)

    if (
        a1["relay_spikes"] > 0
        or b["relay_spikes"] > 0
    ):
        print(
            "market-driven activity beyond "
            "artificial retina: OBSERVED"
        )
    else:
        print(
            "market-driven activity beyond "
            "artificial retina: NOT OBSERVED"
        )

    excitatory_spikes_a = (
        a1["class_spikes"]["L2"]
        + a1["class_spikes"]["L3"]
    )

    excitatory_spikes_b = (
        b["class_spikes"]["L2"]
        + b["class_spikes"]["L3"]
    )

    print(
        "A excitatory relay spikes:",
        excitatory_spikes_a,
    )

    print(
        "B excitatory relay spikes:",
        excitatory_spikes_b,
    )

    if (
        excitatory_spikes_a > 0
        or excitatory_spikes_b > 0
    ):
        print(
            "excitatory visual relay "
            "propagation: OBSERVED"
        )
    else:
        print(
            "excitatory visual relay "
            "propagation: NOT OBSERVED"
        )

    if (
        a1["wider_spikes"] > 0
        or b["wider_spikes"] > 0
    ):
        print(
            "wider-connectome spiking: OBSERVED"
        )
    else:
        print(
            "wider-connectome spiking: "
            "NOT OBSERVED"
        )

    print()
    print(
        "MQ-2.1 MARKET REPLAY COMPLETE"
    )


if __name__ == "__main__":
    main()
