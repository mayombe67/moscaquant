import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "config" / "experiments" / "sq03f2_capo_test_v1.json"

def load():
    return json.loads(CFG.read_text())

def test_identity_and_status():
    cfg = load()
    assert cfg["sidequest_id"] == "SQ-03F.2"
    assert cfg["title"] == "THE CAPO TEST"
    assert cfg["status"] == "FROZEN_BEFORE_ANALYSIS"

def test_no_new_neural_dynamics():
    assert load()["data_and_universe"]["no_new_neural_dynamics"] is True

def test_primary_is_leave_one_edge_out():
    names = [x["name"] for x in load()["primary_features"]]
    assert names == [
        "leave_one_edge_out_source_strength",
        "leave_one_edge_out_mean_outgoing_weight",
    ]

def test_concentration_metrics_frozen():
    names = [x["name"] for x in load()["secondary_features"]]
    assert "source_top1_output_share" in names
    assert "source_top5_output_share" in names
    assert "source_output_hhi" in names

def test_no_pvalues_or_threshold():
    r = load()["reporting"]
    assert r["no_p_values"] is True
    assert r["no_significance_threshold"] is True

def test_family_model_has_no_authority():
    assert "no scientific authority" in load()["family_model"]["firewall"]
