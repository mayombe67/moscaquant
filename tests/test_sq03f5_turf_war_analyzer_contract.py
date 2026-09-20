import json
from pathlib import Path

import pytest

from brain.sq03f5_analyze import (
    classify,
    decile_strata,
    derive_stream_seed,
    jaccard,
    mean_pairwise_jaccard,
    territory,
)

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config/experiments/sq03f5_turf_war_v1.json"


def test_sq03f5_config_is_frozen_and_not_executed():
    cfg = json.loads(CONFIG.read_text())
    assert cfg["experiment_id"] == "SQ-03F.5"
    assert cfg["codename"] == "TURF WAR"
    assert cfg["status"] == "FROZEN_NOT_EXECUTED"
    assert cfg["territory"]["direction"] == "downstream"
    assert cfg["territory"]["max_depth"] == 2
    assert cfg["primary_statistic"]["name"] == "mean_pairwise_jaccard"
    assert cfg["null_model"]["randomizations"] == 10000
    assert cfg["null_model"]["base_seed"] == 314159
    assert cfg["null_model"]["matching"]["feature"] == "out_degree"
    assert cfg["null_model"]["matching"]["strata"] == "deciles"


def test_territory_is_two_hop_downstream_with_cycle_collapse():
    adjacency = {
        1: [2, 3],
        2: [4, 1],
        3: [5],
        4: [6],
        5: [],
    }
    assert territory(adjacency, 1, max_depth=2) == {2, 3, 4, 5}


def test_jaccard_and_mean_pairwise_statistic():
    assert jaccard({1, 2}, {2, 3}) == pytest.approx(1 / 3)

    observed, pairs = mean_pairwise_jaccard({
        10: {1, 2},
        20: {2, 3},
        30: {2},
    })
    expected = ((1 / 3) + (1 / 2) + (1 / 2)) / 3
    assert observed == pytest.approx(expected)
    assert len(pairs) == 3


def test_empty_union_pair_contributes_zero():
    assert jaccard(set(), set()) == 0.0


def test_decile_strata_is_deterministic():
    degrees = {i: i for i in range(20)}
    a = decile_strata(degrees)
    b = decile_strata(dict(reversed(list(degrees.items()))))
    assert a == b
    assert min(a.values()) == 0
    assert max(a.values()) == 9


def test_stream_seed_derivation_is_explicit():
    assert derive_stream_seed(314159, 0) == 314159
    assert derive_stream_seed(314159, 1) == 314160
    assert derive_stream_seed(314159, 9) == 314168


def test_positive_convergence_requires_tail_and_effect_size():
    null = [0.10] * 10000
    result = classify(
        observed=0.20,
        null_values=null,
        upper_p_threshold=0.01,
        lower_p_threshold=0.01,
        convergence_ratio_threshold=1.25,
        separation_ratio_threshold=0.80,
    )
    assert result.label == "GREATER_THAN_NULL_DOWNSTREAM_CONVERGENCE"


def test_separation_requires_tail_and_effect_size():
    null = [0.20] * 10000
    result = classify(
        observed=0.10,
        null_values=null,
        upper_p_threshold=0.01,
        lower_p_threshold=0.01,
        convergence_ratio_threshold=1.25,
        separation_ratio_threshold=0.80,
    )
    assert result.label == "SEPARATED_DOWNSTREAM_TERRITORIES"


def test_middle_result_remains_unclassified():
    null = [0.10, 0.11, 0.09, 0.10] * 2500
    result = classify(
        observed=0.105,
        null_values=null,
        upper_p_threshold=0.01,
        lower_p_threshold=0.01,
        convergence_ratio_threshold=1.25,
        separation_ratio_threshold=0.80,
    )
    assert result.label == "NO_CLEAR_EVIDENCE_OF_UNUSUAL_CONVERGENCE"
