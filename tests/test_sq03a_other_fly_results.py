import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "artifacts" / "sidequests" / "sq03a-other-fly-result-v1.json"
RESULTS = ROOT / "docs" / "experiments" / "sq03a-other-fly-results.md"


def load():
    return json.loads(ARTIFACT.read_text())


def test_sq03a_result_artifact_identity():
    data = load()
    assert data["schema"] == "moscaquant.sq03a_result/v1"
    assert data["classification"] == "AUTHORITATIVE_RESULT_BEARING_EXECUTION"
    assert len(data["input_labels"]) == 12
    assert set(data["anchor_labels"]) == {"DNc02", "DNp27", "DNp30"}


def test_sq03a_result_controls_passed():
    c = load()["controls"]
    assert c["morty_all_aa_exact"] is True
    assert c["lilith_all_aa_exact"] is True
    assert c["identical_runtime_parameters"] is True
    assert c["identical_stimulus_parameters"] is True
    assert c["identical_sparsity_pattern"] is True


def test_sq03a_rank_change_record_matches_artifact():
    data = load()
    changed = {
        label
        for label in data["input_labels"]
        if not data["comparisons"][label]["peak_rank_order_identical"]
    }
    assert changed == {"TmY14", "LPLC2", "AVLP234", "AVLP435"}


def test_sq03a_results_doc_records_source_and_artifact_hash():
    data = load()
    text = RESULTS.read_text()
    digest = hashlib.sha256(ARTIFACT.read_bytes()).hexdigest()
    assert data["source_commit"] in text
    assert digest in text


def test_sq03a_results_doc_preserves_claim_boundary():
    data = load()
    text = RESULTS.read_text()
    assert data["claim_boundary"] in text
    assert "model-level comparative results" in text
    assert "do not establish a general biological or behavioral sex difference" in text
