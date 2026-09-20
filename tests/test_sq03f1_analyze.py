from brain.sq03f1_analyze import (
    exact_context_match_controls,
    summarize_feature_pairs,
)


def test_exact_context_count_required():
    hotspot = {
        "edge_id": 1,
        "context_count": 6,
        "total_weight": 100.0,
        "abs_weight_difference": 20.0,
        "total_weight_decile": 3,
        "abs_weight_difference_decile": 7,
        "score": 10.0,
    }
    wrong_context = {
        "edge_id": 2,
        "context_count": 3,
        "total_weight": 100.0,
        "abs_weight_difference": 20.0,
        "total_weight_decile": 3,
        "abs_weight_difference_decile": 7,
        "score": 0.0,
    }
    pairs, unmatched = exact_context_match_controls(
        [hotspot, wrong_context], [hotspot], "score"
    )
    assert pairs == []
    assert len(unmatched) == 1


def test_exact_three_way_match_selects_valid_control():
    hotspot = {
        "edge_id": 1,
        "context_count": 6,
        "total_weight": 100.0,
        "abs_weight_difference": 20.0,
        "total_weight_decile": 3,
        "abs_weight_difference_decile": 7,
        "score": 10.0,
    }
    control = {
        "edge_id": 2,
        "context_count": 6,
        "total_weight": 99.0,
        "abs_weight_difference": 19.0,
        "total_weight_decile": 3,
        "abs_weight_difference_decile": 7,
        "score": 0.0,
    }
    pairs, unmatched = exact_context_match_controls(
        [hotspot, control], [hotspot], "score"
    )
    assert not unmatched
    assert pairs[0]["control"]["edge_id"] == 2


def test_feature_summary():
    pairs = [
        {"hotspot": {"features": {"x": 5}}, "control": {"features": {"x": 2}}},
        {"hotspot": {"features": {"x": 1}}, "control": {"features": {"x": 3}}},
    ]
    got = summarize_feature_pairs(pairs, "x")
    assert got["hotspot_median"] == 3.0
    assert got["control_median"] == 2.5
    assert got["fraction_hotspot_gt_control"] == 0.5
