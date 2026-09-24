from __future__ import annotations

import json
import tomllib
from pathlib import Path

import numpy as np

import brain.sq06_silent_cartographer_runner as r


ROOT = Path(__file__).resolve().parents[2]
CFG = ROOT / "config/controls/sq06-silent-cartographer-runner-v1.toml"
SCHEMA = ROOT / "config/controls/sq06-silent-cartographer-result-schema-v1.json"


def fake_episode(value: float):
    return {
        "positive_voltage": np.full((192, 1191), value, dtype=np.float32),
        "spikes": np.zeros((192, 1191), dtype=np.uint8),
        "channel_mean_positive_voltage": np.full((3, 192), value, dtype=np.float64),
        "channel_positive_fraction": np.zeros((3, 192), dtype=np.float64),
        "channel_spike_count": np.zeros((3, 192), dtype=np.int32),
        "channel_spike_rate": np.zeros((3, 192), dtype=np.float64),
    }


def test_episode_plan_is_exactly_28_and_frozen_order():
    plan = r.episode_plan()
    assert len(plan) == 28
    assert plan[0] == {"arm": "INTACT", "layout": "LR", "replicate": 1}
    assert plan[1] == {"arm": "INTACT", "layout": "LR", "replicate": 2}
    assert plan[-1] == {"arm": "RL_GROUP_SHAM", "layout": "RL", "replicate": 2}


def test_runner_config_does_not_authorize_execution():
    with CFG.open("rb") as f:
        cfg = tomllib.load(f)
    assert cfg["execution"]["result_execution_authorized"] is False
    assert cfg["execution"]["neural_execution_authorized"] is False
    assert cfg["execution"]["topology_randomization_required"] is False
    assert cfg["episode_plan"]["expected_total_episode_count"] == 28


def test_result_schema_is_28_episode_contract():
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    assert schema["sidecar"]["episode_count_expected"] == 28
    assert schema["sidecar"]["arrays"]["primary_positive_voltage"]["shape"] == [28, 192, 1191]
    assert schema["sidecar"]["arrays"]["primary_spikes"]["shape"] == [28, 192, 1191]
    assert schema["primary"]["minimum_meaningful_effect_floor"] == "NOT_DEFINED"
    assert schema["manifest"]["single_overall_winner_forbidden"] is True


def test_primary_classifier_exact_partition_passes_constructed_case():
    first = {arm: {} for arm in r.ARMS}
    for layout in r.LAYOUTS:
        first["INTACT"][layout] = fake_episode(0.0)
        first["FULL13_SHAM"][layout] = fake_episode(0.0)
        first["LR_GROUP_SHAM"][layout] = fake_episode(0.0)
        first["RL_GROUP_SHAM"][layout] = fake_episode(0.0)

    first["FULL13_TARGETED"]["LR"] = fake_episode(1.0)
    first["FULL13_TARGETED"]["RL"] = fake_episode(2.0)

    first["LR_GROUP_TARGETED"]["LR"] = fake_episode(1.0)
    first["RL_GROUP_TARGETED"]["LR"] = fake_episode(0.0)

    first["RL_GROUP_TARGETED"]["RL"] = fake_episode(2.0)
    first["LR_GROUP_TARGETED"]["RL"] = fake_episode(0.0)

    report = r.classify_primary(first)
    assert report["all_primary_conditions_satisfied"] is True
    assert report["single_overall_winner"] is None
    assert all(x["pass"] for x in report["conditions"].values())


