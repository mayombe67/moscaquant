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
from oracle.d6_execution import (
    build_d6_execution_plan,
)
from oracle.plasticity_state import (
    apply_plasticity_update,
    build_empty_plasticity_state,
)
from oracle.reinforcement import (
    ReinforcementCondition,
)
from oracle.selector import select_d6


EXPERIMENT = "mq7-d6-full-smoke-v1"
MARKET_CONDITION = "A"

#
# Acute interventions begin after the neural
# system has had time to respond to input.
#
INTERVENTION_GENERATION = 32

CONDITIONS = (
    ReinforcementCondition.SC_01_SHOCK,
    ReinforcementCondition.SC_02_DARKNESS,
    ReinforcementCondition.SC_03_BAD_SYNAPSE,
    ReinforcementCondition.SC_04_TIME_OUT,
    ReinforcementCondition.SC_05_SCAR_TISSUE,
    ReinforcementCondition.SC_06_MERCY,
)


def first_seed_for(
    condition,
    session_id,
):
    for seed in range(100000):
        result = select_d6(
            seed=seed,
            experiment_id=EXPERIMENT,
            session_id=session_id,
            plasticity_active=True,
        )

        if (
            result.selection.condition
            is condition
        ):
            return seed, result

    raise RuntimeError(
        f"seed not found for {condition}"
    )


def build_plasticity(
    connectome,
):
    pre = 56393
    post = 68045

    weight = float(
        connectome[
            post,
            pre,
        ]
    )

    if weight == 0.0:
        raise RuntimeError(
            "frozen SC-03 edge missing"
        )

    state = (
        build_empty_plasticity_state()
    )

    return apply_plasticity_update(
        state,
        presynaptic=pre,
        postsynaptic=post,
        baseline_artifact_id=ARTIFACT_ID,
        baseline_weight=weight,
        session_id="smoke-preload",
        evidence_reference=(
            "mq7-smoke-preloaded-sc03"
        ),
    )


def flatten_readout_indices(
    channel_indices,
):
    return np.concatenate(
        [
            np.asarray(
                channel_indices[channel],
                dtype=np.int64,
            )
            for channel
            in (
                "DN-C0",
                "DN-C1",
                "DN-C2",
            )
        ]
    )


def compare(
    baseline,
    intervention,
):
    return {
        "voltage_identical": (
            baseline[
                "voltage_trace_sha256"
            ]
            == intervention[
                "voltage_trace_sha256"
            ]
        ),
        "spikes_identical": (
            baseline[
                "spike_trace_sha256"
            ]
            == intervention[
                "spike_trace_sha256"
            ]
        ),
        "scores_identical": (
            baseline["scores"]
            == intervention["scores"]
        ),
        "decision_identical": (
            baseline["decision"]
            == intervention["decision"]
        ),
        "score_deltas": {
            channel: (
                intervention[
                    "scores"
                ][channel]
                - baseline[
                    "scores"
                ][channel]
            )
            for channel
            in baseline["scores"]
        },
    }


def run_with_plan(
    *,
    plan,
    connectome,
    retinal_indices,
    channel_indices,
    release_gain,
):
    return run_replay(
        MARKET_CONDITION,
        connectome,
        retinal_indices,
        channel_indices,
        release_gain,
        stimulus_modifier=(
            plan.stimulus_modifier
        ),
        activity_modifier=(
            plan.activity_modifier
        ),
        synaptic_modifier=(
            plan.synaptic_modifier
        ),
        readout_modifier=(
            plan.readout_modifier
        ),
    )


