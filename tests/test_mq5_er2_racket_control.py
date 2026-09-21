from brain.mq5_er2_racket_control import (
    FOCUSED_EDGE,
    MATCH_TARGETS,
    MAX_HOPS,
    _score_match,
)


def test_control_selector_contract_is_frozen():
    assert FOCUSED_EDGE == (116680, 12024)
    assert MATCH_TARGETS == (92, 656, 137122, 1273)
    assert MAX_HOPS == 3


def test_balanced_distance_penalizes_single_large_degree_mismatch():
    balanced = _score_match(
        candidate_weight=0.02,
        focused_weight=0.01,
        candidate_pre_out=12,
        focused_pre_out=10,
        candidate_post_in=22,
        focused_post_in=20,
    )
    extreme_degree = _score_match(
        candidate_weight=0.010001,
        focused_weight=0.01,
        candidate_pre_out=280,
        focused_pre_out=10,
        candidate_post_in=100,
        focused_post_in=20,
    )

    balanced_key = (
        balanced["max_distance"],
        balanced["sum_distance"],
        balanced["log10_abs_weight"],
        balanced["log1p_pre_outdegree"],
        balanced["log1p_post_indegree"],
    )
    extreme_key = (
        extreme_degree["max_distance"],
        extreme_degree["sum_distance"],
        extreme_degree["log10_abs_weight"],
        extreme_degree["log1p_pre_outdegree"],
        extreme_degree["log1p_post_indegree"],
    )

    assert balanced_key < extreme_key
