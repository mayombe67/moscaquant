from __future__ import annotations

from collections import Counter
from pathlib import Path

import pytest

import brain.sq07_the_maw_plan as p


ROOT = Path(__file__).resolve().parents[2]
PLAN_SOURCE = ROOT / "brain/sq07_the_maw_plan.py"


def test_planner_binds_exact_frozen_sq07_authority():
    authority = p.verify_frozen_authority()

    assert authority["prereg_sha256"] == (
        "0ff34f0f4c2c1315b766ecc1acf66e2e6c24650aba87ae033e5a71a2b707a84a"
    )
    assert authority["registry_sha256"] == (
        "0e9502f3147d2f833d00ce2c05af258b973f7391a43c9d89f695556d8823dedd"
    )

    assert authority["edge_count"] == 13
    assert authority["mask_count"] == 8192
    assert authority["condition_count"] == 32768


def test_mask_universe_is_exact_complete_lexicographic_13_bit_space():
    masks = p.masks()

    assert len(masks) == 8192
    assert len(set(masks)) == 8192

    assert masks[0] == "0000000000000"
    assert masks[-1] == "1111111111111"

    assert list(masks) == sorted(masks)

    assert masks == tuple(f"{value:013b}" for value in range(8192))


def test_frozen_named_masks_remain_exact():
    assert p.INTACT_MASK == "0000000000000"
    assert p.FULL13_MASK == "1111111111111"
    assert p.LR_GROUP_MASK == "1111111111000"
    assert p.RL_GROUP_MASK == "0000000000111"


def test_condition_plan_contains_exactly_32768_unique_conditions():
    plan = p.condition_plan()

    assert len(plan) == 32768
    assert len({row["condition_id"] for row in plan}) == 32768

    assert [row["ordinal"] for row in plan] == list(range(32768))


def test_each_mask_occurs_exactly_four_times():
    plan = p.condition_plan()

    counts = Counter(row["mask13"] for row in plan)

    assert len(counts) == 8192
    assert set(counts.values()) == {4}


def test_each_mask_layout_occurs_exactly_twice():
    plan = p.condition_plan()

    counts = Counter(
        (row["mask13"], row["layout"])
        for row in plan
    )

    assert len(counts) == 8192 * 2
    assert set(counts.values()) == {2}


def test_each_mask_layout_replicate_occurs_exactly_once():
    plan = p.condition_plan()

    counts = Counter(
        (row["mask13"], row["layout"], row["replicate"])
        for row in plan
    )

    assert len(counts) == 32768
    assert set(counts.values()) == {1}


def test_condition_order_is_mask_then_layout_then_replicate():
    plan = p.condition_plan()

    assert plan[0] == {
        "ordinal": 0,
        "condition_id": "sq07:0000000000000:LR:r1",
        "mask13": "0000000000000",
        "layout": "LR",
        "replicate": 1,
    }

    assert plan[1]["condition_id"] == "sq07:0000000000000:LR:r2"
    assert plan[2]["condition_id"] == "sq07:0000000000000:RL:r1"
    assert plan[3]["condition_id"] == "sq07:0000000000000:RL:r2"

    assert plan[4]["condition_id"] == "sq07:0000000000001:LR:r1"

    assert plan[-1] == {
        "ordinal": 32767,
        "condition_id": "sq07:1111111111111:RL:r2",
        "mask13": "1111111111111",
        "layout": "RL",
        "replicate": 2,
    }

    ordered_masks = [
        plan[offset]["mask13"]
        for offset in range(0, len(plan), 4)
    ]

    assert ordered_masks == [f"{value:013b}" for value in range(8192)]


def test_condition_id_rejects_invalid_coordinates():
    with pytest.raises(ValueError):
        p.condition_id("0000", "LR", 1)

    with pytest.raises(ValueError):
        p.condition_id("000000000000X", "LR", 1)

    with pytest.raises(ValueError):
        p.condition_id(p.INTACT_MASK, "XX", 1)

    with pytest.raises(ValueError):
        p.condition_id(p.INTACT_MASK, "LR", 3)


def test_plan_digest_is_deterministic_and_complete():
    plan = p.condition_plan()

    first = p.condition_plan_sha256(plan)
    second = p.condition_plan_sha256(plan)

    assert first == second
    assert len(first) == 64
    int(first, 16)

    with pytest.raises(p.Refusal):
        p.condition_plan_sha256(plan[:-1])


def test_authority_drift_fails_closed(monkeypatch):
    monkeypatch.setitem(
        p.EXPECTED_SHA256,
        "prereg",
        "0" * 64,
    )

    with pytest.raises(p.Refusal, match="SHA mismatch"):
        p.verify_frozen_authority()


def test_planner_has_no_neural_execution_or_result_classification_surface():
    source = PLAN_SOURCE.read_text(encoding="utf-8")

    forbidden = [
        "argparse",
        "--run-frozen",
        "run_episode",
        "mq5_ts_runtime",
        "CONNECTOME",
        "RETINA",
        "scipy",
        "numpy",
        "EXACT_INTACT",
        "EXACT_FULL13",
        "INTERMEDIATE",
        "symmetric_normalized_l2",
        "max_abs_difference",
    ]

    for token in forbidden:
        assert token not in source
