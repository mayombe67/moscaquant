import importlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "experiments" / "sq04_global_modulation_v1.json"
RUNNER = ROOT / "brain" / "sq04_global_modulation.py"


def test_sq04_runner_exists_and_imports():
    assert RUNNER.exists()
    module = importlib.import_module("brain.sq04_global_modulation")

    assert module.CONDITION == "A"
    assert module.FRAME_COUNT == 16
    assert module.DT_MS == 1.0
    assert module.RESET == 0.0


def test_sq04_runner_matches_frozen_matrix():
    data = json.loads(CONFIG.read_text())
    variants = {item["id"]: item for item in data["variants"]}

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


def test_sq04_runner_keeps_clock_fixed():
    module = importlib.import_module("brain.sq04_global_modulation")
    data = json.loads(CONFIG.read_text())

    assert module.DT_MS == data["clock_rule"]["dt_ms"]
    assert data["clock_rule"]["dt_ms_frozen"] is True


def test_sq04_determinism_keys_cover_required_measurements():
    module = importlib.import_module("brain.sq04_global_modulation")
    keys = set(module.DETERMINISM_KEYS)

    assert "neural_hash" in keys
    assert "relay_hash" in keys
    assert "wider_hash" in keys
    assert "relay_spike_count" in keys
    assert "wider_network_spike_count" in keys
    assert "first_relay_spike_time_ms_if_any" in keys
    assert "first_wider_spike_time_ms_if_any" in keys
    assert "final_voltage_hash" in keys
