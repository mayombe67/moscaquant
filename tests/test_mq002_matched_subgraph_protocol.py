import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "experiments" / "mq002_matched_subgraph_v1.json"
PROTOCOL = ROOT / "docs" / "experiments" / "mq002-1-matched-subgraph-protocol.md"
IDENTITY_RESULTS = ROOT / "docs" / "experiments" / "mq002-0-identity-check-results.md"


def test_mq002_1_is_non_result_bearing():
    data = json.loads(CONFIG.read_text())
    assert data["experiment_id"] == "MQ-002.1"
    assert data["status"] == "FROZEN_BEFORE_ACQUISITION"
    assert data["result_bearing_neural_experiment"] is False


def test_identity_overlap_is_locked():
    data = json.loads(CONFIG.read_text())
    obs = data["identity_check_observations"]

    assert obs["mapping_entry_count"] == 281656
    assert obs["unique_cross_matched_labels"] == 8586
    assert obs["retinal_overlap"] == {"matched": 3241, "total": 3241}
    assert obs["relay_overlap"] == {"matched": 2430, "total": 2430}
    assert obs["descending_overlap"] == {"matched": 1310, "total": 1314}


def test_construction_boundaries_are_explicit():
    data = json.loads(CONFIG.read_text())
    scope = data["construction_scope"]

    assert scope["initial_family"] == "isomorphic_only"
    assert scope["central_brain_only"] is True
    assert scope["vnc_excluded"] is True
    assert scope["no_inferred_edges"] is True
    assert scope["no_shuffled_fill"] is True

    text = PROTOCOL.read_text()
    assert "No neural simulation is executed." in text
    assert "no VNC equivalence is implied" in text


def test_identity_results_recorded():
    text = IDENTITY_RESULTS.read_text()
    assert "3241 | 3241 | 100.0%" in text
    assert "2430 | 2430 | 100.0%" in text
    assert "1310 | 1314 | 99.7%" in text
    assert "MQ-002 remains provisional." in text
