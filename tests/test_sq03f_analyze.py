from brain.sq03f_analyze import (
    assign_equal_count_deciles,
    match_controls,
    summarize_feature_pairs,
)


def test_equal_count_deciles_deterministic_ties():
    rows = [{"edge_id": i, "v": 1.0} for i in range(20)]
    got = assign_equal_count_deciles(rows, lambda r: r["v"])
    assert got[0] == 1
    assert got[1] == 1
    assert got[18] == 10
    assert got[19] == 10


def test_matching_stays_in_exact_structural_bin():
    def row(edge_id, tw, dw, score=0.0):
        return {
            "edge_id": edge_id,
            "total_weight": tw,
            "abs_weight_difference": dw,
            "total_weight_decile": 3,
            "abs_weight_difference_decile": 7,
            "score": score,
        }

    hotspot = row(1, 100.0, 20.0, 9.0)
    c1 = row(2, 99.0, 19.0)
    c2 = row(3, 80.0, 18.0)

    pairs, unmatched = match_controls(
        [hotspot, c1, c2], [hotspot], "score"
    )
    assert not unmatched
    assert pairs[0]["control"]["edge_id"] == 2


def test_matching_does_not_widen_bins():
    hotspot = {
        "edge_id": 1,
        "total_weight": 10.0,
        "abs_weight_difference": 2.0,
        "total_weight_decile": 1,
        "abs_weight_difference_decile": 1,
        "score": 5.0,
    }
    control = {
        "edge_id": 2,
        "total_weight": 10.0,
        "abs_weight_difference": 2.0,
        "total_weight_decile": 2,
        "abs_weight_difference_decile": 1,
        "score": 0.0,
    }
    pairs, unmatched = match_controls(
        [hotspot, control], [hotspot], "score"
    )
    assert pairs == []
    assert len(unmatched) == 1


def test_feature_summary_reports_direction_fraction():
    pairs = [
        {"hotspot": {"features": {"x": 3}}, "control": {"features": {"x": 1}}},
        {"hotspot": {"features": {"x": 2}}, "control": {"features": {"x": 4}}},
        {"hotspot": {"features": {"x": 5}}, "control": {"features": {"x": 2}}},
    ]
    got = summarize_feature_pairs(pairs, "x")
    assert got["hotspot_median"] == 3.0
    assert got["control_median"] == 2.0
    assert got["fraction_hotspot_gt_control"] == 2 / 3
