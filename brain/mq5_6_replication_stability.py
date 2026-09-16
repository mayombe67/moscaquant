from __future__ import annotations

import hashlib
import json
import os
import subprocess
import tomllib
from pathlib import Path

import numpy as np
from scipy import sparse

from market.features import compute_features
from market.normalization import CausalNormalizer

from brain.market_replay import (
    ASSETS,
    FRAME_COUNT,
    OBSERVATIONS,
    SENSORY_GAIN,
    market_window_at,
    synthetic_series,
)
from brain.market_temporal import MarketVisionTemporalEncoder
from brain.mq5_6_independent_reference_runtime import (
    IndependentReferenceRuntime,
    ReferenceRuntimeConfig,
)


DATA_ROOT = Path(
    os.environ.get(
        "MOSCAQUANT_DATA_ROOT",
        str(Path.home() / "moscaquant-data"),
    )
)

PROCESSED = DATA_ROOT / "processed"
EXPERIMENTS = DATA_ROOT / "experiments"

CONNECTOME = PROCESSED / "connectome-baseline-v1.npz"
RETINA = PROCESSED / "visual-r1-r6-map-v1.npz"
RELAY = PROCESSED / "visual-relay-map-v1.npz"
GRADED = PROCESSED / "mq3-2-graded-visual-types-v1.npz"
TERRITORIES = PROCESSED / "market-retinal-territories-v1.npz"

GENERALIZED = (
    EXPERIMENTS
    / "mq5-generalized-intervention-matrix-v1.json"
)

PATHWAY = (
    EXPERIMENTS
    / "mq5-4-pathway-56393-68045-1273-v1.json"
)

CONVERGENCE = (
    EXPERIMENTS
    / "mq5-5-convergence-specificity-v1.json"
)

CONFIG = Path(
    "config/controls/"
    "mq5-6-replication-stability-v1.toml"
)

PROTOCOL = Path(
    "docs/experiments/"
    "mq5-6-replication-stability-protocol.md"
)

OUTPUT = (
    EXPERIMENTS
    / "mq5-6-replication-stability-v1.json"
)

DIRECT_SOURCE = 43417
DIRECT_TARGET = 656
DIRECT_FRAME = 145

UPSTREAM = 56393
INTERMEDIATE = 68045
DOWNSTREAM = 1273
UPSTREAM_FRAME = 146
INTERMEDIATE_FRAME = 147

INPUT_A = 44274
INPUT_B = 55925
CONVERGENCE_TARGET = 55
CONVERGENCE_FRAME = 146

DOSES = (25, 50, 75, 100)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()

    with path.open("rb") as f:
        while True:
            block = f.read(1024 * 1024)

            if not block:
                break

            h.update(block)

    return h.hexdigest()


def git_commit() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"],
        text=True,
    ).strip()


def load_json(path: Path):
    return json.loads(
        path.read_text(encoding="utf-8")
    )


def load_toml(path: Path):
    with path.open("rb") as f:
        return tomllib.load(f)


def build_input():
    normalizers = [
        CausalNormalizer(
            window_size=64,
            min_history=8,
        )
        for _ in ASSETS
    ]

    series = [
        synthetic_series(
            "A",
            i,
        )
        for i in range(len(ASSETS))
    ]

    encoder = MarketVisionTemporalEncoder(
        TERRITORIES
    )

    stimuli = []

    for observation in range(OBSERVATIONS):
        normalized = np.empty(
            (
                len(ASSETS),
                7,
            ),
            dtype=np.float32,
        )

        for asset_index in range(len(ASSETS)):
            window = market_window_at(
                series[asset_index],
                observation,
            )

            normalized[
                asset_index
            ] = normalizers[
                asset_index
            ].transform(
                compute_features(window)
            )

        frames = encoder.encode_sequence(
            normalized,
            frame_count=FRAME_COUNT,
        )

        for stimulus in frames:
            stimuli.append(
                np.asarray(
                    stimulus
                    * SENSORY_GAIN,
                    dtype=np.float32,
                )
            )

    expected = (
        OBSERVATIONS
        * FRAME_COUNT
    )

    if len(stimuli) != expected:
        raise RuntimeError(
            "unexpected stimulus count"
        )

    return stimuli


def make_runtime(
    connectome,
    retinal,
    relay,
    graded,
):
    return IndependentReferenceRuntime(
        connectome=connectome,
        retinal_indices=retinal,
        relay_indices=relay,
        graded_indices=graded,
        config=ReferenceRuntimeConfig(),
    )


