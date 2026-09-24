from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "config/controls/sq07-the-maw-evidence-schema-v1.json"


def load_schema():
    return json.loads(SCHEMA.read_text(encoding="utf-8"))


def test_evidence_schema_binds_exact_frozen_authority_chain():
    s = load_schema()
    a = s["authority_chain"]

    assert a["preregistration_sha256"] == (
        "0ff34f0f4c2c1315b766ecc1acf66e2e6c24650aba87ae033e5a71a2b707a84a"
    )

    assert a["condition_plan_sha256"] == (
        "850ae560ab1b25c65f9932615f8ea1851781881c4492672767bcda692667becb"
    )

    assert a["sharding_contract_sha256"] == (
        "ede14b0add5d13e723c443be241504dea36d4bb0424e3f718b199b8c1c665d8a"
    )

    assert a["shard_plan_sha256"] == (
        "9039b8e708c2ffdb74436e5c6fdc8f7d2f38f3f3fb27fd7478dd2cc8101d2a55"
    )

    assert a["condition_planner_source_sha256"] == (
        "38b8e628492a475f63c40c332232b36c929512dfae8341f5b64afd1597f5411f"
    )

    assert a["shard_planner_source_sha256"] == (
        "7cde07ad921543cdb9dba95f3299ccb4a1cfbb20f32a3a75fc678a2df61ef1af"
    )

    assert a["subset_operator_source_sha256"] == (
        "693ae8c2455361351802d0ac0c9cee4ada3bb8a25a60043264de5da14da00a5e"
    )

    assert a["episode_executor_source_sha256"] == (
        "a4b85e45779ab98c9a1275a0e97ced9f1abb48bfadd974319bfcecf4305be9d8"
    )


def test_schema_is_exactly_64_episode_shard_contract():
    s = load_schema()

    assert s["shard_contract"]["conditions_per_shard"] == 64
    assert s["shard_contract"]["masks_per_shard"] == 16
    assert s["shard_contract"]["layouts"] == ["LR", "RL"]
    assert s["shard_contract"]["replicates_per_mask_layout"] == 2
    assert s["sidecar"]["episode_count"] == 64


def test_primary_evidence_is_preserved_for_every_episode():
    arrays = load_schema()["sidecar"]["arrays"]

    assert arrays["primary_positive_voltage"] == {
        "dtype": "float32",
        "shape": [64, 192, 1191],
    }

    assert arrays["primary_spikes"] == {
        "dtype": "uint8",
        "shape": [64, 192, 1191],
    }


def test_all_six_episode_result_arrays_are_preserved():
    arrays = load_schema()["sidecar"]["arrays"]

    expected = {
        "primary_positive_voltage",
        "primary_spikes",
        "channel_mean_positive_voltage",
        "channel_positive_fraction",
        "channel_spike_count",
        "channel_spike_rate",
    }

    assert expected <= set(arrays)


def test_condition_identity_is_preserved_inside_sidecar():
    arrays = load_schema()["sidecar"]["arrays"]

    assert arrays["condition_ordinal"] == {
        "dtype": "int32",
        "shape": [64],
    }

    assert arrays["condition_id"]["shape"] == [64]
    assert arrays["condition_mask13"]["shape"] == [64]
    assert arrays["condition_layout"]["shape"] == [64]

    assert arrays["condition_replicate"] == {
        "dtype": "int8",
        "shape": [64],
    }


def test_dn_identity_is_preserved_for_independent_recomputation():
    arrays = load_schema()["sidecar"]["arrays"]

    assert arrays["dn_indices"] == {
        "dtype": "int32",
        "shape": [1191],
    }


def test_per_episode_and_shard_timing_are_required_but_non_scientific():
    s = load_schema()
    arrays = s["sidecar"]["arrays"]
    timing = s["timing"]

    assert arrays["episode_started_at_utc"]["shape"] == [64]
    assert arrays["episode_completed_at_utc"]["shape"] == [64]

    assert arrays["episode_elapsed_seconds"] == {
        "dtype": "float64",
        "shape": [64],
    }

    assert timing["shard_started_at_utc_required"] is True
    assert timing["shard_completed_at_utc_required"] is True
    assert timing["shard_elapsed_seconds_required"] is True
    assert timing["per_episode_timing_required"] is True
    assert timing["timing_has_scientific_semantics"] is False


def test_manifest_must_bind_shard_and_sidecar_identity():
    s = load_schema()
    manifest = s["manifest"]

    required = set(manifest["required_shard_identity_fields"])

    assert {
        "shard_id",
        "shard_index",
        "parent_plan_sha256",
        "shard_plan_sha256",
        "sharding_contract_sha256",
        "condition_membership_sha256",
        "start_ordinal",
        "end_ordinal_exclusive",
        "condition_count",
        "mask_count",
        "first_condition_id",
        "last_condition_id",
        "condition_ids",
    } <= required

    assert manifest["sidecar_must_be_content_addressed"] is True
    assert manifest["sidecar_must_exist_before_manifest_commit"] is True
    assert manifest["atomic_manifest_write_required"] is True
    assert manifest["atomic_sidecar_write_required"] is True


def test_completeness_requires_exact_shard_membership_and_duplicate_pairs():
    c = load_schema()["completeness"]

    assert c["all_64_conditions_required"] is True
    assert c["condition_ids_must_exactly_equal_shard_membership"] is True
    assert c["condition_order_must_equal_canonical_shard_order"] is True

    assert c["duplicate_condition_ids_forbidden"] is True
    assert c["missing_condition_ids_forbidden"] is True
    assert c["unexpected_condition_ids_forbidden"] is True

    assert c["all_16_masks_required"] is True
    assert c["whole_mask_quartets_required"] is True
    assert c["both_layouts_required_per_mask"] is True
    assert c["both_replicates_required_per_mask_layout"] is True

    assert c["duplicate_replay_verification_required"] is True
    assert c["duplicate_replay_uses_all_six_episode_arrays"] is True


def test_evidence_is_sufficient_for_independent_recomputation():
    r = load_schema()["recomputation"]

    assert r["preserve_primary_fingerprint_for_every_episode"] is True
    assert r["preserve_spikes_for_every_episode"] is True

    assert (
        r["independent_recomputation_from_preserved_evidence_required"]
        is True
    )

    assert r["runner_summary_alone_is_not_sufficient_evidence"] is True


def test_evidence_layer_cannot_classify_select_stop_or_authorize():
    b = load_schema()["claim_boundaries"]

    assert b["evidence_layer_may_classify_results"] is False
    assert b["evidence_layer_may_select_conditions"] is False
    assert b["evidence_layer_may_stop_early_based_on_results"] is False
    assert b["evidence_layer_may_authorize_neural_execution"] is False
    assert b["evidence_layer_may_authorize_result_execution"] is False
    assert b["evidence_layer_may_reinterpret_sq05_or_sq06"] is False

    assert b["single_overall_winner"] is None
    assert b["minimum_meaningful_effect_floor"] == "NOT_DEFINED"


def test_schema_contains_no_result_classification_vocabulary():
    source = SCHEMA.read_text(encoding="utf-8")

    forbidden = [
        "EXACT_INTACT",
        "EXACT_FULL13",
        "INTERMEDIATE",
        "minimal_recapitulator",
        "inactive_subset_closure_supported",
        "strict_subset_separability_supported"
    ]

    for token in forbidden:
        assert token not in source
