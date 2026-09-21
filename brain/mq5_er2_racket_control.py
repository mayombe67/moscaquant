from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

from brain.mq5_er1_detour_runner import load_inputs

FOCUSED_EDGE = (116680, 12024)
MATCH_TARGETS = (92, 656, 137122, 1273)
MAX_HOPS = 3
DETOUR_RESULT = Path("/home/wil/moscaquant-data/experiments/mq5-er1-detour-v1.json")


def _reverse_node_distances(connectome, target: int, max_hops: int = MAX_HOPS) -> np.ndarray:
    """Minimum backward node distance to target, following presynaptic ancestry."""
    n = int(connectome.shape[0])
    dist = np.full(n, -1, dtype=np.int16)
    dist[int(target)] = 0
    frontier = np.asarray([int(target)], dtype=np.int64)

    for depth in range(1, max_hops + 1):
        if frontier.size == 0:
            break

        chunks = []
        for post in frontier:
            start = int(connectome.indptr[int(post)])
            end = int(connectome.indptr[int(post) + 1])
            if end > start:
                chunks.append(connectome.indices[start:end])

        if not chunks:
            break

        pres = np.unique(np.concatenate(chunks))
        pres = pres[dist[pres] < 0]
        if pres.size == 0:
            frontier = pres
            continue

        dist[pres] = depth
        frontier = pres

    return dist


def _edge_hop_signature(connectome, pre: int, post: int, targets=MATCH_TARGETS) -> tuple[int, ...]:
    sig = []
    for target in targets:
        dist = _reverse_node_distances(connectome, int(target), MAX_HOPS)
        post_dist = int(dist[int(post)])
        hop = post_dist + 1 if 0 <= post_dist < MAX_HOPS else -1
        sig.append(hop)
    return tuple(sig)


def _degrees(connectome) -> tuple[np.ndarray, np.ndarray]:
    # Matrix convention: row=postsynaptic, column=presynaptic.
    indegree = np.diff(connectome.indptr).astype(np.int64, copy=False)
    csc = connectome.tocsc()
    outdegree = np.diff(csc.indptr).astype(np.int64, copy=False)
    return indegree, outdegree


