from __future__ import annotations

import gc
import json
from pathlib import Path
import tomllib

import numpy as np
from scipy import sparse

from brain.mq2_1_relay_attribution import (
    run_condition,
)
from brain.shuffled_connectome_v2 import (
    build_interface_preserving_permutation,
)


BIOLOGICAL = Path(
    "/home/wil/moscaquant-data/processed/"
    "connectome-baseline-v1.npz"
)

RETINA = Path(
    "/home/wil/moscaquant-data/processed/"
    "visual-r1-r6-map-v1.npz"
)

RELAY = Path(
    "/home/wil/moscaquant-data/processed/"
    "visual-relay-map-v1.npz"
)

SIGNS = Path(
    "/home/wil/moscaquant-data/processed/"
    "transmitter_sign.npy"
)

NEURON_IDS = Path(
    "/home/wil/moscaquant-data/processed/"
    "neuron_ids.npy"
)

TRANSDUCTION_CONFIG = Path(
    "config/sensory/visual-transduction-v1.toml"
)

ENSEMBLE_CONFIG = Path(
    "config/controls/shuffled-mosca-ensemble-v2.toml"
)

OUTPUT = Path(
    "/home/wil/moscaquant-data/experiments/"
    "mq2-1-shuffled-ensemble-v2.json"
)


def build_in_memory_control(
    original,
    transmitter_sign,
    retinal_indices,
    seed,
):
    permutation = (
        build_interface_preserving_permutation(
            transmitter_sign,
            retinal_indices,
            seed,
        )
    )

    shuffled = sparse.csr_matrix(
        (
            original.data.copy(),
            permutation[
                original.indices
            ].astype(
                np.int32,
                copy=False,
            ),
            original.indptr.copy(),
        ),
        shape=original.shape,
        dtype=original.dtype,
    )

    if shuffled.nnz != original.nnz:
        raise RuntimeError(
            f"seed {seed}: edge count changed"
        )

    shuffled.sort_indices()

    return shuffled


def stats(values):
    array = np.asarray(
        values,
        dtype=np.float64,
    )

    return {
        "min": float(array.min()),
        "max": float(array.max()),
        "mean": float(array.mean()),
        "median": float(
            np.median(array)
        ),
        "std_population": float(
            array.std(ddof=0)
        ),
    }


def upper_tail_summary(
    biological,
    shuffled_values,
):
    values = np.asarray(
        shuffled_values,
        dtype=np.float64,
    )

    equal_or_greater = int(
        np.count_nonzero(
            values >= biological
        )
    )

    greater = int(
        np.count_nonzero(
            values > biological
        )
    )

    #
    # Conservative finite-ensemble empirical
    # one-sided p estimate.
    #
    p_plus_one = (
        equal_or_greater + 1
    ) / (
        len(values) + 1
    )

    return {
        "biological": float(
            biological
        ),
        "shuffled_equal_or_greater": (
            equal_or_greater
        ),
        "shuffled_strictly_greater": (
            greater
        ),
        "empirical_p_plus_one": float(
            p_plus_one
        ),
        "shuffled_stats": stats(
            values
        ),
    }


def lower_tail_summary(
    biological,
    shuffled_values,
):
    values = np.asarray(
        shuffled_values,
        dtype=np.float64,
    )

    #
    # For threshold gap, LOWER is the stronger
    # threshold approach.
    #
    equal_or_lower = int(
        np.count_nonzero(
            values <= biological
        )
    )

    lower = int(
        np.count_nonzero(
            values < biological
        )
    )

    p_plus_one = (
        equal_or_lower + 1
    ) / (
        len(values) + 1
    )

    return {
        "biological": float(
            biological
        ),
        "shuffled_equal_or_lower": (
            equal_or_lower
        ),
        "shuffled_strictly_lower": (
            lower
        ),
        "empirical_p_plus_one": float(
            p_plus_one
        ),
        "shuffled_stats": stats(
            values
        ),
    }


