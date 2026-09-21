from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from scipy import sparse

from brain.mq5_er3_retour_eligibility import build_runtime_inputs
from brain.mq5_ts_runtime import frozen_edges


OUTPUT = Path("artifacts/mq5-er4-stevedores-matched-controls-v1.json")

CANDIDATES = (
    {
        "id": "S1",
        "presynaptic": 11725,
        "postsynaptic": 29921,
        "weight": -0.23459716141223907,
        "associated_targets": (55, 126002, 137122),
        "hop_signature": (3, 3, 3),
        "pre_outdegree": 17,
        "post_indegree": 88,
    },
    {
        "id": "S2",
        "presynaptic": 11345,
        "postsynaptic": 47350,
        "weight": -0.3401360511779785,
        "associated_targets": (92, 656, 126002),
        "hop_signature": (3, 2, 3),
        "pre_outdegree": 21,
        "post_indegree": 38,
    },
    {
        "id": "S3",
        "presynaptic": 10647,
        "postsynaptic": 51642,
        "weight": 0.35854342579841614,
        "associated_targets": (55, 92, 656),
        "hop_signature": (3, 2, 2),
        "pre_outdegree": 47,
        "post_indegree": 61,
    },
)

RTOL = 1e-6
ATOL = 1e-12


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def reverse_hop_array(
    graph: sparse.csr_matrix,
    target: int,
    max_hops: int = 3,
) -> np.ndarray:
    distances = np.full(graph.shape[0], -1, dtype=np.int8)
    seen = np.zeros(graph.shape[0], dtype=bool)
    frontier = np.asarray([int(target)], dtype=np.int32)
    seen[frontier] = True

    for hop in range(1, int(max_hops) + 1):
        if frontier.size == 0:
            break
        block = graph[frontier]
        pres = np.unique(block.indices.astype(np.int32, copy=False))
        if pres.size == 0:
            break
        new_pres = pres[~seen[pres]]
        distances[new_pres] = int(hop)
        seen[pres] = True
        frontier = new_pres

    return distances


def degree_arrays(graph: sparse.csr_matrix):
    indegree = np.diff(graph.indptr).astype(np.int64)
    outdegree = np.bincount(
        graph.indices,
        minlength=graph.shape[0],
    ).astype(np.int64)
    return indegree, outdegree


def log_distance(a: float, b: float) -> float:
    return abs(np.log10(float(a)) - np.log10(float(b)))


def build_edge_arrays(graph: sparse.csr_matrix):
    posts = np.repeat(
        np.arange(graph.shape[0], dtype=np.int32),
        np.diff(graph.indptr),
    )
    pres = graph.indices.astype(np.int32, copy=False)
    weights = graph.data.astype(np.float64, copy=False)
    return pres, posts, weights


def intervention_addressable_mask(
    *,
    pres: np.ndarray,
    posts: np.ndarray,
    runtime,
) -> np.ndarray:
    retina = np.zeros(runtime.connectome.shape[0], dtype=bool)
    relay = np.zeros(runtime.connectome.shape[0], dtype=bool)
    retina[np.asarray(runtime.retinal_indices, dtype=np.int32)] = True
    relay[np.asarray(runtime.relay_indices, dtype=np.int32)] = True

    # Under frozen RETOUR semantics, retina->relay ordinary edges are a
    # special interface whose connectome contribution is reconciled against
    # the frozen relay artifact. They are not eligible matched-control edges.
    return ~(retina[pres] & relay[posts])


def rank_key(
    *,
    weight: float,
    pre_degree: int,
    post_degree: int,
    candidate: dict,
    pre: int,
    post: int,
):
    d_weight = log_distance(abs(weight), abs(candidate["weight"]))
    d_pre = log_distance(int(pre_degree) + 1, int(candidate["pre_outdegree"]) + 1)
    d_post = log_distance(int(post_degree) + 1, int(candidate["post_indegree"]) + 1)

    return (
        max(d_weight, d_pre, d_post),
        d_weight + d_pre + d_post,
        d_weight,
        d_pre,
        d_post,
        int(post),
        int(pre),
    )


