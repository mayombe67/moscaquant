from __future__ import annotations

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
    select_shock_target,
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
    "mq7-11-causal-route-ablation-v1"
)

SESSION = "mq7-11-shock-56393"

INTERVENTION_GENERATION = 32

PLASTICITY_PRE = 56393
PLASTICITY_POST = 68045

SHOCK_TARGET = 56393


def build_plasticity(connectome):
    weight = float(
        connectome[
            PLASTICITY_POST,
            PLASTICITY_PRE,
        ]
    )

    if weight == 0.0:
        raise RuntimeError(
            "validated edge missing"
        )

    state = build_empty_plasticity_state()

    state = apply_plasticity_update(
        state,
        presynaptic=PLASTICITY_PRE,
        postsynaptic=PLASTICITY_POST,
        baseline_artifact_id=ARTIFACT_ID,
        baseline_weight=weight,
        session_id="mq7-11-preload",
        evidence_reference=(
            "mq7-11-validated-sc03-edge"
        ),
    )

    if not np.isclose(
        state.edges[0].multiplier,
        0.95,
    ):
        raise RuntimeError(
            "expected 0.95 multiplier"
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
        "seed not found"
    )


def build_shock_modifier():
    seed = find_shock_seed()

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
        activity,
        generation,
    ):
        return apply_shock_activity(
            effective_activity=activity,
            intervention=intervention,
            generation=generation,
        )

    return seed, modifier


def choose_control_edge(
    connectome,
):
    row = connectome[
        PLASTICITY_POST
    ].tocsr()

    candidates = []

    for pre, weight in zip(
        row.indices,
        row.data,
    ):
        pre = int(pre)
        weight = float(weight)

        if pre == PLASTICITY_PRE:
            continue

        if weight == 0.0:
            continue

        candidates.append(
            (
                -abs(weight),
                pre,
                weight,
            )
        )

    if not candidates:
        raise RuntimeError(
            "no control edge available"
        )

    candidates.sort()

    _neg_abs, pre, weight = (
        candidates[0]
    )

    return pre, PLASTICITY_POST, weight


def ablation_modifier(
    *,
    presynaptic,
    postsynaptic,
    baseline_weight,
):
    def modifier(
        activity,
        synaptic,
    ):
        output = np.array(
            synaptic,
            copy=True,
        )

        output[postsynaptic] -= (
            baseline_weight
            * activity[presynaptic]
        )

        return output

    return modifier


def compose_synaptic(
    *modifiers,
):
    modifiers = [
        modifier
        for modifier in modifiers
        if modifier is not None
    ]

    def combined(
        activity,
        synaptic,
    ):
        output = synaptic

        for modifier in modifiers:
            output = modifier(
                activity,
                output,
            )

        return output

    return combined


