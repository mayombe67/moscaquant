from __future__ import annotations

from collections import defaultdict, deque
from pathlib import Path
import hashlib
import json

import pyarrow.feather as feather


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_matched_edges(feather_path: Path):
    table = feather.read_table(
        feather_path,
        columns=["pre", "post", "weight_m", "weight_f", "verdict_corr"],
    )

    pre = table["pre"].combine_chunks().to_pylist()
    post = table["post"].combine_chunks().to_pylist()
    wm = table["weight_m"].combine_chunks().to_pylist()
    wf = table["weight_f"].combine_chunks().to_pylist()
    verdict = table["verdict_corr"].combine_chunks().to_pylist()

    edges = []
    out_adj = defaultdict(list)
    rev_adj = defaultdict(list)

    for a, b, m, f, v in zip(pre, post, wm, wf, verdict):
        if a is None or b is None:
            continue
        if v != "isomorphic" or m <= 0 or f <= 0:
            continue

        a = str(a)
        b = str(b)
        m = int(m)
        f = int(f)

        idx = len(edges)
        edges.append({
            "pre": a,
            "post": b,
            "weight_m": m,
            "weight_f": f,
            "weight_delta_f_minus_m": f - m,
        })
        out_adj[a].append((b, idx))
        rev_adj[b].append((a, idx))

    return edges, out_adj, rev_adj


def reverse_distances(anchor: str, rev_adj, max_hops: int) -> dict[str, int]:
    dist = {anchor: 0}
    q = deque([anchor])

    while q:
        node = q.popleft()
        d = dist[node]
        if d >= max_hops:
            continue
        for prev, _ in rev_adj.get(node, []):
            if prev not in dist:
                dist[prev] = d + 1
                q.append(prev)

    return dist


def collect_simple_path_edges(
    source: str,
    anchor: str,
    edges,
    out_adj,
    rev_dist,
    max_hops: int,
) -> set[int]:
    """
    Exact bounded simple-path enumeration with reverse-distance pruning.

    Only branches that can still reach the requested anchor within the
    remaining hop budget are explored. Candidate edge IDs are recorded only
    when an actual simple source->anchor path is completed.
    """
    candidate_ids = set()
    path_nodes = {source}
    path_edge_ids = []

    def dfs(node: str, depth: int):
        if node == anchor:
            candidate_ids.update(path_edge_ids)
            return

        if depth >= max_hops:
            return

        remaining_after_next = max_hops - (depth + 1)

        for nxt, edge_id in out_adj.get(node, []):
            if nxt in path_nodes:
                continue

            d = rev_dist.get(nxt)
            if d is None or d > remaining_after_next:
                continue

            path_nodes.add(nxt)
            path_edge_ids.append(edge_id)
            dfs(nxt, depth + 1)
            path_edge_ids.pop()
            path_nodes.remove(nxt)

    dfs(source, 0)
    return candidate_ids


def freeze_candidate_set(
    feather_path: Path,
    inputs: list[str],
    anchors: list[str],
    max_hops: int,
) -> dict:
    edges, out_adj, rev_adj = load_matched_edges(feather_path)

    missing_inputs = [x for x in inputs if x not in out_adj and x not in rev_adj]
    missing_anchors = [x for x in anchors if x not in out_adj and x not in rev_adj]
    if missing_inputs or missing_anchors:
        raise RuntimeError(
            f"Frozen label missing: inputs={missing_inputs} anchors={missing_anchors}"
        )

    anchor_dist = {
        anchor: reverse_distances(anchor, rev_adj, max_hops)
        for anchor in anchors
    }

    pair_records = []
    union_ids = set()

    for source in inputs:
        for anchor in anchors:
            ids = collect_simple_path_edges(
                source=source,
                anchor=anchor,
                edges=edges,
                out_adj=out_adj,
                rev_dist=anchor_dist[anchor],
                max_hops=max_hops,
            )

            differing = {
                i for i in ids
                if edges[i]["weight_m"] != edges[i]["weight_f"]
            }
            union_ids.update(differing)

            pair_records.append({
                "input": source,
                "anchor": anchor,
                "simple_path_edge_count": len(ids),
                "weight_differing_candidate_edge_count": len(differing),
                "candidate_edge_ids": sorted(differing),
            })

    candidate_edges = []
    for edge_id in sorted(union_ids):
        row = dict(edges[edge_id])
        row["edge_id"] = edge_id

        memberships = []
        for pair in pair_records:
            if edge_id in pair["candidate_edge_ids"]:
                memberships.append({
                    "input": pair["input"],
                    "anchor": pair["anchor"],
                })

        row["memberships"] = memberships
        candidate_edges.append(row)

    return {
        "matched_edge_count": len(edges),
        "candidate_edge_count": len(candidate_edges),
        "candidate_edges": candidate_edges,
        "pair_records": pair_records,
    }
