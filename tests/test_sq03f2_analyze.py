from brain.sq03f2_analyze import (
    focal_source_features,
    summarize_feature_pairs,
)


def test_leave_one_edge_out_math_and_rank():
    profiles = {
        "A": {
            "source_out_edge_count": 3,
            "source_out_strength": 60.0,
            "source_median_outgoing_weight": 20.0,
            "source_max_outgoing_weight": 30.0,
            "source_top1_output_share": 0.5,
            "source_top5_output_share": 1.0,
            "source_output_hhi": (10/60)**2 + (20/60)**2 + (30/60)**2,
            "_weights": __import__("numpy").array([10.0, 20.0, 30.0]),
            "_edge_ids": [1, 2, 3],
        }
    }
    row = {"pre": "A", "edge_id": 2, "mean_weight": 20.0}
    got = focal_source_features(row, profiles)
    assert got["leave_one_edge_out_source_strength"] == 40.0
    assert got["leave_one_edge_out_mean_outgoing_weight"] == 20.0
    assert got["focal_edge_output_rank_percentile"] == 2 / 3


def test_single_edge_source_has_null_loo_mean():
    import numpy as np
    profiles = {
        "A": {
            "source_out_edge_count": 1,
            "source_out_strength": 10.0,
            "source_median_outgoing_weight": 10.0,
            "source_max_outgoing_weight": 10.0,
            "source_top1_output_share": 1.0,
            "source_top5_output_share": 1.0,
            "source_output_hhi": 1.0,
            "_weights": np.array([10.0]),
            "_edge_ids": [1],
        }
    }
    row = {"pre": "A", "edge_id": 1, "mean_weight": 10.0}
    got = focal_source_features(row, profiles)
    assert got["leave_one_edge_out_source_strength"] == 0.0
    assert got["leave_one_edge_out_mean_outgoing_weight"] is None


def test_summary_records_null_pairs():
    pairs = [
        {
            "hotspot": {"capo_features": {"x": 5.0}},
            "control": {"capo_features": {"x": 2.0}},
        },
        {
            "hotspot": {"capo_features": {"x": None}},
            "control": {"capo_features": {"x": 3.0}},
        },
    ]
    got = summarize_feature_pairs(pairs, "x")
    assert got["valid_pair_count"] == 1
    assert got["null_pair_count"] == 1
    assert got["median_paired_difference"] == 3.0
    assert got["fraction_hotspot_gt_control"] == 1.0
