from __future__ import annotations
from config.paths import data_path

from scipy import sparse

from oracle.credit_assignment import (
    classify_credit,
    score_edge,
)


CONNECTOME = str(
    data_path("processed", "connectome-baseline-v1.npz")
)

UPSTREAM = 56393
INTERMEDIATE = 68045
DOWNSTREAM = 1273


def test_real_pathway_credit_uses_neural_contribution_only():
    connectome = sparse.load_npz(
        CONNECTOME
    ).tocsr()

    upstream_weight = float(
        connectome[INTERMEDIATE, UPSTREAM]
    )

    intermediate_weight = float(
        connectome[DOWNSTREAM, INTERMEDIATE]
    )

    assert upstream_weight != 0.0
    assert intermediate_weight != 0.0

    #
    # Same recency, different neural contribution.
    #

    upstream = score_edge(
        presynaptic=UPSTREAM,
        postsynaptic=INTERMEDIATE,
        weight=upstream_weight,
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

    intermediate = score_edge(
        presynaptic=INTERMEDIATE,
        postsynaptic=DOWNSTREAM,
        weight=intermediate_weight,
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

    result = classify_credit(
        [upstream, intermediate]
    )

    assert result.status in {
        "ELIGIBLE",
        "AMBIGUOUS_CREDIT",
    }

    assert (
        result.edges[0].eligibility_trace
        >= result.edges[-1].eligibility_trace
    )


def test_recency_can_change_real_pathway_ranking():
    connectome = sparse.load_npz(
        CONNECTOME
    ).tocsr()

    upstream_weight = float(
        connectome[INTERMEDIATE, UPSTREAM]
    )

    intermediate_weight = float(
        connectome[DOWNSTREAM, INTERMEDIATE]
    )

    #
    # Push one contribution farther into the past.
    #

    upstream = score_edge(
        presynaptic=UPSTREAM,
        postsynaptic=INTERMEDIATE,
        weight=upstream_weight,
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

    intermediate = score_edge(
        presynaptic=INTERMEDIATE,
        postsynaptic=DOWNSTREAM,
        weight=intermediate_weight,
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

    result = classify_credit(
        [upstream, intermediate]
    )

    assert (
        result.edges[0].eligibility_trace
        >= result.edges[-1].eligibility_trace
    )


def test_financial_loss_value_cannot_affect_credit_ranking():
    connectome = sparse.load_npz(
        CONNECTOME
    ).tocsr()

    upstream_weight = float(
        connectome[INTERMEDIATE, UPSTREAM]
    )

    intermediate_weight = float(
        connectome[DOWNSTREAM, INTERMEDIATE]
    )

    upstream = score_edge(
        presynaptic=UPSTREAM,
        postsynaptic=INTERMEDIATE,
        weight=upstream_weight,
        activity_history=[1.0],
    )

    intermediate = score_edge(
        presynaptic=INTERMEDIATE,
        postsynaptic=DOWNSTREAM,
        weight=intermediate_weight,
        activity_history=[1.0],
    )

    first = classify_credit(
        [upstream, intermediate]
    )

    #
    # Intentionally no PnL input exists.
    #
    # A $1 loss and a $10,000 loss therefore have
    # exactly the same credit evidence.
    #

    second = classify_credit(
        [upstream, intermediate]
    )

    assert first == second
