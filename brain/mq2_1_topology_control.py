from __future__ import annotations

from pathlib import Path
import tomllib

import numpy as np
from scipy import sparse

from brain.mq2_1_market_replay import (
    run_replay,
)
from brain.visual_transduction import (
    VisualTransductionConfig,
)


BIOLOGICAL = Path(
    "/home/wil/moscaquant-data/processed/"
    "connectome-baseline-v1.npz"
)

SHUFFLED = Path(
    "/home/wil/moscaquant-data/processed/"
    "connectome-shuffled-mosca-v2.npz"
)

RETINA = Path(
    "/home/wil/moscaquant-data/processed/"
    "visual-r1-r6-map-v1.npz"
)

RELAY = Path(
    "/home/wil/moscaquant-data/processed/"
    "visual-relay-map-v1.npz"
)

TRANSDUCTION_CONFIG = Path(
    "config/sensory/visual-transduction-v1.toml"
)

CONTROL_CONFIG = Path(
    "config/controls/shuffled-mosca-v2.toml"
)


def compare_condition(
    name,
    biological,
    shuffled,
):
    print()
    print("=" * 72)
    print(
        f"{name}: BIOLOGICAL vs SHUFFLED MOSCA v2"
    )
    print("=" * 72)

    print(
        "normalized percept identical:",
        biological["normalized_hash"]
        == shuffled["normalized_hash"],
    )

    print(
        "retinal stream identical:",
        biological["retinal_hash"]
        == shuffled["retinal_hash"],
    )

    print(
        "relay trajectory identical:",
        biological["relay_hash"]
        == shuffled["relay_hash"],
    )

    print(
        "wider spike trajectory identical:",
        biological["wider_hash"]
        == shuffled["wider_hash"],
    )

    print()
    print(
        "retinal spikes:",
        f"bio={biological['retinal_spikes']}",
        f"shuf={shuffled['retinal_spikes']}",
    )

    print(
        "relay spikes:",
        f"bio={biological['relay_spikes']}",
        f"shuf={shuffled['relay_spikes']}",
    )

    print(
        "wider spikes:",
        f"bio={biological['wider_spikes']}",
        f"shuf={shuffled['wider_spikes']}",
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
            f"bio={biological['class_spikes'][cell_type]} "
            f"shuf={shuffled['class_spikes'][cell_type]}"
        )

    print()
    print(
        "first relay frame:",
        f"bio={biological['first_relay_frame']}",
        f"shuf={shuffled['first_relay_frame']}",
    )

    print(
        "first excitatory relay frame:",
        f"bio={biological['first_excitatory_relay_frame']}",
        f"shuf={shuffled['first_excitatory_relay_frame']}",
    )

    print(
        "first wider frame:",
        f"bio={biological['first_wider_frame']}",
        f"shuf={shuffled['first_wider_frame']}",
    )

    print()
    print(
        "final max voltage:",
        f"bio={biological['final_voltage_max']}",
        f"shuf={shuffled['final_voltage_max']}",
    )

    print(
        "final min voltage:",
        f"bio={biological['final_voltage_min']}",
        f"shuf={shuffled['final_voltage_min']}",
    )


