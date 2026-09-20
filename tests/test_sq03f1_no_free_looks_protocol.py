import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "config" / "experiments" / "sq03f1_no_free_looks_v1.json"


def load():
    return json.loads(CFG.read_text())


def test_identity_and_status():
    cfg = load()
    assert cfg["sidequest_id"] == "SQ-03F.1"
    assert cfg["title"] == "NO FREE LOOKS"
    assert cfg["status"] == "FROZEN_BEFORE_ANALYSIS"


def test_reuses_exact_sq03f_hotspots():
    h = load()["hotspots"]
    assert h["reuse_sq03f_exact_hotspot_sets"] is True
    assert h["no_reranking"] is True


def test_matching_is_exact_three_way():
    m = load()["matching"]
    assert m["exact_match"] == [
        "context_count",
        "total_weight_decile",
        "abs_weight_difference_decile",
    ]
    assert m["without_replacement"] is True


def test_matching_cannot_relax_context_count():
    rule = load()["matching"]["failure_rule"]
    assert "do not relax context_count" in rule


def test_context_count_is_not_outcome():
    assert "matching variable only" in load()["features"]["context_count"]


def test_no_pvalues_or_threshold():
    c = load()["comparisons"]
    assert c["no_p_values"] is True
    assert c["no_significance_threshold"] is True
