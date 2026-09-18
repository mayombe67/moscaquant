from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Sequence


CREDIT_VERSION = "mq7-credit-assignment/v1"
LOOKBACK_TRANSITIONS = 10
RECENCY_HALF_LIFE = 5.0


class CreditAssignmentError(ValueError):
    pass


@dataclass(frozen=True)
class EdgeCredit:
    presynaptic: int
    postsynaptic: int
    weight: float
    eligibility_trace: float
    contributing_transitions: int


@dataclass(frozen=True)
class CreditResult:
    status: str
    edges: tuple[EdgeCredit, ...]
    leaders: tuple[EdgeCredit, ...]


def recency_weight(age: int) -> float:
    if age < 0:
        raise CreditAssignmentError(
            "age must be non-negative"
        )

    return 0.5 ** (
        float(age) / RECENCY_HALF_LIFE
    )


def contribution_score(
    *,
    weight: float,
    presynaptic_effective_activity: float,
) -> float:
    return abs(
        float(weight)
        * float(presynaptic_effective_activity)
    )


def eligibility_trace(
    *,
    weight: float,
    activity_history: Sequence[float],
) -> tuple[float, int]:
    history = tuple(
        float(x)
        for x in activity_history
    )

    if len(history) > LOOKBACK_TRANSITIONS:
        history = history[
            -LOOKBACK_TRANSITIONS:
        ]

    total = 0.0
    contributing = 0

    # newest observation has age 0
    for age, activity in enumerate(
        reversed(history)
    ):
        score = contribution_score(
            weight=weight,
            presynaptic_effective_activity=activity,
        )

        if score > 0.0:
            contributing += 1

        total += (
            score
            * recency_weight(age)
        )

    return total, contributing


def score_edge(
    *,
    presynaptic: int,
    postsynaptic: int,
    weight: float,
    activity_history: Sequence[float],
) -> EdgeCredit:
    trace, contributing = eligibility_trace(
        weight=weight,
        activity_history=activity_history,
    )

    return EdgeCredit(
        presynaptic=presynaptic,
        postsynaptic=postsynaptic,
        weight=float(weight),
        eligibility_trace=trace,
        contributing_transitions=contributing,
    )


def classify_credit(
    edges: Sequence[EdgeCredit],
) -> CreditResult:
    eligible = tuple(
        edge
        for edge in edges
        if edge.eligibility_trace > 0.0
    )

    if not eligible:
        return CreditResult(
            status="NO_ELIGIBLE_PATHWAY",
            edges=tuple(edges),
            leaders=(),
        )

    highest = max(
        edge.eligibility_trace
        for edge in eligible
    )

    leaders = tuple(
        edge
        for edge in eligible
        if math.isclose(
            edge.eligibility_trace,
            highest,
            rel_tol=0.0,
            abs_tol=0.0,
        )
    )

    if len(leaders) > 1:
        status = "AMBIGUOUS_CREDIT"
    else:
        status = "ELIGIBLE"

    ranked = tuple(
        sorted(
            eligible,
            key=lambda edge: (
                -edge.eligibility_trace,
                edge.presynaptic,
                edge.postsynaptic,
            ),
        )
    )

    return CreditResult(
        status=status,
        edges=ranked,
        leaders=leaders,
    )
