from brain.sq03f4_analyze import (
    equal_count_bins,
    made_sources,
    exact_match_controls,
)


def test_equal_count_bins_are_deterministic():
    rows = [
        {"source": "C", "x": 3},
        {"source": "A", "x": 1},
        {"source": "B", "x": 2},
        {"source": "D", "x": 4},
    ]
    got = equal_count_bins(rows, "x", bins=2)
    assert got["A"] == 1
    assert got["B"] == 1
    assert got["C"] == 2
    assert got["D"] == 2


def test_made_sources_exact_top_one_percent_with_label_tie_break():
    candidate = [f"S{i:03d}" for i in range(100)]
    hot = [
        {"pre": "S003"},
        {"pre": "S003"},
        {"pre": "S002"},
        {"pre": "S002"},
        {"pre": "S001"},
    ]
    made, counts, k = made_sources(candidate, hot)
    assert k == 1
    assert made == ["S002"]
    assert counts["S003"] == 2


def test_exact_match_controls_respects_bins_and_tiebreak():
    opportunities = {
        "M": {
            "candidate_edge_count": 10,
            "sum_candidate_context_count": 20,
            "distinct_candidate_context_signature_count": 4,
            "candidate_edge_count_decile": 2,
            "sum_candidate_context_count_decile": 3,
            "distinct_candidate_context_signature_count_decile": 4,
        },
        "A": {
            "candidate_edge_count": 9,
            "sum_candidate_context_count": 19,
            "distinct_candidate_context_signature_count": 4,
            "candidate_edge_count_decile": 2,
            "sum_candidate_context_count_decile": 3,
            "distinct_candidate_context_signature_count_decile": 4,
        },
        "B": {
            "candidate_edge_count": 11,
            "sum_candidate_context_count": 21,
            "distinct_candidate_context_signature_count": 4,
            "candidate_edge_count_decile": 2,
            "sum_candidate_context_count_decile": 3,
            "distinct_candidate_context_signature_count_decile": 4,
        },
    }
    pairs, unmatched = exact_match_controls(["M"], opportunities, {"M": 7})
    assert pairs == [("M", "A")]
    assert unmatched == []
