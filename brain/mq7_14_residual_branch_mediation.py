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

EXPERIMENT = "mq7-14-residual-branch-mediation-v1"
SESSION = "mq7-14-shock-56393"

INTERVENTION_GENERATION = 32

SHOCK_TARGET = 56393

PLASTICITY_PRE = 56393
PLASTICITY_POST = 68045

SOURCE = 68045

PRIMARY_TARGETS = (
    18444,
    107,
    6647,
)

MQ713 = (
    Path.home()
    / "moscaquant-data"
    / "experiments"
    / "mq7-13-residual-route-discovery-v1.json"
)

OUTPUT = (
    Path.home()
    / "moscaquant-data"
    / "experiments"
    / "mq7-14-residual-branch-mediation-v1.json"
)


def build_plasticity(connectome):
    weight = float(
        connectome[
            PLASTICITY_POST,
            PLASTICITY_PRE,
        ]
    )

    state = build_empty_plasticity_state()

    state = apply_plasticity_update(
        state,
        presynaptic=PLASTICITY_PRE,
        postsynaptic=PLASTICITY_POST,
        baseline_artifact_id=ARTIFACT_ID,
        baseline_weight=weight,
        session_id="mq7-14-preload",
        evidence_reference="mq7-14-sc03",
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


def edge_weight(
    connectome,
    pre,
    post,
):
    return float(
        connectome[
            post,
            pre,
        ]
    )


def choose_control_target(
    connectome,
):
    payload = json.loads(
        MQ713.read_text()
    )

    excluded = {
        1273,
        *PRIMARY_TARGETS,
    }

    for route in payload[
        "top_residual_routes"
    ]:
        path = route["path"]

        for node in path[1:-1]:
            excluded.add(
                int(node)
            )

    column = connectome[
        :,
        SOURCE,
    ].tocoo()

    candidates = []

    for post, weight in zip(
        column.row,
        column.data,
    ):
        post = int(post)
        weight = float(weight)

        if post in excluded:
            continue

        if weight == 0.0:
            continue

        candidates.append(
            (
                -abs(weight),
                post,
                weight,
            )
        )

    if not candidates:
        raise RuntimeError(
            "no control branch available"
        )

    candidates.sort()

    _neg_abs, post, weight = (
        candidates[0]
    )

    return post, weight


def ablation_modifier(
    connectome,
    targets,
):
    weights = {
        int(target):
            edge_weight(
                connectome,
                SOURCE,
                int(target),
            )
        for target in targets
    }

    for target, weight in (
        weights.items()
    ):
        if weight == 0.0:
            raise RuntimeError(
                f"missing edge "
                f"{SOURCE}->{target}"
            )

    def modifier(
        activity,
        synaptic,
    ):
        output = np.array(
            synaptic,
            copy=True,
        )

        for target, weight in (
            weights.items()
        ):
            output[target] -= (
                weight
                * activity[SOURCE]
            )

        return output

    return modifier, weights


def compose(
    *modifiers,
):
    active = [
        modifier
        for modifier in modifiers
        if modifier is not None
    ]

    def combined(
        activity,
        synaptic,
    ):
        output = synaptic

        for modifier in active:
            output = modifier(
                activity,
                output,
            )

        return output

    return combined


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
        activity_modifier=shock_modifier,
        synaptic_modifier=synaptic_modifier,
    )


def difference(
    first,
    second,
):
    deltas = {
        channel:
            second["scores"][channel]
            - first["scores"][channel]
        for channel
        in first["scores"]
    }

    return {
        "voltage_identical":
            first[
                "voltage_trace_sha256"
            ]
            == second[
                "voltage_trace_sha256"
            ],
        "spikes_identical":
            first[
                "spike_trace_sha256"
            ]
            == second[
                "spike_trace_sha256"
            ],
        "scores_identical":
            first["scores"]
            == second["scores"],
        "decision_identical":
            first["decision"]
            == second["decision"],
        "score_deltas":
            deltas,
        "abs_dn_c1_delta":
            abs(
                float(
                    deltas["DN-C1"]
                )
            ),
    }


