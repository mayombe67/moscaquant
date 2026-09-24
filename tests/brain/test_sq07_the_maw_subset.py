from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from scipy import sparse

import brain.sq05_betrayal_i as b1
import brain.sq06_orientation_groups as g
import brain.sq07_the_maw_subset as s
from brain.mq3_2_causal_intervention import zero_edges


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "brain/sq07_the_maw_subset.py"


def matrices_equal(a, b) -> bool:
    return (
        a.shape == b.shape
        and a.nnz == b.nnz
        and (a != b).nnz == 0
    )


def historical_baseline():
    edges, _ = b1.load_betrayal_i_edges()

    rows = [post for pre, post, weight in edges]
    cols = [pre for pre, post, weight in edges]
    data = [weight for pre, post, weight in edges]

    # One unrelated positive edge proves non-registry topology survives.
    rows.append(0)
    cols.append(0)
    data.append(0.25)

    shape = (
        max(rows) + 1,
        max(cols) + 1,
    )

    return sparse.csr_matrix(
        (
            np.asarray(data, dtype=np.float64),
            (
                np.asarray(rows, dtype=np.int32),
                np.asarray(cols, dtype=np.int32),
            ),
        ),
        shape=shape,
    )


def test_subset_operator_binds_exact_frozen_dependencies():
    deps = s.verify_frozen_dependencies()

    assert deps["dependencies"]["registry"] == (
        "0e9502f3147d2f833d00ce2c05af258b973f7391a43c9d89f695556d8823dedd"
    )
    assert deps["dependencies"]["sq05_betrayal_i"] == (
        "c62767cac434f380104c8da5cd9b73dcee89fefbeea0a0efe17ca9bd812c8664"
    )
    assert deps["dependencies"]["mq32_zero_edge_operator"] == (
        "007aa507ac22b07811bff5ae8102a0916c88549aa3011fa22fa57c70598c6a87"
    )
    assert deps["edge_count"] == 13


def test_registry_resolves_exact_historical_full13_in_registry_order():
    resolved = s.resolve_registry_edges()
    historical, _ = b1.load_betrayal_i_edges()

    assert len(resolved) == 13
    assert set(resolved) == set(historical)

    assert [(a, b) for a, b, _ in resolved] == [
        (43417, 656),
        (44274, 55),
        (55548, 51),
        (55925, 55),
        (56393, 68045),
        (64717, 92),
        (68045, 1273),
        (87441, 51),
        (92657, 129),
        (93484, 129),
        (65084, 137122),
        (128590, 317),
        (135589, 126002),
    ]


def test_mask_selection_is_exact_bit_to_edge_coordinate_mapping():
    resolved = s.resolve_registry_edges()

    mask = "".join(
        "1" if i in {0, 4, 12} else "0"
        for i in range(13)
    )

    selected = s.selected_edges_for_mask(mask, resolved)

    assert selected == (
        resolved[0],
        resolved[4],
        resolved[12],
    )


def test_intact_mask_selects_no_edges():
    resolved = s.resolve_registry_edges()

    assert s.selected_edges_for_mask(
        s.INTACT_MASK,
        resolved,
    ) == ()


def test_full13_mask_is_exact_historical_betrayal_i_edge_set():
    resolved = s.resolve_registry_edges()

    selected = s.selected_edges_for_mask(
        s.FULL13_MASK,
        resolved,
    )

    historical, _ = b1.load_betrayal_i_edges()

    assert selected == resolved
    assert len(selected) == 13
    assert set(selected) == set(historical)


def test_lr_anchor_is_exact_sq06_target_group():
    resolved = s.resolve_registry_edges()

    selected = s.selected_edges_for_mask(
        s.LR_GROUP_MASK,
        resolved,
    )

    expected, _, _ = g.resolve_group_edges("LR_OBSERVED")

    assert selected == tuple(expected)


