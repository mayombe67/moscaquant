from __future__ import annotations

import hashlib

import numpy as np

from brain.mq3_2_anonymous_market_readout import (
    run_replay,
)
from brain.mq7_o1_o2_activation import (
    ARTIFACT_ID,
    csr_digest,
    load_inputs,
)
from oracle.d6_shock import (
    apply_shock_activity,
    build_shock,
)
from oracle.plasticity_modifier import (
    build_synaptic_modifier,
)
from oracle.plasticity_state import (
    apply_plasticity_update,
    build_empty_plasticity_state,
)


MARKET = "B"

EXPERIMENT = (
    "mq7-8-shock-plasticity-interaction-v1"
)

SESSION = "mq7-8-targeted-shock"

INTERVENTION_GENERATION = 32

PLASTICITY_PRE = 56393
PLASTICITY_POST = 68045

SHOCK_TARGET = 68045


def find_shock_seed() -> int:
    from oracle.d6_shock import (
        select_shock_target,
    )

    for seed in range(100000):
        _, target = select_shock_target(
            seed=seed,
            experiment_id=EXPERIMENT,
            session_id=SESSION,
        )

        if target == SHOCK_TARGET:
            return seed

    raise RuntimeError(
        "could not deterministically select "
        "SHOCK target 68045"
    )


def build_plasticity(
    connectome,
):
    weight = float(
        connectome[
            PLASTICITY_POST,
            PLASTICITY_PRE,
        ]
    )

    if weight == 0.0:
        raise RuntimeError(
            "validated SC-03 edge missing"
        )

    state = build_empty_plasticity_state()

    return apply_plasticity_update(
        state,
        presynaptic=PLASTICITY_PRE,
        postsynaptic=PLASTICITY_POST,
        baseline_artifact_id=ARTIFACT_ID,
        baseline_weight=weight,
        session_id="mq7-8-preload",
        evidence_reference=(
            "mq7-8-validated-sc03-edge"
        ),
    )


def build_shock_modifier(
    seed: int,
):
    intervention = build_shock(
        seed=seed,
        experiment_id=EXPERIMENT,
        session_id=SESSION,
        current_generation=(
            INTERVENTION_GENERATION
        ),
    )

    if (
        intervention.target_model_index
        != SHOCK_TARGET
    ):
        raise RuntimeError(
            "SHOCK target mismatch"
        )

    def modifier(
        activity: np.ndarray,
        generation: int,
    ) -> np.ndarray:
        return apply_shock_activity(
            effective_activity=activity,
            intervention=intervention,
            generation=generation,
        )

    return intervention, modifier


def summarize_difference(
    first,
    second,
):
    return {
        "voltage_identical": (
            first["voltage_trace_sha256"]
            == second["voltage_trace_sha256"]
        ),
        "spikes_identical": (
            first["spike_trace_sha256"]
            == second["spike_trace_sha256"]
        ),
        "scores_identical": (
            first["scores"]
            == second["scores"]
        ),
        "decision_identical": (
            first["decision"]
            == second["decision"]
        ),
        "score_deltas": {
            channel: (
                second["scores"][channel]
                - first["scores"][channel]
            )
            for channel
            in first["scores"]
        },
    }


def print_comparison(
    label,
    first,
    second,
):
    result = summarize_difference(
        first,
        second,
    )

    print()
    print("=" * 72)
    print(label)
    print("=" * 72)

    print(
        "voltage identical:",
        result["voltage_identical"],
    )

    print(
        "spikes identical:",
        result["spikes_identical"],
    )

    print(
        "scores identical:",
        result["scores_identical"],
    )

    print(
        "decision identical:",
        result["decision_identical"],
    )

    print(
        "score deltas:",
        result["score_deltas"],
    )

    return result


