from __future__ import annotations

import json
from pathlib import Path


PATH = Path(
    "config/controls/"
    "sq08-three-body-analysis-contract-v1.json"
)


def contract():
    return json.loads(PATH.read_text())


def test_mask_semantics_are_lesion_based():
    data = contract()

    assert data["mask_semantics"]["0"] == (
        "frozen BODY edge retained"
    )

    assert data["mask_semantics"]["1"] == (
        "frozen BODY edge zeroed"
    )

    assert data["mask_semantics"]["bit_order"] == [
        "A",
        "B",
        "C",
    ]


def test_complete_factorial_cube_is_required():
    assert contract()["required_masks"] == [
        "000",
        "001",
        "010",
        "011",
        "100",
        "101",
        "110",
        "111",
    ]


def test_three_way_formula_is_frozen():
    assert (
        contract()["factorial_terms"]["I_ABC"]
        == (
            "Y111 - Y110 - Y101 - Y011 "
            "+ Y100 + Y010 + Y001 - Y000"
        )
    )


def test_pairwise_complete_identity_is_frozen():
    reconstruction = contract()[
        "pairwise_complete_reconstruction"
    ]

    assert reconstruction["identity"] == (
        "Y111 - Y111_pairwise = I_ABC"
    )


def test_primary_exactness_is_inherited():
    exactness = contract()["exactness"]

    assert (
        exactness[
            "symmetric_normalized_l2_max"
        ]
        == 1e-9
    )

    assert (
        exactness[
            "max_abs_difference_max"
        ]
        == 1e-12
    )


def test_no_effect_threshold_can_be_added_later():
    temporal = contract()[
        "frontier_temporal_analysis"
    ]

    assert (
        temporal[
            "no_post_result_effect_threshold"
        ]
        is True
    )


def test_all_18_frontier_nodes_are_reported():
    temporal = contract()[
        "frontier_temporal_analysis"
    ]

    assert temporal["node_count"] == 18
    assert temporal["report_each_node"] is True
    assert (
        temporal[
            "node_selection_after_results_forbidden"
        ]
        is True
    )


def test_unresolved_is_valid_mechanism_result():
    mechanism = contract()[
        "mechanism_classification"
    ]

    assert mechanism["UNRESOLVED_is_valid"] is True

    assert "UNRESOLVED" in mechanism[
        "allowed_labels"
    ]


def test_replicates_must_match_before_analysis():
    policy = contract()["replicate_policy"]

    assert policy["replicates"] == [1, 2]

    assert (
        policy[
            "must_be_bit_exact_before_analysis"
        ]
        is True
    )


def test_claim_boundaries_are_explicit():
    boundaries = set(
        contract()["claim_boundaries"]
    )

    assert "no consciousness claim" in boundaries
    assert "no behavioral claim" in boundaries
    assert (
        "no biological necessity or sufficiency claim"
        in boundaries
    )
    assert (
        "no post-result threshold invention"
        in boundaries
    )
