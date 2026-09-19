from brain.mq7_18_pairwise_route_interaction import independent_residual_expectation
from brain import mq7_17_cumulative_first_wave_mediation as base
import itertools


def test_pair_count_is_45():
    assert len(list(itertools.combinations(base.CUMULATIVE_ORDER, 2))) == 45


def test_independent_residual_expectation():
    assert independent_residual_expectation(0.5, 0.5) == 0.75
    assert independent_residual_expectation(0.0, 0.0) == 0.0
    assert independent_residual_expectation(1.0, 0.2) == 1.0


def test_frozen_candidate_set():
    assert len(base.CUMULATIVE_ORDER) == 10
    assert base.NULL_CONTROL not in base.CUMULATIVE_ORDER