def main():
    with TRANSDUCTION_CONFIG.open(
        "rb"
    ) as handle:
        transduction = tomllib.load(
            handle
        )

    with CONTROL_CONFIG.open(
        "rb"
    ) as handle:
        control = tomllib.load(
            handle
        )

    release_gain = float(
        transduction[
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
        "shuffled artifact sha256:",
        control[
            "control"
        ][
            "artifact_sha256"
        ],
    )

    print(
        "loading biological connectome..."
    )

    biological_connectome = (
        sparse.load_npz(
            BIOLOGICAL
        ).tocsr()
    )

    print(
        "loading SHUFFLED MOSCA v2..."
    )

    shuffled_connectome = (
        sparse.load_npz(
            SHUFFLED
        ).tocsr()
    )

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

    print()
    print(
        "RUN BIOLOGICAL A1"
    )

    bio_a1 = run_replay(
        "A",
        biological_connectome,
        retinal_indices,
        relay_indices,
        relay_types,
        release_gain,
    )

    print(
        "RUN BIOLOGICAL A2"
    )

    bio_a2 = run_replay(
        "A",
        biological_connectome,
        retinal_indices,
        relay_indices,
        relay_types,
        release_gain,
    )

    print(
        "RUN BIOLOGICAL B"
    )

    bio_b = run_replay(
        "B",
        biological_connectome,
        retinal_indices,
        relay_indices,
        relay_types,
        release_gain,
    )

    print()
    print(
        "RUN SHUFFLED A1"
    )

    shuf_a1 = run_replay(
        "A",
        shuffled_connectome,
        retinal_indices,
        relay_indices,
        relay_types,
        release_gain,
    )

    print(
        "RUN SHUFFLED A2"
    )

    shuf_a2 = run_replay(
        "A",
        shuffled_connectome,
        retinal_indices,
        relay_indices,
        relay_types,
        release_gain,
    )

    print(
        "RUN SHUFFLED B"
    )

    shuf_b = run_replay(
        "B",
        shuffled_connectome,
        retinal_indices,
        relay_indices,
        relay_types,
        release_gain,
    )

    #
    # Determinism first.
    #
    assert (
        bio_a1["neural_hash"]
        == bio_a2["neural_hash"]
    )

    assert (
        bio_a1["final_voltage_hash"]
        == bio_a2["final_voltage_hash"]
    )

    assert (
        shuf_a1["neural_hash"]
        == shuf_a2["neural_hash"]
    )

    assert (
        shuf_a1["final_voltage_hash"]
        == shuf_a2["final_voltage_hash"]
    )

    print()
    print("=" * 72)
    print("DETERMINISM")
    print("=" * 72)

    print(
        "BIO A1 == A2: PASS"
    )

    print(
        "SHUFFLED A1 == A2: PASS"
    )

    #
    # Because the full R1-R6 output interface
    # is protected, retinal percept hashes must
    # be identical between biological and control.
    #
    for label, bio, shuf in (
        (
            "A",
            bio_a1,
            shuf_a1,
        ),
        (
            "B",
            bio_b,
            shuf_b,
        ),
    ):
        assert (
            bio["normalized_hash"]
            == shuf["normalized_hash"]
        )

        assert (
            bio["retinal_hash"]
            == shuf["retinal_hash"]
        )

        print()
        print(
            f"{label} normalized percept "
            "BIO == SHUFFLED: PASS"
        )

        print(
            f"{label} retinal stream "
            "BIO == SHUFFLED: PASS"
        )

    compare_condition(
        "CONDITION A",
        bio_a1,
        shuf_a1,
    )

    compare_condition(
        "CONDITION B",
        bio_b,
        shuf_b,
    )

    print()
    print("=" * 72)
    print("TOPOLOGY CONTROL SUMMARY")
    print("=" * 72)

    print(
        "A relay trajectory BIO == SHUFFLED:",
        bio_a1["relay_hash"]
        == shuf_a1["relay_hash"],
    )

    print(
        "A wider trajectory BIO == SHUFFLED:",
        bio_a1["wider_hash"]
        == shuf_a1["wider_hash"],
    )

    print(
        "B relay trajectory BIO == SHUFFLED:",
        bio_b["relay_hash"]
        == shuf_b["relay_hash"],
    )

    print(
        "B wider trajectory BIO == SHUFFLED:",
        bio_b["wider_hash"]
        == shuf_b["wider_hash"],
    )

    print()
    print(
        "BIO A excitatory relay spikes:",
        bio_a1["class_spikes"]["L2"]
        + bio_a1["class_spikes"]["L3"],
    )

    print(
        "SHUFFLED A excitatory relay spikes:",
        shuf_a1["class_spikes"]["L2"]
        + shuf_a1["class_spikes"]["L3"],
    )

    print()
    print(
        "BIO A wider spikes:",
        bio_a1["wider_spikes"],
    )

    print(
        "SHUFFLED A wider spikes:",
        shuf_a1["wider_spikes"],
    )

    print()
    print(
        "MQ-2.1 TOPOLOGY CONTROL COMPLETE"
    )


if __name__ == "__main__":
    main()
