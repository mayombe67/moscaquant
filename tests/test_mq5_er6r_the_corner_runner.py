from __future__ import annotations

import json

import numpy as np
import pytest
from scipy import sparse

from brain import mq5_er6r_the_corner as corner
from brain import mq5_er6r_the_corner_runner as runner


def test_execution_refuses_before_any_neural_input_or_output(monkeypatch, tmp_path):
    monkeypatch.setattr(runner, "QUALIFICATION", tmp_path / "missing-qualification.json")
    monkeypatch.setattr(runner, "AUTHORIZATION", tmp_path / "missing-authorization.json")
    monkeypatch.setattr(runner, "OUTPUT", tmp_path / "result.json")
    monkeypatch.setattr(runner, "build_stimuli", lambda _: pytest.fail("stimuli loaded"))
    monkeypatch.setattr(runner, "load_c13", lambda: pytest.fail("connectome loaded"))
    with pytest.raises(corner.CornerRefusal, match="qualification or authorization missing"):
        runner.execute()
    assert not runner.OUTPUT.exists()


def test_run_arm_uses_native_p0_and_symmetric_shared_modifier(monkeypatch):
    observations = []

    class FakeRuntime:
        def __init__(self, *, connectome, retinal_indices, relay_artifact,
                     graded_artifact, config, activity_modifier):
            self.activity_modifier = activity_modifier
            self.voltage = np.zeros(4000, dtype=np.float32)
            self.spikes = np.zeros(4000, dtype=np.float32)
            self.spikes[[1952, 3056]] = 1.0
            observations.append(self)

        def step(self, stimulus, *, generation=0):
            native = self.spikes.copy()
            modified = (native if self.activity_modifier is None else
                        self.activity_modifier(native, generation))
            observations.append((generation, native, modified))
            self.voltage[55] = generation + 1.0

    monkeypatch.setattr(runner, "PhysiologyConstrainedVisualTransductionRuntime", FakeRuntime)
    connectome = sparse.csr_matrix((4000, 4000), dtype=np.float32)
    stimuli = [np.zeros(4000, dtype=np.float32) for _ in range(2)]
    for arm, target in (("P0", None), ("P1952", 1952), ("PCONTROL", 3056)):
        observations.clear()
        result = runner.run_arm(arm, connectome, np.array([], dtype=np.int32), (55,), stimuli)
        for frame, native, modified in observations[1:]:
            assert np.all(native[[1952, 3056]] == 1.0)
            changed = np.flatnonzero(native != modified).tolist()
            assert changed == ([] if target is None else [target])
        assert len(result["native_target_activity_before_silencing"]) == (0 if target is None else 2)
        assert result["onsets"] == {55: 0}


def test_analysis_keeps_retained_as_diagnostics():
    targets = corner.load_frozen_stage()["all_targets"]
    base = dict.fromkeys(targets, 10)
    candidate = base.copy()
    candidate[55] = 11
    candidate[51] = None
    control = base.copy()
    control[51] = None
    arms = {
        "P0": {"onsets": base, "positive_fingerprint": [1.0, 0.0]},
        "P1952": {"onsets": candidate, "positive_fingerprint": [0.0, 1.0]},
        "PCONTROL": {"onsets": control, "positive_fingerprint": [1.0, 0.0]},
    }
    result = runner.analyze(arms)
    assert result["P1952"]["affected_dependency_count"] == 1
    assert result["P1952"]["classification"] == "WARRANT_NECESSITY_PARTIAL"
    assert result["PCONTROL"]["affected_dependency_count"] == 0
    assert result["PCONTROL"]["retained_dependency_count"] == 1
    assert result["PCONTROL"]["classification"] == "WARRANT_NECESSITY_NOT_OBSERVED"


def test_authorized_write_is_atomic_and_no_overwrite(monkeypatch, tmp_path):
    stage = corner.load_frozen_stage()
    targets = tuple(stage["all_targets"])
    frozen = {int(k): v for k, v in __import__("tomllib").loads(
        corner.WARRANT_CONFIG.read_text(encoding="utf-8")
    )["c13_onsets"].items()}
    fixture_auth = tmp_path / "fixture-authorization.json"
    fixture_qual = tmp_path / "fixture-qualification.json"
    fixture_auth.write_text("{}", encoding="utf-8")
    fixture_qual.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(runner, "AUTHORIZATION", fixture_auth)
    monkeypatch.setattr(runner, "QUALIFICATION", fixture_qual)
    monkeypatch.setattr(runner, "OUTPUT", tmp_path / "result.json")
    monkeypatch.setattr(runner, "execution_gate", lambda: {
        "implementation_git_sha": "a" * 40, "input_sha256": {"fixture": "b" * 64}
    })
    monkeypatch.setattr(runner, "build_stimuli", lambda _: [np.array([0.0])])
    monkeypatch.setattr(runner, "load_c13", lambda: (
        None, sparse.eye(4000, format="csr"), np.array([], dtype=np.int32), targets
    ))
    monkeypatch.setattr(runner, "run_arm", lambda arm, *args: {
        "onsets": frozen.copy(), "positive_fingerprint": [1.0],
        "native_target_activity_before_silencing": [],
    })
    path = runner.execute()
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["stage"] == stage["stage_id"]
    assert payload["comparisons"]["P1952"]["classification"] == "WARRANT_NECESSITY_NOT_OBSERVED"
    before = path.read_bytes()
    with pytest.raises(corner.CornerRefusal, match="appeared during execution"):
        runner.execute()
    assert path.read_bytes() == before


def test_baseline_drift_refuses_before_intervention_arms(monkeypatch, tmp_path):
    stage = corner.load_frozen_stage()
    targets = tuple(stage["all_targets"])
    called = []
    monkeypatch.setattr(runner, "execution_gate", lambda: {})
    monkeypatch.setattr(runner, "build_stimuli", lambda _: [np.array([0.0])])
    monkeypatch.setattr(runner, "load_c13", lambda: (
        None, sparse.eye(4000, format="csr"), np.array([], dtype=np.int32), targets
    ))

    def fake_run(arm, *args):
        called.append(arm)
        return {"onsets": dict.fromkeys(targets, None)}

    monkeypatch.setattr(runner, "run_arm", fake_run)
    with pytest.raises(corner.CornerRefusal, match="P0 C13 onset vector drift"):
        runner.execute()
    assert called == ["P0"]