def main():
    (
        connectome,
        retinal_indices,
        channel_indices,
        release_gain,
    ) = load_inputs()

    before_digest = csr_digest(
        connectome
    )

    plasticity = build_plasticity(
        connectome
    )

    edge = plasticity.edges[0]

    if not np.isclose(
        edge.multiplier,
        0.95,
    ):
        raise RuntimeError(
            "expected one 0.95 "
            "plasticity update"
        )

    plasticity_modifier = (
        build_synaptic_modifier(
            plasticity
        )
    )

    shock_seed = find_shock_seed()

    (
        shock,
        shock_modifier,
    ) = build_shock_modifier(
        shock_seed
    )

    print("=" * 72)
    print(
        "MQ-7.8 SHOCK × PLASTICITY "
        "INTERACTION"
    )
    print("=" * 72)

    print("market:", MARKET)
    print(
        "plasticized edge:",
        f"{PLASTICITY_PRE}"
        f"->{PLASTICITY_POST}",
    )
    print(
        "plasticity multiplier:",
        edge.multiplier,
    )
    print(
        "SHOCK target:",
        shock.target_model_index,
    )
    print(
        "SHOCK seed:",
        shock_seed,
    )
    print(
        "intervention generation:",
        INTERVENTION_GENERATION,
    )

    #
    # B0 — baseline.
    #
    print()
    print("running B0 baseline...")

    b0 = run_replay(
        MARKET,
        connectome,
        retinal_indices,
        channel_indices,
        release_gain,
    )

    #
    # BP — plasticity only.
    #
    print("running BP plasticity only...")

    bp = run_replay(
        MARKET,
        connectome,
        retinal_indices,
        channel_indices,
        release_gain,
        synaptic_modifier=(
            plasticity_modifier
        ),
    )

    #
    # BS — SHOCK only.
    #
    print("running BS SHOCK only...")

    bs = run_replay(
        MARKET,
        connectome,
        retinal_indices,
        channel_indices,
        release_gain,
        activity_modifier=(
            shock_modifier
        ),
    )

    #
    # BPS — SHOCK + identical plasticity.
    #
    print(
        "running BPS SHOCK + plasticity..."
    )

    bps = run_replay(
        MARKET,
        connectome,
        retinal_indices,
        channel_indices,
        release_gain,
        activity_modifier=(
            shock_modifier
        ),
        synaptic_modifier=(
            plasticity_modifier
        ),
    )

    plasticity_alone = (
        print_comparison(
            "B0 vs BP — PLASTICITY ALONE",
            b0,
            bp,
        )
    )

    shock_with_plasticity = (
        print_comparison(
            "BS vs BPS — PLASTICITY "
            "UNDER SHOCK",
            bs,
            bps,
        )
    )

    shock_effect = print_comparison(
        "B0 vs BS — SHOCK EFFECT",
        b0,
        bs,
    )

    combined_effect = print_comparison(
        "B0 vs BPS — COMBINED EFFECT",
        b0,
        bps,
    )

    print()
    print("=" * 72)
    print("INTERACTION CLASSIFICATION")
    print("=" * 72)

    if (
        plasticity_alone[
            "voltage_identical"
        ]
        and not shock_with_plasticity[
            "voltage_identical"
        ]
    ):
        print(
            "RESULT: PERTURBATION-DEPENDENT "
            "PLASTICITY EXPRESSION SUPPORTED"
        )
    elif (
        not plasticity_alone[
            "voltage_identical"
        ]
    ):
        print(
            "RESULT: PLASTICITY ALREADY "
            "EXPRESSED WITHOUT SHOCK"
        )
    else:
        print(
            "RESULT: NO MEASURABLE "
            "PLASTICITY EXPRESSION"
        )

    if (
        csr_digest(connectome)
        != before_digest
    ):
        raise RuntimeError(
            "structural connectome mutated"
        )

    print()
    print(
        "connectome unchanged: True"
    )
    print(
        "MQ-7.8 COMPLETE"
    )


if __name__ == "__main__":
    main()
