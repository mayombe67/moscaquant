from __future__ import annotations

import hashlib
import json
import math
import random
from dataclasses import dataclass
from pathlib import Path
from statistics import mean, median
from typing import Dict, Iterable, List, Mapping, Sequence, Set, Tuple

import pandas as pd

from brain.sq03f1_analyze import (
    FEATHER,
    SQ03B_LEDGER,
    build_candidate_edges,
    rebuild_pair_rows,
)

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config/experiments/sq03f5_turf_war_v1.json"
F4_RESULT = ROOT / "artifacts/sidequests/sq03f4-sit-down-result-v1.json"
OUTPUT = ROOT / "artifacts/sidequests/sq03f5-turf-war-result-v1.json"


@dataclass(frozen=True)
class Classification:
    label: str
    upper_tail_p: float
    lower_tail_p: float
    effect_ratio: float


@dataclass(frozen=True)
class PreparedInputs:
    eligible_sources: Tuple[str, ...]
    candidate_sources: Tuple[str, ...]
    adjacency: Dict[str, Tuple[str, ...]]
    candidate_edge_count: int
    conservative_graph_edge_count: int


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_config() -> dict:
    return json.loads(CONFIG_PATH.read_text())


def load_f4_result() -> dict:
    row = json.loads(F4_RESULT.read_text())
    if row.get("schema") != "moscaquant.sq03f4_result/v1":
        raise RuntimeError("Unexpected SQ-03F.4 result schema")
    return row


def conservative_graph_frame() -> pd.DataFrame:
    aligned = pd.read_feather(FEATHER)
    required = {"verdict_corr", "weight_m", "weight_f", "pre", "post"}
    missing = sorted(required - set(aligned.columns))
    if missing:
        raise RuntimeError(
            f"aligned-edge table missing required conservative-graph columns: {missing}"
        )

    mask = (
        (aligned["verdict_corr"] == "isomorphic")
        & (aligned["weight_m"] > 0)
        & (aligned["weight_f"] > 0)
    )
    matched = aligned.loc[mask].copy()
    matched["original_feather_row"] = matched.index.astype(int)
    return matched.reset_index(drop=True)


def adjacency_from_matched(matched: pd.DataFrame) -> Dict[str, Tuple[str, ...]]:
    adj: Dict[str, Set[str]] = {}
    for pre, post in zip(matched["pre"], matched["post"]):
        a = str(pre)
        b = str(post)
        adj.setdefault(a, set()).add(b)
    return {node: tuple(sorted(children)) for node, children in adj.items()}


def prepare_inputs() -> PreparedInputs:
    cfg = load_config()
    f4 = load_f4_result()

    configured = cfg["input"]["authoritative_sq03f4_result"]
    if configured != str(F4_RESULT.relative_to(ROOT)):
        raise RuntimeError("SQ-03F.5 configured F.4 artifact path mismatch")

    eligible_raw = f4.get("S_C_made_source_overlap", {}).get("sources")
    if not isinstance(eligible_raw, list) or not eligible_raw:
        raise RuntimeError("F.4 overlap source list missing or empty")
    if not all(isinstance(x, str) for x in eligible_raw):
        raise RuntimeError("F.4 overlap sources must be strings")

    eligible_sources = tuple(sorted(eligible_raw))
    if len(set(eligible_sources)) != len(eligible_sources):
        raise RuntimeError("F.4 overlap sources contain duplicates")

    matched = conservative_graph_frame()

    if sha256(FEATHER) != f4["aligned_edges_sha256"]:
        raise RuntimeError("aligned-edge hash mismatch versus F.4")
    if len(matched) != int(f4["conservative_graph_edge_count"]):
        raise RuntimeError("conservative graph edge-count mismatch versus F.4")

    pair_rows = rebuild_pair_rows(SQ03B_LEDGER)
    candidate_rows = build_candidate_edges(pair_rows, matched)
    candidate_sources = tuple(sorted({str(r["pre"]) for r in candidate_rows}))

    if len(candidate_rows) != int(f4["candidate_edge_count"]):
        raise RuntimeError("candidate edge-count mismatch versus F.4")
    if len(candidate_sources) != int(f4["candidate_source_count"]):
        raise RuntimeError("candidate source-count mismatch versus F.4")
    if not set(eligible_sources).issubset(candidate_sources):
        raise RuntimeError("F.4 eligible sources are not a subset of candidate universe")

    return PreparedInputs(
        eligible_sources=eligible_sources,
        candidate_sources=candidate_sources,
        adjacency=adjacency_from_matched(matched),
        candidate_edge_count=len(candidate_rows),
        conservative_graph_edge_count=len(matched),
    )


