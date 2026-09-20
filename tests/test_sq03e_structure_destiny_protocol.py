import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "config" / "experiments" / "sq03e_structure_destiny_v1.json"
DOC = ROOT / "docs" / "experiments" / "sq03e-structure-destiny-protocol.md"


def load():
    return json.loads(CFG.read_text())


def test_identity_and_status():
    cfg = load()
    assert cfg["sidequest_id"] == "SQ-03E"
    assert cfg["title"] == "STRUCTURE IS NOT DESTINY"
    assert cfg["status"] == "FROZEN_BEFORE_ANALYSIS"


def test_primary_unit_is_edge():
    cfg = load()
    assert cfg["unit_of_analysis"]["primary"] == "edge_id"


def test_primary_structural_predictor_is_absolute_weight_difference():
    cfg = load()
    assert cfg["structural_predictors"]["primary"] == "abs(weight_m - weight_f)"


def test_primary_dynamic_outcome_uses_raw_s_not_ratio_a():
    cfg = load()
    assert "total_effect_magnitude S" in cfg["dynamic_outcomes"]["primary"]
    assert cfg["dynamic_outcomes"]["normalized_asymmetry_A_excluded_from_acceptance"] is True


def test_top_fraction_is_frozen():
    cfg = load()
    assert cfg["analyses"]["extreme_overlap"]["top_fraction"] == 0.01


def test_absolute_weight_stratification_is_frozen():
    cfg = load()
    s = cfg["analyses"]["weight_magnitude_stratification"]
    assert s["enabled"] is True
    assert s["bins"] == 10


def test_sq03d1_failure_is_preserved():
    cfg = load()
    h = cfg["sq03d1_status_handling"]
    assert h["formal_result"] == "FAILED"
    assert "normalized asymmetry ratio A failed" in h["reason"]


def test_no_fake_population_statistics():
    cfg = load()
    s = cfg["statistics"]
    assert s["population_p_values"] is False
    assert s["confidence_intervals_for_flies"] is False
    assert s["formal_significance_threshold"] is False


def test_protocol_does_not_assume_title_is_true():
    text = DOC.read_text()
    assert "The experiment does not assume the title is true." in text

def test_deterministic_implementation_is_frozen():
    cfg = load()
    impl = cfg["deterministic_implementation"]
    assert impl["spearman"]["rank_method"] == "average"
    assert impl["top_fraction"]["k_rule"] == "ceil(N * 0.01)"
    assert impl["top_fraction"]["tie_break"] == "edge_id ASC"
    assert impl["top_fraction"]["exact_k_no_tie_expansion"] is True
    assert impl["deciles"]["assignment"] == "equal-count bins after ascending sort"
    assert impl["edge_lookup"]["pre_post_identity_must_match"] is True
    assert "conservative matched-edge table" in impl["edge_lookup"]["edge_id_semantics"]
    assert all(a["timing"] == "BEFORE_ANALYSIS" for a in cfg["protocol_amendments"])



def test_sq03e_a2_preserves_conservative_filter():
    cfg = load()
    lookup = cfg["deterministic_implementation"]["edge_lookup"]
    assert lookup["conservative_filter"] == (
        'verdict_corr == "isomorphic" AND weight_m > 0 AND weight_f > 0'
    )
    assert lookup["original_feather_row_preserved_for_audit"] is True
    assert any(a["id"] == "SQ-03E-A2" for a in cfg["protocol_amendments"])
