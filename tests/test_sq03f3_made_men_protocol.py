import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "config" / "experiments" / "sq03f3_made_men_v1.json"

def load():
    return json.loads(CFG.read_text())

def test_identity_and_status():
    cfg = load()
    assert cfg["sidequest_id"] == "SQ-03F.3"
    assert cfg["title"] == "MADE MEN"
    assert cfg["status"] == "FROZEN_BEFORE_ANALYSIS"

def test_hotspots_are_reused_exactly():
    h = load()["universe"]["hotspot_sets"]
    assert "reuse exact SQ-03F" in h["S"]
    assert "reuse exact SQ-03F" in h["C"]

def test_null_is_stratified_and_fixed():
    n = load()["null_model"]
    assert n["iterations"] == 10000
    assert n["seed"] == 314159
    assert n["strata"] == [
        "context_count",
        "total_weight_decile",
        "abs_weight_difference_decile",
    ]

def test_no_new_neural_dynamics():
    assert load()["universe"]["no_new_neural_dynamics"] is True

def test_no_pvalues_or_threshold():
    r = load()["randomization_reporting"]
    assert r["no_p_values"] is True
    assert r["no_significance_threshold"] is True

def test_family_model_is_presentation_only():
    assert "presentation-only" in load()["family_model"]["firewall"]
