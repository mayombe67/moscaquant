import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "artifacts/sidequests/sq03f6-the-commission-result-v1.json"
PROVENANCE = ROOT / "artifacts/sidequests/sq03f6-the-commission-provenance-v1.json"
DOC = ROOT / "docs/experiments/sq03f6-the-commission-results.md"

def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def test_sq03f6_authoritative_result_is_recorded():
    row = json.loads(RESULT.read_text())
    assert row["schema"] == "moscaquant.sq03f6_result/v1"
    assert row["experiment_id"] == "SQ-03F.6"
    assert row["status"] == "COMPLETE"
    assert row["classification"] == "GREATER_THAN_NULL_TARGET_CONCENTRATION"
    assert row["eligible_source_count"] == 42
    assert row["candidate_source_count"] == 4455
    assert row["candidate_edge_count"] == 114825
    assert row["conservative_graph_edge_count"] == 639435
    assert row["randomizations"] == 10000
    assert row["base_seed"] == 314159

def test_sq03f6_frozen_numeric_result():
    row = json.loads(RESULT.read_text())
    assert row["observed_participation_mass_hhi"] == 0.0002087914357059647
    assert row["null_summary"]["median"] == 0.00016403723846293884
    assert row["empirical_upper_tail_p"] == 9.999000099990002e-05
    assert row["empirical_lower_tail_p"] == 1.0
    assert row["effect_ratio_vs_null_median"] == 1.272829496901932

def test_sq03f6_provenance_binds_original_result():
    prov = json.loads(PROVENANCE.read_text())
    assert prov["schema"] == "moscaquant.sq03f6_provenance/v1"
    assert prov["result_sha256"] == sha256(RESULT)
    assert prov["classification"] == "GREATER_THAN_NULL_TARGET_CONCENTRATION"
    assert prov["randomizations"] == 10000
    assert prov["base_seed"] == 314159
    assert "not regenerated" in prov["note"]

def test_sq03f6_results_doc_preserves_claim_boundary():
    text = DOC.read_text()
    assert "greater-than-null target concentration" in text
    assert "does **not** establish literal biological command hierarchy" in text
    assert "financial usefulness" in text
    assert "was produced once and was not regenerated" in text
