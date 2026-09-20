import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "experiments" / "sq04_global_modulation_v1.json"
PROTOCOL = ROOT / "docs" / "experiments" / "sq04-global-modulation-protocol.md"


def test_sq04_protocol_identity_and_clock():
    data = json.loads(CONFIG.read_text())

    assert data["sidequest_id"] == "SQ-04"
    assert data["name"] == "GLOBAL MODULATION SENSITIVITY"
    assert data["status"] == "FROZEN_BEFORE_EXECUTION"
    assert data["clock_rule"]["dt_ms"] == 1.0
    assert data["clock_rule"]["dt_ms_frozen"] is True
    assert data["precommitted_interpretation"]["no_retuning"] is True


def test_sq04_frozen_matrix():
    data = json.loads(CONFIG.read_text())
    variants = {item["id"]: item for item in data["variants"]}

    assert set(variants) == {
        "REFERENCE",
        "THRESHOLD_LOW_10",
        "THRESHOLD_HIGH_10",
        "TAU_FAST_25",
        "TAU_SLOW_25",
    }

    assert variants["REFERENCE"]["threshold"] == 1.0
    assert variants["REFERENCE"]["tau_ms"] == 20.0

    assert variants["THRESHOLD_LOW_10"]["threshold"] == 0.9
    assert variants["THRESHOLD_LOW_10"]["tau_ms"] == 20.0

    assert variants["THRESHOLD_HIGH_10"]["threshold"] == 1.1
    assert variants["THRESHOLD_HIGH_10"]["tau_ms"] == 20.0

    assert variants["TAU_FAST_25"]["threshold"] == 1.0
    assert variants["TAU_FAST_25"]["tau_ms"] == 15.0

    assert variants["TAU_SLOW_25"]["threshold"] == 1.0
    assert variants["TAU_SLOW_25"]["tau_ms"] == 25.0


def test_sq04_biology_and_authority_boundaries():
    data = json.loads(CONFIG.read_text())
    exclusions = " ".join(data["explicit_exclusions"])
    text = PROTOCOL.read_text()

    assert "No biological neuromodulator identity is assigned." in exclusions
    assert "No plasticity or learning claim." in exclusions
    assert "No broker, WARDEN-01, or Sugar Cube test." in exclusions

    assert '"Global modulation" is a computational label only.' in text
    assert "does not claim to model dopamine" in text
    assert "SQ-03 is therefore deferred" in text
    assert "Protocol/config/tests are committed before the first result-bearing execution." in text
