import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "config" / "experiments" / "sq03f_hotspot_test_v1.json"


def load():
    return json.loads(CFG.read_text())


def test_identity_and_status():
    cfg = load()
    assert cfg["sidequest_id"] == "SQ-03F"
    assert cfg["title"] == "HOTSPOT TEST"
    assert cfg["status"] == "FROZEN_BEFORE_ANALYSIS"


def test_hotspot_fraction_is_frozen():
    h = load()["hotspots"]
    assert h["fraction"] == 0.01
    assert h["k_rule"] == "ceil(N * 0.01)"
    assert h["tie_break"] == "edge_id ASC"
    assert h["exact_k_no_tie_expansion"] is True


def test_primary_features_are_frozen():
    assert load()["features"]["primary"] == [
        "source_out_degree",
        "target_in_degree",
        "source_output_fraction",
        "target_input_fraction",
    ]


def test_controls_match_two_structural_bins():
    m = load()["matched_controls"]
    assert m["ratio"] == "1:1"
    assert m["without_replacement"] is True
    assert m["match_bins"] == [
        "total_weight_decile",
        "abs_weight_difference_decile",
    ]
    assert "do not widen bins post hoc" in m["failure_rule"]


def test_no_population_significance():
    c = load()["comparisons"]
    assert c["no_p_values"] is True
    assert c["no_significance_threshold"] is True


def test_same_conservative_graph():
    assert load()["network"]["edge_filter"] == (
        'verdict_corr == "isomorphic" AND weight_m > 0 AND weight_f > 0'
    )
