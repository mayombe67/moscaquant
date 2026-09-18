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

EXPERIMENT = "mq7-17-cumulative-first-wave-mediation-v1"
SESSION = "mq7-17-shock-56393"

SHOCK_TARGET = 56393
INTERVENTION_GENERATION = 32

PLASTICITY_PRE = 56393
PLASTICITY_POST = 68045

SOURCE = 68045

CUMULATIVE_ORDER = (
    62598,
    69484,
    63192,
    79672,
    77298,
    66309,
    65046,
    73483,
    62142,
    61694,
)

KNOWN_DOWNSTREAM = 1273
NULL_CONTROL = 82348

OUTPUT = (
    Path.home()
    / "moscaquant-data"
    / "experiments"
    / "mq7-17-cumulative-first-wave-mediation-v1.json"
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
        session_id="mq7-17-preload",
        evidence_reference="mq7-17-sc03",
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


def ablation_modifier(
    connectome,
    targets,
):
    weights = {}

    for target in targets:
        target = int(target)

        weight = edge_weight(
            connectome,
            SOURCE,
            target,
        )

        if weight == 0.0:
            raise RuntimeError(
                f"missing edge "
                f"{SOURCE}->{target}"
            )

        weights[target] = weight

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
    lesion,
    plasticity_modifier,
    common,
):
    baseline = replay(
        **common,
        synaptic_modifier=lesion,
    )

    adaptive = replay(
        **common,
        synaptic_modifier=(
            compose(
                lesion,
                plasticity_modifier,
            )
        ),
    )

    return difference(
        baseline,
        adaptive,
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
        "MQ-7.17 CUMULATIVE FIRST-WAVE MEDIATION"
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

    intact = run_pair(
        lesion=None,
        plasticity_modifier=(
            plasticity_modifier
        ),
        common=common,
    )

    intact_effect = (
        intact["abs_dn_c1_delta"]
    )

    print()
    print(
        "C0 intact effect:",
        intact_effect,
    )

    records = []

    current_targets = []

    for index, target in enumerate(
        CUMULATIVE_ORDER,
        start=1,
    ):
        current_targets.append(
            target
        )

        lesion, weights = (
            ablation_modifier(
                connectome,
                current_targets,
            )
        )

        result = run_pair(
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

        print()
        print("=" * 72)

        print(
            f"C{index} cumulative"
        )

        print(
            "targets:",
            current_targets,
        )

        print(
            "|DN-C1|:",
            effect,
        )

        print(
            "attenuation:",
            attenuation,
        )

        print(
            "spikes identical:",
            result[
                "spikes_identical"
            ],
        )

        print(
            "decision identical:",
            result[
                "decision_identical"
            ],
        )

        records.append({
            "condition":
                f"C{index}",
            "targets":
                list(
                    current_targets
                ),
            "weights":
                weights,
            "result":
                result,
            "attenuation":
                attenuation,
        })

    #
    # Known 68045 -> 1273 route alone.
    #
    known_lesion, known_weights = (
        ablation_modifier(
            connectome,
            [KNOWN_DOWNSTREAM],
        )
    )

    known_result = run_pair(
        lesion=known_lesion,
        plasticity_modifier=(
            plasticity_modifier
        ),
        common=common,
    )

    known_effect = (
        known_result[
            "abs_dn_c1_delta"
        ]
    )

    known_attenuation = (
        1.0
        - known_effect
        / intact_effect
    )

    #
    # All ten + known 1273 branch.
    #
    all_plus_known_targets = (
        list(CUMULATIVE_ORDER)
        + [KNOWN_DOWNSTREAM]
    )

    combined_lesion, combined_weights = (
        ablation_modifier(
            connectome,
            all_plus_known_targets,
        )
    )

    combined_result = run_pair(
        lesion=combined_lesion,
        plasticity_modifier=(
            plasticity_modifier
        ),
        common=common,
    )

    combined_effect = (
        combined_result[
            "abs_dn_c1_delta"
        ]
    )

    combined_attenuation = (
        1.0
        - combined_effect
        / intact_effect
    )

    #
    # Null control.
    #
    null_lesion, null_weights = (
        ablation_modifier(
            connectome,
            [NULL_CONTROL],
        )
    )

    null_result = run_pair(
        lesion=null_lesion,
        plasticity_modifier=(
            plasticity_modifier
        ),
        common=common,
    )

    null_effect = (
        null_result[
            "abs_dn_c1_delta"
        ]
    )

    null_attenuation = (
        1.0
        - null_effect
        / intact_effect
    )

    print()
    print("=" * 72)
    print("SUMMARY")
    print("=" * 72)

    print(
        "C0 intact:",
        intact_effect,
    )

    for record in records:
        print(
            record["condition"],
            "attenuation=",
            record["attenuation"],
            "effect=",
            record[
                "result"
            ][
                "abs_dn_c1_delta"
            ],
        )

    print(
        "K 68045->1273:",
        known_attenuation,
    )

    print(
        "C10K all first-wave + 1273:",
        combined_attenuation,
    )

    print(
        "N 68045->82348:",
        null_attenuation,
    )

    residual_fraction = (
        combined_effect
        / intact_effect
    )

    print(
        "residual fraction after C10K:",
        residual_fraction,
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
            "mq7-cumulative-first-wave-mediation/v1",
        "shock_target":
            SHOCK_TARGET,
        "shock_seed":
            seed,
        "intact":
            intact,
        "cumulative":
            records,
        "known_route": {
            "target":
                KNOWN_DOWNSTREAM,
            "weights":
                known_weights,
            "result":
                known_result,
            "attenuation":
                known_attenuation,
        },
        "combined_all_plus_known": {
            "targets":
                all_plus_known_targets,
            "weights":
                combined_weights,
            "result":
                combined_result,
            "attenuation":
                combined_attenuation,
            "residual_fraction":
                residual_fraction,
        },
        "null_control": {
            "target":
                NULL_CONTROL,
            "weights":
                null_weights,
            "result":
                null_result,
            "attenuation":
                null_attenuation,
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
        "MQ-7.17 COMPLETE"
    )


if __name__ == "__main__":
    main()
