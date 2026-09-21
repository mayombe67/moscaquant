from __future__ import annotations

from brain.mq5_ts_harness import (
    EXPECTED_B_SEEDS,
    EXPECTED_C_SEEDS,
    EXPECTED_CAUSAL_EDGE_COUNT,
    EXPECTED_RESPONDER_COUNT,
    expected_seed_plan,
)


def test_frozen_seed_plan_is_exact():
    plan = expected_seed_plan()

    assert plan["A"] == [None]
    assert plan["D"] == [None]
    assert tuple(plan["B"]) == EXPECTED_B_SEEDS
    assert tuple(plan["C"]) == EXPECTED_C_SEEDS
    assert len(plan["B"]) == 20
    assert len(plan["C"]) == 20
    assert set(plan["B"]).isdisjoint(plan["C"])


def test_frozen_contract_counts():
    assert EXPECTED_RESPONDER_COUNT == 9
    assert EXPECTED_CAUSAL_EDGE_COUNT == 13
