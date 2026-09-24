from pathlib import Path
import json
import tomllib

ROOT = Path(__file__).resolve().parents[2]
CFG = ROOT / "config/controls/sq06-silent-cartographer-v1.toml"
GROUPS = ROOT / "config/controls/sq06-orientation-edge-groups-v1.json"

def load_cfg():
    with CFG.open("rb") as f:
        return tomllib.load(f)

def load_groups():
    return json.loads(GROUPS.read_text(encoding="utf-8"))

def test_sq06_is_prospective_validation_of_post_result_grouping():
    c = load_cfg()
    assert c["post_result_origin"]["grouping_is_derived_from_sq05_outcome"] is True
    assert c["post_result_origin"]["grouping_is_independent_discovery"] is False
    assert c["post_result_origin"]["future_test_is_prospective_validation"] is True
    assert c["post_result_origin"]["sq05_result_may_not_be_rewritten"] is True

def test_group_partition_is_exact_10_plus_3():
    g = load_groups()
    lr = g["groups"]["LR_OBSERVED"]
    rl = g["groups"]["RL_OBSERVED"]
    assert len(lr) == 10
    assert len(rl) == 3
    targeted = {
        (x["target_edge"]["presynaptic"], x["target_edge"]["postsynaptic"])
        for x in lr + rl
    }
    assert len(targeted) == 13
    assert {x["accepted_responder"] for x in lr} == {51,55,92,129,656,1273}
    assert {x["accepted_responder"] for x in rl} == {317,126002,137122}

def test_each_target_has_same_presynaptic_matched_sham():
    g = load_groups()
    for rows in g["groups"].values():
        for x in rows:
            assert x["target_edge"]["presynaptic"] == x["matched_sham_edge"]["presynaptic"]

def test_design_is_28_deterministic_episodes():
    c = load_cfg()
    assert len(c["arms"]["names"]) == 7
    assert c["stimulus"]["layouts"] == ["LR", "RL"]
    assert c["arms"]["duplicate_replicates_per_layout"] == 2
    assert c["arms"]["expected_episode_count"] == 28
    assert c["primary_fingerprint"]["exact_duplicate_replay_required"] is True

def test_exact_partition_hypotheses_are_frozen():
    c = load_cfg()
    h = c["primary_hypotheses"]
    assert "exactly reproduces FULL13_TARGETED" in h["lr_recapitulation"]
    assert "exactly reproduces INTACT" in h["lr_cross_group_null"]
    assert "exactly reproduces FULL13_TARGETED" in h["rl_recapitulation"]
    assert "exactly reproduces INTACT" in h["rl_cross_group_null"]
    assert h["all_primary_conditions_required_for_exact_partition"] is True

def test_no_post_result_effect_floor_or_biological_claim():
    c = load_cfg()
    assert c["reporting"]["minimum_meaningful_effect_floor"] == "NOT_DEFINED"
    assert c["reporting"]["no_post_result_threshold_invention"] is True
    b = c["boundaries"]
    assert b["does_not_rewrite_sq05"] is True
    assert b["does_not_claim_biological_orientation_circuit"] is True
    assert b["preregistration_does_not_authorize_neural_execution"] is True
    assert b["preregistration_does_not_authorize_result_execution"] is True
