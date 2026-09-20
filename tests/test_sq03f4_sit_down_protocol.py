import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "config" / "experiments" / "sq03f4_sit_down_v1.json"

def load():
    return json.loads(CFG.read_text())

def test_identity_and_status():
    cfg = load()
    assert cfg["sidequest_id"] == "SQ-03F.4"
    assert cfg["title"] == "THE SIT-DOWN"
    assert cfg["status"] == "FROZEN_BEFORE_ANALYSIS"

def test_made_definition_is_exact_top_one_percent():
    d = load()["made_source_definition"]
    assert "exact top 1%" in d["selection"]
    assert d["ties"] == "source label ASC; exact k; no tie expansion"

def test_controls_match_opportunity():
    c = load()["control_definition"]
    assert c["exact_match_bins"] == [
        "candidate_edge_count_decile",
        "sum_candidate_context_count_decile",
        "distinct_candidate_context_signature_count_decile",
    ]
    assert c["without_replacement"] is True

def test_no_new_neural_dynamics():
    assert load()["universe"]["no_new_neural_dynamics"] is True

def test_no_pvalues_or_threshold():
    r = load()["reporting"]
    assert r["no_p_values"] is True
    assert r["no_significance_threshold"] is True

def test_family_model_has_no_authority():
    assert "no scientific authority" in load()["family_model"]["firewall"]
