from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from brain.mq3_2_anonymous_market_readout import run_replay
from brain.mq7_o1_o2_activation import (
    ARTIFACT_ID,
    csr_digest,
    load_inputs,
)
from oracle.d6_shock import (
    apply_shock_activity,
    build_shock,
    select_shock_target,
)
from oracle.plasticity_modifier import build_synaptic_modifier
from oracle.plasticity_state import (
    apply_plasticity_update,
    build_empty_plasticity_state,
)


MARKET = "B"

EXPERIMENT = "mq7-15-differential-trace-v1"
SESSION = "mq7-15-shock-56393"

SHOCK_TARGET = 56393
INTERVENTION_GENERATION = 32

TRACE_START = 32
TRACE_END = 44

THRESHOLD = 1e-15

PLASTICITY_PRE = 56393
PLASTICITY_POST = 68045

REFERENCE_NODES = (
    56393,
    68045,
    1273,
)

OUTPUT = (
    Path.home()
    / "moscaquant-data"
    / "experiments"
    / "mq7-15-differential-trace-v1.json"
)


def build_plasticity(connectome):
    weight = float(
        connectome[
            PLASTICITY_POST,
            PLASTICITY_PRE,
        ]
    )

    if weight == 0.0:
        raise RuntimeError(
            "validated plasticity edge missing"
        )

    state = build_empty_plasticity_state()

    state = apply_plasticity_update(
        state,
        presynaptic=PLASTICITY_PRE,
        postsynaptic=PLASTICITY_POST,
        baseline_artifact_id=ARTIFACT_ID,
        baseline_weight=weight,
        session_id="mq7-15-preload",
        evidence_reference="mq7-15-sc03",
    )

    if not np.isclose(
        state.edges[0].multiplier,
        0.95,
    ):
        raise RuntimeError(
            "expected multiplier 0.95"
        )

    return state


def find_shock_seed():
    for seed in range(100000):
        _, target = select_shock_target(
            seed=seed,
            experiment_id=EXPERIMENT,
            session_id=SESSION,
        )

        if target == SHOCK_TARGET:
            return seed

    raise RuntimeError(
        "SHOCK seed not found"
    )


def build_shock_modifier():
    seed = find_shock_seed()

    intervention = build_shock(
        seed=seed,
        experiment_id=EXPERIMENT,
        session_id=SESSION,
        current_generation=INTERVENTION_GENERATION,
    )

    if (
        intervention.target_model_index
        != SHOCK_TARGET
    ):
        raise RuntimeError(
            "SHOCK target mismatch"
        )

    def modifier(
        activity,
        generation,
    ):
        return apply_shock_activity(
            effective_activity=activity,
            intervention=intervention,
            generation=generation,
        )

    return seed, modifier


class TraceRecorder:
    def __init__(
        self,
        downstream_modifier=None,
    ):
        self.downstream_modifier = (
            downstream_modifier
        )

        self.generation = 0

        self.activity = {}
        self.synaptic = {}

    def __call__(
        self,
        activity,
        synaptic,
    ):
        generation = self.generation
        self.generation += 1

        if self.downstream_modifier is None:
            output = synaptic
        else:
            output = self.downstream_modifier(
                activity,
                synaptic,
            )

        if (
            TRACE_START
            <= generation
            <= TRACE_END
        ):
            self.activity[generation] = np.asarray(
                activity,
                dtype=np.float64,
            ).copy()

            self.synaptic[generation] = np.asarray(
                output,
                dtype=np.float64,
            ).copy()

        return output


def analyze_matrix_pair(
    *,
    baseline,
    adaptive,
    neuron_count,
):
    first_generation = np.full(
        neuron_count,
        -1,
        dtype=np.int64,
    )

    peak_delta = np.zeros(
        neuron_count,
        dtype=np.float64,
    )

    peak_generation = np.full(
        neuron_count,
        -1,
        dtype=np.int64,
    )

    per_generation = []

    for generation in range(
        TRACE_START,
        TRACE_END + 1,
    ):
        first = baseline[generation]
        second = adaptive[generation]

        delta = np.abs(
            second - first
        )

        active = delta > THRESHOLD

        count = int(
            np.count_nonzero(active)
        )

        per_generation.append({
            "generation": generation,
            "divergent_neuron_count": count,
            "max_abs_delta": float(
                delta.max()
            ),
        })

        new = (
            active
            & (first_generation < 0)
        )

        first_generation[new] = (
            generation
        )

        larger = (
            delta > peak_delta
        )

        peak_delta[larger] = (
            delta[larger]
        )

        peak_generation[larger] = (
            generation
        )

    return (
        first_generation,
        peak_delta,
        peak_generation,
        per_generation,
    )