def territory(adjacency, source, *, max_depth, exclude_source_nodes=True):
    if max_depth < 1:
        raise ValueError("max_depth must be >= 1")
    visited = {source}
    frontier = {source}
    reached = set()
    for _ in range(max_depth):
        nxt = set()
        for node in frontier:
            for child in adjacency.get(node, ()):
                reached.add(child)
                if child not in visited:
                    visited.add(child)
                    nxt.add(child)
        frontier = nxt
        if not frontier:
            break
    if exclude_source_nodes:
        reached.discard(source)
    return reached


def jaccard(a, b):
    union = a | b
    return 0.0 if not union else len(a & b) / len(union)


def mean_pairwise_jaccard(territories):
    sources = sorted(territories)
    values = []
    pairs = []
    for i, left in enumerate(sources):
        for right in sources[i + 1:]:
            a = territories[left]
            b = territories[right]
            inter = len(a & b)
            union = len(a | b)
            value = 0.0 if union == 0 else inter / union
            values.append(value)
            pairs.append({
                "source_a": left,
                "source_b": right,
                "intersection": inter,
                "union": union,
                "jaccard": value,
            })
    if not values:
        raise ValueError("At least two eligible sources are required")
    return mean(values), pairs


def out_degrees(adjacency, universe):
    return {node: len(set(adjacency.get(node, ()))) for node in universe}


