import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "artifacts" / "sidequests" / "sq02-ghost-market-v1.json"
RESULTS = ROOT / "docs" / "experiments" / "sq02-ghost-market-results.md"

SOURCE_COMMIT = "91d0621b44cc8d8f355cfd3e152ca7a7e9f169b9"
CONFIG_SHA256 = "3368df87698a712cd03623e081b02e98ec985c28ececf46ac52438b8115a7045"

EXPECTED_COUNTS = {
    "SEQUENCE_BASELINE": (40, 0),
    "SEQUENCE_DUPLICATE_FRAME": (36, 0),
    "SEQUENCE_DROP_FRAME": (36, 0),
    "SEQUENCE_REVERSED": (41, 0),
    "SEQUENCE_FROZEN": (1, 0),
    "EXTREME_X10": (40, 0),
    "EXTREME_X100": (40, 0),
    "ZERO_VECTOR": (40, 0),
}


def rows_by_variant(data):
    return {row["variant"]["id"]: row for row in data["rows"]}


def test_sq02_artifact_identity_and_determinism():
    data = json.loads(ARTIFACT.read_text())
    assert data["sidequest_id"] == "SQ-02"
    assert data["source_commit"] == SOURCE_COMMIT
    assert data["config_sha256"] == CONFIG_SHA256
    assert all(row["deterministic_AA_replay"] is True for row in data["rows"])


def test_sq02_malformed_feature_cases_rejected_before_neural_execution():
    data = json.loads(ARTIFACT.read_text())
    rows = rows_by_variant(data)

    for variant in (
        "FEATURE_NAN",
        "FEATURE_POS_INF",
        "FEATURE_NEG_INF",
        "FEATURE_SHORT_ROW",
        "FEATURE_LONG_ROW",
    ):
        result = rows[variant]["result"]
        assert result["accepted_or_rejected"] == "REJECTED"
        assert result["neural_execution_reached"] is False


def test_sq02_recorded_spike_counts():
    data = json.loads(ARTIFACT.read_text())
    rows = rows_by_variant(data)

    for variant, (relay, wider) in EXPECTED_COUNTS.items():
        result = rows[variant]["result"]
        assert result["relay_spike_count"] == relay
        assert result["wider_network_spike_count"] == wider


def test_sq02_results_preserve_claim_boundary_and_interpretation():
    data = json.loads(ARTIFACT.read_text())
    text = RESULTS.read_text()

    assert data["claim_boundary"] in text
    assert "Malformed feature-interface rejection:** SUPPORTED" in text
    assert "Deterministic temporal-input sensitivity:** SUPPORTED" in text
    assert "Finite-extreme spike-count sensitivity:** NOT OBSERVED" in text
    assert "Wider-network propagation under SQ-02:** NOT OBSERVED" in text
    assert "No retuning was performed after observing these results." in text
