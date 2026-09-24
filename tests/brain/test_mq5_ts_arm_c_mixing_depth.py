from __future__ import annotations

import numpy as np
from scipy import sparse

from brain.mq5_ts_arm_c_mixing_depth import (
    assert_execution_authorized,
    assert_prefix_contract_source,
    assert_synthetic_determinism,
    baseline_metrics,
    classify_seed_memory,
    eligible_overlap_fraction,
    structural_intersection_count,
)


def graph(edges, n=5):
    rows = np.asarray([post for post, pre in edges], dtype=np.int32)
    cols = np.asarray([pre for post, pre in edges], dtype=np.int32)
    data = np.ones(len(edges), dtype=np.float32)
    m = sparse.csr_matrix(
        (data, (rows, cols)),
        shape=(n, n),
        dtype=np.float32,
    )
    m.sort_indices()
    return m


def test_structural_intersection_counts_directed_edge_identity():
    a = graph([(0, 1), (0, 2), (1, 3), (2, 4)])
    b = graph([(0, 1), (0, 3), (1, 3), (2, 0)])
    assert structural_intersection_count(a, b) == 2


def test_eligible_overlap_subtracts_protected_exact_edges():
    a = graph([(1, 0), (1, 2), (2, 3), (3, 4)])
    b = graph([(1, 0), (1, 3), (2, 2), (3, 4)])

    value = eligible_overlap_fraction(
        a,
        b,
        protected_edges=1,
        eligible_edges=3,
    )
    assert np.isclose(value, 1.0 / 3.0)


def test_baseline_metrics_equal_set_sizes():
    a = graph([(0, 1), (1, 2), (2, 3), (3, 4)])
    b = graph([(0, 1), (1, 3), (2, 2), (3, 4)])

    m = baseline_metrics(
        a,
        b,
        protected_edges=0,
        eligible_edges=4,
    )

    assert np.isclose(m["retention_fraction"], 0.5)
    assert np.isclose(m["changed_fraction"], 0.5)
    assert np.isclose(m["baseline_edge_jaccard"], 2.0 / 6.0)


def test_classification_accepts_1x_only_when_every_seed_within_tolerance():
    seeds = [1, 2, 3]
    memory = {
        1.0: {1: 0.001, 2: 0.009, 3: 0.010},
        2.0: {1: 0.0, 2: 0.0, 3: 0.0},
    }
    assert classify_seed_memory(
        memory,
        tolerance=0.01,
        required_seeds=seeds,
        complete=True,
        invariants_ok=True,
    ) == "CURRENT_1X_ADEQUATE_FOR_SQ05"


def test_classification_falls_forward_to_2x_prospectively():
    seeds = [1, 2, 3]
    memory = {
        1.0: {1: 0.011, 2: 0.002, 3: 0.001},
        2.0: {1: 0.005, 2: 0.006, 3: 0.007},
    }
    assert classify_seed_memory(
        memory,
        tolerance=0.01,
        required_seeds=seeds,
        complete=True,
        invariants_ok=True,
    ) == "SQ05_REQUIRES_2X_PROSPECTIVE_DEPTH"


def test_classification_blocks_when_2x_also_retains_memory():
    seeds = [1, 2, 3]
    memory = {
        1.0: {1: 0.02, 2: 0.02, 3: 0.02},
        2.0: {1: 0.02, 2: 0.005, 3: 0.005},
    }
    assert classify_seed_memory(
        memory,
        tolerance=0.01,
        required_seeds=seeds,
        complete=True,
        invariants_ok=True,
    ) == "NO_ADEQUATE_DEPTH_WITHIN_TESTED_RANGE"


def test_classification_fails_closed():
    seeds = [1, 2, 3]
    memory = {
        1.0: {1: 0.0, 2: 0.0, 3: 0.0},
        2.0: {1: 0.0, 2: 0.0, 3: 0.0},
    }
    assert classify_seed_memory(
        memory,
        tolerance=0.01,
        required_seeds=seeds,
        complete=False,
        invariants_ok=True,
    ) == "INCOMPLETE_OR_INVALID"
    assert classify_seed_memory(
        memory,
        tolerance=0.01,
        required_seeds=seeds,
        complete=True,
        invariants_ok=False,
    ) == "INCOMPLETE_OR_INVALID"

def test_prefix_source_contract_and_synthetic_determinism():
    source = assert_prefix_contract_source()
    assert source["source_contract_checked"] is True
    assert source["target_use_restricted_to_termination"] is True

    replay = assert_synthetic_determinism()
    assert replay["synthetic_only"] is True
    assert replay["seed_is_preregistered"] is False
    assert replay["same_seed_exact_replay"] is True


def test_result_execution_is_locked_without_authorization(monkeypatch, tmp_path):
    import brain.mq5_ts_arm_c_mixing_depth as mix

    monkeypatch.setattr(
        mix,
        "AUTHORIZATION",
        tmp_path / "missing-authorization.json",
    )

    try:
        assert_execution_authorized()
    except RuntimeError as exc:
        assert "authorization is absent" in str(exc)
    else:
        raise AssertionError("execution unexpectedly authorized")
