from pathlib import Path
import hashlib
import json
import tomllib


ROOT = Path(__file__).resolve().parents[2]
CFG = ROOT / "config/controls/sq07-the-maw-v1.toml"
REGISTRY = ROOT / "config/controls/sq07-the-maw-edge-registry-v1.json"
SQ06_GROUPS = ROOT / "config/controls/sq06-orientation-edge-groups-v1.json"
HUMAN = ROOT / "docs/experiments/sq07-the-maw-prereg.md"


def load_cfg():
    with CFG.open("rb") as f:
        return tomllib.load(f)


def load_registry():
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_sq07_is_prospective_exhaustive_followup_not_new_discovery():
    c = load_cfg()
    p = c["post_result_origin"]

    assert p["edge_universe_is_derived_from_sq06"] is True
    assert p["sq06_partition_was_derived_from_sq05"] is True
    assert p["independent_discovery"] is False
    assert p["future_test_is_prospective_exhaustive_validation"] is True
    assert p["sq05_result_may_not_be_rewritten"] is True
    assert p["sq06_result_may_not_be_rewritten"] is True


def test_registry_is_exact_ordered_copy_of_frozen_sq06_groups():
    r = load_registry()
    source = json.loads(SQ06_GROUPS.read_text(encoding="utf-8"))

    assert r["source"]["sha256"] == sha256(SQ06_GROUPS)
    assert r["source"]["sha256"] == (
        "2fac74225e9874dfe13f919bfc47062065ba85b1ed1b61cce424f9a2c777c38d"
    )

    expected = [
        ("LR_OBSERVED", row)
        for row in source["groups"]["LR_OBSERVED"]
    ] + [
        ("RL_OBSERVED", row)
        for row in source["groups"]["RL_OBSERVED"]
    ]

    assert len(expected) == 13
    assert len(r["edges"]) == 13

    for i, (group, row) in enumerate(expected):
        got = r["edges"][i]
        assert got["edge_index"] == i
        assert got["edge_id"] == f"E{i:02d}"
        assert got["sq06_group"] == group
        assert got["accepted_responder"] == row["accepted_responder"]
        assert got["target_edge"] == row["target_edge"]
        assert got["matched_sham_edge"] == row["matched_sham_edge"]


def test_mask_coordinate_system_is_frozen_and_unambiguous():
    c = load_cfg()
    r = load_registry()

    m = c["mask_contract"]
    rm = r["mask_contract"]

    assert m["intact_mask"] == "0000000000000"
    assert m["full13_mask"] == "1111111111111"
    assert m["lr_group_mask"] == "1111111111000"
    assert m["rl_group_mask"] == "0000000000111"
    assert m["mask_count_per_layout"] == 2**13
    assert m["adaptive_mask_selection_forbidden"] is True
    assert m["mask_pruning_forbidden"] is True
    assert m["early_stop_forbidden"] is True

    assert rm["length"] == 13
    assert rm["subset_count"] == 2**13
    assert rm["character_index_semantics"] == "mask13[i] corresponds to edges[i]"


def test_execution_universe_is_complete_duplicate_lattice():
    c = load_cfg()
    e = c["execution_universe"]

    assert c["stimulus"]["layouts"] == ["LR", "RL"]
    assert e["replicates"] == [1, 2]
    assert e["duplicate_replicates_per_mask_layout"] == 2
    assert e["expected_unique_masks_per_layout"] == 8192
    assert e["expected_mask_layout_conditions"] == 16384
    assert e["expected_total_episode_count"] == 32768
    assert e["exact_duplicate_replay_required"] is True
    assert e["all_conditions_required"] is True
    assert e["missing_condition_replacement_forbidden"] is True


def test_anchor_contract_fails_closed_if_anchors_collapse():
    c = load_cfg()
    a = c["anchor_classification"]
    p = c["primary_fingerprint"]

    assert a["classes"] == ["EXACT_INTACT", "EXACT_FULL13", "INTERMEDIATE"]
    assert a["same_layout_intact_and_full13_must_not_be_exact_equivalent"] is True
    assert a["anchor_collapse_requires_fail_closed"] is True

    assert p["normalized_l2_exact_max"] == 1e-9
    assert p["max_abs_exact_max"] == 1e-12
    assert p["minimum_meaningful_effect_floor"] == "NOT_DEFINED"
    assert p["no_post_result_threshold_invention"] is True


def test_inactive_subset_closure_counts_are_exhaustive():
    c = load_cfg()
    x = c["inactive_subset_closure"]

    assert x["lr_inactive_group_indices"] == [10, 11, 12]
    assert x["lr_inactive_subset_count"] == 2**3

    assert x["rl_inactive_group_indices"] == list(range(10))
    assert x["rl_inactive_subset_count"] == 2**10

    assert x["include_empty_subset"] is True


def test_minimal_recapitulator_definition_is_inclusion_based():
    c = load_cfg()
    m = c["minimal_recapitulators"]

    assert m["target_class"] == "EXACT_FULL13"
    assert "no strict submask" in m["minimality"]
    assert m["hamming_weight_only_minimality_forbidden"] is True
    assert m["enumerate_all_inclusion_minimal_masks"] is True


def test_primary_taxonomy_is_frozen_without_overall_winner():
    c = load_cfg()
    f = c["primary_flags"]

    assert "SQ06_PARTITION_REPLICATED" in f["strict_subset_separability_supported"]
    assert "INACTIVE_SUBSET_CLOSURE_SUPPORTED" in f["strict_subset_separability_supported"]
    assert "ALL_MINIMAL_FULL13_RECAPITULATORS_ACTIVE_ONLY" in f[
        "strict_subset_separability_supported"
    ]
    assert "not MIXED_GROUP_MINIMAL_RECAPITULATOR_PRESENT" in f[
        "strict_subset_separability_supported"
    ]
    assert f["single_overall_winner_forbidden"] is True