def test_primary_classifier_reports_component_failure_without_rewriting_threshold():
    first = {arm: {} for arm in r.ARMS}
    for layout in r.LAYOUTS:
        first["INTACT"][layout] = fake_episode(0.0)
        first["FULL13_SHAM"][layout] = fake_episode(0.0)
        first["LR_GROUP_SHAM"][layout] = fake_episode(0.0)
        first["RL_GROUP_SHAM"][layout] = fake_episode(0.0)

    first["FULL13_TARGETED"]["LR"] = fake_episode(1.0)
    first["FULL13_TARGETED"]["RL"] = fake_episode(2.0)
    first["LR_GROUP_TARGETED"]["LR"] = fake_episode(0.9)
    first["RL_GROUP_TARGETED"]["LR"] = fake_episode(0.0)
    first["RL_GROUP_TARGETED"]["RL"] = fake_episode(2.0)
    first["LR_GROUP_TARGETED"]["RL"] = fake_episode(0.0)

    report = r.classify_primary(first)
    assert report["all_primary_conditions_satisfied"] is False
    assert report["conditions"]["lr_recapitulation"]["pass"] is False
    assert report["minimum_meaningful_effect_floor"] == "NOT_DEFINED"


def test_exact_primary_reproduction_uses_preregistered_tolerances():
    a = fake_episode(0.0)
    b = fake_episode(0.0)
    assert r.exact_primary_reproduction(a, b)["exact_reproduction"] is True

    b["positive_voltage"][0, 0] = np.float32(1e-5)
    assert r.exact_primary_reproduction(a, b)["exact_reproduction"] is False


def test_runner_is_fail_closed_behind_separate_authorization():
    source = (ROOT / "brain/sq06_silent_cartographer_runner.py").read_text(encoding="utf-8")
    required = [
        "--preflight-only",
        "--run-frozen",
        "verify_execution_authorization",
        "result_execution_enabled",
        "implementation_commit",
        "merge-base",
        "--is-ancestor",
        "clean Git working tree",
    ]
    for token in required:
        assert token in source
    assert "build_betrayal_ii" not in source



def test_sq06_preflight_binds_transitive_sq05_runtime_dependencies():
    source = (
        ROOT / "brain/sq06_silent_cartographer_runner.py"
    ).read_text(encoding="utf-8")
    assert "verify_sq05_frozen_dependencies" in source
    assert '"sq05_runtime_dependencies": sq05_runtime' in source


def test_full13_provenance_is_normalized_to_sq06_arm_names(monkeypatch):
    from scipy import sparse

    baseline = sparse.csr_matrix((2, 2), dtype=np.float64)

    monkeypatch.setattr(
        r,
        "build_betrayal_i",
        lambda b: (b, {"arm": "BETRAYAL_I_LESIONED", "legacy": True}),
    )
    monkeypatch.setattr(
        r,
        "build_sham",
        lambda b: (b, {"arm": "BETRAYAL_I_SHAM", "legacy": True}),
    )

    _, targeted = r.build_arm_connectome(baseline, "FULL13_TARGETED")
    _, sham = r.build_arm_connectome(baseline, "FULL13_SHAM")

    assert targeted["arm"] == "FULL13_TARGETED"
    assert sham["arm"] == "FULL13_SHAM"
    assert targeted["legacy"] is True
    assert sham["legacy"] is True


def test_direct_neural_runtime_sources_are_frozen_in_config_and_preflight():
    with CFG.open("rb") as handle:
        cfg = tomllib.load(handle)

    frozen = cfg["frozen_inputs"]
    assert frozen["physiology_constrained_visual_transduction_sha256"] == (
        "bf754a29155ade789349fbdfc3c579f1b2c8dbea3c63804f2cf3d858d0a2f605"
    )
    assert frozen["visual_transduction_sha256"] == (
        "015cc699f49e16bb59f6e7e5f04f92cca7bfc1a3c7057e73fe54398c755831f6"
    )

    deps = r.verify_frozen_dependencies()["dependencies"]
    assert deps["physiology_constrained_visual_transduction"] == (
        "bf754a29155ade789349fbdfc3c579f1b2c8dbea3c63804f2cf3d858d0a2f605"
    )
    assert deps["visual_transduction"] == (
        "015cc699f49e16bb59f6e7e5f04f92cca7bfc1a3c7057e73fe54398c755831f6"
    )
