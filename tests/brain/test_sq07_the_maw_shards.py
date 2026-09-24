from __future__ import annotations

from pathlib import Path

import pytest

import brain.sq07_the_maw_shards as s


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "brain/sq07_the_maw_shards.py"


def test_sharding_contract_is_exactly_bound():
    cfg = s.load_sharding_contract()

    assert s.sha256_file(s.SHARDING) == (
        "ede14b0add5d13e723c443be241504dea36d4bb0424e3f718b199b8c1c665d8a"
    )

    assert cfg["parent_plan"]["condition_plan_sha256"] == (
        "850ae560ab1b25c65f9932615f8ea1851781881c4492672767bcda692667becb"
    )

    assert cfg["partition"]["conditions_per_shard"] == 64
    assert cfg["partition"]["masks_per_shard"] == 16
    assert cfg["partition"]["expected_shard_count"] == 512


def test_shard_plan_is_exactly_512_complete_descriptors():
    shards = s.shard_plan()

    assert len(shards) == 512
    assert [x["shard_index"] for x in shards] == list(range(512))

    assert shards[0]["shard_id"] == "sq07-shard-000"
    assert shards[-1]["shard_id"] == "sq07-shard-511"


def test_every_shard_contains_exactly_64_conditions_and_16_masks():
    shards = s.shard_plan()

    assert {x["condition_count"] for x in shards} == {64}
    assert {x["mask_count"] for x in shards} == {16}


def test_first_and_last_shard_boundaries_are_exact():
    shards = s.shard_plan()

    first = shards[0]
    last = shards[-1]

    assert first["start_ordinal"] == 0
    assert first["end_ordinal_exclusive"] == 64
    assert first["first_condition_id"] == "sq07:0000000000000:LR:r1"
    assert first["last_condition_id"] == "sq07:0000000001111:RL:r2"

    assert last["start_ordinal"] == 32704
    assert last["end_ordinal_exclusive"] == 32768
    assert last["first_condition_id"] == "sq07:1111111110000:LR:r1"
    assert last["last_condition_id"] == "sq07:1111111111111:RL:r2"


def test_all_canonical_ordinals_are_covered_exactly_once():
    shards = s.shard_plan()

    ordinals = []

    for shard in shards:
        ordinals.extend(
            range(
                shard["start_ordinal"],
                shard["end_ordinal_exclusive"],
            )
        )

    assert ordinals == list(range(32768))


def test_union_of_condition_ids_is_exact_parent_plan():
    parent = s.condition_plan()
    shards = s.shard_plan()

    observed = [
        condition_id
        for shard in shards
        for condition_id in shard["condition_ids"]
    ]

    expected = [row["condition_id"] for row in parent]

    assert observed == expected
    assert len(observed) == 32768
    assert len(set(observed)) == 32768


def test_each_shard_preserves_complete_mask_quartets():
    parent = s.condition_plan()
    by_id = {
        row["condition_id"]: row
        for row in parent
    }

    for shard in s.shard_plan():
        masks = {}

        for condition_id in shard["condition_ids"]:
            row = by_id[condition_id]
            masks.setdefault(row["mask13"], []).append(
                (row["layout"], row["replicate"])
            )

        assert len(masks) == 16

        for coordinates in masks.values():
            assert coordinates == [
                ("LR", 1),
                ("LR", 2),
                ("RL", 1),
                ("RL", 2),
            ]


def test_every_shard_has_unique_membership_digest():
    shards = s.shard_plan()

    digests = [
        shard["condition_membership_sha256"]
        for shard in shards
    ]

    assert len(digests) == 512
    assert len(set(digests)) == 512

    for digest in digests:
        assert len(digest) == 64
        int(digest, 16)


def test_shard_plan_digest_is_deterministic():
    shards = s.shard_plan()

    first = s.shard_plan_sha256(shards)
    second = s.shard_plan_sha256(shards)

    assert first == second
    assert len(first) == 64
    int(first, 16)


def test_shard_plan_digest_refuses_incomplete_universe():
    shards = s.shard_plan()

    with pytest.raises(s.Refusal):
        s.shard_plan_sha256(shards[:-1])


def test_verifier_rejects_duplicate_condition():
    shards = s.shard_plan()

    corrupted = [
        {
            **shard,
            "condition_ids": list(shard["condition_ids"]),
        }
        for shard in shards
    ]

    corrupted[1]["condition_ids"][0] = corrupted[0]["condition_ids"][0]

    corrupted[1]["condition_membership_sha256"] = s.canonical_json_sha256(
        corrupted[1]["condition_ids"]
    )

    with pytest.raises(s.Refusal):
        s.verify_shard_plan(corrupted)


def test_verifier_rejects_membership_digest_tamper():
    shards = s.shard_plan()

    corrupted = [dict(shard) for shard in shards]
    corrupted[10] = {
        **corrupted[10],
        "condition_membership_sha256": "0" * 64,
    }

    with pytest.raises(s.Refusal, match="membership digest"):
        s.verify_shard_plan(corrupted)


def test_sharder_has_no_neural_execution_or_result_analysis_surface():
    source = SOURCE.read_text(encoding="utf-8")

    forbidden = [
        "argparse",
        "--run-frozen",
        "run_episode",
        "CONNECTOME",
        "RETINA",
        "mq5_ts_runtime",
        "numpy",
        "scipy",
        "EXACT_INTACT",
        "EXACT_FULL13",
        "INTERMEDIATE",
        "symmetric_normalized_l2",
    ]

    for token in forbidden:
        assert token not in source
