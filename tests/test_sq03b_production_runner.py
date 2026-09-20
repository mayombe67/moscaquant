import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "config" / "experiments" / "sq03b_execution_v1.json"
RUNNER = ROOT / "brain" / "sq03b_run.py"


def load():
    return json.loads(CFG.read_text())


def test_batch_size_is_frozen_at_validated_value():
    cfg = load()
    assert cfg["status"] == "FROZEN_BEFORE_COUNTERFACTUAL_EXECUTION"
    assert cfg["batch_size"] == 32


def test_runtime_matches_sq03a():
    cfg = load()
    assert cfg["frames"] == 64
    assert cfg["stimulus"] == {"frame": 0, "amplitude": 0.5}
    assert cfg["runtime"] == {
        "dt_ms": 1.0,
        "tau_ms": 20.0,
        "threshold": 1.0,
        "reset_voltage": 0.0,
    }


def test_validation_contract_is_frozen():
    cfg = load()
    assert cfg["parity"]["scalar_vs_batched_rtol"] == 1e-6
    assert cfg["parity"]["scalar_vs_batched_atol"] == 1e-7
    assert cfg["parity"]["aa_replay_exact"] is True


def test_runner_is_resumable_and_hash_guarded():
    text = RUNNER.read_text()
    assert "--resume" in text
    assert "candidate_artifact_sha256" in text
    assert "execution_config_sha256" in text
    assert "Checkpoint identity mismatch" in text


def test_runner_requires_baseline_replay_and_exact_batch_aa():
    text = RUNNER.read_text()
    assert "SQ-03A baseline replay: PASS" in text
    assert "A/A batch replay failed" in text


def test_runner_fsyncs_checkpoint_ledger():
    text = RUNNER.read_text()
    assert "os.fsync" in text
    assert "results.ndjson" in json.dumps(load()["checkpoint"])


def test_claim_boundary_blocks_overreach():
    text = load()["claim_boundary"]
    for phrase in (
        "biological mechanism",
        "general sex differences",
        "behavior",
        "intelligence",
        "market skill",
        "profitability",
        "financial usefulness",
    ):
        assert phrase in text
