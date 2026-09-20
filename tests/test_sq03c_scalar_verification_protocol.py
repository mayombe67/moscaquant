import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "config" / "experiments" / "sq03c_scalar_verification_v1.json"
DOC = ROOT / "docs" / "experiments" / "sq03c-scalar-verification-protocol.md"

def load():
    return json.loads(CFG.read_text())

def test_sq03c_identity_and_status():
    cfg = load()
    assert cfg["sidequest_id"] == "SQ-03C"
    assert cfg["title"] == "CHECK THE RECEIPTS"
    assert cfg["status"] == "FROZEN_BEFORE_PANEL_SELECTION"

def test_source_hashes_are_frozen():
    cfg = load()
    assert cfg["parents"]["sq03b_result_sha256"] == "0bcfbeef18ba43e4a3371cae13f1d05a04fc63fc988084e9bf45a33f6a00a2f8"
    assert cfg["parents"]["sq03b_ledger_sha256"] == "7b2632de5792973534177b697efdd7c3af0b82a836d9d2b597812dbc0dd1f725"

def test_panel_selection_is_stratified_and_deterministic():
    cfg = load()
    sel = cfg["panel_selection"]
    assert cfg["strata"]["expected_count"] == 8
    assert sel["upper_tail_per_stratum"]["top_by_abs_integrated_positive_voltage_delta"] == 8
    assert sel["upper_tail_per_stratum"]["top_by_abs_peak_voltage_delta"] == 8
    assert sel["lower_tail_controls_per_stratum"] == 8
    assert sel["no_manual_candidate_addition"] is True
    assert sel["no_post_selection_substitution"] is True

def test_scalar_runtime_is_frozen():
    cfg = load()
    rt = cfg["runtime"]
    assert rt["implementation"] == "brain.hybrid_runtime.HybridRuntime"
    assert rt["execution_mode"] == "scalar_one_job_at_a_time"
    assert rt["frames"] == 64
    assert rt["stimulus_frame"] == 0
    assert rt["stimulus_amplitude"] == 0.5

def test_existing_engineering_tolerance_is_reused():
    cfg = load()
    v = cfg["verification"]
    assert v["batched_vs_scalar_rtol"] == 1e-6
    assert v["batched_vs_scalar_atol"] == 1e-7
    assert "Already-frozen" in v["tolerance_source"]

def test_no_fake_statistical_significance():
    cfg = load()
    assert cfg["verification"]["formal_p_value_claim"] is False
    text = cfg["claim_boundary"]
    assert "does not establish a biological mechanism" in text
    assert "formal population-level statistical significance" in text

def test_protocol_rejects_posthoc_sq03b_threshold_as_significance():
    text = DOC.read_text()
    assert "No numerical threshold is used to define the upper or lower panel." in text
    assert "SQ-03B post-hoc tolerance table remains descriptive only." in text
