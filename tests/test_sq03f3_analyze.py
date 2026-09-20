from brain.sq03f3_analyze import (
    observed_metrics,
    hotspot_counts_by_stratum,
)


def test_observed_recurrence_metrics():
    rows = [
        {"edge_id": 1, "pre": "A"},
        {"edge_id": 2, "pre": "A"},
        {"edge_id": 3, "pre": "B"},
    ]
    contexts = {
        1: {("x", "a")},
        2: {("y", "a")},
        3: {("x", "a")},
    }
    got = observed_metrics(rows, contexts)
    assert got["unique_hotspot_source_count"] == 2
    assert got["fraction_hotspot_edges_repeated_source"] == 2 / 3
    assert got["max_hotspot_edges_one_source"] == 2
    assert got["sources_with_2plus_context_signatures"] == 1


def test_stratum_hotspot_counts():
    rows = [
        {
            "context_count": 2,
            "total_weight_decile": 1,
            "abs_weight_difference_decile": 3,
        },
        {
            "context_count": 2,
            "total_weight_decile": 1,
            "abs_weight_difference_decile": 3,
        },
        {
            "context_count": 4,
            "total_weight_decile": 2,
            "abs_weight_difference_decile": 5,
        },
    ]
    got = hotspot_counts_by_stratum(rows)
    assert got[(2, 1, 3)] == 2
    assert got[(4, 2, 5)] == 1
