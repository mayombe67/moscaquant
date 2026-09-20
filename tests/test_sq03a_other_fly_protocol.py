import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "experiments" / "sq03a_other_fly_v1.json"
PROTOCOL = ROOT / "docs" / "experiments" / "sq03a-other-fly-protocol.md"

EXPECTED_INPUTS = {
    "TmY14","AN_multi_124","AVLP532","CB2576","DNc01","LHPV6q1",
    "LPLC2","aMe4","AVLP234","AVLP435","CB4116","SLP230",
}
EXPECTED_ANCHORS = {"DNc02","DNp27","DNp30"}

def load():
    return json.loads(CONFIG.read_text())

def test_sq03a_is_frozen_before_execution():
    cfg = load()
    assert cfg["sidequest_id"] == "SQ-03A"
    assert cfg["title"] == "THE OTHER FLY"
    assert cfg["status"] == "FROZEN_BEFORE_NEURAL_EXECUTION"

def test_sq03a_uses_only_official_matched_graph():
    cfg = load()
    scope = cfg["comparison_scope"]
    assert scope["edge_rule"]["verdict_corr"] == "isomorphic"
    assert scope["edge_rule"]["weight_m"] == ">0"
    assert scope["edge_rule"]["weight_f"] == ">0"
    assert scope["vnc_excluded"] is True
    assert scope["optic_lobe_source_reconstruction"] is False
    assert scope["inferred_edges"] is False
    assert scope["shuffled_fill"] is False

def test_sq03a_input_panel_is_fixed():
    cfg = load()
    rule = cfg["frozen_input_panel_rule"]
    assert rule["minimum_anchor_count"] == 2
    assert set(rule["expected_labels_from_qualification"]) == EXPECTED_INPUTS
    assert rule["post_execution_selection_allowed"] is False

def test_sq03a_output_anchors_are_fixed():
    cfg = load()
    assert {x["label"] for x in cfg["frozen_output_anchors"]} == EXPECTED_ANCHORS

def test_sq03a_only_connectomic_difference_is_aligned_weight():
    cfg = load()
    assert cfg["subject_a"]["weight_column"] == "weight_m"
    assert cfg["subject_b"]["weight_column"] == "weight_f"
    assert cfg["runtime_rule"]["same_model_equations"] is True
    assert cfg["runtime_rule"]["same_nonconnectomic_parameters"] is True
    assert cfg["stimulus"]["same_schedule_both_subjects"] is True
    assert cfg["stimulus"]["same_amplitude_both_subjects"] is True

def test_sq03a_has_no_financial_semantics():
    cfg = load()
    assert cfg["stimulus"]["market_semantics"] is False
    assert cfg["stimulus"]["financial_semantics"] is False
    text = PROTOCOL.read_text()
    assert "No financial authority" in text
