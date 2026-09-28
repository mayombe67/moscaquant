from brain.sq09_rl_classifier_closure import (
    build_report,
)


def test_rl_classifier_closure():
    report = build_report()

    assert (
        report["status"]
        == "RL_CLASSIFIER_CLOSURE_COMPLETE"
    )

    assert (
        report["neural_execution_performed"]
        is False
    )

    assert (
        report["sq09_decomposition"][
            "responder_identity_status"
        ]
        == "INHERITED_FROM_FROZEN_EDGE_REGISTRY"
    )

    assert (
        report["sq09_decomposition"][
            "pairwise_interactions_literal_zero"
        ]
        is True
    )

    assert (
        report["sq09_decomposition"][
            "three_way_interaction_literal_zero"
        ]
        is True
    )

    assert (
        report["sq09_decomposition"][
            "supports_disjoint"
        ]
        is True
    )

    rows = report[
        "strict_rl_submasks"
    ]

    assert len(rows) == 7

    assert {
        row["mask"]
        for row in rows
    } == {
        "000",
        "001",
        "010",
        "011",
        "100",
        "101",
        "110",
    }

    assert all(
        row[
            "exact_full13_excluded_by_max_abs_gate"
        ]
        for row in rows
    )

    assert all(
        row[
            "passes_sq07_max_abs_gate"
        ]
        is False
        for row in rows
    )

    assert (
        report["smallest_main_effect"]["body"]
        == "C"
    )

    assert (
        report["smallest_main_effect"]["max_abs"]
        == 2.9374905352597125e-07
    )

    assert (
        report["sq07_classifier"][
            "max_abs_difference_max"
        ]
        == 1e-12
    )

    assert (
        report["result"][
            "canonical_short_form"
        ]
        == "BOOKKEEPING_NOT_TEAMWORK"
    )

    assert (
        report["result"][
            "interaction_required_to_explain_minimality"
        ]
        is False
    )