def rank_nodes(
    *,
    first_generation,
    peak_delta,
    peak_generation,
    dn_c1,
    limit=50,
):
    indices = np.flatnonzero(
        peak_delta > THRESHOLD
    )

    ordered = sorted(
        (
            int(index)
            for index in indices
        ),
        key=lambda index: (
            -float(
                peak_delta[index]
            ),
            int(index),
        ),
    )

    result = []

    for index in ordered[:limit]:
        result.append({
            "model_index": index,
            "first_generation":
                int(
                    first_generation[
                        index
                    ]
                ),
            "peak_abs_delta":
                float(
                    peak_delta[
                        index
                    ]
                ),
            "peak_generation":
                int(
                    peak_generation[
                        index
                    ]
                ),
            "is_dn_c1":
                index in dn_c1,
        })

    return result


def reference_trace(
    *,
    baseline,
    adaptive,
    node,
):
    rows = []

    for generation in range(
        TRACE_START,
        TRACE_END + 1,
    ):
        first = float(
            baseline[
                generation
            ][node]
        )

        second = float(
            adaptive[
                generation
            ][node]
        )

        rows.append({
            "generation":
                generation,
            "baseline":
                first,
            "adaptive":
                second,
            "delta":
                second - first,
        })

    return rows


def main():
    (
        connectome,
        retinal_indices,
        channel_indices,
        release_gain,
    ) = load_inputs()

    digest_before = csr_digest(
        connectome
    )

    dn_c1 = {
        int(index)
        for index
        in channel_indices[
            "DN-C1"
        ]
    }

    plasticity = build_plasticity(
        connectome
    )

    plasticity_modifier = (
        build_synaptic_modifier(
            plasticity
        )
    )

    seed, shock_modifier = (
        build_shock_modifier()
    )

    baseline_recorder = TraceRecorder()

    adaptive_recorder = TraceRecorder(
        downstream_modifier=(
            plasticity_modifier
        )
    )

    print("=" * 72)
    print(
        "MQ-7.15 DYNAMIC DIFFERENTIAL TRACE"
    )
    print("=" * 72)

    print(
        "market:",
        MARKET,
    )

    print(
        "SHOCK target:",
        SHOCK_TARGET,
    )

    print(
        "SHOCK seed:",
        seed,
    )

    print(
        "trace window:",
        TRACE_START,
        "through",
        TRACE_END,
    )

    print(
        "threshold:",
        THRESHOLD,
    )

    print()
    print(
        "running SHOCK control..."
    )

    baseline_result = run_replay(
        MARKET,
        connectome,
        retinal_indices,
        channel_indices,
        release_gain,
        activity_modifier=(
            shock_modifier
        ),
        synaptic_modifier=(
            baseline_recorder
        ),
    )

    print(
        "running SHOCK + plasticity..."
    )

    adaptive_result = run_replay(
        MARKET,
        connectome,
        retinal_indices,
        channel_indices,
        release_gain,
        activity_modifier=(
            shock_modifier
        ),
        synaptic_modifier=(
            adaptive_recorder
        ),
    )

    generations = set(
        range(
            TRACE_START,
            TRACE_END + 1,
        )
    )

    if (
        set(
            baseline_recorder.activity
        )
        != generations
        or set(
            adaptive_recorder.activity
        )
        != generations
    ):
        raise RuntimeError(
            "trace window incomplete"
        )

    neuron_count = (
        connectome.shape[0]
    )

    (
        activity_first,
        activity_peak,
        activity_peak_generation,
        activity_per_generation,
    ) = analyze_matrix_pair(
        baseline=(
            baseline_recorder.activity
        ),
        adaptive=(
            adaptive_recorder.activity
        ),
        neuron_count=neuron_count,
    )

    (
        synaptic_first,
        synaptic_peak,
        synaptic_peak_generation,
        synaptic_per_generation,
    ) = analyze_matrix_pair(
        baseline=(
            baseline_recorder.synaptic
        ),
        adaptive=(
            adaptive_recorder.synaptic
        ),
        neuron_count=neuron_count,
    )

    activity_rank = rank_nodes(
        first_generation=(
            activity_first
        ),
        peak_delta=activity_peak,
        peak_generation=(
            activity_peak_generation
        ),
        dn_c1=dn_c1,
    )

    synaptic_rank = rank_nodes(
        first_generation=(
            synaptic_first
        ),
        peak_delta=synaptic_peak,
        peak_generation=(
            synaptic_peak_generation
        ),
        dn_c1=dn_c1,
    )

    print()
    print("=" * 72)
    print(
        "ACTIVITY DIVERGENCE BY GENERATION"
    )
    print("=" * 72)

    for row in activity_per_generation:
        print(
            "g",
            row["generation"],
            "count=",
            row[
                "divergent_neuron_count"
            ],
            "max=",
            row[
                "max_abs_delta"
            ],
        )

    print()
    print("=" * 72)
    print(
        "SYNAPTIC DIVERGENCE BY GENERATION"
    )
    print("=" * 72)

    for row in synaptic_per_generation:
        print(
            "g",
            row["generation"],
            "count=",
            row[
                "divergent_neuron_count"
            ],
            "max=",
            row[
                "max_abs_delta"
            ],
        )

    print()
    print("=" * 72)
    print(
        "TOP ACTIVITY-DIVERGENCE NODES"
    )
    print("=" * 72)

    for rank, row in enumerate(
        activity_rank[:20],
        start=1,
    ):
        print(
            rank,
            "node=",
            row["model_index"],
            "first=",
            row["first_generation"],
            "peak=",
            row["peak_abs_delta"],
            "peak_g=",
            row["peak_generation"],
            "DN-C1=",
            row["is_dn_c1"],
        )

    print()
    print("=" * 72)
    print(
        "TOP SYNAPTIC-DIVERGENCE NODES"
    )
    print("=" * 72)

    for rank, row in enumerate(
        synaptic_rank[:20],
        start=1,
    ):
        print(
            rank,
            "node=",
            row["model_index"],
            "first=",
            row["first_generation"],
            "peak=",
            row["peak_abs_delta"],
            "peak_g=",
            row["peak_generation"],
            "DN-C1=",
            row["is_dn_c1"],
        )

    print()
    print("=" * 72)
    print(
        "REFERENCE NODE TIMING"
    )
    print("=" * 72)

    for node in REFERENCE_NODES:
        print()
        print(
            "node:",
            node,
        )

        print(
            "activity first:",
            int(
                activity_first[
                    node
                ]
            ),
        )

        print(
            "activity peak:",
            float(
                activity_peak[
                    node
                ]
            ),
        )

        print(
            "synaptic first:",
            int(
                synaptic_first[
                    node
                ]
            ),
        )

        print(
            "synaptic peak:",
            float(
                synaptic_peak[
                    node
                ]
            ),
        )

    if (
        csr_digest(connectome)
        != digest_before
    ):
        raise RuntimeError(
            "structural connectome mutated"
        )

    payload = {
        "schema_version":
            "mq7-differential-trace/v1",
        "market_condition":
            MARKET,
        "shock_target":
            SHOCK_TARGET,
        "shock_seed":
            seed,
        "trace_window": [
            TRACE_START,
            TRACE_END,
        ],
        "threshold":
            THRESHOLD,
        "plasticized_edge": [
            PLASTICITY_PRE,
            PLASTICITY_POST,
        ],
        "activity_per_generation":
            activity_per_generation,
        "synaptic_per_generation":
            synaptic_per_generation,
        "top_activity_nodes":
            activity_rank,
        "top_synaptic_nodes":
            synaptic_rank,
        "reference_nodes": {
            str(node): {
                "activity_trace":
                    reference_trace(
                        baseline=(
                            baseline_recorder.activity
                        ),
                        adaptive=(
                            adaptive_recorder.activity
                        ),
                        node=node,
                    ),
                "synaptic_trace":
                    reference_trace(
                        baseline=(
                            baseline_recorder.synaptic
                        ),
                        adaptive=(
                            adaptive_recorder.synaptic
                        ),
                        node=node,
                    ),
            }
            for node in REFERENCE_NODES
        },
        "final_voltage_identical":
            baseline_result[
                "voltage_trace_sha256"
            ]
            == adaptive_result[
                "voltage_trace_sha256"
            ],
        "final_spikes_identical":
            baseline_result[
                "spike_trace_sha256"
            ]
            == adaptive_result[
                "spike_trace_sha256"
            ],
        "final_scores_identical":
            baseline_result[
                "scores"
            ]
            == adaptive_result[
                "scores"
            ],
        "final_decision_identical":
            baseline_result[
                "decision"
            ]
            == adaptive_result[
                "decision"
            ],
        "connectome_unchanged":
            True,
    }

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT.write_text(
        json.dumps(
            payload,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )

    print()
    print(
        "connectome unchanged: True"
    )

    print(
        "results:",
        OUTPUT,
    )

    print(
        "MQ-7.15 COMPLETE"
    )


if __name__ == "__main__":
    main()
