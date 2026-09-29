import json
from pathlib import Path

import numpy as np
import pytest

from brain import mq5_er6r_the_corner as corner


def test_all_arms_share_one_operator_and_p0_is_unmodified():
    stage = corner.load_frozen_stage()
    assert corner.arm_modifier("P0", population_size=4000) is None
    native = np.ones(4000, dtype=np.float32)
    for arm, target in (("P1952", 1952), ("PCONTROL", 3056)):
        modifier = corner.arm_modifier(arm, population_size=4000)
        for frame in (0, 191):
            result = modifier(native, frame)
            assert result[target] == 0.0
            assert np.count_nonzero(result != native) == 1
            assert native[target] == 1.0
        with pytest.raises(corner.CornerRefusal):
            modifier(native, 192)
    assert stage["neural_execution_enabled"] is False
    with pytest.raises(corner.CornerRefusal):
        corner.arm_modifier("PSECOND_CONTROL", population_size=4000)


def test_onset_endpoint_and_retained_specificity_boundary():
    targets = corner.load_frozen_stage()["all_targets"]
    baseline = dict.fromkeys(targets, 10)
    intervention = dict.fromkeys(targets, 10)
    intervention[55] = 11
    intervention[92] = None
    intervention[656] = 9  # earlier is not necessity
    intervention[51] = None  # retained remains diagnostic only
    deps = corner.dependency_by_onset(baseline, intervention)
    assert deps[55] and deps[92] and deps[51]
    assert not deps[656]
    assert corner.classify_affected(deps) == ("WARRANT_NECESSITY_PARTIAL", 2)

    intervention[55] = 10
    intervention[92] = 10
    assert corner.classify_affected(
        corner.dependency_by_onset(baseline, intervention)
    ) == ("WARRANT_NECESSITY_NOT_OBSERVED", 0)
    for target in (55, 92, 656, 126002, 137122):
        intervention[target] = None
    assert corner.classify_affected(
        corner.dependency_by_onset(baseline, intervention)
    ) == ("WARRANT_NECESSITY_COMPLETE", 5)


def test_semantic_control_identity_drift_refuses_without_neural_execution(monkeypatch, tmp_path):
    control = json.loads(corner.CONTROL.read_text(encoding="utf-8"))
    control["selected_control"]["node"] = 3057
    changed = tmp_path / "control.json"
    changed.write_text(json.dumps(control), encoding="utf-8")
    monkeypatch.setattr(corner, "CONTROL", changed)
    with pytest.raises(corner.CornerRefusal, match="artifact_sha256 drift"):
        corner.load_frozen_stage()
