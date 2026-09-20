from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "brain" / "sq03d1_scalar_verify.py"


def test_runner_uses_scalar_runtime_path():
    text = RUNNER.read_text()
    assert "run_single(" in text
    assert "sq03b_batched_engine" not in text


def test_runner_requires_exact_aa():
    text = RUNNER.read_text()
    assert "SQ-03D.1 A/A mismatch" in text
    assert "np.array_equal" in text


def test_runner_requires_baseline_replay():
    text = RUNNER.read_text()
    assert "SQ-03A baseline replay mismatch" in text


def test_runner_reconstructs_pair_metrics():
    text = RUNNER.read_text()
    assert "reconstructed_integrated = pair_metrics" in text
    assert "reconstructed_peak = pair_metrics" in text


def test_runner_checks_both_subjects():
    text = RUNNER.read_text()
    assert 'for subject in ("MORTY", "LILITH")' in text


def test_runner_reuses_frozen_tolerance():
    text = RUNNER.read_text()
    assert 'cfg["verification"]["batched_scalar_rtol"]' in text
    assert 'cfg["verification"]["batched_scalar_atol"]' in text
