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


def test_structural_match_distance_prefers_closer_weight_first():
    exact = _score_match(
        candidate_weight=0.01,
        focused_weight=0.01,
        candidate_pre_out=10,
        focused_pre_out=10,
        candidate_post_in=20,
        focused_post_in=20,
    )
    farther = _score_match(
        candidate_weight=0.02,
        focused_weight=0.01,
        candidate_pre_out=10,
        focused_pre_out=10,
        candidate_post_in=20,
        focused_post_in=20,
    )
    assert exact < farther
