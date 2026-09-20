import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
F3 = ROOT / "artifacts" / "sidequests" / "sq03f3-made-men-result-v1.json"
F4 = ROOT / "artifacts" / "sidequests" / "sq03f4-sit-down-result-v1.json"
F3_NOTE = ROOT / "docs" / "experiments" / "sq03f3-randomization-stream-clarification.md"
F4_DOC = ROOT / "docs" / "experiments" / "sq03f4-sit-down-results.md"


def test_f3_seed_streams_are_explicitly_recorded():
    row = json.loads(F3.read_text())["null_model"]
    assert row["seed_S"] == 314159
    assert row["seed_C"] == 314160
    text = F3_NOTE.read_text()
    assert "documentation-specificity gap" in text
    assert "base_seed + 1" in text


def test_f4_result_is_recorded_without_recomputing():
    row = json.loads(F4.read_text())
    assert row["sidequest_id"] == "SQ-03F.4"
    assert row["title"] == "THE SIT-DOWN"
    assert row["candidate_source_count"] == 4455
    assert row["made_source_k"] == 45
    assert row["S_C_made_source_overlap"]["count"] == 42


def test_f4_results_doc_preserves_claim_boundary():
    text = F4_DOC.read_text()
    assert "Made sources don't get more jobs. Their jobs are heavier." in text
    assert "does not establish biological neuron classes" in text
    assert "No p-value threshold" in text