def run_case(
    connectome,
    retinal,
    relay,
    graded,
    stimuli,
    *,
    effective_nodes=(),
    voltage_nodes=(),
    intervention_frame=None,
    attenuation=None,
):
    runtime = make_runtime(
        connectome,
        retinal,
        relay,
        graded,
    )

    effective_nodes = tuple(
        sorted(set(map(int, effective_nodes)))
    )

    voltage_nodes = tuple(
        sorted(set(map(int, voltage_nodes)))
    )

    effective = {
        node: []
        for node in effective_nodes
    }

    voltage = {
        node: []
        for node in voltage_nodes
    }

    spikes = {
        node: []
        for node in voltage_nodes
    }

    for frame, stimulus in enumerate(stimuli):
        active = (
            attenuation
            if frame == intervention_frame
            else None
        )

        activity = runtime.effective_activity(
            active
        )

        for node in effective_nodes:
            effective[node].append(
                float(activity[node])
            )

        runtime.step(
            stimulus,
            attenuation=active,
        )

        for node in voltage_nodes:
            voltage[node].append(
                float(runtime.voltage[node])
            )

            spikes[node].append(
                float(runtime.spikes[node])
            )

    result = {
        "effective": {},
        "voltage": {},
        "metrics": {},
    }

    for node, values in effective.items():
        result["effective"][node] = (
            np.asarray(
                values,
                dtype=np.float64,
            )
        )

    for node, values in voltage.items():
        v = np.asarray(
            values,
            dtype=np.float64,
        )

        s = np.asarray(
            spikes[node],
            dtype=np.float64,
        )

        positive = np.flatnonzero(
            v > 0.0
        )

        peak_frame = int(
            np.argmax(v)
        )

        result["voltage"][node] = v

        result["metrics"][node] = {
            "first_positive_frame":
                (
                    int(positive[0])
                    if len(positive)
                    else None
                ),

            "integrated_positive_voltage":
                float(
                    np.maximum(
                        v,
                        0.0,
                    ).sum()
                ),

            "peak_frame":
                peak_frame,

            "peak_voltage":
                float(v[peak_frame]),

            "positive_frame_count":
                int(
                    np.count_nonzero(
                        v > 0.0
                    )
                ),

            "spike_count":
                int(
                    np.count_nonzero(
                        s > 0.0
                    )
                ),
        }

    return result


def numeric_compare(
    production,
    independent,
    abs_tol,
    rel_tol,
    small_threshold,
):
    production = float(production)
    independent = float(independent)

    abs_diff = abs(
        independent - production
    )

    if abs(production) <= small_threshold:
        rel_diff = None
        passed = (
            abs_diff <= abs_tol
        )
        mode = "absolute"
    else:
        rel_diff = (
            abs_diff
            / abs(production)
        )

        passed = (
            abs_diff <= abs_tol
            or rel_diff <= rel_tol
        )

        mode = "absolute_or_relative"

    return {
        "production": production,
        "independent": independent,
        "absolute_difference": abs_diff,
        "relative_difference": rel_diff,
        "comparison_mode": mode,
        "passed": bool(passed),
    }


def compare_metrics(
    production,
    independent,
    abs_tol,
    rel_tol,
    small_threshold,
):
    out = {}

    for key in (
        "integrated_positive_voltage",
        "peak_voltage",
    ):
        out[key] = numeric_compare(
            production[key],
            independent[key],
            abs_tol,
            rel_tol,
            small_threshold,
        )

    for key in (
        "first_positive_frame",
        "peak_frame",
        "positive_frame_count",
    ):
        out[key] = {
            "production":
                production[key],

            "independent":
                independent[key],

            "passed":
                production[key]
                == independent[key],
        }

    prod_spikes = production.get(
        "target_spike_count",
        production.get(
            "spike_count"
        ),
    )

    ind_spikes = independent[
        "spike_count"
    ]

    out["spike_count"] = {
        "production":
            prod_spikes,

        "independent":
            ind_spikes,

        "passed":
            prod_spikes == ind_spikes,
    }

    return out


def all_pass(obj):
    if isinstance(obj, dict):
        if (
            "passed" in obj
            and isinstance(
                obj["passed"],
                bool,
            )
        ):
            return obj["passed"]

        return all(
            all_pass(v)
            for v in obj.values()
        )

    if isinstance(obj, list):
        return all(
            all_pass(v)
            for v in obj
        )

    return True


