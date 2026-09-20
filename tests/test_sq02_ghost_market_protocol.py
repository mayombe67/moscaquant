import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "experiments" / "sq02_ghost_market_v1.json"
PROTOCOL = ROOT / "docs" / "experiments" / "sq02-ghost-market-protocol.md"

EXPECTED_STAGE_A = {
    "BASELINE_VALID",
    "FEATURE_NAN",
    "FEATURE_POS_INF",
    "FEATURE_NEG_INF",
    "FEATURE_SHORT_ROW",
    "FEATURE_LONG_ROW",
}

EXPECTED_STAGE_B = {
    "SEQUENCE_BASELINE",
    "SEQUENCE_DUPLICATE_FRAME",
    "SEQUENCE_DROP_FRAME",
    "SEQUENCE_REVERSED",
    "SEQUENCE_FROZEN",
}

EXPECTED_STAGE_C = {
    "EXTREME_X10",
    "EXTREME_X100",
    "ZERO_VECTOR",
}


def test_sq02_protocol_is_frozen_and_scoped():
    data = json.loads(CONFIG.read_text())

    assert data["sidequest_id"] == "SQ-02"
    assert data["name"] == "GHOST MARKET"
    assert data["status"] == "FROZEN_BEFORE_EXECUTION"
    assert data["clock_rule"]["dt_ms_may_not_change"] is True
    assert data["precommitted_interpretation"]["no_retuning"] is True

    stages = {stage["id"]: stage for stage in data["stages"]}
    assert set(stages) == {"A", "B", "C"}
    assert {v["id"] for v in stages["A"]["variants"]} == EXPECTED_STAGE_A
    assert {v["id"] for v in stages["B"]["variants"]} == EXPECTED_STAGE_B
    assert {v["id"] for v in stages["C"]["variants"]} == EXPECTED_STAGE_C


def test_sq02_measurement_and_authority_boundaries():
    data = json.loads(CONFIG.read_text())
    measurements = set(data["measurements"])

    assert "accepted_or_rejected" in measurements
    assert "deterministic_AA_replay" in measurements
    assert "relay_spike_count" in measurements
    assert "wider_network_spike_count" in measurements

    exclusions = " ".join(data["explicit_exclusions"])
    assert "WARDEN-01" in exclusions
    assert "Sugar Cube" in exclusions
    assert "D6" in exclusions
    assert "profitability" in exclusions


def test_sq02_protocol_records_clock_and_claim_boundaries():
    text = PROTOCOL.read_text()

    assert "wall-clock execution rate" in text
    assert "`dt_ms`" in text
    assert "No effect is a valid result." in text
    assert "Raw-feed timestamp validation is a separate future interface test" in text
    assert "does not establish biological robustness" in text
    assert "Protocol/config/tests are committed before the first result-bearing execution." in text
