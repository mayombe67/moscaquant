from pathlib import Path
import tomllib

ROOT = Path(__file__).resolve().parents[2]
CFG = ROOT / "config/controls/mq5-ts-arm-c-mixing-depth-v1.toml"


def load():
    with CFG.open("rb") as f:
        return tomllib.load(f)


def test_mixing_depth_prereg_is_structural_only():
    cfg = load()
    assert cfg["experiment"]["id"] == "mq5-ts-arm-c-mixing-depth-v1"
    assert cfg["experiment"]["neural_execution"] is False
    assert cfg["experiment"]["reopens_parent_result"] is False
    assert cfg["metrics"]["neural_metrics_forbidden"] is True
    assert cfg["experiment"]["narrative_label_scientific"] is False


def test_mixing_depth_grid_and_seeds_are_frozen():
    cfg = load()
    assert cfg["design"]["depths"] == [0.5, 1.0, 2.0, 4.0]
    assert cfg["design"]["seeds"] == [20264000, 20264001, 20264002]
    assert cfg["design"]["expected_build_count"] == 12
    assert cfg["design"]["no_early_stopping"] is True
    assert cfg["design"]["no_seed_replacement"] is True


def test_mixing_depth_seeds_do_not_overlap_accepted_arm_c_range():
    cfg = load()
    accepted = set(range(20263000, 20263020))
    proposed = set(cfg["design"]["seeds"])
    assert accepted.isdisjoint(proposed)


def test_mixing_depth_decision_rule_is_frozen():
    cfg = load()
    d = cfg["decision"]
    assert d["deep_reference_depth"] == 4.0
    assert d["current_depth"] == 1.0
    assert d["prospective_alternate_depth"] == 2.0
    assert d["seed_memory_excess_tolerance"] == 0.01
    assert d["require_all_three_seeds"] is True
    assert d["classification_no_adequate"] == (
        "NO_ADEQUATE_DEPTH_WITHIN_TESTED_RANGE"
    )


def test_mixing_depth_reuses_production_backend():
    cfg = load()
    b = cfg["backend"]
    assert b["reuse_production_arm_c_backend"] is True
    assert b["reference_backend_full_connectome_forbidden"] is True
    assert b["max_attempt_multiplier"] == 20
    assert b["require_same_seed_prefix_determinism_test_before_execution"] is True


def test_mixing_depth_inputs_are_portable_and_hash_bound():
    cfg = load()
    i = cfg["inputs"]
    assert i["path_resolution"] == "MOSCAQUANT_DATA_ROOT_relative"
    assert i["connectome"] == "processed/connectome-baseline-v1.npz"
    assert i["transmitter"] == "processed/transmitter_sign.npy"
    assert i["retina"] == "processed/visual-r1-r6-map-v1.npz"
    assert i["fail_closed_on_hash_mismatch"] is True
    assert len(i["connectome_sha256"]) == 64
    assert len(i["transmitter_sha256"]) == 64
    assert len(i["retina_sha256"]) == 64


def test_mixing_depth_primary_adequacy_metric_is_seed_memory_excess():
    cfg = load()
    m = cfg["metrics"]
    assert m["within_seed_checkpoint_to_deep_overlap"] is True
    assert m["cross_seed_checkpoint_to_other_deep_mean_overlap"] is True
    assert m["seed_memory_excess"] is True
    assert m["deep_pairwise_overlap"] is True


def test_mixing_depth_cannot_rewrite_parent_result():
    cfg = load()
    b = cfg["boundaries"]
    assert b["does_not_reinterpret_mq5_ts"] is True
    assert b["does_not_modify_mq5_ts_artifact"] is True
    assert b["does_not_authorize_sq05_by_itself"] is True