def test_rl_anchor_is_exact_sq06_target_group():
    resolved = s.resolve_registry_edges()

    selected = s.selected_edges_for_mask(
        s.RL_GROUP_MASK,
        resolved,
    )

    expected, _, _ = g.resolve_group_edges("RL_OBSERVED")

    assert selected == tuple(expected)


def test_four_anchor_topologies_exactly_reproduce_inherited_operators():
    baseline = historical_baseline()
    resolved = s.resolve_registry_edges()

    intact, _ = s.build_mask_subset(
        baseline,
        s.INTACT_MASK,
        resolved,
    )
    assert matrices_equal(intact, baseline)

    full13, _ = s.build_mask_subset(
        baseline,
        s.FULL13_MASK,
        resolved,
    )
    inherited_full13, _ = b1.build_betrayal_i(baseline)
    assert matrices_equal(full13, inherited_full13)

    lr, _ = s.build_mask_subset(
        baseline,
        s.LR_GROUP_MASK,
        resolved,
    )
    inherited_lr, _ = g.build_orientation_group(
        baseline,
        "LR_OBSERVED",
        "TARGETED",
    )
    assert matrices_equal(lr, inherited_lr)

    rl, _ = s.build_mask_subset(
        baseline,
        s.RL_GROUP_MASK,
        resolved,
    )
    inherited_rl, _ = g.build_orientation_group(
        baseline,
        "RL_OBSERVED",
        "TARGETED",
    )
    assert matrices_equal(rl, inherited_rl)


def test_arbitrary_mask_changes_only_selected_frozen_edges():
    baseline = historical_baseline()
    resolved = s.resolve_registry_edges()

    selected_indices = {0, 3, 6, 11}

    mask = "".join(
        "1" if i in selected_indices else "0"
        for i in range(13)
    )

    candidate, provenance = s.build_mask_subset(
        baseline,
        mask,
        resolved,
    )

    assert candidate.nnz == baseline.nnz - len(selected_indices)
    assert float(candidate[0, 0]) == 0.25

    for i, (pre, post, weight) in enumerate(resolved):
        expected = 0.0 if i in selected_indices else weight
        assert float(candidate[post, pre]) == pytest.approx(expected)

    assert provenance["selected_edge_indices"] == [0, 3, 6, 11]
    assert provenance["selected_edge_ids"] == [
        "E00",
        "E03",
        "E06",
        "E11",
    ]


def test_operator_does_not_mutate_baseline_in_place():
    baseline = historical_baseline()
    before = baseline.copy()
    resolved = s.resolve_registry_edges()

    s.build_mask_subset(
        baseline,
        "1010101010101",
        resolved,
    )

    assert matrices_equal(baseline, before)


def test_exact_subset_verifier_rejects_extra_mutation():
    baseline = historical_baseline()
    resolved = s.resolve_registry_edges()

    expected = (resolved[0],)

    candidate = zero_edges(
        baseline,
        expected,
    )

    candidate = zero_edges(
        candidate,
        (resolved[1],),
    )

    with pytest.raises(s.Refusal):
        s.verify_exact_mask_subset(
            baseline,
            candidate,
            expected,
        )


def test_invalid_masks_fail_closed():
    with pytest.raises(ValueError):
        s.validate_mask("")

    with pytest.raises(ValueError):
        s.validate_mask("0" * 12)

    with pytest.raises(ValueError):
        s.validate_mask("0" * 12 + "X")

    with pytest.raises(ValueError):
        s.validate_mask(0)


def test_subset_operator_has_no_execution_or_analysis_surface():
    source = SOURCE.read_text(encoding="utf-8")

    forbidden = [
        "argparse",
        "--run-frozen",
        "run_episode",
        "CONNECTOME",
        "RETINA",
        "mq5_ts_runtime",
        "EXACT_INTACT",
        "EXACT_FULL13",
        "INTERMEDIATE",
        "condition_plan",
        "shard_plan",
        "symmetric_normalized_l2",
    ]

    for token in forbidden:
        assert token not in source
