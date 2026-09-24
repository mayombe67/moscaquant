from pathlib import Path

import numpy as np
from scipy import sparse

import brain.sq06_orientation_groups as g


def test_group_resolution_exact_sizes_and_responders():
    lr_target, lr_sham, _ = g.resolve_group_edges("LR_OBSERVED")
    rl_target, rl_sham, _ = g.resolve_group_edges("RL_OBSERVED")

    assert len(lr_target) == len(lr_sham) == 10
    assert len(rl_target) == len(rl_sham) == 3

    target_union = {(a, b) for a, b, _ in lr_target + rl_target}
    assert len(target_union) == 13

    lr_responders = {
        row["accepted_responder"]
        for row in g._load_frozen_group_payload()["groups"]["LR_OBSERVED"]
    }
    rl_responders = {
        row["accepted_responder"]
        for row in g._load_frozen_group_payload()["groups"]["RL_OBSERVED"]
    }
    assert lr_responders == {51, 55, 92, 129, 656, 1273}
    assert rl_responders == {317, 126002, 137122}


def test_group_target_and_sham_presynaptic_sequences_match():
    for name in g.GROUP_NAMES:
        target, sham, _ = g.resolve_group_edges(name)
        assert [x[0] for x in target] == [x[0] for x in sham]


def test_groups_are_disjoint_and_union_historical_13():
    lr, _, _ = g.resolve_group_edges("LR_OBSERVED")
    rl, _, _ = g.resolve_group_edges("RL_OBSERVED")
    historical, _ = g.load_betrayal_i_edges()

    lr_pairs = {(a, b) for a, b, _ in lr}
    rl_pairs = {(a, b) for a, b, _ in rl}
    all_pairs = {(a, b) for a, b, _ in historical}

    assert lr_pairs.isdisjoint(rl_pairs)
    assert lr_pairs | rl_pairs == all_pairs


def test_zero_subset_verifier_on_synthetic_matrix():
    baseline = sparse.csr_matrix(
        np.asarray(
            [
                [0.0, 0.0, 0.0, 0.0],
                [0.5, 0.0, 0.0, 0.0],
                [0.0, 0.7, 0.0, 0.0],
                [0.0, 0.0, 0.9, 0.0],
            ],
            dtype=np.float64,
        )
    )
    edges = [(0, 1, 0.5), (1, 2, 0.7)]
    candidate = g.zero_edges(baseline, edges)
    g.verify_exact_zero_subset(baseline, candidate, edges)


def test_zero_subset_verifier_rejects_extra_change():
    baseline = sparse.csr_matrix(
        np.asarray(
            [
                [0.0, 0.0, 0.0],
                [0.5, 0.0, 0.0],
                [0.0, 0.7, 0.0],
            ],
            dtype=np.float64,
        )
    )
    expected = [(0, 1, 0.5)]
    candidate = g.zero_edges(baseline, expected)
    candidate = g.zero_edges(candidate, [(1, 2, 0.7)])

    try:
        g.verify_exact_zero_subset(baseline, candidate, expected)
    except RuntimeError:
        pass
    else:
        raise AssertionError("extra mutation should be rejected")


def test_module_has_no_result_cli():
    source = Path(g.__file__).read_text(encoding="utf-8")
    assert "--run-frozen" not in source
    assert "argparse" not in source
    assert "result writer" not in source.lower()