def decile_strata(degrees):
    items = sorted(degrees.items(), key=lambda kv: (kv[1], kv[0]))
    n = len(items)
    if n == 0:
        raise ValueError("Cannot stratify an empty universe")
    return {node: min(9, (rank * 10) // n) for rank, (node, _d) in enumerate(items)}


def derive_stream_seed(base_seed, stream_index):
    if stream_index < 0:
        raise ValueError("stream_index must be non-negative")
    return base_seed + stream_index


def sample_matched_sources(observed_sources, universe, strata, rng):
    observed_set = set(observed_sources)
    pools = {}
    for node in universe:
        if node in observed_set:
            continue
        pools.setdefault(strata[node], []).append(node)

    sampled = []
    used = set()
    for source in observed_sources:
        stratum = strata[source]
        eligible = [n for n in pools.get(stratum, ()) if n not in used]
        if not eligible:
            raise ValueError(f"Matched-null pool exhausted for out-degree stratum {stratum}")
        pick = rng.choice(eligible)
        sampled.append(pick)
        used.add(pick)
    return sampled


def empirical_upper_tail(null_values, observed):
    ge = sum(v >= observed for v in null_values)
    return (ge + 1) / (len(null_values) + 1)


def empirical_lower_tail(null_values, observed):
    le = sum(v <= observed for v in null_values)
    return (le + 1) / (len(null_values) + 1)


def effect_ratio(observed, null_median):
    if null_median == 0:
        return 1.0 if observed == 0 else math.inf
    return observed / null_median


def classify(*, observed, null_values, upper_p_threshold, lower_p_threshold,
             convergence_ratio_threshold, separation_ratio_threshold):
    if not null_values:
        raise ValueError("null_values must not be empty")
    upper = empirical_upper_tail(null_values, observed)
    lower = empirical_lower_tail(null_values, observed)
    ratio = effect_ratio(observed, median(null_values))
    if upper <= upper_p_threshold and ratio >= convergence_ratio_threshold:
        label = "GREATER_THAN_NULL_DOWNSTREAM_CONVERGENCE"
    elif lower <= lower_p_threshold and ratio <= separation_ratio_threshold:
        label = "SEPARATED_DOWNSTREAM_TERRITORIES"
    else:
        label = "NO_CLEAR_EVIDENCE_OF_UNUSUAL_CONVERGENCE"
    return Classification(label, upper, lower, ratio)


def build_result_payload(*, prepared, territory_sizes, pairwise_overlap, observed,
                         null_values, classification, derived_streams):
    cfg = load_config()
    f4 = load_f4_result()
    return {
        "schema": "moscaquant.sq03f5_result/v1",
        "experiment_id": "SQ-03F.5",
        "title": "TURF WAR",
        "status": "COMPLETE",
        "input_artifacts": {
            "sq03f4_result": str(F4_RESULT.relative_to(ROOT)),
            "sq03f4_result_sha256": sha256(F4_RESULT),
            "aligned_edges_sha256": sha256(FEATHER),
        },
        "eligible_sources": list(prepared.eligible_sources),
        "candidate_source_count": len(prepared.candidate_sources),
        "candidate_edge_count": prepared.candidate_edge_count,
        "conservative_graph_edge_count": prepared.conservative_graph_edge_count,
        "territory_parameters": cfg["territory"],
        "territory_sizes": dict(sorted(territory_sizes.items())),
        "pairwise_overlap": list(pairwise_overlap),
        "observed_mean_pairwise_jaccard": observed,
        "null_summary": {
            "median": median(null_values),
            "mean": mean(null_values),
            "min": min(null_values),
            "max": max(null_values),
        },
        "empirical_upper_tail_p": classification.upper_tail_p,
        "empirical_lower_tail_p": classification.lower_tail_p,
        "effect_ratio_vs_null_median": classification.effect_ratio,
        "randomizations": cfg["null_model"]["randomizations"],
        "base_seed": cfg["null_model"]["base_seed"],
        "derived_streams": list(derived_streams),
        "classification": classification.label,
        "claim_boundary": (
            "This result concerns downstream convergence within the frozen MoscaQuant "
            "model and frozen SQ-03F source set only. It does not establish biological "
            "gang-like organization, anatomical territory, sex-specific organization, "
            "financial usefulness, or trading usefulness."
        ),
        "parent_classification": f4["classification"],
    }


def write_result(payload):
    if OUTPUT.exists():
        raise RuntimeError(f"Refusing to overwrite existing result: {OUTPUT}")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")

def build_node_bit_index(adjacency):
    nodes = set(adjacency)
    for children in adjacency.values():
        nodes.update(children)
    return {node: i for i, node in enumerate(sorted(nodes))}


def territory_bitmask(adjacency, source, *, max_depth, node_bits):
    if max_depth < 1:
        raise ValueError("max_depth must be >= 1")

    visited = {source}
    frontier = {source}
    reached = set()

    for _ in range(max_depth):
        nxt = set()
        for node in frontier:
            for child in adjacency.get(node, ()):
                reached.add(child)
                if child not in visited:
                    visited.add(child)
                    nxt.add(child)
        frontier = nxt
        if not frontier:
            break

    reached.discard(source)

    mask = 0
    for node in reached:
        mask |= 1 << node_bits[node]
    return mask


def precompute_territory_masks(adjacency, sources, *, max_depth):
    node_bits = build_node_bit_index(adjacency)
    return {
        source: territory_bitmask(
            adjacency,
            source,
            max_depth=max_depth,
            node_bits=node_bits,
        )
        for source in sources
    }


def bitmask_jaccard(a, b):
    union = a | b
    if union == 0:
        return 0.0
    return (a & b).bit_count() / union.bit_count()


def mean_pairwise_jaccard_masks(sources, masks):
    total = 0.0
    count = 0
    ordered = sorted(sources)
    for i, left in enumerate(ordered):
        a = masks[left]
        for right in ordered[i + 1:]:
            total += bitmask_jaccard(a, masks[right])
            count += 1
    if count == 0:
        raise ValueError("At least two sources are required")
    return total / count


def observed_pairwise_from_masks(sources, masks):
    pairs = []
    values = []
    ordered = sorted(sources)
    for i, left in enumerate(ordered):
        a = masks[left]
        for right in ordered[i + 1:]:
            b = masks[right]
            inter = (a & b).bit_count()
            union = (a | b).bit_count()
            value = 0.0 if union == 0 else inter / union
            values.append(value)
            pairs.append({
                "source_a": left,
                "source_b": right,
                "intersection": inter,
                "union": union,
                "jaccard": value,
            })
    if not values:
        raise ValueError("At least two sources are required")
    return mean(values), pairs


def run_experiment():
    cfg = load_config()

    max_depth = int(cfg["territory"]["max_depth"])
    randomizations = int(cfg["null_model"]["randomizations"])
    base_seed = int(cfg["null_model"]["base_seed"])

    if randomizations != 10000:
        raise RuntimeError("Frozen randomization count changed")
    if base_seed != 314159:
        raise RuntimeError("Frozen base seed changed")
    if max_depth != 2:
        raise RuntimeError("Frozen territory depth changed")

    prepared = prepare_inputs()

    masks = precompute_territory_masks(
        prepared.adjacency,
        prepared.candidate_sources,
        max_depth=max_depth,
    )

    observed, pairwise = observed_pairwise_from_masks(
        prepared.eligible_sources,
        masks,
    )
    territory_sizes = {
        source: masks[source].bit_count()
        for source in prepared.eligible_sources
    }

    degrees = out_degrees(prepared.adjacency, prepared.candidate_sources)
    strata = decile_strata(degrees)

    rng = random.Random(base_seed)
    null_values = []
    for _ in range(randomizations):
        sampled = sample_matched_sources(
            prepared.eligible_sources,
            prepared.candidate_sources,
            strata,
            rng,
        )
        null_values.append(
            mean_pairwise_jaccard_masks(sampled, masks)
        )

    cls_cfg = cfg["classification"]
    classification = classify(
        observed=observed,
        null_values=null_values,
        upper_p_threshold=float(
            cls_cfg["greater_than_null"]["empirical_upper_tail_p_lte"]
        ),
        lower_p_threshold=float(
            cls_cfg["separated_territories"]["empirical_lower_tail_p_lte"]
        ),
        convergence_ratio_threshold=float(
            cls_cfg["greater_than_null"]["effect_ratio_gte"]
        ),
        separation_ratio_threshold=float(
            cls_cfg["separated_territories"]["effect_ratio_lte"]
        ),
    )

    return build_result_payload(
        prepared=prepared,
        territory_sizes=territory_sizes,
        pairwise_overlap=pairwise,
        observed=observed,
        null_values=null_values,
        classification=classification,
        derived_streams=[base_seed],
    )


def execute_once():
    if OUTPUT.exists():
        raise RuntimeError(f"Refusing to overwrite existing result: {OUTPUT}")
    payload = run_experiment()
    write_result(payload)
    return payload

def main():
    payload = execute_once()
    print("SQ-03F.5 TURF WAR complete.")
    print("result:", OUTPUT.relative_to(ROOT))
    print("eligible sources:", len(payload["eligible_sources"]))
    print("observed mean pairwise Jaccard:", payload["observed_mean_pairwise_jaccard"])
    print("null median:", payload["null_summary"]["median"])
    print("upper-tail p:", payload["empirical_upper_tail_p"])
    print("lower-tail p:", payload["empirical_lower_tail_p"])
    print("effect ratio:", payload["effect_ratio_vs_null_median"])
    print("classification:", payload["classification"])


if __name__ == "__main__":
    main()
