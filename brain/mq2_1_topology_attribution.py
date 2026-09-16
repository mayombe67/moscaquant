from __future__ import annotations

from pathlib import Path
import tomllib

import numpy as np
from scipy import sparse

from brain.mq2_1_relay_attribution import (
    run_condition,
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

NEURON_IDS = Path(
    "/home/wil/moscaquant-data/processed/"
    "neuron_ids.npy"
)

TRANSDUCTION_CONFIG = Path(
    "config/sensory/visual-transduction-v1.toml"
)

CONTROL_CONFIG = Path(
    "config/controls/shuffled-mosca-v2.toml"
)


def print_value(
    label,
    biological,
    shuffled,
):
    print(
        f"{label}:",
        f"BIO={biological}",
        f"SHUF={shuffled}",
    )


def compare(
    condition,
    bio,
    shuf,
):
    print()
    print("=" * 72)
    print(
        f"CONDITION {condition}: "
        "BIOLOGICAL vs SHUFFLED MOSCA v2"
    )
    print("=" * 72)

    print_value(
        "relay-only max positive voltage",
        bio["relay_peak"],
        shuf["relay_peak"],
    )

    print_value(
        "relay-only peak frame",
        bio["relay_peak_frame"],
        shuf["relay_peak_frame"],
    )

    print_value(
        "relay-only peak target",
        bio["relay_peak_body"],
        shuf["relay_peak_body"],
    )

    print()

    print_value(
        "L2/L3-only max positive voltage",
        bio["excitatory_peak"],
        shuf["excitatory_peak"],
    )

    print_value(
        "L2/L3 peak frame",
        bio["excitatory_peak_frame"],
        shuf["excitatory_peak_frame"],
    )

    print_value(
        "L2/L3 peak target",
        bio["excitatory_peak_body"],
        shuf["excitatory_peak_body"],
    )

    print()

    print_value(
        "L1/Lai-only minimum voltage",
        bio["inhibitory_min"],
        shuf["inhibitory_min"],
    )

    print_value(
        "L1/Lai minimum frame",
        bio["inhibitory_min_frame"],
        shuf["inhibitory_min_frame"],
    )

    print_value(
        "L1/Lai minimum target",
        bio["inhibitory_min_body"],
        shuf["inhibitory_min_body"],
    )

    print()

    print_value(
        "actual wider-network max",
        bio["actual_peak"],
        shuf["actual_peak"],
    )

    print_value(
        "actual peak frame",
        bio["actual_peak_frame"],
        shuf["actual_peak_frame"],
    )

    print_value(
        "actual peak target",
        bio["actual_peak_body"],
        shuf["actual_peak_body"],
    )

    print()

    print(
        "closest relay-excited target:"
    )

    print_value(
        "  gap to +1",
        bio["closest_gap"],
        shuf["closest_gap"],
    )

    print_value(
        "  frame",
        bio["closest_gap_frame"],
        shuf["closest_gap_frame"],
    )

    print_value(
        "  target body_id",
        bio["closest_gap_body"],
        shuf["closest_gap_body"],
    )

    print_value(
        "  actual membrane voltage",
        bio["closest_actual_voltage"],
        shuf["closest_actual_voltage"],
    )

    print_value(
        "  relay-attributed voltage",
        bio["closest_relay_contribution"],
        shuf["closest_relay_contribution"],
    )

    print()

    if (
        bio["relay_peak"] is not None
        and shuf["relay_peak"] is not None
    ):
        print(
            "relay-only peak difference "
            "(BIO - SHUF):",
            float(
                bio["relay_peak"]
                - shuf["relay_peak"]
            ),
        )

    if (
        bio["excitatory_peak"] is not None
        and shuf["excitatory_peak"] is not None
    ):
        print(
            "L2/L3 peak difference "
            "(BIO - SHUF):",
            float(
                bio["excitatory_peak"]
                - shuf["excitatory_peak"]
            ),
        )

    if (
        bio["actual_peak"] is not None
        and shuf["actual_peak"] is not None
    ):
        print(
            "actual wider peak difference "
            "(BIO - SHUF):",
            float(
                bio["actual_peak"]
                - shuf["actual_peak"]
            ),
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
        "frozen shuffled artifact:",
        control[
            "control"
        ][
            "artifact_sha256"
        ],
    )

    print(
        "loading biological connectome..."
    )

    biological = sparse.load_npz(
        BIOLOGICAL
    ).tocsr()

    print(
        "loading SHUFFLED MOSCA v2..."
    )

    shuffled = sparse.load_npz(
        SHUFFLED
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

    neuron_ids = np.load(
        NEURON_IDS
    )

    print()
    print("RUN BIOLOGICAL A")

    bio_a = run_condition(
        "A",
        biological,
        retinal_indices,
        relay_indices,
        relay_types,
        neuron_ids,
        release_gain,
    )

    print("RUN SHUFFLED A")

    shuf_a = run_condition(
        "A",
        shuffled,
        retinal_indices,
        relay_indices,
        relay_types,
        neuron_ids,
        release_gain,
    )

    print("RUN BIOLOGICAL B")

    bio_b = run_condition(
        "B",
        biological,
        retinal_indices,
        relay_indices,
        relay_types,
        neuron_ids,
        release_gain,
    )

    print("RUN SHUFFLED B")

    shuf_b = run_condition(
        "B",
        shuffled,
        retinal_indices,
        relay_indices,
        relay_types,
        neuron_ids,
        release_gain,
    )

    compare(
        "A",
        bio_a,
        shuf_a,
    )

    compare(
        "B",
        bio_b,
        shuf_b,
    )

    print()
    print("=" * 72)
    print("TOPOLOGY ATTRIBUTION SUMMARY")
    print("=" * 72)

    print(
        "A relay-only peak:",
        f"BIO={bio_a['relay_peak']}",
        f"SHUF={shuf_a['relay_peak']}",
    )

    print(
        "A L2/L3-only peak:",
        f"BIO={bio_a['excitatory_peak']}",
        f"SHUF={shuf_a['excitatory_peak']}",
    )

    print(
        "A actual wider peak:",
        f"BIO={bio_a['actual_peak']}",
        f"SHUF={shuf_a['actual_peak']}",
    )

    print()
    print(
        "B relay-only peak:",
        f"BIO={bio_b['relay_peak']}",
        f"SHUF={shuf_b['relay_peak']}",
    )

    print(
        "B L2/L3-only peak:",
        f"BIO={bio_b['excitatory_peak']}",
        f"SHUF={shuf_b['excitatory_peak']}",
    )

    print(
        "B actual wider peak:",
        f"BIO={bio_b['actual_peak']}",
        f"SHUF={shuf_b['actual_peak']}",
    )

    print()
    print(
        "MQ-2.1 TOPOLOGY ATTRIBUTION "
        "COMPLETE"
    )


if __name__ == "__main__":
    main()