def difference(
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


def print_result(
    label,
    first,
    second,
):
    result = difference(
        first,
        second,
    )

    print()
    print("=" * 72)
    print(label)
    print("=" * 72)

    for key in (
        "voltage_identical",
        "spikes_identical",
        "scores_identical",
        "decision_identical",
    ):
        print(
            key + ":",
            result[key],
        )

    print(
        "score deltas:",
        result["score_deltas"],
    )

    return result


def replay(
    *,
    connectome,
    retinal_indices,
    channel_indices,
    release_gain,
    shock_modifier,
    synaptic_modifier=None,
):
    return run_replay(
        MARKET,
        connectome,
        retinal_indices,
        channel_indices,
        release_gain,
        activity_modifier=(
            shock_modifier
        ),
        synaptic_modifier=(
            synaptic_modifier
        ),
    )


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

    plasticity = build_plasticity(
        connectome
    )

    plasticity_modifier = (
        build_synaptic_modifier(
            plasticity
        )
    )

    validated_weight = float(
        connectome[
            PLASTICITY_POST,
            PLASTICITY_PRE,
        ]
    )

    (
        control_pre,
        control_post,
        control_weight,
    ) = choose_control_edge(
        connectome
    )

    validated_ablation = (
        ablation_modifier(
            presynaptic=PLASTICITY_PRE,
            postsynaptic=PLASTICITY_POST,
            baseline_weight=(
                validated_weight
            ),
        )
    )

    control_ablation = (
        ablation_modifier(
            presynaptic=control_pre,
            postsynaptic=control_post,
            baseline_weight=(
                control_weight
            ),
        )
    )

    seed, shock_modifier = (
        build_shock_modifier()
    )

    print("=" * 72)
    print(
        "MQ-7.11 CAUSAL ROUTE ABLATION"
    )
    print("=" * 72)

    print("market:", MARKET)
    print(
        "SHOCK target:",
        SHOCK_TARGET,
    )
    print(
        "SHOCK seed:",
        seed,
    )
    print(
        "validated edge:",
        f"{PLASTICITY_PRE}"
        f"->{PLASTICITY_POST}",
        "weight=",
        validated_weight,
    )
    print(
        "control edge:",
        f"{control_pre}"
        f"->{control_post}",
        "weight=",
        control_weight,
    )

    #
    # Intact route.
    #
    si = replay(
        connectome=connectome,
        retinal_indices=retinal_indices,
        channel_indices=channel_indices,
        release_gain=release_gain,
        shock_modifier=shock_modifier,
    )

    spi = replay(
        connectome=connectome,
        retinal_indices=retinal_indices,
        channel_indices=channel_indices,
        release_gain=release_gain,
        shock_modifier=shock_modifier,
        synaptic_modifier=(
            plasticity_modifier
        ),
    )

    #
    # Validated route ablated.
    #
    sa = replay(
        connectome=connectome,
        retinal_indices=retinal_indices,
        channel_indices=channel_indices,
        release_gain=release_gain,
        shock_modifier=shock_modifier,
        synaptic_modifier=(
            validated_ablation
        ),
    )

    #
    # Once the edge is fully ablated, its
    # 0.95 overlay has no remaining signal
    # to modify.
    #
    spa = replay(
        connectome=connectome,
        retinal_indices=retinal_indices,
        channel_indices=channel_indices,
        release_gain=release_gain,
        shock_modifier=shock_modifier,
        synaptic_modifier=(
            validated_ablation
        ),
    )

    #
    # Control lesion.
    #
    sc = replay(
        connectome=connectome,
        retinal_indices=retinal_indices,
        channel_indices=channel_indices,
        release_gain=release_gain,
        shock_modifier=shock_modifier,
        synaptic_modifier=(
            control_ablation
        ),
    )

    spc = replay(
        connectome=connectome,
        retinal_indices=retinal_indices,
        channel_indices=channel_indices,
        release_gain=release_gain,
        shock_modifier=shock_modifier,
        synaptic_modifier=(
            compose_synaptic(
                control_ablation,
                plasticity_modifier,
            )
        ),
    )

    intact = print_result(
        "SI vs SPI — ROUTE INTACT",
        si,
        spi,
    )

    ablated = print_result(
        "SA vs SPA — VALIDATED EDGE ABLATED",
        sa,
        spa,
    )

    control = print_result(
        "SC vs SPC — CONTROL EDGE ABLATED",
        sc,
        spc,
    )

    print()
    print("=" * 72)
    print("CAUSAL CLASSIFICATION")
    print("=" * 72)

    intact_expression = (
        not intact[
            "voltage_identical"
        ]
        or not intact[
            "scores_identical"
        ]
    )

    ablated_expression = (
        not ablated[
            "voltage_identical"
        ]
        or not ablated[
            "scores_identical"
        ]
    )

    control_expression = (
        not control[
            "voltage_identical"
        ]
        or not control[
            "scores_identical"
        ]
    )

    print(
        "intact route expresses plasticity:",
        intact_expression,
    )

    print(
        "validated-edge ablation "
        "expresses plasticity:",
        ablated_expression,
    )

    print(
        "control-edge ablation "
        "expresses plasticity:",
        control_expression,
    )

    if (
        intact_expression
        and not ablated_expression
        and control_expression
    ):
        print(
            "RESULT: CAUSAL ROUTE "
            "DEPENDENCE SUPPORTED"
        )

    elif (
        intact_expression
        and not ablated_expression
    ):
        print(
            "RESULT: VALIDATED EDGE "
            "DEPENDENCE SUPPORTED; "
            "CONTROL SPECIFICITY "
            "NOT ESTABLISHED"
        )

    else:
        print(
            "RESULT: CAUSAL ROUTE "
            "DEPENDENCE NOT SUPPORTED"
        )

    if (
        csr_digest(connectome)
        != digest_before
    ):
        raise RuntimeError(
            "structural connectome mutated"
        )

    print()
    print(
        "connectome unchanged: True"
    )
    print(
        "MQ-7.11 COMPLETE"
    )


if __name__ == "__main__":
    main()
