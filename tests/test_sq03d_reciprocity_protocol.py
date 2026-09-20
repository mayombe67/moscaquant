import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "config" / "experiments" / "sq03d_reciprocity_v1.json"
DOC = ROOT / "docs" / "experiments" / "sq03d-reciprocity-protocol.md"


def load():
    return json.loads(CFG.read_text())


def test_identity_and_status():
    cfg = load()
    assert cfg["sidequest_id"] == "SQ-03D"
    assert cfg["title"] == "THE SAME KNIFE CUTS DIFFERENTLY"
    assert cfg["status"] == "FROZEN_BEFORE_ANALYSIS"


def test_sq03b_source_hash_is_frozen():
    cfg = load()
    assert cfg["parents"]["sq03b_ledger_sha256"] == (
        "7b2632de5792973534177b697efdd7c3af0b82a836d9d2b597812dbc0dd1f725"
    )


def test_pairing_requires_both_subjects():
    cfg = load()
    pairing = cfg["pairing"]
    assert pairing["key"] == ["input", "edge_id", "anchor"]
    assert pairing["subjects_required"] == ["MORTY", "LILITH"]
    assert pairing["unpaired_is_error"] is True
    assert pairing["drop_unpaired"] is False


def test_primary_metric_is_raw_context_residual():
    cfg = load()
    primary = cfg["primary_metric"]
    assert primary["name"] == "integrated_positive_voltage_context_residual"
    assert primary["formula"] == (
        "abs(delta_morty_integrated + delta_lilith_integrated)"
    )


def test_normalized_metric_does_not_need_epsilon():
    cfg = load()
    formula = cfg["definitions"]["normalized_asymmetry"]
    assert "both deltas are exactly zero" in formula
    assert "abs(delta_morty + delta_lilith)" in formula


def test_no_fake_population_statistics():
    cfg = load()
    stats = cfg["statistics"]
    assert stats["population_p_values"] is False
    assert stats["simulation_replicates_as_samples"] is False
    assert stats["formal_significance_threshold"] is False
    assert stats["descriptive_census_only"] is True


def test_candidate_ranking_frozen_before_analysis():
    cfg = load()
    ranking = cfg["ranking"]
    assert ranking["primary"] == (
        "integrated_positive_voltage_context_residual DESC"
    )
    assert ranking["no_candidate_execution_in_sq03d"] is True


def test_claim_boundary_is_model_level():
    cfg = load()
    boundary = cfg["claim_boundary"]
    assert "inside the frozen MoscaQuant matched central-brain model" in boundary
    assert "does not establish a biological sex mechanism" in boundary


def test_protocol_explicitly_preserves_nulls():
    text = DOC.read_text()
    assert "A null first-positive-frame result remains a valid null." in text
    assert "No p-value is generated from deterministic simulation rows." in text
