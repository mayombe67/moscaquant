import numpy as np

from brain import sq07_the_maw_analysis as a


def fp(value: float) -> np.ndarray:
    return np.full((4, 5), value, dtype=np.float32)


def test_exact_classifier_uses_frozen_sq06_endpoint():
    intact = fp(0.0)
    full13 = fp(1.0)

    assert (
        a.classify_fingerprint(intact, intact, full13)["classification"]
        == "EXACT_INTACT"
    )

    assert (
        a.classify_fingerprint(full13, intact, full13)["classification"]
        == "EXACT_FULL13"
    )

    assert (
        a.classify_fingerprint(fp(0.5), intact, full13)["classification"]
        == "INTERMEDIATE"
    )


def test_frozen_group_masks_are_exact():
    assert a.LR_GROUP_MASK == "1111111111000"
    assert a.RL_GROUP_MASK == "0000000000111"

    assert a.mask_contained_in_lr_group(a.LR_GROUP_MASK)
    assert not a.mask_contained_in_lr_group(a.RL_GROUP_MASK)

    assert a.mask_contained_in_rl_group(a.RL_GROUP_MASK)
    assert not a.mask_contained_in_rl_group(a.LR_GROUP_MASK)


def test_inactive_subset_universes_are_exact():
    lr = a.inactive_masks("LR")
    rl = a.inactive_masks("RL")

    assert len(lr) == 8
    assert len(set(lr)) == 8

    assert len(rl) == 1024
    assert len(set(rl)) == 1024

    assert a.INTACT_MASK in lr
    assert a.INTACT_MASK in rl

    assert a.RL_GROUP_MASK in lr
    assert a.LR_GROUP_MASK in rl


def test_minimality_checks_all_strict_submasks_not_only_immediate():
    # 000...001 is exact FULL13.
    # 000...111 is therefore NOT inclusion-minimal even if its
    # immediate submasks are absent from the exact set.
    lower = "0000000000001"
    upper = "0000000000111"

    exact = {lower, upper}

    assert a.inclusion_minimal_full13(exact) == [lower]


def test_mixed_group_detection():
    assert not a.mask_is_mixed_group(a.LR_GROUP_MASK)
    assert not a.mask_is_mixed_group(a.RL_GROUP_MASK)

    assert a.mask_is_mixed_group("1000000000001")


def test_build_result_preregistered_positive_case():
    masks = [f"{x:013b}" for x in range(8192)]

    classes = {
        "LR": {mask: "INTERMEDIATE" for mask in masks},
        "RL": {mask: "INTERMEDIATE" for mask in masks},
    }

    # Anchors.
    for layout in a.LAYOUTS:
        classes[layout][a.INTACT_MASK] = "EXACT_INTACT"
        classes[layout][a.FULL13_MASK] = "EXACT_FULL13"

    # Frozen SQ-06 partition.
    classes["LR"][a.LR_GROUP_MASK] = "EXACT_FULL13"
    classes["LR"][a.RL_GROUP_MASK] = "EXACT_INTACT"

    classes["RL"][a.RL_GROUP_MASK] = "EXACT_FULL13"
    classes["RL"][a.LR_GROUP_MASK] = "EXACT_INTACT"

    # Complete inactive closure.
    for mask in a.inactive_masks("LR"):
        classes["LR"][mask] = "EXACT_INTACT"

    for mask in a.inactive_masks("RL"):
        classes["RL"][mask] = "EXACT_INTACT"

    result = a.build_result(
        classes,
        anchor_distinguishability={
            "LR": {"distinguishable": True},
            "RL": {"distinguishable": True},
        },
        analysis_head="test",
    )

    flags = result["result_flags"]

    assert flags["SQ06_PARTITION_REPLICATED"] is True
    assert flags["INACTIVE_SUBSET_CLOSURE_SUPPORTED"] is True
    assert flags["INACTIVE_SUBSET_EFFECT_PRESENT"] is False
    assert flags["ALL_MINIMAL_FULL13_RECAPITULATORS_ACTIVE_ONLY"] is True
    assert flags["MIXED_GROUP_MINIMAL_RECAPITULATOR_PRESENT"] is False
    assert flags["STRICT_SUBSET_SEPARABILITY_SUPPORTED"] is True

    assert result["single_overall_winner"] is None
    assert result["minimum_meaningful_effect_floor"] == "NOT_DEFINED"


def test_hidden_inactive_subset_effect_flips_flags():
    masks = [f"{x:013b}" for x in range(8192)]

    classes = {
        "LR": {mask: "INTERMEDIATE" for mask in masks},
        "RL": {mask: "INTERMEDIATE" for mask in masks},
    }

    for layout in a.LAYOUTS:
        classes[layout][a.INTACT_MASK] = "EXACT_INTACT"
        classes[layout][a.FULL13_MASK] = "EXACT_FULL13"

    classes["LR"][a.LR_GROUP_MASK] = "EXACT_FULL13"
    classes["LR"][a.RL_GROUP_MASK] = "EXACT_INTACT"
    classes["RL"][a.RL_GROUP_MASK] = "EXACT_FULL13"
    classes["RL"][a.LR_GROUP_MASK] = "EXACT_INTACT"

    for mask in a.inactive_masks("LR"):
        classes["LR"][mask] = "EXACT_INTACT"

    for mask in a.inactive_masks("RL"):
        classes["RL"][mask] = "EXACT_INTACT"

    hidden = "0000000000001"
    classes["LR"][hidden] = "INTERMEDIATE"

    result = a.build_result(
        classes,
        anchor_distinguishability={
            "LR": {"distinguishable": True},
            "RL": {"distinguishable": True},
        },
        analysis_head="test",
    )

    assert (
        result["result_flags"]["INACTIVE_SUBSET_CLOSURE_SUPPORTED"]
        is False
    )

    assert (
        result["result_flags"]["INACTIVE_SUBSET_EFFECT_PRESENT"]
        is True
    )

    assert (
        hidden
        in result["inactive_subset"]["failures_by_layout"]["LR"]
    )