def choose_control(
    *,
    graph: sparse.csr_matrix,
    runtime,
    candidate: dict,
    hop_arrays: dict[int, np.ndarray],
    indegree: np.ndarray,
    outdegree: np.ndarray,
    pres: np.ndarray,
    posts: np.ndarray,
    weights: np.ndarray,
    addressable: np.ndarray,
    forbidden_edges: set[tuple[int, int]],
) -> dict:
    signature = tuple(int(x) for x in candidate["hop_signature"])
    targets = tuple(int(x) for x in candidate["associated_targets"])

    mask = addressable.copy()
    mask &= weights != 0.0

    for target, required_hop in zip(targets, signature):
        mask &= hop_arrays[target][pres] == int(required_hop)

    indices = np.flatnonzero(mask)

    best = None
    best_key = None

    for idx in indices.tolist():
        pre = int(pres[idx])
        post = int(posts[idx])
        edge = (pre, post)

        if edge in forbidden_edges:
            continue

        key = rank_key(
            weight=float(weights[idx]),
            pre_degree=int(outdegree[pre]),
            post_degree=int(indegree[post]),
            candidate=candidate,
            pre=pre,
            post=post,
        )

        if best_key is None or key < best_key:
            best_key = key
            best = {
                "presynaptic": pre,
                "postsynaptic": post,
                "weight": float(weights[idx]),
                "hop_signature": list(signature),
                "presynaptic_outdegree": int(outdegree[pre]),
                "postsynaptic_indegree": int(indegree[post]),
                "balance": {
                    "max_log_mismatch": float(key[0]),
                    "sum_log_mismatch": float(key[1]),
                    "weight_log_mismatch": float(key[2]),
                    "pre_outdegree_log1p_mismatch": float(key[3]),
                    "post_indegree_log1p_mismatch": float(key[4]),
                },
            }

    if best is None:
        raise RuntimeError(
            f"{candidate['id']}: no exact-hop-signature structural control found"
        )

    return best


def build_payload() -> dict:
    graph, runtime = build_runtime_inputs()
    graph = graph.tocsr(copy=False)
    graph.sum_duplicates()
    graph.sort_indices()

    indegree, outdegree = degree_arrays(graph)
    pres, posts, weights = build_edge_arrays(graph)
    addressable = intervention_addressable_mask(
        pres=pres,
        posts=posts,
        runtime=runtime,
    )

    unique_targets = sorted({
        int(t)
        for candidate in CANDIDATES
        for t in candidate["associated_targets"]
    })
    hop_arrays = {
        target: reverse_hop_array(graph, target, 3)
        for target in unique_targets
    }

    original_13 = {
        (int(pre), int(post))
        for pre, post, _weight in frozen_edges()
    }
    candidate_edges = {
        (int(c["presynaptic"]), int(c["postsynaptic"]))
        for c in CANDIDATES
    }

    forbidden = set(original_13) | set(candidate_edges)
    controls = {}

    for candidate in CANDIDATES:
        control = choose_control(
            graph=graph,
            runtime=runtime,
            candidate=candidate,
            hop_arrays=hop_arrays,
            indegree=indegree,
            outdegree=outdegree,
            pres=pres,
            posts=posts,
            weights=weights,
            addressable=addressable,
            forbidden_edges=forbidden,
        )
        controls[candidate["id"]] = control
        forbidden.add(
            (control["presynaptic"], control["postsynaptic"])
        )

    return {
        "experiment": "mq5-er4-the-stevedores-v1",
        "kind": "PRE-OUTCOME STRUCTURAL CONTROL SELECTION",
        "neural_outcomes_used": False,
        "selector_version": "V1-exact-hop-signature",
        "selection_rule": [
            "intervention-addressable under RETOUR semantics",
            "exact associated-target hop signature required",
            "minimize maximum log mismatch across abs(weight), pre outdegree, post indegree",
            "minimize summed log mismatch",
            "then weight mismatch",
            "then pre-degree mismatch",
            "then post-degree mismatch",
            "then lower postsynaptic ID",
            "then lower presynaptic ID",
        ],
        "candidates": {
            c["id"]: {
                "presynaptic": c["presynaptic"],
                "postsynaptic": c["postsynaptic"],
                "weight": c["weight"],
                "associated_targets": list(c["associated_targets"]),
                "hop_signature": list(c["hop_signature"]),
                "presynaptic_outdegree": c["pre_outdegree"],
                "postsynaptic_indegree": c["post_indegree"],
            }
            for c in CANDIDATES
        },
        "controls": controls,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--select", action="store_true", required=True)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    payload = build_payload()
    encoded = (
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False)
        + "\n"
    ).encode("utf-8")

    if args.write:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        if OUTPUT.exists():
            raise RuntimeError(
                f"refusing to overwrite existing control artifact: {OUTPUT}"
            )
        OUTPUT.write_bytes(encoded)
        payload["artifact"] = str(OUTPUT)
        payload["artifact_sha256"] = sha256_bytes(encoded)

    print(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
