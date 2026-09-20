import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "experiments" / "sq03b_mechanistic_localization_v1.json"
PROTOCOL = ROOT / "docs" / "experiments" / "sq03b-mechanistic-localization-protocol.md"

EXPECTED_INPUTS = {"TmY14", "LPLC2", "AVLP234", "AVLP435"}
EXPECTED_ANCHORS = {"DNc02", "DNp27", "DNp30"}


def load():
    return json.loads(CONFIG.read_text())


def test_sq03b_is_frozen_before_localization():
    cfg = load()
    assert cfg["sidequest_id"] == "SQ-03B"
    assert cfg["title"] == "FIND THE DIFFERENCE"
    assert cfg["status"] == "FROZEN_BEFORE_LOCALIZATION_EXECUTION"


def test_sq03b_followup_inputs_are_exact():
    cfg = load()
    assert set(cfg["frozen_inputs"]) == EXPECTED_INPUTS
    assert set(cfg["frozen_anchors"]) == EXPECTED_ANCHORS
    assert "SQ-03A" in cfg["parent_result"]["sidequest_id"]


def test_sq03b_candidate_selection_is_structural_and_preoutcome():
    cfg = load()
    rule = cfg["candidate_edge_rule"]
    assert rule["max_hops"] == 4
    assert rule["simple_paths_only"] is True
    assert rule["selection_uses_sq03b_outcomes"] is False
    assert rule["weight_difference_required"] is True


def test_sq03b_uses_single_edge_equalization_only():
    cfg = load()
    method = cfg["localization_method"]
    assert method["name"] == "single-edge counterfactual equalization"
    assert method["no_multi_edge_search"] is True
    assert method["no_greedy_combination_search"] is True
    assert method["no_parameter_retuning"] is True


def test_sq03b_preserves_controls():
    cfg = load()
    controls = cfg["controls"]
    assert controls["baseline_replay_must_match_sq03a"] is True
    assert controls["aa_replay_required"] is True
    assert controls["candidate_set_frozen_before_counterfactual_execution"] is True


def test_sq03b_claim_boundary_blocks_biological_overreach():
    cfg = load()
    text = cfg["claim_boundary"]
    assert "does not establish biological mechanism" in text
    assert "general sex differences" in text
    assert "financial utility" in text
