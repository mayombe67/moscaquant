from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
from scipy import sparse

from brain.mq3_2_anonymous_market_readout import (
    CONNECTOME,
    CONSENSUS,
    RETINA,
    TRANSDUCTION_CONFIG,
    build_channel_indices,
    run_replay,
)
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
    complete_trading_session,
)
from oracle.reinforcement import (
    ReinforcementCondition,
)
from oracle.selector import select_d6
from oracle.state import initial_state

import tomllib


O1_CONFIG = Path(
    "config/experiments/mq7-o1-static-v1.toml"
)

O2_CONFIG = Path(
    "config/experiments/mq7-o2-adaptive-v1.toml"
)

ARTIFACT_ID = "connectome-baseline-v1.npz"

SESSION_1 = "mq7-activation-session-1"

PATH_EDGES = (
    (56393, 68045),
    (68045, 1273),
)


def csr_digest(matrix) -> str:
    digest = hashlib.sha256()

    for array in (
        matrix.data,
        matrix.indices,
        matrix.indptr,
    ):
        digest.update(
            np.ascontiguousarray(
                array
            ).tobytes()
        )

    return digest.hexdigest()


def load_inputs():
    with TRANSDUCTION_CONFIG.open(
        "rb"
    ) as handle:
        config = tomllib.load(handle)

    release_gain = float(
        config["transduction"]["release_gain"]
    )

    connectome = sparse.load_npz(
        CONNECTOME
    ).tocsr()

    retina = np.load(RETINA)

    retinal_indices = np.asarray(
        retina["neuron_index"],
        dtype=np.int32,
    )

    consensus = np.load(CONSENSUS)

    channel_indices = build_channel_indices(
        consensus
    )

    return (
        connectome,
        retinal_indices,
        channel_indices,
        release_gain,
    )


class ActivityRecorder:
    def __init__(self):
        self.history = {
            56393: [],
            68045: [],
        }

    def __call__(
        self,
        activity,
        synaptic,
    ):
        for neuron in self.history:
            self.history[neuron].append(
                float(activity[neuron])
            )

        return synaptic


def first_sc03_seed(
    experiment_id: str,
    session_id: str,
) -> int:
    for seed in range(100000):
        result = select_d6(
            seed=seed,
            experiment_id=experiment_id,
            session_id=session_id,
            plasticity_active=True,
        )

        if (
            result.selection.condition
            is ReinforcementCondition.SC_03_BAD_SYNAPSE
        ):
            return seed

    raise RuntimeError(
        "SC-03 seed not found"
    )


def build_credit(
    connectome,
    history,
):
    scored = []

    for presynaptic, postsynaptic in PATH_EDGES:
        weight = float(
            connectome[
                postsynaptic,
                presynaptic,
            ]
        )

        if weight == 0.0:
            raise RuntimeError(
                f"frozen edge absent: "
                f"{presynaptic}->{postsynaptic}"
            )

        scored.append(
            score_edge(
                presynaptic=presynaptic,
                postsynaptic=postsynaptic,
                weight=weight,
                activity_history=(
                    history[presynaptic][-10:]
                ),
            )
        )

    return classify_credit(
        scored
    )


def compare_replay(
    label,
    o1,
    o2,
):
    print()
    print("=" * 72)
    print(label)
    print("=" * 72)

    print(
        "voltage identical:",
        o1["voltage_trace_sha256"]
        == o2["voltage_trace_sha256"],
    )

    print(
        "spikes identical:",
        o1["spike_trace_sha256"]
        == o2["spike_trace_sha256"],
    )

    print(
        "O1 decision:",
        o1["decision"],
    )

    print(
        "O2 decision:",
        o2["decision"],
    )

    print("score deltas:")

    for channel in o1["scores"]:
        print(
            f"  {channel}:",
            (
                o2["scores"][channel]
                - o1["scores"][channel]
            ),
        )


