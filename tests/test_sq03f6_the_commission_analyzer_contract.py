import json
from pathlib import Path

import pytest

from brain.sq03f6_analyze import (
    classify_concentration,
    participation_counts,
    participation_mass_hhi,
    participation_summary,
)

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config/experiments/sq03f6_the_commission_v1.json"


def test_sq03f6_config_is_frozen_not_executed():
    cfg = json.loads(CONFIG.read_text())
    assert cfg["experiment_id"] == "SQ-03F.6"
    assert cfg["codename"] == "THE COMMISSION"
    assert cfg["status"] == "FROZEN_NOT_EXECUTED"
    assert cfg["primary_statistic"]["name"] == "participation_mass_hhi"
    assert cfg["null_model"]["randomizations"] == 10000
    assert cfg["null_model"]["base_seed"] == 314159
    assert cfg["null_model"]["matching"]["feature"] == "out_degree"
    assert cfg["null_model"]["matching"]["strata"] == "deciles"


def test_participation_counts_deduplicate_within_source():
    territories = {
        "a": {"x", "y"},
        "b": ["x", "x", "z"],
        "c": {"x"},
    }
    counts = participation_counts(territories)
    assert counts == {"x": 3, "y": 1, "z": 1}


def test_participation_mass_hhi():
    # shares = 3/5, 1/5, 1/5
    counts = {"x": 3, "y": 1, "z": 1}
    assert participation_mass_hhi(counts) == pytest.approx(
        (3/5)**2 + (1/5)**2 + (1/5)**2
    )


def test_hhi_increases_when_mass_is_more_concentrated():
    broad = {"a": 1, "b": 1, "c": 1, "d": 1}
    concentrated = {"a": 3, "b": 1}
    assert participation_mass_hhi(concentrated) > participation_mass_hhi(broad)


def test_participation_summary_is_deterministic():
    summary = participation_summary({"z": 1, "a": 4, "b": 2}, source_count=4)
    assert summary["unique_target_count"] == 3
    assert summary["total_participation_mass"] == 7
    assert summary["max_participation_count"] == 4
    assert summary["targets_reached_by_all_sources"] == 1
    assert summary["targets_reached_by_at_least_half_sources"] == 2
    assert summary["ordered_targets"][0] == {
        "target": "a",
        "participation_count": 4,
    }


def test_positive_concentration_requires_tail_and_effect():
    null = [0.10] * 10000
    result = classify_concentration(
        observed=0.14,
        null_values=null,
        upper_p_threshold=0.01,
        lower_p_threshold=0.01,
        concentration_ratio_threshold=1.25,
        dispersion_ratio_threshold=0.80,
    )
    assert result.label == "GREATER_THAN_NULL_TARGET_CONCENTRATION"


def test_less_than_null_requires_tail_and_effect():
    null = [0.20] * 10000
    result = classify_concentration(
        observed=0.15,
        null_values=null,
        upper_p_threshold=0.01,
        lower_p_threshold=0.01,
        concentration_ratio_threshold=1.25,
        dispersion_ratio_threshold=0.80,
    )
    assert result.label == "LESS_THAN_NULL_TARGET_CONCENTRATION"


def test_middle_result_is_unclassified():
    null = [0.10, 0.11, 0.09, 0.10] * 2500
    result = classify_concentration(
        observed=0.105,
        null_values=null,
        upper_p_threshold=0.01,
        lower_p_threshold=0.01,
        concentration_ratio_threshold=1.25,
        dispersion_ratio_threshold=0.80,
    )
    assert result.label == "NO_CLEAR_EVIDENCE_OF_UNUSUAL_TARGET_CONCENTRATION"
