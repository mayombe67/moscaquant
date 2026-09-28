from __future__ import annotations

from brain.sq08_three_body_plan import (
    MASKS,
    REPLICATES,
    build_conditions,
    condition_id,
)


def test_sq08_masks_are_complete_boolean_cube():
    assert MASKS == (
        "000",
        "001",
        "010",
        "011",
        "100",
        "101",
        "110",
        "111",
    )


def test_sq08_inherits_two_replicates():
    assert REPLICATES == (1, 2)


def test_sq08_has_exactly_16_work_units():
    conditions = build_conditions()

    assert len(conditions) == 16

    assert len({
        row["condition_id"]
        for row in conditions
    }) == 16


def test_sq08_every_mask_has_both_replicates():
    conditions = build_conditions()

    for mask in MASKS:
        reps = {
            row["replicate"]
            for row in conditions
            if row["mask"] == mask
        }

        assert reps == {1, 2}


def test_sq08_condition_id_contract():
    assert condition_id("000", 1) == "sq08:000:r1"
    assert condition_id("111", 2) == "sq08:111:r2"


def test_sq08_body_bit_order_and_lesion_semantics_are_abc():
    lookup = {
        row["condition_id"]: row
        for row in build_conditions()
    }

    assert lookup["sq08:101:r1"]["edge_zeroed"] == {
        "A": 1,
        "B": 0,
        "C": 1,
    }
