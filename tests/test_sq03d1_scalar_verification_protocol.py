import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "config" / "experiments" / "sq03d1_scalar_verification_v1.json"
DOC = ROOT / "docs" / "experiments" / "sq03d1-scalar-verification-protocol.md"

def load():
    return json.loads(CFG.read_text())

def test_identity_and_status():
    cfg = load()
    assert cfg["sidequest_id"] == "SQ-03D.1"
    assert cfg["title"] == "DOUBLE CHECK THE KNIFE"
    assert cfg["status"] == "FROZEN_BEFORE_PANEL_SELECTION"

def test_panel_sizes_are_frozen():
    cfg = load()
    sel = cfg["panel_selection"]
    assert sel["upper_tail_pairs"] == 16
    assert sel["low_tail_controls"] == 16

def test_selection_is_stratified():
    cfg = load()
    sel = cfg["panel_selection"]
    assert sel["stratify_by_input"] is True
    assert sel["minimum_upper_per_input"] == 2
    assert sel["minimum_low_per_input"] == 2

def test_no_manual_posthoc_selection():
    cfg = load()
    sel = cfg["panel_selection"]
    assert sel["no_manual_addition"] is True
    assert sel["no_post_selection_substitution"] is True


def test_panel_source_replay_is_evidence_recovery_only():
    cfg = load()
    sel = cfg["panel_selection"]
    replay = sel["replay_constraints"]
    assert replay["sq03d_result_summary_must_match"] is True
    assert replay["sq03d_top100_must_match"] is True
    assert replay["sq03b_ledger_hash_must_match_sq03d"] is True
    assert replay["no_new_neural_dynamics"] is True
    assert replay["no_selection_rule_change"] is True
    assert cfg["protocol_amendments"][0]["timing"] == "BEFORE_PANEL_SELECTION"

def test_both_subjects_are_required():
    cfg = load()
    assert cfg["execution"]["subjects"] == ["MORTY", "LILITH"]

def test_scalar_controls_are_required():
    cfg = load()
    ex = cfg["execution"]
    assert ex["exact_aa_required"] is True
    assert ex["sq03a_baseline_replay_required"] is True

def test_existing_tolerance_reused():
    cfg = load()
    ver = cfg["verification"]
    assert ver["batched_scalar_rtol"] == 1e-6
    assert ver["batched_scalar_atol"] == 1e-7

def test_no_fake_statistics():
    cfg = load()
    assert cfg["verification"]["formal_p_value_claim"] is False
    assert "No p-value is generated from simulation rows." in DOC.read_text()

def test_stratified_allocation_is_fully_algorithmic():
    cfg = load()
    alloc = cfg["panel_selection"]["stratified_allocation"]
    assert alloc["pair_identity"] == ["input", "edge_id", "anchor"]
    assert alloc["upper_low_overlap_allowed"] is False
    assert alloc["manual_override_allowed"] is False
    assert "first 2 pairs for each input" in alloc["upper"][1]
    assert "first 2 remaining pairs for each input" in alloc["low"][2]
    ids = [a["id"] for a in cfg["protocol_amendments"]]
    assert "SQ-03D.1-A1" in ids
    assert "SQ-03D.1-A2" in ids
    assert all(a["timing"] == "BEFORE_PANEL_SELECTION" for a in cfg["protocol_amendments"])

