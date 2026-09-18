from __future__ import annotations

import json
from pathlib import Path

from oracle.adaptive_experiment_config import (
    load_adaptive_experiment_config,
    validate_matched_pair,
)
from oracle.credit_assignment import (
    classify_credit,
    score_edge,
)
from oracle.live_plasticity import (
    apply_live_bad_synapse,
)
from oracle.plasticity_adapter import (
    with_plasticity_state,
)
from oracle.plasticity_modifier import (
    build_synaptic_modifier,
)
from oracle.plasticity_state import (
    build_empty_plasticity_state,
    complete_trading_session,
)
from oracle.selector import select_d6
from oracle.state import initial_state

from brain.mq7_o1_o2_activation import (
    ARTIFACT_ID,
    PATH_EDGES,
    csr_digest,
    load_inputs,
)
from brain.mq3_2_anonymous_market_readout import (
    run_replay,
)


SEED = 20260918
SESSION_COUNT = 36

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
    / "mq7-adaptive-activation-replication-v1.json"
)


class RecordingModifier:
    def __init__(
        self,
        *,
        plasticity=None,
    ):
        self.history = {
            56393: [],
            68045: [],
        }

        self.plasticity_modifier = (
            build_synaptic_modifier(
                plasticity
            )
            if plasticity is not None
            else None
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

        if self.plasticity_modifier is None:
            return synaptic

        return self.plasticity_modifier(
            activity,
            synaptic,
        )


def build_credit(
    connectome,
    history,
):
    edges = []

    for presynaptic, postsynaptic in PATH_EDGES:
        weight = float(
            connectome[
                postsynaptic,
                presynaptic,
            ]
        )

        if weight == 0.0:
            raise RuntimeError(
                "frozen pathway edge absent: "
                f"{presynaptic}->{postsynaptic}"
            )

        edges.append(
            score_edge(
                presynaptic=presynaptic,
                postsynaptic=postsynaptic,
                weight=weight,
                activity_history=(
                    history[presynaptic][-10:]
                ),
            )
        )

    return classify_credit(edges)


def replay_difference(
    o1,
    o2,
):
    score_deltas = {
        channel: (
            o2["scores"][channel]
            - o1["scores"][channel]
        )
        for channel in o1["scores"]
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
        "score_deltas": score_deltas,
        "o1_decision": o1["decision"],
        "o2_decision": o2["decision"],
    }


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

    d6_namespace = (
        o1_config.d6_experiment_id
    )

    (
        connectome,
        retinal_indices,
        channel_indices,
        release_gain,
    ) = load_inputs()

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

    first_update_seen = False

    records = []

    d6_counts = {}

    update_count = 0
    voltage_divergence_count = 0
    spike_divergence_count = 0
    decision_divergence_count = 0

    print("=" * 72)
    print(
        "MQ-7 ADAPTIVE ACTIVATION "
        "REPLICATION"
    )
    print("=" * 72)

    print("seed:", SEED)
    print("sessions:", SESSION_COUNT)
    print(
        "D6 namespace:",
        d6_namespace,
    )

    for index in range(
        1,
        SESSION_COUNT + 1,
    ):
        session_id = (
            f"mq7-repl-{index:03d}"
        )

        market_condition = (
            "A"
            if index % 2 == 1
            else "B"
        )

        print()
        print("-" * 72)
        print(
            session_id,
            "market=",
            market_condition,
        )

        o1_recorder = RecordingModifier()

        o2_recorder = RecordingModifier(
            plasticity=plasticity,
        )

        o1_replay = run_replay(
            market_condition,
            connectome,
            retinal_indices,
            channel_indices,
            release_gain,
            synaptic_modifier=o1_recorder,
        )

        o2_replay = run_replay(
            market_condition,
            connectome,
            retinal_indices,
            channel_indices,
            release_gain,
            synaptic_modifier=o2_recorder,
        )

        difference = replay_difference(
            o1_replay,
            o2_replay,
        )

        if not first_update_seen:
            if (
                not difference[
                    "voltage_identical"
                ]
                or not difference[
                    "spikes_identical"
                ]
                or not difference[
                    "scores_identical"
                ]
                or not difference[
                    "decision_identical"
                ]
            ):
                raise RuntimeError(
                    "O1/O2 diverged before "
                    "first legitimate update"
                )

        credit = build_credit(
            connectome,
            o2_recorder.history,
        )

        d6_o1 = select_d6(
            seed=SEED,
            experiment_id=d6_namespace,
            session_id=session_id,
            plasticity_active=False,
        )

        d6_o2 = select_d6(
            seed=SEED,
            experiment_id=d6_namespace,
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

        condition = str(
            d6_o1.selection.condition
        )

        d6_counts[condition] = (
            d6_counts.get(
                condition,
                0,
            )
            + 1
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
            first_update_seen = True

            o2_state = update.oracle_state
            plasticity = (
                update.plasticity_state
            )

        else:
            current = (
                update.plasticity_state
            )

            if current is not None:
                plasticity = current

        plasticity = complete_trading_session(
            plasticity,
            session_id=session_id,
        )

        o2_state = with_plasticity_state(
            o2_state,
            plasticity,
        )

        if not difference[
            "voltage_identical"
        ]:
            voltage_divergence_count += 1

        if not difference[
            "spikes_identical"
        ]:
            spike_divergence_count += 1

        if not difference[
            "decision_identical"
        ]:
            decision_divergence_count += 1

        edge_state = None

        if plasticity.edges:
            edge_state = plasticity.edges[0]

        print(
            "D6:",
            condition,
            "O1=",
            d6_o1.status,
            "O2=",
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

        if edge_state is not None:
            print(
                "edge:",
                f"{edge_state.presynaptic}"
                f"->{edge_state.postsynaptic}",
                "multiplier=",
                edge_state.multiplier,
                "updates=",
                edge_state.update_count,
                "inactive=",
                edge_state.inactive_completed_sessions,
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
            "decision identical:",
            difference[
                "decision_identical"
            ],
        )

        records.append({
            "session_id": session_id,
            "market_condition":
                market_condition,
            "d6_condition": condition,
            "o1_d6_status":
                d6_o1.status,
            "o2_d6_status":
                d6_o2.status,
            "credit_status":
                credit.status,
            "plasticity_status":
                update.status,
            "difference":
                difference,
            "plasticity_edges": [
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
            ],
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
            "mq7-adaptive-replication/v1",
        "seed":
            SEED,
        "session_count":
            SESSION_COUNT,
        "d6_experiment_id":
            d6_namespace,
        "d6_counts":
            d6_counts,
        "plasticity_update_count":
            update_count,
        "voltage_divergence_sessions":
            voltage_divergence_count,
        "spike_divergence_sessions":
            spike_divergence_count,
        "decision_divergence_sessions":
            decision_divergence_count,
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
    print("REPLICATION COMPLETE")
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
        voltage_divergence_count,
    )

    print(
        "spike divergence sessions:",
        spike_divergence_count,
    )

    print(
        "decision divergence sessions:",
        decision_divergence_count,
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
