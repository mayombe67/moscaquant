from __future__ import annotations

from pathlib import Path

import numpy as np
from scipy import sparse

from oracle.credit_assignment import (
    classify_credit,
    score_edge,
)
from oracle.d6_bad_synapse import (
    apply_bad_synapse_overlay,
    build_bad_synapse_overlay,
)
from oracle.live_plasticity import (
    apply_live_bad_synapse,
)
from oracle.persistence import (
    load_state,
    write_state,
)
from oracle.plasticity_adapter import (
    get_plasticity_state,
)
from oracle.selector import select_d6
from oracle.state import initial_state


CONNECTOME = (
    "/home/wil/moscaquant-data/processed/"
    "connectome-baseline-v1.npz"
)

ARTIFACT = "connectome-baseline-v1.npz"

SOURCE = 56393
TARGET = 68045


def find_sc03():
    for seed in range(10000):
        result = select_d6(
            seed=seed,
            experiment_id="mq7-live-integration",
            session_id="session-A",
            plasticity_active=True,
        )

        if result.selection.condition.value == "SC-03":
            return result

    raise AssertionError(
        "could not select SC-03"
    )


def test_live_sc03_survives_restart_and_changes_real_edge(
    tmp_path: Path,
):
    connectome = sparse.load_npz(
        CONNECTOME
    ).tocsr()

    original_data = connectome.data.copy()
    original_indices = connectome.indices.copy()
    original_indptr = connectome.indptr.copy()

    weight = float(
        connectome[TARGET, SOURCE]
    )

    assert weight != 0.0

    #
    # 1. Build unique neural credit using the real
    #    frozen connectome weight.
    #

    credit_edge = score_edge(
        presynaptic=SOURCE,
        postsynaptic=TARGET,
        weight=weight,
        activity_history=[1.0],
    )

    credit = classify_credit(
        [credit_edge]
    )

    assert credit.status == "ELIGIBLE"
    assert len(credit.leaders) == 1

    #
    # 2. D6 genuinely selects SC-03 with plasticity enabled.
    #

    d6 = find_sc03()

    assert d6.applicable is True
    assert d6.status == "SELECTED"

    #
    # 3. Apply live BAD SYNAPSE adaptation.
    #

    oracle = initial_state(
        oracle_version="oracle-test-v1",
    )

    live = apply_live_bad_synapse(
        oracle_state=oracle,
        d6_result=d6,
        credit_result=credit,
        baseline_artifact_id=ARTIFACT,
        session_id="session-A",
        evidence_reference="credit-integration-001",
    )

    assert live.status == "UPDATED"

    plasticity = get_plasticity_state(
        live.oracle_state
    )

    assert plasticity is not None
    assert len(plasticity.edges) == 1

    edge_state = plasticity.edges[0]

    assert edge_state.presynaptic == SOURCE
    assert edge_state.postsynaptic == TARGET
    assert np.isclose(
        edge_state.multiplier,
        0.95,
    )

    #
    # 4. Persist Oracle state and simulate restart.
    #

    state_path = tmp_path / "state.json"

    write_state(
        state_path,
        live.oracle_state,
    )

    restarted_oracle = load_state(
        state_path
    )

    restarted_plasticity = get_plasticity_state(
        restarted_oracle
    )

    assert restarted_plasticity is not None

    restarted_edge = restarted_plasticity.edges[0]

    assert restarted_edge == edge_state
    assert np.isclose(
        restarted_edge.multiplier,
        0.95,
    )

    #
    # 5. Use the persisted multiplier on the real edge.
    #

    activity = np.zeros(
        connectome.shape[1],
        dtype=np.float32,
    )

    activity[SOURCE] = 1.0

    baseline = np.asarray(
        connectome @ activity,
        dtype=np.float32,
    ).ravel()

    overlay = build_bad_synapse_overlay(
        presynaptic=restarted_edge.presynaptic,
        postsynaptic=restarted_edge.postsynaptic,
        multiplier=restarted_edge.multiplier,
    )

    adapted = apply_bad_synapse_overlay(
        connectome=connectome,
        effective_activity=activity,
        overlay=overlay,
    )

    #
    # 6. Real postsynaptic contribution must be
    #    exactly 5% lower than baseline.
    #

    expected = (
        baseline[TARGET] * 0.95
    )

    assert np.isclose(
        adapted[TARGET],
        expected,
        rtol=1e-6,
        atol=1e-7,
    )

    expected_delta = (
        weight * -0.05
    )

    actual_delta = (
        adapted[TARGET]
        - baseline[TARGET]
    )

    assert np.isclose(
        actual_delta,
        expected_delta,
        rtol=1e-6,
        atol=1e-7,
    )

    #
    # 7. Structural connectome remains frozen.
    #

    np.testing.assert_array_equal(
        connectome.data,
        original_data,
    )

    np.testing.assert_array_equal(
        connectome.indices,
        original_indices,
    )

    np.testing.assert_array_equal(
        connectome.indptr,
        original_indptr,
    )
