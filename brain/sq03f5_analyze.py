from __future__ import annotations

import json
import math
import random
from dataclasses import dataclass
from pathlib import Path
from statistics import mean, median
from typing import Dict, Iterable, List, Mapping, Sequence, Set, Tuple

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config/experiments/sq03f5_turf_war_v1.json"


@dataclass(frozen=True)
class Classification:
    label: str
    upper_tail_p: float
    lower_tail_p: float
    effect_ratio: float


def load_config() -> dict:
    return json.loads(CONFIG_PATH.read_text())


def territory(
    adjacency: Mapping[int, Sequence[int]],
    source: int,
    *,
    max_depth: int,
    exclude_source_nodes: bool = True,
) -> Set[int]:
    if max_depth < 1:
        raise ValueError("max_depth must be >= 1")

    visited: Set[int] = {source}
    frontier: Set[int] = {source}
    reached: Set[int] = set()

    for _ in range(max_depth):
        nxt: Set[int] = set()
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


def jaccard(a: Set[int], b: Set[int]) -> float:
    union = a | b
    if not union:
        return 0.0
    return len(a & b) / len(union)


def mean_pairwise_jaccard(
    territories: Mapping[int, Set[int]]
) -> Tuple[float, List[dict]]:
    sources = sorted(territories)
    values: List[float] = []
    pairs: List[dict] = []

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


def out_degrees(
    adjacency: Mapping[int, Sequence[int]],
    universe: Iterable[int],
) -> Dict[int, int]:
    return {node: len(set(adjacency.get(node, ()))) for node in universe}


def decile_strata(degrees: Mapping[int, int]) -> Dict[int, int]:
    items = sorted(degrees.items(), key=lambda kv: (kv[1], kv[0]))
    n = len(items)
    if n == 0:
        raise ValueError("Cannot stratify an empty universe")

    result: Dict[int, int] = {}
    for rank, (node, _degree) in enumerate(items):
        result[node] = min(9, (rank * 10) // n)
    return result


def derive_stream_seed(base_seed: int, stream_index: int) -> int:
    if stream_index < 0:
        raise ValueError("stream_index must be non-negative")
    return base_seed + stream_index


def empirical_upper_tail(null_values: Sequence[float], observed: float) -> float:
    ge = sum(v >= observed for v in null_values)
    return (ge + 1) / (len(null_values) + 1)


def empirical_lower_tail(null_values: Sequence[float], observed: float) -> float:
    le = sum(v <= observed for v in null_values)
    return (le + 1) / (len(null_values) + 1)


def effect_ratio(observed: float, null_median: float) -> float:
    if null_median == 0:
        return 1.0 if observed == 0 else math.inf
    return observed / null_median


def classify(
    *,
    observed: float,
    null_values: Sequence[float],
    upper_p_threshold: float,
    lower_p_threshold: float,
    convergence_ratio_threshold: float,
    separation_ratio_threshold: float,
) -> Classification:
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


def main() -> None:
    load_config()
    raise SystemExit(
        "SQ-03F.5 analyzer contract is frozen but execution is intentionally "
        "disabled in this commit."
    )


if __name__ == "__main__":
    main()
