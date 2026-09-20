from __future__ import annotations

import json
import math
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from statistics import median
from typing import Iterable, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config/experiments/sq03f6_the_commission_v1.json"


@dataclass(frozen=True)
class ConcentrationClassification:
    label: str
    upper_tail_p: float
    lower_tail_p: float
    effect_ratio: float


def load_config() -> dict:
    return json.loads(CONFIG_PATH.read_text())


def participation_counts(territories: Mapping[str, Iterable[str]]) -> Counter:
    counts = Counter()
    for source in sorted(territories):
        for target in set(territories[source]):
            counts[str(target)] += 1
    return counts


def participation_mass_hhi(counts: Mapping[str, int]) -> float:
    positive = [int(v) for v in counts.values() if int(v) > 0]
    if not positive:
        raise ValueError("No positive downstream participation mass")
    total = sum(positive)
    return sum((v / total) ** 2 for v in positive)


def participation_summary(counts: Mapping[str, int], source_count: int) -> dict:
    if source_count < 1:
        raise ValueError("source_count must be positive")
    positive = {str(k): int(v) for k, v in counts.items() if int(v) > 0}
    if not positive:
        raise ValueError("No positive downstream participation counts")

    ordered = sorted(positive.items(), key=lambda kv: (-kv[1], kv[0]))
    total_mass = sum(positive.values())

    return {
        "unique_target_count": len(positive),
        "total_participation_mass": total_mass,
        "max_participation_count": ordered[0][1],
        "targets_reached_by_all_sources": sum(v == source_count for v in positive.values()),
        "targets_reached_by_at_least_half_sources": sum(
            v * 2 >= source_count for v in positive.values()
        ),
        "top1_participation_share": ordered[0][1] / total_mass,
        "top5_participation_share": sum(v for _, v in ordered[:5]) / total_mass,
        "top10_participation_share": sum(v for _, v in ordered[:10]) / total_mass,
        "ordered_targets": [
            {"target": target, "participation_count": value}
            for target, value in ordered
        ],
    }


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


def classify_concentration(
    *,
    observed: float,
    null_values: Sequence[float],
    upper_p_threshold: float,
    lower_p_threshold: float,
    concentration_ratio_threshold: float,
    dispersion_ratio_threshold: float,
) -> ConcentrationClassification:
    if not null_values:
        raise ValueError("null_values must not be empty")

    upper = empirical_upper_tail(null_values, observed)
    lower = empirical_lower_tail(null_values, observed)
    ratio = effect_ratio(observed, median(null_values))

    if upper <= upper_p_threshold and ratio >= concentration_ratio_threshold:
        label = "GREATER_THAN_NULL_TARGET_CONCENTRATION"
    elif lower <= lower_p_threshold and ratio <= dispersion_ratio_threshold:
        label = "LESS_THAN_NULL_TARGET_CONCENTRATION"
    else:
        label = "NO_CLEAR_EVIDENCE_OF_UNUSUAL_TARGET_CONCENTRATION"

    return ConcentrationClassification(label, upper, lower, ratio)


def main() -> None:
    load_config()
    raise SystemExit(
        "SQ-03F.6 analyzer contract is frozen but result-bearing execution "
        "is intentionally disabled in this commit."
    )


if __name__ == "__main__":
    main()
