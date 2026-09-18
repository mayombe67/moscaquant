from __future__ import annotations

import json
from pathlib import Path

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
    "mq7-12-downstream-mediation-v1"
)

SESSION = "mq7-12-shock-56393"

INTERVENTION_GENERATION = 32

PLASTICITY_PRE = 56393
PLASTICITY_POST = 68045

DOWNSTREAM_PRE = 68045
DOWNSTREAM_POST = 1273

SHOCK_TARGET = 56393

OUTPUT = (
    Path.home()
    / "moscaquant-data"
    / "experiments"
    / "mq7-12-downstream-mediation-v1.json"
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
        session_id="mq7-12-preload",
        evidence_reference=(
            "mq7-12-validated-sc03-edge"
        ),
    )

    if not np.isclose(
        state.edges[0].multiplier,
        0.95,
    ):
        raise RuntimeError(
            "expected plasticity multiplier 0.95"
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
        "could not select SHOCK target 56393"
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
        DOWNSTREAM_POST
    ].tocsr()

    candidates = []

    for pre, weight in zip(
        row.indices,
        row.data,
    ):
        pre = int(pre)
        weight = float(weight)

        if pre == DOWNSTREAM_PRE:
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
            "no control edge into 1273"
        )

    candidates.sort()

    _negative_abs, pre, weight = (
        candidates[0]
    )

    return (
        pre,
        DOWNSTREAM_POST,
        weight,
    )


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
    score_deltas = {
        channel: (
            second["scores"][channel]
            - first["scores"][channel]
        )
        for channel
        in first["scores"]
    }

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
        "score_deltas":
            score_deltas,
        "abs_dn_c1_delta":
            abs(
                float(
                    score_deltas["DN-C1"]
                )
            ),
    }


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

    print(
        "|DN-C1 delta|:",
        result["abs_dn_c1_delta"],
    )

    return result


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

    downstream_weight = float(
        connectome[
            DOWNSTREAM_POST,
            DOWNSTREAM_PRE,
        ]
    )

    if downstream_weight == 0.0:
        raise RuntimeError(
            "validated downstream edge missing"
        )

    plasticity = build_plasticity(
        connectome
    )

    plasticity_modifier = (
        build_synaptic_modifier(
            plasticity
        )
    )

    downstream_ablation = (
        ablation_modifier(
            presynaptic=DOWNSTREAM_PRE,
            postsynaptic=DOWNSTREAM_POST,
            baseline_weight=(
                downstream_weight
            ),
        )
    )

    (
        control_pre,
        control_post,
        control_weight,
    ) = choose_control_edge(
        connectome
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
        "MQ-7.12 DOWNSTREAM MEDIATION"
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
        "plasticized edge:",
        f"{PLASTICITY_PRE}"
        f"->{PLASTICITY_POST}",
    )

    print(
        "downstream edge:",
        f"{DOWNSTREAM_PRE}"
        f"->{DOWNSTREAM_POST}",
        "weight=",
        downstream_weight,
    )

    print(
        "control edge:",
        f"{control_pre}"
        f"->{control_post}",
        "weight=",
        control_weight,
    )

    #
    # Downstream route intact.
    #
    di = replay(
        connectome=connectome,
        retinal_indices=retinal_indices,
        channel_indices=channel_indices,
        release_gain=release_gain,
        shock_modifier=shock_modifier,
    )

    dpi = replay(
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
    # 68045 -> 1273 ablated.
    #
    da = replay(
        connectome=connectome,
        retinal_indices=retinal_indices,
        channel_indices=channel_indices,
        release_gain=release_gain,
        shock_modifier=shock_modifier,
        synaptic_modifier=(
            downstream_ablation
        ),
    )

    dpa = replay(
        connectome=connectome,
        retinal_indices=retinal_indices,
        channel_indices=channel_indices,
        release_gain=release_gain,
        shock_modifier=shock_modifier,
        synaptic_modifier=(
            compose_synaptic(
                downstream_ablation,
                plasticity_modifier,
            )
        ),
    )

    #
    # Control edge into 1273 ablated.
    #
    dc = replay(
        connectome=connectome,
        retinal_indices=retinal_indices,
        channel_indices=channel_indices,
        release_gain=release_gain,
        shock_modifier=shock_modifier,
        synaptic_modifier=(
            control_ablation
        ),
    )

    dpc = replay(
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
        "DI vs DPI — DOWNSTREAM ROUTE INTACT",
        di,
        dpi,
    )

    ablated = print_result(
        "DA vs DPA — 68045->1273 ABLATED",
        da,
        dpa,
    )

    control = print_result(
        "DC vs DPC — CONTROL EDGE ABLATED",
        dc,
        dpc,
    )

    intact_effect = (
        intact["abs_dn_c1_delta"]
    )

    ablated_effect = (
        ablated["abs_dn_c1_delta"]
    )

    control_effect = (
        control["abs_dn_c1_delta"]
    )

    if intact_effect > 0.0:
        attenuation = (
            1.0
            - (
                ablated_effect
                / intact_effect
            )
        )
    else:
        attenuation = None

    print()
    print("=" * 72)
    print("MEDIATION CLASSIFICATION")
    print("=" * 72)

    print(
        "intact |DN-C1|:",
        intact_effect,
    )

    print(
        "downstream-ablated |DN-C1|:",
        ablated_effect,
    )

    print(
        "control-ablated |DN-C1|:",
        control_effect,
    )

    print(
        "downstream attenuation:",
        attenuation,
    )

    intact_expression = (
        not intact["voltage_identical"]
        or not intact["scores_identical"]
    )

    ablated_expression = (
        not ablated["voltage_identical"]
        or not ablated["scores_identical"]
    )

    control_expression = (
        not control["voltage_identical"]
        or not control["scores_identical"]
    )

    if (
        intact_expression
        and not ablated_expression
        and control_expression
    ):
        classification = (
            "DOWNSTREAM MEDIATION "
            "SUPPORTED — COMPLETE COLLAPSE"
        )

    elif (
        intact_expression
        and ablated_effect < intact_effect
        and control_expression
    ):
        classification = (
            "DOWNSTREAM MEDIATION "
            "SUPPORTED — PARTIAL ATTENUATION"
        )

    else:
        classification = (
            "DOWNSTREAM MEDIATION "
            "NOT SUPPORTED"
        )

    print(
        "RESULT:",
        classification,
    )

    if (
        csr_digest(connectome)
        != digest_before
    ):
        raise RuntimeError(
            "structural connectome mutated"
        )

    print(
        "connectome unchanged: True"
    )

    result = {
        "schema_version":
            "mq7-downstream-mediation/v1",
        "market_condition":
            MARKET,
        "shock_target":
            SHOCK_TARGET,
        "shock_seed":
            seed,
        "plasticized_edge": [
            PLASTICITY_PRE,
            PLASTICITY_POST,
        ],
        "downstream_edge": {
            "presynaptic":
                DOWNSTREAM_PRE,
            "postsynaptic":
                DOWNSTREAM_POST,
            "weight":
                downstream_weight,
        },
        "control_edge": {
            "presynaptic":
                control_pre,
            "postsynaptic":
                control_post,
            "weight":
                control_weight,
        },
        "intact":
            intact,
        "downstream_ablated":
            ablated,
        "control_ablated":
            control,
        "downstream_attenuation":
            attenuation,
        "classification":
            classification,
        "connectome_unchanged":
            True,
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
        + "\n"
    )

    print(
        "results:",
        OUTPUT,
    )

    print(
        "MQ-7.12 COMPLETE"
    )


if __name__ == "__main__":
    main()