def test_evidence_and_claim_boundaries_are_fail_closed():
    c = load_cfg()

    e = c["evidence"]
    assert e["preserve_primary_fingerprint_for_every_episode"] is True
    assert e["every_shard_requires_sha256"] is True
    assert e["independent_recomputation_from_preserved_evidence_required"] is True
    assert e["runner_summary_alone_is_not_sufficient_evidence"] is True

    b = c["boundaries"]
    assert b["does_not_rewrite_sq05"] is True
    assert b["does_not_rewrite_sq06"] is True
    assert b["does_not_claim_independent_discovery"] is True
    assert b["does_not_claim_biological_orientation_circuit"] is True
    assert b["does_not_claim_behavior"] is True
    assert b["preregistration_does_not_authorize_neural_execution"] is True
    assert b["preregistration_does_not_authorize_result_execution"] is True


def test_prereg_pins_exact_registry_bytes():
    c = load_cfg()
    assert c["provenance"]["sq07_edge_registry_sha256"] == sha256(REGISTRY)



def test_sq07_edge_universe_coordinates_are_explicitly_frozen():
    c = load_cfg()
    e = c["edge_universe"]
    m = c["mask_contract"]
    r = load_registry()

    assert e["edge_count"] == 13
    assert e["lr_observed_indices"] == list(range(10))
    assert e["rl_observed_indices"] == [10, 11, 12]
    assert e["union_is_exact_historical_13_edge_lesion"] is True
    assert e["groups_are_disjoint"] is True

    assert m["enumeration"] == "lexicographic ascending"
    assert r["mask_contract"]["enumeration"] == "lexicographic ascending"


def test_human_prereg_matches_frozen_machine_contract():
    c = load_cfg()
    h = " ".join(HUMAN.read_text(encoding="utf-8").split())

    # Complete intervention universe.
    assert c["edge_universe"]["edge_count"] == 13
    assert c["mask_contract"]["mask_count_per_layout"] == 8192
    assert c["execution_universe"]["expected_mask_layout_conditions"] == 16384
    assert c["execution_universe"]["expected_total_episode_count"] == 32768

    assert "exactly 13 targeted historical lesion edges" in h
    assert "All `2^13 = 8192` masks are enumerated in frozen lexicographic order." in h
    assert "Total planned conditions before duplication: **16,384**." in h
    assert "Total planned episodes: **32,768**." in h

    # Exact endpoint contract.
    assert c["primary_fingerprint"]["normalized_l2_exact_max"] == 1e-9
    assert c["primary_fingerprint"]["max_abs_exact_max"] == 1e-12
    assert (
        c["anchor_classification"][
            "same_layout_intact_and_full13_must_not_be_exact_equivalent"
        ]
        is True
    )
    assert c["anchor_classification"]["anchor_collapse_requires_fail_closed"] is True

    assert "symmetric normalized L2 `<= 1e-9`;" in h
    assert "maximum absolute difference `<= 1e-12`." in h
    assert (
        "If they collapse into exact equivalence, the experiment fails closed "
        "rather than redefining the classification."
    ) in h

    # Exhaustive inactive-subset closure.
    assert c["inactive_subset_closure"]["lr_inactive_subset_count"] == 8
    assert c["inactive_subset_closure"]["rl_inactive_subset_count"] == 1024
    assert c["inactive_subset_closure"]["include_empty_subset"] is True

    assert "For LR, all `2^3 = 8` masks composed only of the frozen RL group" in h
    assert "For RL, all `2^10 = 1024` masks composed only of the frozen LR group" in h

    # Inclusion-minimal means inclusion-minimal, not merely smallest weight.
    assert (
        c["minimal_recapitulators"]["hamming_weight_only_minimality_forbidden"]
        is True
    )
    assert c["minimal_recapitulators"]["enumerate_all_inclusion_minimal_masks"] is True

    assert "no strict submask is also `EXACT_FULL13`." in h
    assert "Minimum Hamming weight alone is not sufficient to define minimality." in h

    # Reporting and scientific boundaries.
    assert c["reporting"]["single_overall_winner_forbidden"] is True
    assert c["reporting"]["minimum_meaningful_effect_floor"] == "NOT_DEFINED"
    assert c["boundaries"]["does_not_claim_independent_discovery"] is True
    assert c["boundaries"]["preregistration_does_not_authorize_neural_execution"] is True
    assert c["boundaries"]["preregistration_does_not_authorize_result_execution"] is True

    assert "There is no overall scientific winner." in h
    assert "No minimum meaningful-effect floor is introduced." in h
    assert (
        "SQ-07 therefore does not transform either history into independent discovery."
    ) in h
    assert "No neural or result execution is authorized by this preregistration." in h



def test_human_execution_authority_cannot_be_inferred_or_delegated():
    c = load_cfg()
    a = c["human_command_authority"]

    assert a["human_execution_authorization_required"] is True
    assert a["automated_authorization_forbidden"] is True
    assert a["ai_generated_authorization_forbidden"] is True
    assert a["ci_success_is_not_execution_authorization"] is True
    assert a["test_success_is_not_execution_authorization"] is True
    assert a["runner_presence_is_not_execution_authorization"] is True
    assert a["authorization_must_be_explicit_and_run_specific"] is True
    assert a["authorization_may_not_be_inferred_from_prior_runs"] is True

    h = " ".join(HUMAN.read_text(encoding="utf-8").split())

    assert (
        "SQ-07 execution requires explicit, run-specific authorization from the human "
        "operator."
    ) in h

    assert (
        "No software agent, automated system, successful test or CI result, runner "
        "availability, or prior authorization may be treated as execution authorization."
    ) in h
