from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from brain.mq3_2_anonymous_market_readout import (
    run_replay,
)
from brain.mq7_o1_o2_activation import (
    ARTIFACT_ID,
    PATH_EDGES,
    csr_digest,
    load_inputs,
)
from oracle.adaptive_experiment_config import (
    load_adaptive_experiment_config,
    validate_matched_pair,
)
from oracle.credit_assignment import (
    classify_credit,
    score_edge,
)
from oracle.d6_execution import (
    build_d6_execution_plan,
)
from oracle.live_plasticity import (
    apply_live_bad_synapse,
)
from oracle.plasticity_adapter import (
    with_plasticity_state,
)
from oracle.plasticity_state import (
    build_empty_plasticity_state,
    complete_trading_session,
)
from oracle.reinforcement import (
    ReinforcementCondition,
)
from oracle.selector import select_d6
from oracle.state import initial_state


SEED = 20260918
SESSION_COUNT = 48
INTERVENTION_GENERATION = 32

O1_CONFIG = Path(
    "config/experiments/mq7-o1-static-v1.toml"
)

O2_CONFIG = Path(
    "config/experiments/mq7-o2-adaptive-v1.toml"
)

OUTPUT = (
    Path.home()
    / "moscaquant-data"
    / "experiments"
    / "mq7-full-d6-multisession-v1.json"
)


def flatten_readout_indices(
    channel_indices,
):
    return np.concatenate(
        [
            np.asarray(
                indices,
                dtype=np.int64,
            )
            for indices
            in channel_indices.values()
        ]
    )


class RecordingSynapticModifier:
    def __init__(
        self,
        downstream_modifier=None,
    ):
        self.history = {
            56393: [],
            68045: [],
        }

        self.downstream_modifier = (
            downstream_modifier
        )

    def __call__(
        self,
        activity,
        synaptic,
    ):
        for neuron in self.history:
            self.history[neuron].append(
                float(activity[neuron])
            )

        if self.downstream_modifier is None:
            return synaptic

        return self.downstream_modifier(
            activity,
            synaptic,
        )


def build_credit(
    connectome,
    history,
):
    scored = []

    for pre, post in PATH_EDGES:
        weight = float(
            connectome[
                post,
                pre,
            ]
        )

        if weight == 0.0:
            raise RuntimeError(
                f"frozen edge absent: "
                f"{pre}->{post}"
            )

        scored.append(
            score_edge(
                presynaptic=pre,
                postsynaptic=post,
                weight=weight,
                activity_history=(
                    history[pre][-10:]
                ),
            )
        )

    return classify_credit(
        scored
    )


def compare(
    o1,
    o2,
):
    deltas = {
        channel: (
            o2["scores"][channel]
            - o1["scores"][channel]
        )
        for channel
        in o1["scores"]
    }

    return {
        "voltage_identical": (
            o1["voltage_trace_sha256"]
            == o2["voltage_trace_sha256"]
        ),
        "spikes_identical": (
            o1["spike_trace_sha256"]
            == o2["spike_trace_sha256"]
        ),
        "scores_identical": (
            o1["scores"]
            == o2["scores"]
        ),
        "decision_identical": (
            o1["decision"]
            == o2["decision"]
        ),
        "score_deltas": deltas,
        "o1_decision": o1["decision"],
        "o2_decision": o2["decision"],
    }


def run_plan(
    *,
    plan,
    recorder,
    condition,
    connectome,
    retinal_indices,
    channel_indices,
    release_gain,
):
    recorder.downstream_modifier = (
        plan.synaptic_modifier
    )

    return run_replay(
        condition,
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
        synaptic_modifier=recorder,
        readout_modifier=(
            plan.readout_modifier
        ),
    )