def main():
    o1_config = (
        load_adaptive_experiment_config(
            O1_CONFIG
        )
    )

    o2_config = (
        load_adaptive_experiment_config(
            O2_CONFIG
        )
    )

    validate_matched_pair(
        o1_config,
        o2_config,
    )

    if (
        o1_config.d6_experiment_id
        != o2_config.d6_experiment_id
    ):
        raise RuntimeError(
            "D6 namespaces differ"
        )

    (
        connectome,
        retinal_indices,
        channel_indices,
        release_gain,
    ) = load_inputs()

    original_digest = csr_digest(
        connectome
    )

    print("=" * 72)
    print("MQ-7 O1/O2 SC-03 ACTIVATION TRIAL")
    print("=" * 72)

    print(
        "D6 namespace:",
        o1_config.d6_experiment_id,
    )

    #
    # SESSION 1
    #
    # Both conditions are baseline here.
    # Plasticity has not yet been earned.
    #
    recorder_o1 = ActivityRecorder()
    recorder_o2 = ActivityRecorder()

    print()
    print("SESSION 1: O1 baseline...")

    session1_o1 = run_replay(
        "A",
        connectome,
        retinal_indices,
        channel_indices,
        release_gain,
        synaptic_modifier=recorder_o1,
    )

    print("SESSION 1: O2 baseline...")

    session1_o2 = run_replay(
        "A",
        connectome,
        retinal_indices,
        channel_indices,
        release_gain,
        synaptic_modifier=recorder_o2,
    )

    if (
        session1_o1["voltage_trace_sha256"]
        != session1_o2["voltage_trace_sha256"]
        or session1_o1["spike_trace_sha256"]
        != session1_o2["spike_trace_sha256"]
        or session1_o1["scores"]
        != session1_o2["scores"]
        or session1_o1["decision"]
        != session1_o2["decision"]
    ):
        raise RuntimeError(
            "O1/O2 diverged before plasticity"
        )

    if recorder_o1.history != recorder_o2.history:
        raise RuntimeError(
            "credit evidence differed before plasticity"
        )

    print(
        "pre-plasticity replay identical: True"
    )

    credit = build_credit(
        connectome,
        recorder_o2.history,
    )

    print()
    print(
        "credit status:",
        credit.status,
    )

    for edge in credit.edges:
        print(
            "credit:",
            f"{edge.presynaptic}"
            f"->{edge.postsynaptic}",
            "trace=",
            edge.eligibility_trace,
            "transitions=",
            edge.contributing_transitions,
        )

    seed = first_sc03_seed(
        o1_config.d6_experiment_id,
        SESSION_1,
    )

    print()
    print("SC-03 activation seed:", seed)

    d6_o1 = select_d6(
        seed=seed,
        experiment_id=(
            o1_config.d6_experiment_id
        ),
        session_id=SESSION_1,
        plasticity_active=False,
    )

    d6_o2 = select_d6(
        seed=seed,
        experiment_id=(
            o2_config.d6_experiment_id
        ),
        session_id=SESSION_1,
        plasticity_active=True,
    )

    if d6_o1.selection != d6_o2.selection:
        raise RuntimeError(
            "matched D6 selection diverged"
        )

    print(
        "D6 condition:",
        d6_o1.selection.condition,
    )

    print(
        "O1 D6:",
        d6_o1.status,
    )

    print(
        "O2 D6:",
        d6_o2.status,
    )

    o1_state = initial_state(
        oracle_version="oracle-mq7-v1"
    )

    o2_state = initial_state(
        oracle_version="oracle-mq7-v1"
    )

    o1_update = apply_live_bad_synapse(
        oracle_state=o1_state,
        d6_result=d6_o1,
        credit_result=credit,
        baseline_artifact_id=ARTIFACT_ID,
        session_id=SESSION_1,
        evidence_reference=(
            "mq7-activation-session-1-credit"
        ),
    )

    o2_update = apply_live_bad_synapse(
        oracle_state=o2_state,
        d6_result=d6_o2,
        credit_result=credit,
        baseline_artifact_id=ARTIFACT_ID,
        session_id=SESSION_1,
        evidence_reference=(
            "mq7-activation-session-1-credit"
        ),
    )

    print()
    print(
        "O1 plasticity status:",
        o1_update.status,
    )

    print(
        "O2 plasticity status:",
        o2_update.status,
    )

    if o1_update.status != "NOT_APPLICABLE":
        raise RuntimeError(
            "O1 unexpectedly adapted"
        )

    if o2_update.status != "UPDATED":
        print()
        print(
            "VALID NULL RESULT:"
            " O2 did not earn a unique update."
        )
        return

    plasticity = (
        o2_update.plasticity_state
    )

    plasticity = complete_trading_session(
        plasticity,
        session_id=SESSION_1,
    )

    o2_state = with_plasticity_state(
        o2_update.oracle_state,
        plasticity,
    )

    edge = plasticity.edges[0]

    print()
    print(
        "earned edge:",
        f"{edge.presynaptic}"
        f"->{edge.postsynaptic}",
    )

    print(
        "persisted multiplier:",
        edge.multiplier,
    )

    print(
        "update count:",
        edge.update_count,
    )

    #
    # SESSION 2
    #
    # O1 remains baseline.
    # O2 now receives ONLY legitimately earned
    # persisted plasticity.
    #
    modifier = build_synaptic_modifier(
        plasticity
    )

    for market_condition in (
        "A",
        "B",
    ):
        print()
        print(
            f"SESSION 2 {market_condition}: O1..."
        )

        o1_replay = run_replay(
            market_condition,
            connectome,
            retinal_indices,
            channel_indices,
            release_gain,
        )

        print(
            f"SESSION 2 {market_condition}: O2..."
        )

        o2_replay = run_replay(
            market_condition,
            connectome,
            retinal_indices,
            channel_indices,
            release_gain,
            synaptic_modifier=modifier,
        )

        compare_replay(
            f"SESSION 2 CONDITION "
            f"{market_condition}",
            o1_replay,
            o2_replay,
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
    print("connectome unchanged: True")
    print("ACTIVATION TRIAL COMPLETE")


if __name__ == "__main__":
    main()
