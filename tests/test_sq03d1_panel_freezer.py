from brain.sq03d1_panel_freezer import (
    allocate_stratified,
    low_sort_key,
    pair_metrics,
    upper_sort_key,
)


def make_row(input_label, edge_id, c_int, s_int, c_peak):
    # Construct precomputed row shape used by allocator.
    return {
        "input": input_label,
        "edge_id": edge_id,
        "anchor": "DN",
        "pre": f"P{edge_id}",
        "post": f"Q{edge_id}",
        "integrated": {
            "context_residual": c_int,
            "total_effect_magnitude": s_int,
            "normalized_asymmetry": 0.0,
            "delta_morty": 0.0,
            "delta_lilith": 0.0,
        },
        "peak": {
            "context_residual": c_peak,
            "total_effect_magnitude": c_peak,
            "normalized_asymmetry": 0.0,
            "delta_morty": 0.0,
            "delta_lilith": 0.0,
        },
    }


def test_pair_metrics_exact_reciprocity():
    got = pair_metrics(3.0, -3.0)
    assert got["context_residual"] == 0.0
    assert got["total_effect_magnitude"] == 6.0
    assert got["normalized_asymmetry"] == 0.0
    assert got["sign_relation"] == "OPPOSITE"


def test_upper_allocator_seeds_each_input_then_fills_globally():
    rows = []
    edge = 1
    for input_label, base in [("A", 100.0), ("B", 50.0), ("C", 10.0), ("D", 1.0)]:
        for offset in range(4):
            rows.append(make_row(input_label, edge, base - offset, base - offset, base - offset))
            edge += 1

    got = allocate_stratified(
        rows, total=10, minimum_per_input=2, sort_key=upper_sort_key
    )
    counts = {}
    for r in got:
        counts[r["input"]] = counts.get(r["input"], 0) + 1

    assert all(counts[x] >= 2 for x in ["A", "B", "C", "D"])
    assert len(got) == 10


def test_low_allocator_excludes_upper_keys():
    rows = [
        make_row("A", 1, 0.0, 0.0, 0.0),
        make_row("A", 2, 0.1, 0.1, 0.1),
        make_row("A", 3, 0.2, 0.2, 0.2),
        make_row("B", 4, 0.0, 0.0, 0.0),
        make_row("B", 5, 0.1, 0.1, 0.1),
        make_row("B", 6, 0.2, 0.2, 0.2),
    ]
    excluded = {("A", 1, "DN"), ("B", 4, "DN")}
    got = allocate_stratified(
        rows,
        total=4,
        minimum_per_input=2,
        sort_key=low_sort_key,
        excluded=excluded,
    )
    keys = {(r["input"], r["edge_id"], r["anchor"]) for r in got}
    assert not (keys & excluded)
    assert len(got) == 4


def test_upper_and_low_sort_keys_are_opposed_on_residual():
    a = make_row("A", 1, 10.0, 10.0, 10.0)
    b = make_row("A", 2, 1.0, 1.0, 1.0)
    assert sorted([a, b], key=upper_sort_key)[0]["edge_id"] == 1
    assert sorted([a, b], key=low_sort_key)[0]["edge_id"] == 2