def main():
    o1_config = load_adaptive_experiment_config(
        O1_CONFIG
    )

    o2_config = load_adaptive_experiment_config(
        O2_CONFIG
    )

    validate_matched_pair(
        o1_config,
        o2_config,
    )

    namespace = (
        o1_config.d6_experiment_id
    )

    (
        connectome,
        retinal_indices,
        channel_indices,
        release_gain,
    ) = load_inputs()

    readout_indices = (
        flatten_readout_indices(
            channel_indices
        )
    )

    baseline_digest = csr_digest(
        connectome
    )

    o2_state = initial_state(
        oracle_version="oracle-mq7-v1"
    )

    plasticity = (
        build_empty_plasticity_state()
    )

    o2_state = with_plasticity_state(
        o2_state,
        plasticity,
    )

    o1_scar = None
    o1_scar_target = None

    o2_scar = None
    o2_scar_target = None

    records = []

    d6_counts = {}
    update_count = 0
    voltage_divergence = 0
    spike_divergence = 0
    score_divergence = 0
    decision_divergence = 0
    scar_following_sessions = 0

    print("=" * 72)
    print(
        "MQ-7 FULL D6 MULTI-SESSION "
        "EXPERIMENT"
    )
    print("=" * 72)

    print("seed:", SEED)
    print("sessions:", SESSION_COUNT)
    print(
        "intervention generation:",
        INTERVENTION_GENERATION,
    )

    for index in range(
        1,
        SESSION_COUNT + 1,
    ):
        session_id = (
            f"mq7-full-d6-{index:03d}"
        )

        market = (
            "A"
            if index % 2 == 1
            else "B"
        )

        d6_o1 = select_d6(
            seed=SEED,
            experiment_id=namespace,
            session_id=session_id,
            plasticity_active=False,
        )

        d6_o2 = select_d6(
            seed=SEED,
            experiment_id=namespace,
            session_id=session_id,
            plasticity_active=True,
        )

        if (
            d6_o1.selection
            != d6_o2.selection
        ):
            raise RuntimeError(
                "matched D6 selection diverged"
            )

        condition = (
            d6_o1.selection.condition
        )

        d6_counts[
            condition.value
        ] = (
            d6_counts.get(
                condition.value,
                0,
            )
            + 1
        )

        o1_plan = build_d6_execution_plan(
            d6_result=d6_o1,
            seed=SEED,
            experiment_id=namespace,
            session_id=session_id,
            readout_indices=readout_indices,
            intervention_generation=(
                INTERVENTION_GENERATION
            ),
            prior_scar_state=o1_scar,
            prior_scar_target_model_index=(
                o1_scar_target
            ),
        )

        o2_plan = build_d6_execution_plan(
            d6_result=d6_o2,
            seed=SEED,
            experiment_id=namespace,
            session_id=session_id,
            readout_indices=readout_indices,
            intervention_generation=(
                INTERVENTION_GENERATION
            ),
            plasticity_state=plasticity,
            prior_scar_state=o2_scar,
            prior_scar_target_model_index=(
                o2_scar_target
            ),
        )

        if (
            o1_plan.scar_state
            != o2_plan.scar_state
            or o1_plan.scar_target_model_index
            != o2_plan.scar_target_model_index
        ):
            raise RuntimeError(
                "matched SC-05 state diverged"
            )

        o1_scar = o1_plan.scar_state
        o1_scar_target = (
            o1_plan.scar_target_model_index
        )

        o2_scar = o2_plan.scar_state
        o2_scar_target = (
            o2_plan.scar_target_model_index
        )

        if (
            o1_scar is not None
            and str(o1_scar.phase)
            == "FOLLOWING_SESSION"
        ):
            scar_following_sessions += 1

        o1_recorder = (
            RecordingSynapticModifier()
        )

        o2_recorder = (
            RecordingSynapticModifier()
        )

        o1_replay = run_plan(
            plan=o1_plan,
            recorder=o1_recorder,
            condition=market,
            connectome=connectome,
            retinal_indices=retinal_indices,
            channel_indices=channel_indices,
            release_gain=release_gain,
        )

        o2_replay = run_plan(
            plan=o2_plan,
            recorder=o2_recorder,
            condition=market,
            connectome=connectome,
            retinal_indices=retinal_indices,
            channel_indices=channel_indices,
            release_gain=release_gain,
        )

        difference = compare(
            o1_replay,
            o2_replay,
        )

        credit = build_credit(
            connectome,
            o2_recorder.history,
        )

        update = apply_live_bad_synapse(
            oracle_state=o2_state,
            d6_result=d6_o2,
            credit_result=credit,
            baseline_artifact_id=ARTIFACT_ID,
            session_id=session_id,
            evidence_reference=(
                f"{session_id}-credit"
            ),
        )

        if update.status == "UPDATED":
            update_count += 1
            o2_state = update.oracle_state
            plasticity = (
                update.plasticity_state
            )

        elif (
            update.plasticity_state
            is not None
        ):
            plasticity = (
                update.plasticity_state
            )

        plasticity = (
            complete_trading_session(
                plasticity,
                session_id=session_id,
            )
        )

        o2_state = with_plasticity_state(
            o2_state,
            plasticity,
        )

        if not difference[
            "voltage_identical"
        ]:
            voltage_divergence += 1

        if not difference[
            "spikes_identical"
        ]:
            spike_divergence += 1

        if not difference[
            "scores_identical"
        ]:
            score_divergence += 1

        if not difference[
            "decision_identical"
        ]:
            decision_divergence += 1

        edges = [
            {
                "presynaptic":
                    edge.presynaptic,
                "postsynaptic":
                    edge.postsynaptic,
                "multiplier":
                    edge.multiplier,
                "update_count":
                    edge.update_count,
                "inactive_completed_sessions":
                    edge.inactive_completed_sessions,
            }
            for edge
            in plasticity.edges
        ]

        print()
        print("-" * 72)

        print(
            session_id,
            "market=",
            market,
            "D6=",
            condition.value,
        )

        print(
            "O1:",
            d6_o1.status,
            "O2:",
            d6_o2.status,
        )

        print(
            "credit:",
            credit.status,
        )

        print(
            "plasticity:",
            update.status,
        )

        if o1_plan.shock is not None:
            print(
                "shock target:",
                o1_plan.shock.target_model_index,
            )

        if o1_plan.darkness is not None:
            print(
                "darkness active"
            )

        if o1_plan.timeout is not None:
            print(
                "time out active"
            )

        if o1_plan.mercy is not None:
            print(
                "mercy target:",
                o1_plan.mercy.target_model_index,
            )

        if o1_plan.scar_state is not None:
            print(
                "scar:",
                o1_plan.scar_state.phase,
                "target=",
                o1_plan.scar_target_model_index,
            )

        if edges:
            print(
                "plasticity edges:",
                edges,
            )

        print(
            "voltage identical:",
            difference[
                "voltage_identical"
            ],
        )

        print(
            "spikes identical:",
            difference[
                "spikes_identical"
            ],
        )

        print(
            "scores identical:",
            difference[
                "scores_identical"
            ],
        )

        print(
            "decision identical:",
            difference[
                "decision_identical"
            ],
        )

        records.append({
            "session_id": session_id,
            "market_condition": market,
            "d6_condition":
                condition.value,
            "o1_status":
                d6_o1.status,
            "o2_status":
                d6_o2.status,
            "credit_status":
                credit.status,
            "plasticity_status":
                update.status,
            "scar_phase": (
                str(
                    o1_plan.scar_state.phase
                )
                if o1_plan.scar_state
                is not None
                else None
            ),
            "scar_target":
                o1_plan.scar_target_model_index,
            "difference":
                difference,
            "plasticity_edges":
                edges,
        })

    if (
        csr_digest(connectome)
        != baseline_digest
    ):
        raise RuntimeError(
            "structural connectome mutated"
        )

    result = {
        "schema_version":
            "mq7-full-d6-multisession/v1",
        "seed":
            SEED,
        "session_count":
            SESSION_COUNT,
        "intervention_generation":
            INTERVENTION_GENERATION,
        "d6_counts":
            d6_counts,
        "plasticity_updates":
            update_count,
        "voltage_divergence_sessions":
            voltage_divergence,
        "spike_divergence_sessions":
            spike_divergence,
        "score_divergence_sessions":
            score_divergence,
        "decision_divergence_sessions":
            decision_divergence,
        "scar_following_sessions":
            scar_following_sessions,
        "connectome_unchanged":
            True,
        "sessions":
            records,
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

    print()
    print("=" * 72)
    print(
        "FULL D6 EXPERIMENT COMPLETE"
    )
    print("=" * 72)

    print(
        "D6 counts:",
        d6_counts,
    )

    print(
        "plasticity updates:",
        update_count,
    )

    print(
        "voltage divergence sessions:",
        voltage_divergence,
    )

    print(
        "spike divergence sessions:",
        spike_divergence,
    )

    print(
        "score divergence sessions:",
        score_divergence,
    )

    print(
        "decision divergence sessions:",
        decision_divergence,
    )

    print(
        "scar following sessions:",
        scar_following_sessions,
    )

    print(
        "connectome unchanged: True"
    )

    print(
        "results:",
        OUTPUT,
    )


if __name__ == "__main__":
    main()