def main():
    (
        connectome,
        retinal_indices,
        channel_indices,
        release_gain,
    ) = load_inputs()

    original_digest = csr_digest(
        connectome
    )

    readout_indices = (
        flatten_readout_indices(
            channel_indices
        )
    )

    plasticity = build_plasticity(
        connectome
    )

    print("=" * 72)
    print(
        "MQ-7 FULL D6 INTEGRATION "
        "SMOKE TEST"
    )
    print("=" * 72)

    print(
        "market condition:",
        MARKET_CONDITION,
    )

    print(
        "intervention generation:",
        INTERVENTION_GENERATION,
    )

    print()
    print("running matched baseline...")

    baseline = run_replay(
        MARKET_CONDITION,
        connectome,
        retinal_indices,
        channel_indices,
        release_gain,
    )

    scar_origin_plan = None

    for condition in CONDITIONS:
        session_id = (
            f"smoke-{condition.value}"
        )

        seed, result = (
            first_seed_for(
                condition,
                session_id,
            )
        )

        plan = build_d6_execution_plan(
            d6_result=result,
            seed=seed,
            experiment_id=EXPERIMENT,
            session_id=session_id,
            readout_indices=readout_indices,
            intervention_generation=(
                INTERVENTION_GENERATION
            ),
            plasticity_state=(
                plasticity
                if (
                    condition
                    is ReinforcementCondition.SC_03_BAD_SYNAPSE
                )
                else None
            ),
        )

        print()
        print("-" * 72)
        print(
            condition.value,
            condition.name,
        )

        print("seed:", seed)

        intervention = run_with_plan(
            plan=plan,
            connectome=connectome,
            retinal_indices=retinal_indices,
            channel_indices=channel_indices,
            release_gain=release_gain,
        )

        result_summary = compare(
            baseline,
            intervention,
        )

        print(
            "voltage identical:",
            result_summary[
                "voltage_identical"
            ],
        )

        print(
            "spikes identical:",
            result_summary[
                "spikes_identical"
            ],
        )

        print(
            "scores identical:",
            result_summary[
                "scores_identical"
            ],
        )

        print(
            "decision identical:",
            result_summary[
                "decision_identical"
            ],
        )

        print(
            "score deltas:",
            result_summary[
                "score_deltas"
            ],
        )

        if plan.shock is not None:
            print(
                "shock target:",
                plan.shock.target_model_index,
            )

        if plan.darkness is not None:
            print(
                "darkness transitions:",
                plan.darkness.duration_transitions,
            )

        if plan.timeout is not None:
            print(
                "timeout transitions:",
                plan.timeout.duration_transitions,
            )

        if plan.mercy is not None:
            print(
                "mercy target:",
                plan.mercy.target_model_index,
            )

        if (
            condition
            is ReinforcementCondition.SC_05_SCAR_TISSUE
        ):
            scar_origin_plan = plan

            print(
                "scar target:",
                plan.scar_target_model_index,
            )

            print(
                "scar phase:",
                plan.scar_state.phase,
            )

    #
    # Explicitly test SC-05 carryover into
    # the following session.
    #
    if scar_origin_plan is None:
        raise RuntimeError(
            "SC-05 origin plan missing"
        )

    following_session = (
        "smoke-SC-05-following"
    )

    next_seed, next_result = (
        first_seed_for(
            ReinforcementCondition.SC_01_SHOCK,
            following_session,
        )
    )

    following_plan = (
        build_d6_execution_plan(
            d6_result=next_result,
            seed=next_seed,
            experiment_id=EXPERIMENT,
            session_id=following_session,
            readout_indices=readout_indices,
            intervention_generation=(
                INTERVENTION_GENERATION
            ),
            prior_scar_state=(
                scar_origin_plan.scar_state
            ),
            prior_scar_target_model_index=(
                scar_origin_plan.scar_target_model_index
            ),
        )
    )

    print()
    print("-" * 72)
    print(
        "SC-05 FOLLOWING SESSION"
    )

    print(
        "scar active:",
        following_plan.scar_state.active,
    )

    print(
        "scar phase:",
        following_plan.scar_state.phase,
    )

    print(
        "scar target:",
        following_plan.scar_target_model_index,
    )

    following_replay = run_with_plan(
        plan=following_plan,
        connectome=connectome,
        retinal_indices=retinal_indices,
        channel_indices=channel_indices,
        release_gain=release_gain,
    )

    following_summary = compare(
        baseline,
        following_replay,
    )

    print(
        "voltage identical:",
        following_summary[
            "voltage_identical"
        ],
    )

    print(
        "spikes identical:",
        following_summary[
            "spikes_identical"
        ],
    )

    if (
        csr_digest(connectome)
        != original_digest
    ):
        raise RuntimeError(
            "structural connectome mutated"
        )

    print()
    print("=" * 72)
    print(
        "connectome unchanged: True"
    )
    print(
        "FULL D6 SMOKE COMPLETE"
    )


if __name__ == "__main__":
    main()