def main():
    with TRANSDUCTION_CONFIG.open(
        "rb"
    ) as handle:
        transduction = tomllib.load(
            handle
        )

    with ENSEMBLE_CONFIG.open(
        "rb"
    ) as handle:
        ensemble = tomllib.load(
            handle
        )

    release_gain = float(
        transduction[
            "transduction"
        ][
            "release_gain"
        ]
    )

    configured_gain = float(
        ensemble[
            "experiment"
        ][
            "release_gain"
        ]
    )

    if release_gain != configured_gain:
        raise RuntimeError(
            "precommitted ensemble gain does "
            "not match frozen transduction gain"
        )

    condition = str(
        ensemble[
            "experiment"
        ][
            "condition"
        ]
    )

    if condition != "A":
        raise RuntimeError(
            "ensemble v1 must use "
            "precommitted Condition A"
        )

    seed_start = int(
        ensemble[
            "ensemble"
        ][
            "seed_start"
        ]
    )

    seed_count = int(
        ensemble[
            "ensemble"
        ][
            "seed_count"
        ]
    )

    seeds = list(
        range(
            seed_start,
            seed_start + seed_count,
        )
    )

    print(
        "loading biological connectome..."
    )

    biological = sparse.load_npz(
        BIOLOGICAL
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

    transmitter_sign = np.load(
        SIGNS
    )

    neuron_ids = np.load(
        NEURON_IDS
    )

    print(
        "frozen release gain:",
        release_gain,
    )

    print(
        "condition:",
        condition,
    )

    print(
        "seed start:",
        seed_start,
    )

    print(
        "seed count:",
        seed_count,
    )

    print()
    print(
        "RUN BIOLOGICAL REFERENCE"
    )

    bio = run_condition(
        condition,
        biological,
        retinal_indices,
        relay_indices,
        relay_types,
        neuron_ids,
        release_gain,
    )

    biological_metrics = {
        "relay_only_peak": float(
            bio[
                "relay_peak"
            ]
        ),
        "l2_l3_only_peak": float(
            bio[
                "excitatory_peak"
            ]
        ),
        "actual_wider_peak": float(
            bio[
                "actual_peak"
            ]
        ),
        "closest_threshold_gap": float(
            bio[
                "closest_gap"
            ]
        ),
    }

    print()
    print("=" * 72)
    print("BIOLOGICAL REFERENCE")
    print("=" * 72)

    for key, value in (
        biological_metrics.items()
    ):
        print(
            f"{key}:",
            value,
        )

    results = []

    for position, seed in enumerate(
        seeds,
        start=1,
    ):
        print()
        print("=" * 72)
        print(
            f"SHUFFLE {position}/{seed_count} "
            f"— seed {seed}"
        )
        print("=" * 72)

        shuffled = (
            build_in_memory_control(
                biological,
                transmitter_sign,
                retinal_indices,
                seed,
            )
        )

        result = run_condition(
            condition,
            shuffled,
            retinal_indices,
            relay_indices,
            relay_types,
            neuron_ids,
            release_gain,
        )

        record = {
            "seed": seed,
            "relay_only_peak": float(
                result[
                    "relay_peak"
                ]
            ),
            "l2_l3_only_peak": float(
                result[
                    "excitatory_peak"
                ]
            ),
            "actual_wider_peak": float(
                result[
                    "actual_peak"
                ]
            ),
            "closest_threshold_gap": float(
                result[
                    "closest_gap"
                ]
            ),
        }

        results.append(
            record
        )

        print(
            "relay-only peak:",
            record[
                "relay_only_peak"
            ],
        )

        print(
            "L2/L3-only peak:",
            record[
                "l2_l3_only_peak"
            ],
        )

        print(
            "actual wider peak:",
            record[
                "actual_wider_peak"
            ],
        )

        print(
            "closest threshold gap:",
            record[
                "closest_threshold_gap"
            ],
        )

        #
        # Ensure this ~1 GB shuffled matrix
        # does not survive into the next seed.
        #
        del result
        del shuffled

        gc.collect()

    relay_values = [
        item["relay_only_peak"]
        for item in results
    ]

    excitatory_values = [
        item["l2_l3_only_peak"]
        for item in results
    ]

    actual_values = [
        item["actual_wider_peak"]
        for item in results
    ]

    gap_values = [
        item["closest_threshold_gap"]
        for item in results
    ]

    summary = {
        "relay_only_peak": (
            upper_tail_summary(
                biological_metrics[
                    "relay_only_peak"
                ],
                relay_values,
            )
        ),
        "l2_l3_only_peak": (
            upper_tail_summary(
                biological_metrics[
                    "l2_l3_only_peak"
                ],
                excitatory_values,
            )
        ),
        "actual_wider_peak": (
            upper_tail_summary(
                biological_metrics[
                    "actual_wider_peak"
                ],
                actual_values,
            )
        ),
        "closest_threshold_gap": (
            lower_tail_summary(
                biological_metrics[
                    "closest_threshold_gap"
                ],
                gap_values,
            )
        ),
    }

    output = {
        "experiment": (
            "mq2-1-shuffled-ensemble-v2"
        ),
        "condition": condition,
        "release_gain": release_gain,
        "seed_start": seed_start,
        "seed_count": seed_count,
        "seeds": seeds,
        "biological": biological_metrics,
        "shuffled": results,
        "summary": summary,
    }

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT.write_text(
        json.dumps(
            output,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    print()
    print("=" * 72)
    print("ENSEMBLE SUMMARY")
    print("=" * 72)

    for name in (
        "relay_only_peak",
        "l2_l3_only_peak",
        "actual_wider_peak",
    ):
        item = summary[
            name
        ]

        print()
        print(name)

        print(
            "  biological:",
            item[
                "biological"
            ],
        )

        print(
            "  shuffled min:",
            item[
                "shuffled_stats"
            ][
                "min"
            ],
        )

        print(
            "  shuffled median:",
            item[
                "shuffled_stats"
            ][
                "median"
            ],
        )

        print(
            "  shuffled max:",
            item[
                "shuffled_stats"
            ][
                "max"
            ],
        )

        print(
            "  shuffled >= biological:",
            item[
                "shuffled_equal_or_greater"
            ],
        )

        print(
            "  empirical p (+1):",
            item[
                "empirical_p_plus_one"
            ],
        )

    item = summary[
        "closest_threshold_gap"
    ]

    print()
    print(
        "closest_threshold_gap"
    )

    print(
        "  biological:",
        item[
            "biological"
        ],
    )

    print(
        "  shuffled min:",
        item[
            "shuffled_stats"
        ][
            "min"
        ],
    )

    print(
        "  shuffled median:",
        item[
            "shuffled_stats"
        ][
            "median"
        ],
    )

    print(
        "  shuffled max:",
        item[
            "shuffled_stats"
        ][
            "max"
        ],
    )

    print(
        "  shuffled <= biological:",
        item[
            "shuffled_equal_or_lower"
        ],
    )

    print(
        "  empirical p (+1):",
        item[
            "empirical_p_plus_one"
        ],
    )

    print()
    print(
        "results:",
        OUTPUT,
    )

    print()
    print(
        "MQ-2.1 SHUFFLED ENSEMBLE COMPLETE"
    )


if __name__ == "__main__":
    main()
