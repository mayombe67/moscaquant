from __future__ import annotations

import hashlib
import tomllib

import numpy as np
from scipy import sparse

from brain.mq3_2_anonymous_market_readout import (
    CONNECTOME,
    RETINA,
    CONSENSUS,
    TRANSDUCTION_CONFIG,
    build_channel_indices,
    run_replay,
)
from oracle.plasticity_modifier import (
    build_synaptic_modifier,
)
from oracle.plasticity_state import (
    apply_plasticity_update,
    build_empty_plasticity_state,
)


PRE = 56393
POST = 68045

ARTIFACT_ID = "connectome-baseline-v1.npz"


def csr_digest(matrix) -> str:
    digest = hashlib.sha256()

    digest.update(
        np.ascontiguousarray(
            matrix.data
        ).tobytes()
    )

    digest.update(
        np.ascontiguousarray(
            matrix.indices
        ).tobytes()
    )

    digest.update(
        np.ascontiguousarray(
            matrix.indptr
        ).tobytes()
    )

    return digest.hexdigest()


def load_inputs():
    with TRANSDUCTION_CONFIG.open(
        "rb"
    ) as handle:
        transduction = tomllib.load(
            handle
        )

    release_gain = float(
        transduction[
            "transduction"
        ][
            "release_gain"
        ]
    )

    connectome = sparse.load_npz(
        CONNECTOME
    ).tocsr()

    retina = np.load(
        RETINA
    )

    retinal_indices = np.asarray(
        retina["neuron_index"],
        dtype=np.int32,
    )

    consensus = np.load(
        CONSENSUS
    )

    channel_indices = build_channel_indices(
        consensus
    )

    return (
        connectome,
        retinal_indices,
        channel_indices,
        release_gain,
    )


def build_test_plasticity(
    connectome,
):
    baseline_weight = float(
        connectome[
            POST,
            PRE,
        ]
    )

    if baseline_weight == 0.0:
        raise RuntimeError(
            "frozen validation edge is absent"
        )

    state = build_empty_plasticity_state()

    state = apply_plasticity_update(
        state,
        presynaptic=PRE,
        postsynaptic=POST,
        baseline_artifact_id=ARTIFACT_ID,
        baseline_weight=baseline_weight,
        session_id="mq7-smoke-preload",
        evidence_reference=(
            "mq7-validated-pathway-"
            "56393-68045-1273"
        ),
    )

    return state, baseline_weight


def compare(
    condition,
    baseline,
    adaptive,
):
    print()
    print("=" * 72)
    print(
        f"CONDITION {condition}"
    )
    print("=" * 72)

    voltage_same = (
        baseline[
            "voltage_trace_sha256"
        ]
        == adaptive[
            "voltage_trace_sha256"
        ]
    )

    spike_same = (
        baseline[
            "spike_trace_sha256"
        ]
        == adaptive[
            "spike_trace_sha256"
        ]
    )

    print(
        "voltage trace identical:",
        voltage_same,
    )

    print(
        "spike trace identical:",
        spike_same,
    )

    print(
        "baseline decision:",
        baseline["decision"],
    )

    print(
        "plasticity decision:",
        adaptive["decision"],
    )

    print()
    print("channel score deltas:")

    any_score_delta = False

    for channel in baseline["scores"]:
        delta = (
            adaptive["scores"][channel]
            - baseline["scores"][channel]
        )

        if delta != 0.0:
            any_score_delta = True

        print(
            f"  {channel}:",
            delta,
        )

    print()

    if (
        voltage_same
        and spike_same
        and not any_score_delta
    ):
        print(
            "RESULT: NO MEASURABLE REPLAY "
            "DIVERGENCE"
        )

        print(
            "Interpretation: this replay did not "
            "measurably exercise the preloaded "
            "SC-03 edge."
        )

    else:
        print(
            "RESULT: MEASURABLE NEURAL "
            "DIVERGENCE"
        )

        print(
            "Interpretation: the preloaded "
            "SC-03 multiplier altered this "
            "matched replay."
        )


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

    (
        plasticity_state,
        baseline_weight,
    ) = build_test_plasticity(
        connectome
    )

    modifier = build_synaptic_modifier(
        plasticity_state
    )

    edge = plasticity_state.edges[0]

    print("=" * 72)
    print(
        "MQ-7 MATCHED PLASTICITY "
        "MECHANICS SMOKE TEST"
    )
    print("=" * 72)

    print(
        "edge:",
        f"{PRE} -> {POST}",
    )

    print(
        "baseline weight:",
        baseline_weight,
    )

    print(
        "persisted multiplier:",
        edge.multiplier,
    )

    print(
        "financial semantics used: NO"
    )

    print(
        "biological learning claim: NO"
    )

    for condition in (
        "A",
        "B",
    ):
        print()
        print(
            f"running {condition} baseline..."
        )

        baseline = run_replay(
            condition,
            connectome,
            retinal_indices,
            channel_indices,
            release_gain,
        )

        print(
            f"running {condition} "
            "with preloaded SC-03..."
        )

        adaptive = run_replay(
            condition,
            connectome,
            retinal_indices,
            channel_indices,
            release_gain,
            synaptic_modifier=modifier,
        )

        compare(
            condition,
            baseline,
            adaptive,
        )

    after_digest = csr_digest(
        connectome
    )

    print()
    print("=" * 72)

    print(
        "connectome unchanged:",
        before_digest == after_digest,
    )

    if before_digest != after_digest:
        raise RuntimeError(
            "baseline connectome was mutated"
        )

    print(
        "SMOKE TEST COMPLETE"
    )


if __name__ == "__main__":
    main()
