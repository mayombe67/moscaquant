from __future__ import annotations

import json
import tomllib
from pathlib import Path

import numpy as np

import brain.sq05_two_betrayals_runner as r


ROOT = Path(__file__).resolve().parents[2]
CFG = ROOT / "config/controls/sq05-two-betrayals-runner-v1.toml"
SCHEMA = ROOT / "config/controls/sq05-two-betrayals-result-schema-v1.json"


def load_cfg():
    with CFG.open("rb") as f:
        return tomllib.load(f)


def load_schema():
    return json.loads(SCHEMA.read_text(encoding="utf-8"))


def fake_episode(value: float):
    primary = np.full((192, 1191), value, dtype=np.float32)
    channel = np.full((3, 192), value, dtype=np.float64)
    return {
        "positive_voltage": primary,
        "spikes": np.zeros((192, 1191), dtype=np.uint8),
        "channel_mean_positive_voltage": channel,
        "channel_positive_fraction": np.zeros((3, 192), dtype=np.float64),
        "channel_spike_count": np.zeros((3, 192), dtype=np.int32),
        "channel_spike_rate": np.zeros((3, 192), dtype=np.float64),
    }


def test_capacity_decision_is_local_but_not_authorized():
    cfg = load_cfg()
    assert cfg["execution"]["mode"] == "local"
    assert cfg["execution"]["capacity_decision"] == (
        "HABITAT_LOCAL_CAPACITY_SUPPORTED"
    )
    assert cfg["execution"]["result_execution_authorized"] is False
    assert cfg["capacity_evidence"]["rasputin_required"] is False


def test_episode_plan_is_exactly_52():
    cfg = load_cfg()
    plan = cfg["episode_plan"]
    assert plan["deterministic_episode_count"] == 12
    assert plan["randomized_episode_count"] == 40
    assert plan["expected_total_episode_count"] == 52
    assert plan["randomized_seeds"] == list(range(20265100, 20265120))
    assert plan["reuse_betrayal_ii_topology_for_both_layouts"] is True
    assert plan["no_early_stopping"] is True
    assert plan["no_failed_seed_replacement"] is True


def test_result_schema_binds_dense_binary_arrays():
    schema = load_schema()
    sidecar = schema["sidecar"]
    arrays = sidecar["arrays"]
    assert sidecar["episode_count_expected"] == 52
    assert arrays["primary_positive_voltage"] == {
        "dtype": "float32",
        "shape": [52, 192, 1191],
    }
    assert arrays["primary_spikes"] == {
        "dtype": "uint8",
        "shape": [52, 192, 1191],
    }
    assert arrays["channel_mean_positive_voltage"] == {
        "dtype": "float64",
        "shape": [52, 3, 192],
    }


def test_symmetric_normalized_l2_identity_and_difference():
    x = np.asarray([0.0, 1.0, 2.0])
    assert r.symmetric_normalized_l2(x, x) == 0.0
    assert r.symmetric_normalized_l2(x, x + 1.0) > 0.0


def test_exact_reproduction_checks_primary_and_channel():
    intact = fake_episode(1.0)
    same = fake_episode(1.0)
    report = r.exact_reproduction_against_intact(same, intact)
    assert report["exact_reproduction"] is True

    changed = fake_episode(1.0)
    changed["channel_mean_positive_voltage"][0, 0] += 1e-6
    report = r.exact_reproduction_against_intact(changed, intact)
    assert report["primary_pass"] is True
    assert report["channel_summary_pass"] is False
    assert report["exact_reproduction"] is False


def test_betrayal_i_classification_is_layout_explicit():
    # Use a nonzero INTACT reference. For the preregistered symmetric
    # normalized L2 metric, D(x, 0) == 1 for every nonzero x, so a zero
    # reference cannot distinguish a larger lesion displacement from a
    # smaller sham displacement.
    intact = {"LR": fake_episode(1.0), "RL": fake_episode(1.0)}
    sham = {"LR": fake_episode(1.1), "RL": fake_episode(1.1)}
    lesion = {"LR": fake_episode(1.4), "RL": fake_episode(1.4)}
    report = r.classify_betrayal_i(intact, lesion, sham)
    assert report["status"] == "LESION_EFFECT_EXCEEDS_SHAM_BOTH_LAYOUTS"

    lesion["RL"] = fake_episode(1.05)
    report = r.classify_betrayal_i(intact, lesion, sham)
    assert report["status"] == "LAYOUT_DEPENDENT_LESION_EFFECT"


def test_betrayal_ii_count_bands_and_incomplete():
    assert r.classify_betrayal_ii(0, 20) == (
        "STRICT_NULL_RARELY_REPRODUCES_INTACT_RESPONSE"
    )
    assert r.classify_betrayal_ii(9, 20) == (
        "MIXED_STRICT_NULL_REPRODUCTION"
    )
    assert r.classify_betrayal_ii(10, 20) == (
        "STRICT_NULL_FREQUENTLY_REPRODUCES_INTACT_RESPONSE"
    )
    assert r.classify_betrayal_ii(0, 19) == "INCOMPLETE_OR_INVALID"


def test_cue_transition_uses_fixed_a_reference_and_b_blocks():
    episode = fake_episode(0.0)
    episode["channel_mean_positive_voltage"][1, 96:112] = 0.5
    report = r.cue_transition_for_layout(episode)
    assert report["responds"] is True

    none = r.cue_transition_for_layout(fake_episode(0.0))
    assert none["responds"] is False


def test_duplicate_replay_requires_all_primary_and_summary_arrays():
    a = fake_episode(1.0)
    b = fake_episode(1.0)
    assert r.duplicate_exact(a, b) is True
    b["spikes"][0, 0] = 1
    assert r.duplicate_exact(a, b) is False


def test_runner_requires_separate_authorization_for_result_execution():
    source = (
        ROOT / "brain/sq05_two_betrayals_runner.py"
    ).read_text(encoding="utf-8")

    required = [
        "--preflight-only",
        "--run-frozen",
        "verify_execution_authorization",
        "result_execution_enabled",
        "execution_mode",
        "runner_sha256",
        "runner_config_sha256",
        "core_prereg_sha256",
        "result_schema_sha256",
        "merge-base",
        "--is-ancestor",
        "clean Git working tree",
    ]
    for marker in required:
        assert marker in source


def test_single_overall_winner_is_forbidden():
    cfg = load_cfg()
    schema = load_schema()
    assert cfg["classification"]["single_overall_winner_forbidden"] is True
    assert schema["manifest"]["single_overall_winner_forbidden"] is True