def _load_detour_exclusions(path: Path = DETOUR_RESULT) -> set[tuple[int, int]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    excluded = set()
    for target_row in data["targets"].values():
        for row in target_row["top_candidates"]:
            excluded.add((int(row["presynaptic"]), int(row["postsynaptic"])))
    return excluded


def _edge_weight(connectome, pre: int, post: int) -> float:
    return float(connectome[int(post), int(pre)])


def _score_match(
    *,
    candidate_weight: float,
    focused_weight: float,
    candidate_pre_out: int,
    focused_pre_out: int,
    candidate_post_in: int,
    focused_post_in: int,
) -> tuple[float, float, float]:
    eps = 1e-30
    weight_distance = abs(
        math.log10(abs(candidate_weight) + eps) - math.log10(abs(focused_weight) + eps)
    )
    pre_out_distance = abs(
        math.log1p(candidate_pre_out) - math.log1p(focused_pre_out)
    )
    post_in_distance = abs(
        math.log1p(candidate_post_in) - math.log1p(focused_post_in)
    )
    return (weight_distance, pre_out_distance, post_in_distance)


def select_control() -> dict:
    original, _lesioned, _retina, _responders, _causal_edges = load_inputs()
    original = original.tocsr()
    original.sort_indices()

    focused_pre, focused_post = FOCUSED_EDGE
    focused_weight = _edge_weight(original, focused_pre, focused_post)
    if focused_weight == 0.0:
        raise RuntimeError("focused edge is absent from the frozen connectome")

    focused_signature = _edge_hop_signature(
        original, focused_pre, focused_post, MATCH_TARGETS
    )

    # Freeze the structural rule to the exact signature actually occupied by the
    # focused edge across the three primary targets plus key comparison 1273.
    if focused_signature != (3, 3, 3, 3):
        raise RuntimeError(
            f"unexpected focused-edge hop signature: {focused_signature!r}"
        )

    excluded = _load_detour_exclusions()
    excluded.add(FOCUSED_EDGE)

    indegree, outdegree = _degrees(original)
    focused_pre_out = int(outdegree[focused_pre])
    focused_post_in = int(indegree[focused_post])
    focused_sign = 1 if focused_weight > 0 else -1

    # Cache node-distance arrays once per target.
    dists = {
        int(target): _reverse_node_distances(original, int(target), MAX_HOPS)
        for target in MATCH_TARGETS
    }

    best = None

    for post in range(original.shape[0]):
        signature = tuple(
            int(dists[target][post]) + 1
            if 0 <= int(dists[target][post]) < MAX_HOPS
            else -1
            for target in MATCH_TARGETS
        )
        if signature != focused_signature:
            continue

        start = int(original.indptr[post])
        end = int(original.indptr[post + 1])

        for idx in range(start, end):
            pre = int(original.indices[idx])
            weight = float(original.data[idx])
            edge = (pre, post)

            if edge in excluded:
                continue
            if weight == 0.0:
                continue
            if (1 if weight > 0 else -1) != focused_sign:
                continue

            distances = _score_match(
                candidate_weight=weight,
                focused_weight=focused_weight,
                candidate_pre_out=int(outdegree[pre]),
                focused_pre_out=focused_pre_out,
                candidate_post_in=int(indegree[post]),
                focused_post_in=focused_post_in,
            )

            # Lexicographic structural match:
            # 1) nearest log absolute weight
            # 2) nearest log presynaptic outdegree
            # 3) nearest log postsynaptic indegree
            # 4) deterministic edge-id tie break
            key = (*distances, post, pre)

            if best is None or key < best["key"]:
                best = {
                    "key": key,
                    "pre": pre,
                    "post": post,
                    "weight": weight,
                    "signature": signature,
                    "pre_outdegree": int(outdegree[pre]),
                    "post_indegree": int(indegree[post]),
                    "weight_distance": distances[0],
                    "pre_outdegree_distance": distances[1],
                    "post_indegree_distance": distances[2],
                }

    if best is None:
        raise RuntimeError("no eligible topology-matched control edge found")

    return {
        "selector": "mq5-er2-the-racket-control-v1",
        "kind": "PRE-OUTCOME STRUCTURAL CONTROL SELECTION",
        "confirmatory_outcomes_used": False,
        "focused_edge": {
            "presynaptic": focused_pre,
            "postsynaptic": focused_post,
            "weight": focused_weight,
            "hop_signature_targets": list(MATCH_TARGETS),
            "hop_signature": list(focused_signature),
            "pre_outdegree": focused_pre_out,
            "post_indegree": focused_post_in,
        },
        "control_edge": {
            "presynaptic": best["pre"],
            "postsynaptic": best["post"],
            "weight": best["weight"],
            "hop_signature": list(best["signature"]),
            "pre_outdegree": best["pre_outdegree"],
            "post_indegree": best["post_indegree"],
        },
        "matching_distances": {
            "log10_abs_weight": best["weight_distance"],
            "log1p_pre_outdegree": best["pre_outdegree_distance"],
            "log1p_post_indegree": best["post_indegree_distance"],
        },
        "exclusions": {
            "focused_edge": True,
            "all_detour_top5_edges": True,
            "opposite_sign_edges": True,
        },
        "tie_break": [
            "minimum log10 absolute-weight distance",
            "minimum log1p presynaptic-outdegree distance",
            "minimum log1p postsynaptic-indegree distance",
            "lower postsynaptic id",
            "lower presynaptic id",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--select", action="store_true", required=True)
    args = parser.parse_args()
    _ = args

    print(json.dumps(select_control(), indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
