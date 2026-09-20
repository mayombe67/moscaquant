from collections import defaultdict

from brain.sq03b_candidate_freezer import collect_simple_path_edges


def make_graph(edge_pairs):
    edges = []
    out_adj = defaultdict(list)
    rev_adj = defaultdict(list)

    for a, b in edge_pairs:
        idx = len(edges)
        edges.append({
            "pre": a,
            "post": b,
            "weight_m": 1,
            "weight_f": 2,
        })
        out_adj[a].append((b, idx))
        rev_adj[b].append((a, idx))

    return edges, out_adj, rev_adj


def reverse_dist(anchor, rev_adj, max_hops):
    from brain.sq03b_candidate_freezer import reverse_distances
    return reverse_distances(anchor, rev_adj, max_hops)


def test_collects_edges_on_simple_path():
    edges, out_adj, rev_adj = make_graph([
        ("S", "A"),
        ("A", "T"),
        ("S", "X"),
        ("X", "Y"),
    ])
    ids = collect_simple_path_edges(
        "S", "T", edges, out_adj, reverse_dist("T", rev_adj, 4), 4
    )
    assert ids == {0, 1}


def test_respects_max_hops():
    edges, out_adj, rev_adj = make_graph([
        ("S", "A"),
        ("A", "B"),
        ("B", "C"),
        ("C", "D"),
        ("D", "T"),
    ])
    ids = collect_simple_path_edges(
        "S", "T", edges, out_adj, reverse_dist("T", rev_adj, 4), 4
    )
    assert ids == set()


def test_cycle_does_not_create_non_simple_candidate():
    edges, out_adj, rev_adj = make_graph([
        ("S", "A"),
        ("A", "B"),
        ("B", "A"),
        ("B", "T"),
    ])
    ids = collect_simple_path_edges(
        "S", "T", edges, out_adj, reverse_dist("T", rev_adj, 4), 4
    )
    # Valid simple path is S-A-B-T; reverse B-A must not be included.
    assert ids == {0, 1, 3}


def test_direct_edge_is_included():
    edges, out_adj, rev_adj = make_graph([("S", "T")])
    ids = collect_simple_path_edges(
        "S", "T", edges, out_adj, reverse_dist("T", rev_adj, 4), 4
    )
    assert ids == {0}
