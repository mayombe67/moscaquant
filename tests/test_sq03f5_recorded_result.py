import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "artifacts/sidequests/sq03f5-turf-war-result-v1.json"
PROVENANCE = ROOT / "artifacts/sidequests/sq03f5-turf-war-provenance-v1.json"
DOC = ROOT / "docs/experiments/sq03f5-turf-war-results.md"

def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def test_sq03f5_authoritative_result_is_recorded():
    row = json.loads(RESULT.read_text())
    assert row["schema"] == "moscaquant.sq03f5_result/v1"
    assert row["experiment_id"] == "SQ-03F.5"
    assert row["status"] == "COMPLETE"
    assert row["classification"] == "GREATER_THAN_NULL_DOWNSTREAM_CONVERGENCE"
    assert len(row["eligible_sources"]) == 42
    assert row["candidate_source_count"] == 4455
    assert row["candidate_edge_count"] == 114825
    assert row["conservative_graph_edge_count"] == 639435
    assert row["randomizations"] == 10000
    assert row["base_seed"] == 314159

def test_sq03f5_frozen_numeric_result():
    row = json.loads(RESULT.read_text())
    assert row["observed_mean_pairwise_jaccard"] == 0.5621987198049191
    assert row["null_summary"]["median"] == 0.40521662251703366
    assert row["empirical_upper_tail_p"] == 9.999000099990002e-05
    assert row["empirical_lower_tail_p"] == 1.0
    assert row["effect_ratio_vs_null_median"] == 1.3874029064078843

def test_sq03f5_provenance_binds_original_result():
    prov = json.loads(PROVENANCE.read_text())
    assert prov["schema"] == "moscaquant.sq03f5_provenance/v1"
    assert prov["result_sha256"] == sha256(RESULT)
    assert prov["classification"] == "GREATER_THAN_NULL_DOWNSTREAM_CONVERGENCE"
    assert "not regenerated" in prov["note"]

def test_sq03f5_results_doc_preserves_claim_boundary():
    text = DOC.read_text()
    assert "greater-than-null downstream convergence" in text
    assert "does **not** establish biological gang-like" in text
    assert "financial usefulness" in text
    assert "was produced once and was not regenerated" in text
