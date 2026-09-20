import math

from brain.sq03e_analyze import (
    average_ranks,
    exact_top_k,
    overlap_summary,
    spearman_no_p,
)


def test_average_ranks_uses_average_for_ties():
    got = average_ranks([10.0, 10.0, 20.0])
    assert list(got) == [1.5, 1.5, 3.0]


def test_spearman_perfect_monotonic_positive():
    rho, n = spearman_no_p([1, 2, 3, 4], [10, 20, 30, 40])
    assert n == 4
    assert math.isclose(rho, 1.0)


def test_spearman_constant_vector_returns_null():
    rho, n = spearman_no_p([1, 1, 1], [2, 3, 4])
    assert n == 3
    assert rho is None


def test_exact_top_k_uses_ceil_and_edge_id_tiebreak():
    rows = [
        {"edge_id": 2, "v": 10.0},
        {"edge_id": 1, "v": 10.0},
        {"edge_id": 3, "v": 9.0},
        {"edge_id": 4, "v": 8.0},
    ]
    got = exact_top_k(rows, lambda r: r["v"], 0.5)
    assert [r["edge_id"] for r in got] == [1, 2]


def test_overlap_summary_jaccard():
    a = [{"edge_id": 1}, {"edge_id": 2}]
    b = [{"edge_id": 2}, {"edge_id": 3}]
    got = overlap_summary(a, b)
    assert got["overlap_count"] == 1
    assert math.isclose(got["jaccard"], 1 / 3)


def test_analyzer_uses_conservative_matched_indexing():
    from pathlib import Path
    import brain.sq03e_analyze as mod

    text = Path(mod.__file__).read_text()
    assert '(aligned["verdict_corr"] == "isomorphic")' in text
    assert '(aligned["weight_m"] > 0)' in text
    assert '(aligned["weight_f"] > 0)' in text
    assert 'matched["original_feather_row"]' in text
    assert 'a = matched.iloc[edge_id]' in text
