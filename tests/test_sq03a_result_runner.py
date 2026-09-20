import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "config" / "experiments" / "sq03a_other_fly_v1.json"
EXECUTION = ROOT / "config" / "experiments" / "sq03a_result_execution_v1.json"
RUNNER = ROOT / "brain" / "sq03a_other_fly_run.py"


def load(path):
    return json.loads(path.read_text())


def test_result_config_is_frozen_and_authoritative():
    cfg = load(EXECUTION)
    assert cfg["status"] == "FROZEN_BEFORE_RESULT_EXECUTION"
    assert cfg["authoritative_result"] is True
    assert cfg["requires_clean_git_worktree"] is True
    assert cfg["requires_passing_smoke_artifact"] is True


def test_result_inputs_and_anchors_match_protocol_exactly():
    protocol = load(PROTOCOL)
    cfg = load(EXECUTION)
    expected_inputs = protocol["frozen_input_panel_rule"]["expected_labels_from_qualification"]
    expected_anchors = [x["label"] for x in protocol["frozen_output_anchors"]]
    assert cfg["input_labels"] == expected_inputs
    assert cfg["anchor_labels"] == expected_anchors


def test_result_uses_same_smoke_stimulus_without_tuning():
    cfg = load(EXECUTION)
    assert cfg["frames"] == 64
    assert cfg["stimulus"]["frame"] == 0
    assert cfg["stimulus"]["amplitude"] == 0.5
    assert cfg["stimulus"]["duration_frames"] == 1
    assert "without tuning" in cfg["stimulus"]["rationale"]


def test_result_runtime_is_identical_across_subjects():
    cfg = load(EXECUTION)
    assert cfg["subjects"] == {"MORTY": "weight_m", "LILITH": "weight_f"}
    assert cfg["runtime"] == {
        "implementation": "brain.hybrid_runtime.HybridRuntime",
        "dt_ms": 1.0,
        "tau_ms": 20.0,
        "threshold": 1.0,
        "reset_voltage": 0.0,
    }


def test_result_graph_rule_matches_frozen_protocol():
    cfg = load(EXECUTION)
    assert cfg["graph"]["verdict_corr"] == "isomorphic"
    assert cfg["graph"]["require_weight_m_positive"] is True
    assert cfg["graph"]["require_weight_f_positive"] is True
    assert cfg["graph"]["normalization"] == "common_global_max_abs_row_sum"


def test_runner_refuses_dirty_worktree_and_overwrite():
    text = RUNNER.read_text()
    assert "Refusing authoritative SQ-03A execution with a dirty git worktree" in text
    assert "Refusing to overwrite existing authoritative result artifact" in text


def test_claim_boundary_blocks_overreach():
    cfg = load(EXECUTION)
    text = cfg["claim_boundary"]
    for phrase in (
        "sex superiority",
        "intelligence",
        "general behavior",
        "biological mechanism",
        "market skill",
        "profitability",
        "financial usefulness",
    ):
        assert phrase in text
