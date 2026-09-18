from __future__ import annotations

import math

from oracle.credit_assignment import (
    LOOKBACK_TRANSITIONS,
    classify_credit,
    eligibility_trace,
    recency_weight,
    score_edge,
)


def test_recency_function_is_frozen():
    assert math.isclose(
        recency_weight(0),
        1.0,
    )

    assert math.isclose(
        recency_weight(5),
        0.5,
    )


def test_exact_ten_transition_lookback():
    history = [
        1000.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
    ]

    trace_with_extra, count = eligibility_trace(
        weight=1.0,
        activity_history=history,
    )

    trace_last_ten, expected_count = eligibility_trace(
        weight=1.0,
        activity_history=history[
            -LOOKBACK_TRANSITIONS:
        ],
    )

    assert math.isclose(
        trace_with_extra,
        trace_last_ten,
    )

    assert count == expected_count == 10


def test_zero_activity_has_zero_eligibility():
    trace, contributing = eligibility_trace(
        weight=10.0,
        activity_history=[0.0] * 10,
    )

    assert trace == 0.0
    assert contributing == 0


def test_more_recent_equal_activity_gets_more_credit():
    old_trace, _ = eligibility_trace(
        weight=1.0,
        activity_history=[
            1.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
        ],
    )

    recent_trace, _ = eligibility_trace(
        weight=1.0,
        activity_history=[
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            1.0,
        ],
    )

    assert recent_trace > old_trace


def test_larger_contribution_gets_more_credit():
    lower = score_edge(
        presynaptic=1,
        postsynaptic=2,
        weight=1.0,
        activity_history=[1.0],
    )

    higher = score_edge(
        presynaptic=3,
        postsynaptic=4,
        weight=2.0,
        activity_history=[1.0],
    )

    assert (
        higher.eligibility_trace
        > lower.eligibility_trace
    )


def test_no_eligible_pathway():
    edge = score_edge(
        presynaptic=1,
        postsynaptic=2,
        weight=1.0,
        activity_history=[0.0] * 10,
    )

    result = classify_credit([edge])

    assert (
        result.status
        == "NO_ELIGIBLE_PATHWAY"
    )

    assert result.leaders == ()


def test_exact_tie_remains_ambiguous():
    first = score_edge(
        presynaptic=1,
        postsynaptic=2,
        weight=1.0,
        activity_history=[1.0],
    )

    second = score_edge(
        presynaptic=3,
        postsynaptic=4,
        weight=1.0,
        activity_history=[1.0],
    )

    result = classify_credit(
        [first, second]
    )

    assert (
        result.status
        == "AMBIGUOUS_CREDIT"
    )

    assert len(result.leaders) == 2


def test_unique_highest_edge_is_eligible():
    first = score_edge(
        presynaptic=1,
        postsynaptic=2,
        weight=1.0,
        activity_history=[1.0],
    )

    second = score_edge(
        presynaptic=3,
        postsynaptic=4,
        weight=2.0,
        activity_history=[1.0],
    )

    result = classify_credit(
        [first, second]
    )

    assert result.status == "ELIGIBLE"

    assert len(result.leaders) == 1

    assert (
        result.leaders[0].presynaptic
        == 3
    )
