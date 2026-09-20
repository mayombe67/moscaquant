from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "brain" / "sq03c_scalar_verify.py"


def test_runner_uses_scalar_hybrid_runtime_path():
    text = RUNNER.read_text()
    assert "run_single(" in text
    assert "sq03b_batched_engine" not in text


def test_runner_requires_exact_aa():
    text = RUNNER.read_text()
    assert "scalar A/A mismatch" in text
    assert "np.array_equal" in text


def test_runner_replays_sq03a_baselines():
    text = RUNNER.read_text()
    assert "SQ-03A baseline replay mismatch" in text


def test_runner_compares_against_frozen_tolerance():
    text = RUNNER.read_text()
    assert "np.isclose" in text
    assert "batched_vs_scalar_rtol" in text
    assert "batched_vs_scalar_atol" in text