def run_pair(
    *,
    label,
    lesion,
    plasticity_modifier,
    common,
):
    without = replay(
        **common,
        synaptic_modifier=lesion,
    )

    with_plasticity = replay(
        **common,
        synaptic_modifier=(
            compose(
                lesion,
                plasticity_modifier,
            )
        ),
    )

    result = difference(
        without,
        with_plasticity,
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

    common = {
        "connectome":
            connectome,
        "retinal_indices":
            retinal_indices,
        "channel_indices":
            channel_indices,
        "release_gain":
            release_gain,
        "shock_modifier":
            shock_modifier,
    }

    print("=" * 72)
    print(
        "MQ-7.14 RESIDUAL BRANCH MEDIATION"
    )
    print("=" * 72)

    print(
        "SHOCK target:",
        SHOCK_TARGET,
    )

    print(
        "SHOCK seed:",
        seed,
    )

    #
    # Intact reference.
    #
    intact = run_pair(
        label="INTACT",
        lesion=None,
        plasticity_modifier=(
            plasticity_modifier
        ),
        common=common,
    )

    intact_effect = (
        intact["abs_dn_c1_delta"]
    )

    records = {}

    #
    # Individual primary branches.
    #
    for target in PRIMARY_TARGETS:
        lesion, weights = (
            ablation_modifier(
                connectome,
                [target],
            )
        )

        result = run_pair(
            label=(
                f"ABLATE "
                f"{SOURCE}->{target}"
            ),
            lesion=lesion,
            plasticity_modifier=(
                plasticity_modifier
            ),
            common=common,
        )

        effect = (
            result[
                "abs_dn_c1_delta"
            ]
        )

        attenuation = (
            1.0
            - effect
            / intact_effect
        )

        print(
            "attenuation:",
            attenuation,
        )

        records[
            str(target)
        ] = {
            "weights":
                weights,
            "result":
                result,
            "attenuation":
                attenuation,
        }

    #
    # Cumulative top-three removal.
    #
    cumulative, cumulative_weights = (
        ablation_modifier(
            connectome,
            PRIMARY_TARGETS,
        )
    )

    cumulative_result = run_pair(
        label=(
            "ABLATE TOP THREE "
            "RESIDUAL BRANCHES"
        ),
        lesion=cumulative,
        plasticity_modifier=(
            plasticity_modifier
        ),
        common=common,
    )

    cumulative_effect = (
        cumulative_result[
            "abs_dn_c1_delta"
        ]
    )

    cumulative_attenuation = (
        1.0
        - cumulative_effect
        / intact_effect
    )

    print(
        "cumulative attenuation:",
        cumulative_attenuation,
    )

    #
    # Negative-control branch.
    #
    (
        control_target,
        control_weight,
    ) = choose_control_target(
        connectome
    )

    control, control_weights = (
        ablation_modifier(
            connectome,
            [control_target],
        )
    )

    control_result = run_pair(
        label=(
            f"CONTROL ABLATION "
            f"{SOURCE}->{control_target}"
        ),
        lesion=control,
        plasticity_modifier=(
            plasticity_modifier
        ),
        common=common,
    )

    control_effect = (
        control_result[
            "abs_dn_c1_delta"
        ]
    )

    control_attenuation = (
        1.0
        - control_effect
        / intact_effect
    )

    print()
    print("=" * 72)
    print("SUMMARY")
    print("=" * 72)

    print(
        "intact effect:",
        intact_effect,
    )

    for target in PRIMARY_TARGETS:
        print(
            f"{SOURCE}->{target}:",
            records[
                str(target)
            ][
                "attenuation"
            ],
        )

    print(
        "top-three cumulative:",
        cumulative_attenuation,
    )

    print(
        "control branch:",
        f"{SOURCE}->{control_target}",
    )

    print(
        "control weight:",
        control_weight,
    )

    print(
        "control attenuation:",
        control_attenuation,
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
            "mq7-residual-branch-mediation/v1",
        "intact":
            intact,
        "primary_branches":
            records,
        "cumulative": {
            "weights":
                cumulative_weights,
            "result":
                cumulative_result,
            "attenuation":
                cumulative_attenuation,
        },
        "control": {
            "target":
                control_target,
            "weights":
                control_weights,
            "result":
                control_result,
            "attenuation":
                control_attenuation,
        },
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

    print(
        "connectome unchanged: True"
    )

    print(
        "results:",
        OUTPUT,
    )

    print(
        "MQ-7.14 COMPLETE"
    )


if __name__ == "__main__":
    main()