def main():
    if OUTPUT.exists():
        raise RuntimeError(
            f"refusing to overwrite {OUTPUT}"
        )

    cfg = load_toml(CONFIG)

    abs_tol = float(
        cfg["tolerance"]["absolute"]
    )

    rel_tol = float(
        cfg["tolerance"]["relative"]
    )

    small = float(
        cfg["tolerance"][
            "small_value_threshold"
        ]
    )

    frozen_paths = (
        CONNECTOME,
        RETINA,
        RELAY,
        GRADED,
        GENERALIZED,
        PATHWAY,
        CONVERGENCE,
        CONFIG,
        PROTOCOL,
    )

    hashes_before = {
        str(p): sha256_file(p)
        for p in frozen_paths
    }

    print("=" * 100)
    print(
        "MQ-5.6 INDEPENDENT FULL-NETWORK "
        "REPLICATION"
    )
    print("=" * 100)

    print("loading connectome...")

    connectome = sparse.load_npz(
        CONNECTOME
    ).tocsr()

    retinal = np.asarray(
        np.load(RETINA)["neuron_index"],
        dtype=np.int32,
    )

    relay = np.asarray(
        np.load(RELAY)["neuron_index"],
        dtype=np.int32,
    )

    graded = np.asarray(
        np.load(GRADED)["neuron_index"],
        dtype=np.int32,
    )

    print("building frozen sensory input...")

    stimuli = build_input()

    print("baseline")

    baseline = run_case(
        connectome,
        retinal,
        relay,
        graded,
        stimuli,
        effective_nodes=(
            DIRECT_SOURCE,
            UPSTREAM,
            INTERMEDIATE,
            INPUT_A,
            INPUT_B,
        ),
        voltage_nodes=(
            DIRECT_TARGET,
            INTERMEDIATE,
            DOWNSTREAM,
            CONVERGENCE_TARGET,
        ),
    )

    generalized = load_json(
        GENERALIZED
    )

    pathway = load_json(
        PATHWAY
    )

    convergence = load_json(
        CONVERGENCE
    )

    direct_prod = next(
        edge
        for edge in generalized["edges"]
        if (
            int(edge["source"])
            == DIRECT_SOURCE
            and int(edge["target"])
            == DIRECT_TARGET
            and int(edge["causal_frame"])
            == DIRECT_FRAME
        )
    )

    conv_prod = next(
        system
        for system in convergence["systems"]
        if (
            int(system["input_a"])
            == INPUT_A
            and int(system["input_b"])
            == INPUT_B
            and int(system["target"])
            == CONVERGENCE_TARGET
        )
    )

    direct = {
        "baseline": compare_metrics(
            direct_prod["baseline"],
            baseline[
                "metrics"
            ][DIRECT_TARGET],
            abs_tol,
            rel_tol,
            small,
        ),
        "doses": {},
    }

    direct["baseline_source_effective"] = (
        numeric_compare(
            direct_prod[
                "baseline_source_effective_at_causal_frame"
            ],
            baseline[
                "effective"
            ][DIRECT_SOURCE][DIRECT_FRAME],
            abs_tol,
            rel_tol,
            small,
        )
    )

    print()
    print("DIRECT 43417 -> 656")

    for pct in DOSES:
        print(f"  {pct}%")

        dose = pct / 100.0

        run = run_case(
            connectome,
            retinal,
            relay,
            graded,
            stimuli,
            effective_nodes=(
                DIRECT_SOURCE,
            ),
            voltage_nodes=(
                DIRECT_TARGET,
            ),
            intervention_frame=(
                DIRECT_FRAME
            ),
            attenuation={
                DIRECT_SOURCE: dose,
            },
        )

        prod = direct_prod[
            "doses"
        ][str(pct)]

        direct["doses"][
            str(pct)
        ] = {
            "source_effective":
                numeric_compare(
                    prod[
                        "source_effective_at_causal_frame"
                    ],
                    run[
                        "effective"
                    ][DIRECT_SOURCE][DIRECT_FRAME],
                    abs_tol,
                    rel_tol,
                    small,
                ),

            "target_voltage_at_causal_frame":
                numeric_compare(
                    prod[
                        "target_voltage_at_causal_frame"
                    ],
                    run[
                        "voltage"
                    ][DIRECT_TARGET][DIRECT_FRAME],
                    abs_tol,
                    rel_tol,
                    small,
                ),

            "metrics":
                compare_metrics(
                    prod,
                    run[
                        "metrics"
                    ][DIRECT_TARGET],
                    abs_tol,
                    rel_tol,
                    small,
                ),
        }

    path_result = {
        "baseline": {
            "upstream_effective_at_F146":
                numeric_compare(
                    pathway[
                        "baseline"
                    ][
                        "upstream_effective_at_F146"
                    ],
                    baseline[
                        "effective"
                    ][UPSTREAM][UPSTREAM_FRAME],
                    abs_tol,
                    rel_tol,
                    small,
                ),

            "intermediate_voltage_at_F146":
                numeric_compare(
                    pathway[
                        "baseline"
                    ][
                        "intermediate_voltage_at_F146"
                    ],
                    baseline[
                        "voltage"
                    ][INTERMEDIATE][UPSTREAM_FRAME],
                    abs_tol,
                    rel_tol,
                    small,
                ),

            "intermediate_effective_at_F147":
                numeric_compare(
                    pathway[
                        "baseline"
                    ][
                        "intermediate_effective_at_F147"
                    ],
                    baseline[
                        "effective"
                    ][INTERMEDIATE][INTERMEDIATE_FRAME],
                    abs_tol,
                    rel_tol,
                    small,
                ),

            "downstream_voltage_at_F147":
                numeric_compare(
                    pathway[
                        "baseline"
                    ][
                        "downstream_voltage_at_F147"
                    ],
                    baseline[
                        "voltage"
                    ][DOWNSTREAM][INTERMEDIATE_FRAME],
                    abs_tol,
                    rel_tol,
                    small,
                ),

            "intermediate_metrics":
                compare_metrics(
                    pathway[
                        "baseline"
                    ][
                        "intermediate_metrics"
                    ],
                    baseline[
                        "metrics"
                    ][INTERMEDIATE],
                    abs_tol,
                    rel_tol,
                    small,
                ),

            "downstream_metrics":
                compare_metrics(
                    pathway[
                        "baseline"
                    ][
                        "downstream_metrics"
                    ],
                    baseline[
                        "metrics"
                    ][DOWNSTREAM],
                    abs_tol,
                    rel_tol,
                    small,
                ),
        },

        "upstream_interventions": {},
        "intermediate_interventions": {},
    }

    print()
    print(
        "PATHWAY 56393 -> 68045 -> 1273"
    )

    for pct in DOSES:
        dose = pct / 100.0

        print(
            f"  upstream {pct}%"
        )

        run = run_case(
            connectome,
            retinal,
            relay,
            graded,
            stimuli,
            effective_nodes=(
                UPSTREAM,
                INTERMEDIATE,
            ),
            voltage_nodes=(
                INTERMEDIATE,
                DOWNSTREAM,
            ),
            intervention_frame=(
                UPSTREAM_FRAME
            ),
            attenuation={
                UPSTREAM: dose,
            },
        )

        prod = pathway[
            "upstream_interventions"
        ][str(pct)]

        path_result[
            "upstream_interventions"
        ][str(pct)] = {
            "upstream_effective_at_F146":
                numeric_compare(
                    prod[
                        "upstream_effective_at_F146"
                    ],
                    run[
                        "effective"
                    ][UPSTREAM][UPSTREAM_FRAME],
                    abs_tol,
                    rel_tol,
                    small,
                ),

            "intermediate_voltage_at_F146":
                numeric_compare(
                    prod[
                        "intermediate_voltage_at_F146"
                    ],
                    run[
                        "voltage"
                    ][INTERMEDIATE][UPSTREAM_FRAME],
                    abs_tol,
                    rel_tol,
                    small,
                ),

            "intermediate_effective_at_F147":
                numeric_compare(
                    prod[
                        "intermediate_effective_at_F147"
                    ],
                    run[
                        "effective"
                    ][INTERMEDIATE][INTERMEDIATE_FRAME],
                    abs_tol,
                    rel_tol,
                    small,
                ),

            "downstream_voltage_at_F147":
                numeric_compare(
                    prod[
                        "downstream_voltage_at_F147"
                    ],
                    run[
                        "voltage"
                    ][DOWNSTREAM][INTERMEDIATE_FRAME],
                    abs_tol,
                    rel_tol,
                    small,
                ),

            "intermediate_metrics":
                compare_metrics(
                    prod[
                        "intermediate_metrics"
                    ],
                    run[
                        "metrics"
                    ][INTERMEDIATE],
                    abs_tol,
                    rel_tol,
                    small,
                ),

            "downstream_metrics":
                compare_metrics(
                    prod[
                        "downstream_metrics"
                    ],
                    run[
                        "metrics"
                    ][DOWNSTREAM],
                    abs_tol,
                    rel_tol,
                    small,
                ),
        }

        print(
            f"  intermediate {pct}%"
        )

        run = run_case(
            connectome,
            retinal,
            relay,
            graded,
            stimuli,
            effective_nodes=(
                INTERMEDIATE,
            ),
            voltage_nodes=(
                DOWNSTREAM,
            ),
            intervention_frame=(
                INTERMEDIATE_FRAME
            ),
            attenuation={
                INTERMEDIATE: dose,
            },
        )

        prod = pathway[
            "intermediate_interventions"
        ][str(pct)]

        path_result[
            "intermediate_interventions"
        ][str(pct)] = {
            "intermediate_effective_at_F147":
                numeric_compare(
                    prod[
                        "intermediate_effective_at_F147"
                    ],
                    run[
                        "effective"
                    ][INTERMEDIATE][INTERMEDIATE_FRAME],
                    abs_tol,
                    rel_tol,
                    small,
                ),

            "downstream_voltage_at_F147":
                numeric_compare(
                    prod[
                        "downstream_voltage_at_F147"
                    ],
                    run[
                        "voltage"
                    ][DOWNSTREAM][INTERMEDIATE_FRAME],
                    abs_tol,
                    rel_tol,
                    small,
                ),

            "downstream_metrics":
                compare_metrics(
                    prod[
                        "downstream_metrics"
                    ],
                    run[
                        "metrics"
                    ][DOWNSTREAM],
                    abs_tol,
                    rel_tol,
                    small,
                ),
        }

    conv_result = {
        "baseline": {
            "input_a_effective":
                numeric_compare(
                    conv_prod[
                        "baseline"
                    ][
                        "input_a_effective"
                    ],
                    baseline[
                        "effective"
                    ][INPUT_A][CONVERGENCE_FRAME],
                    abs_tol,
                    rel_tol,
                    small,
                ),

            "input_b_effective":
                numeric_compare(
                    conv_prod[
                        "baseline"
                    ][
                        "input_b_effective"
                    ],
                    baseline[
                        "effective"
                    ][INPUT_B][CONVERGENCE_FRAME],
                    abs_tol,
                    rel_tol,
                    small,
                ),

            "metrics":
                compare_metrics(
                    conv_prod[
                        "baseline"
                    ][
                        "metrics"
                    ],
                    baseline[
                        "metrics"
                    ][CONVERGENCE_TARGET],
                    abs_tol,
                    rel_tol,
                    small,
                ),
        },

        "doses": {},
    }

    print()
    print(
        "CONVERGENCE "
        "44274 + 55925 -> 55"
    )

    baseline_integrated = (
        baseline[
            "metrics"
        ][
            CONVERGENCE_TARGET
        ][
            "integrated_positive_voltage"
        ]
    )

    independent_combined_effects = []

    for pct in DOSES:
        dose = pct / 100.0

        conv_result[
            "doses"
        ][str(pct)] = {}

        independent_effects = {}

        for name, attenuation in (
            (
                "a_only",
                {INPUT_A: dose},
            ),
            (
                "b_only",
                {INPUT_B: dose},
            ),
            (
                "combined",
                {
                    INPUT_A: dose,
                    INPUT_B: dose,
                },
            ),
        ):
            print(
                f"  {pct}% {name}"
            )

            run = run_case(
                connectome,
                retinal,
                relay,
                graded,
                stimuli,
                effective_nodes=(
                    INPUT_A,
                    INPUT_B,
                ),
                voltage_nodes=(
                    CONVERGENCE_TARGET,
                ),
                intervention_frame=(
                    CONVERGENCE_FRAME
                ),
                attenuation=attenuation,
            )

            prod = conv_prod[
                "doses"
            ][str(pct)][name]

            integrated = (
                run[
                    "metrics"
                ][
                    CONVERGENCE_TARGET
                ][
                    "integrated_positive_voltage"
                ]
            )

            effect = (
                baseline_integrated
                - integrated
            )

            independent_effects[
                name
            ] = effect

            row = {
                "effect_magnitude":
                    numeric_compare(
                        prod[
                            "effect_magnitude"
                        ],
                        effect,
                        abs_tol,
                        rel_tol,
                        small,
                    ),

                "metrics":
                    compare_metrics(
                        prod[
                            "metrics"
                        ],
                        run[
                            "metrics"
                        ][CONVERGENCE_TARGET],
                        abs_tol,
                        rel_tol,
                        small,
                    ),
            }

            if name == "a_only":
                row[
                    "input_effective"
                ] = numeric_compare(
                    prod[
                        "input_effective"
                    ],
                    run[
                        "effective"
                    ][INPUT_A][CONVERGENCE_FRAME],
                    abs_tol,
                    rel_tol,
                    small,
                )

            elif name == "b_only":
                row[
                    "input_effective"
                ] = numeric_compare(
                    prod[
                        "input_effective"
                    ],
                    run[
                        "effective"
                    ][INPUT_B][CONVERGENCE_FRAME],
                    abs_tol,
                    rel_tol,
                    small,
                )

            else:
                row[
                    "input_a_effective"
                ] = numeric_compare(
                    prod[
                        "input_a_effective"
                    ],
                    run[
                        "effective"
                    ][INPUT_A][CONVERGENCE_FRAME],
                    abs_tol,
                    rel_tol,
                    small,
                )

                row[
                    "input_b_effective"
                ] = numeric_compare(
                    prod[
                        "input_b_effective"
                    ],
                    run[
                        "effective"
                    ][INPUT_B][CONVERGENCE_FRAME],
                    abs_tol,
                    rel_tol,
                    small,
                )

            conv_result[
                "doses"
            ][str(pct)][name] = row

        ea = independent_effects[
            "a_only"
        ]

        eb = independent_effects[
            "b_only"
        ]

        eab = independent_effects[
            "combined"
        ]

        independent_combined_effects.append(
            eab
        )

        conv_result[
            "doses"
        ][str(pct)][
            "combined_gt_each_single"
        ] = bool(
            eab > max(ea, eb)
        )

    conv_result[
        "combined_dose_monotonic"
    ] = bool(
        all(
            independent_combined_effects[i]
            <= independent_combined_effects[
                i + 1
            ]
            for i in range(3)
        )
    )

    conv_result[
        "all_combined_gt_single"
    ] = bool(
        all(
            conv_result[
                "doses"
            ][str(pct)][
                "combined_gt_each_single"
            ]
            for pct in DOSES
        )
    )

    hashes_after = {
        str(p): sha256_file(p)
        for p in frozen_paths
    }

    frozen_unchanged = (
        hashes_before
        == hashes_after
    )

    validation = {
        "frozen_artifacts_unchanged":
            frozen_unchanged,

        "direct_numeric_replication":
            all_pass(direct),

        "pathway_numeric_replication":
            all_pass(path_result),

        "convergence_numeric_replication":
            all_pass(conv_result),

        "convergence_combined_dose_monotonic":
            conv_result[
                "combined_dose_monotonic"
            ],

        "convergence_all_combined_gt_single":
            conv_result[
                "all_combined_gt_single"
            ],
    }

    result = {
        "schema":
            "mq5-6-replication-stability-v1",

        "experiment_id":
            "mq5-6-replication-stability-v1",

        "phase":
            "MQ-5.6",

        "classification":
            "confirmatory-replication",

        "software_commit":
            git_commit(),

        "implementation": {
            "type":
                "independent_full_reference_runtime",

            "inherits_production_runtime":
                False,

            "calls_production_step":
                False,

            "calls_production_effective_activity":
                False,

            "calls_mq5_intervention_runtime":
                False,

            "input_generation_reused":
                True,

            "neural_state_dtype":
                "float32",
        },

        "tolerance": {
            "absolute":
                abs_tol,

            "relative":
                rel_tol,

            "small_value_threshold":
                small,
        },

        "direct":
            direct,

        "pathway":
            path_result,

        "convergence":
            conv_result,

        "validation":
            validation,

        "frozen_artifact_sha256":
            hashes_before,

        "interpretation_status":
            "NOT_YET_INTERPRETED",

        "biological_causality_claim":
            False,

        "financial_semantics_used":
            False,
    }

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT.write_text(
        json.dumps(
            result,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    print()
    print("=" * 100)
    print(
        "MQ-5.6 REPLICATION COMPLETE"
    )
    print("=" * 100)

    for key, value in (
        validation.items()
    ):
        print(
            key.ljust(46),
            value,
        )

    print()
    print("JSON:", OUTPUT)


if __name__ == "__main__":
    main()
