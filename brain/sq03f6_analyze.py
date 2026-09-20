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

import hashlib

from brain.sq03f5_analyze import (
    PreparedInputs as F5PreparedInputs,
    prepare_inputs as prepare_f5_inputs,
)

F5_RESULT = ROOT / "artifacts/sidequests/sq03f5-turf-war-result-v1.json"
F5_PROVENANCE = ROOT / "artifacts/sidequests/sq03f5-turf-war-provenance-v1.json"
OUTPUT = ROOT / "artifacts/sidequests/sq03f6-the-commission-result-v1.json"


@dataclass(frozen=True)
class PreparedCommissionInputs:
    eligible_sources: tuple[str, ...]
    candidate_sources: tuple[str, ...]
    adjacency: dict[str, tuple[str, ...]]
    candidate_edge_count: int
    conservative_graph_edge_count: int
    parent_result_sha256: str
    parent_provenance_sha256: str


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_f5_result() -> dict:
    row = json.loads(F5_RESULT.read_text())
    if row.get("schema") != "moscaquant.sq03f5_result/v1":
        raise RuntimeError("Unexpected SQ-03F.5 result schema")
    if row.get("status") != "COMPLETE":
        raise RuntimeError("SQ-03F.5 result is not complete")
    return row


def load_f5_provenance() -> dict:
    row = json.loads(F5_PROVENANCE.read_text())
    if row.get("schema") != "moscaquant.sq03f5_provenance/v1":
        raise RuntimeError("Unexpected SQ-03F.5 provenance schema")
    return row


def prepare_commission_inputs() -> PreparedCommissionInputs:
    cfg = load_config()
    f5 = load_f5_result()
    provenance = load_f5_provenance()

    if cfg["input"]["authoritative_sq03f5_result"] != str(F5_RESULT.relative_to(ROOT)):
        raise RuntimeError("Configured SQ-03F.5 result path mismatch")
    if cfg["input"]["authoritative_sq03f5_provenance"] != str(F5_PROVENANCE.relative_to(ROOT)):
        raise RuntimeError("Configured SQ-03F.5 provenance path mismatch")

    result_hash = sha256(F5_RESULT)
    provenance_hash = sha256(F5_PROVENANCE)

    if provenance.get("result_sha256") != result_hash:
        raise RuntimeError("SQ-03F.5 result hash does not match provenance sidecar")

    f5_inputs: F5PreparedInputs = prepare_f5_inputs()

    eligible = tuple(sorted(str(x) for x in f5["eligible_sources"]))
    if eligible != tuple(sorted(f5_inputs.eligible_sources)):
        raise RuntimeError("SQ-03F.5 eligible sources do not match reconstruction")
    if len(eligible) != 42:
        raise RuntimeError("Unexpected SQ-03F.5 eligible-source count")

    territory = f5["territory_parameters"]
    if territory["direction"] != "downstream":
        raise RuntimeError("SQ-03F.5 territory direction mismatch")
    if int(territory["max_depth"]) != 2:
        raise RuntimeError("SQ-03F.5 territory depth mismatch")
    if territory["exclude_source_nodes"] is not True:
        raise RuntimeError("SQ-03F.5 source-exclusion rule mismatch")
    if territory["collapse_repeated_nodes"] is not True:
        raise RuntimeError("SQ-03F.5 repeated-node rule mismatch")

    if int(f5["candidate_source_count"]) != len(f5_inputs.candidate_sources):
        raise RuntimeError("SQ-03F.5 candidate-source count mismatch")
    if int(f5["candidate_edge_count"]) != f5_inputs.candidate_edge_count:
        raise RuntimeError("SQ-03F.5 candidate-edge count mismatch")
    if int(f5["conservative_graph_edge_count"]) != f5_inputs.conservative_graph_edge_count:
        raise RuntimeError("SQ-03F.5 conservative-graph edge count mismatch")

    return PreparedCommissionInputs(
        eligible_sources=eligible,
        candidate_sources=f5_inputs.candidate_sources,
        adjacency=f5_inputs.adjacency,
        candidate_edge_count=f5_inputs.candidate_edge_count,
        conservative_graph_edge_count=f5_inputs.conservative_graph_edge_count,
        parent_result_sha256=result_hash,
        parent_provenance_sha256=provenance_hash,
    )


def commission_result_skeleton(prepared: PreparedCommissionInputs) -> dict:
    return {
        "schema": "moscaquant.sq03f6_result/v1",
        "experiment_id": "SQ-03F.6",
        "title": "THE COMMISSION",
        "status": "NOT_EXECUTED",
        "input_artifacts": {
            "sq03f5_result": str(F5_RESULT.relative_to(ROOT)),
            "sq03f5_result_sha256": prepared.parent_result_sha256,
            "sq03f5_provenance": str(F5_PROVENANCE.relative_to(ROOT)),
            "sq03f5_provenance_sha256": prepared.parent_provenance_sha256,
        },
        "eligible_source_count": len(prepared.eligible_sources),
        "candidate_source_count": len(prepared.candidate_sources),
        "candidate_edge_count": prepared.candidate_edge_count,
        "conservative_graph_edge_count": prepared.conservative_graph_edge_count,
    }

from brain.sq03f5_analyze import (
    precompute_territory_masks,
    out_degrees,
    decile_strata,
    sample_matched_sources,
)
import random
from statistics import mean


def participation_counts_from_masks(sources, masks):
    counts = Counter()
    for source in sources:
        mask = masks[source]
        bit_index = 0
        while mask:
            if mask & 1:
                counts[bit_index] += 1
            mask >>= 1
            bit_index += 1
    return counts


def hhi_from_masks(sources, masks):
    # Exact algebraic fast path for participation-mass HHI.
    #
    # Let c_t be the number of selected source territories containing target t.
    #
    #   HHI = sum_t (c_t / total_mass)^2
    #       = sum_t c_t^2 / total_mass^2
    #
    # Also:
    #
    #   sum_t c_t^2
    #     = sum_i |T_i| + 2 * sum_{i<j} |T_i intersect T_j|
    #
    # This is exactly equivalent to materializing target participation counts,
    # but avoids walking every set bit for every randomized draw.
    ordered = list(sources)
    if not ordered:
        raise ValueError("At least one source is required")

    total_mass = 0
    squared_mass = 0

    for source in ordered:
        size = masks[source].bit_count()
        total_mass += size
        squared_mass += size

    if total_mass == 0:
        raise ValueError("No positive downstream participation mass")

    for i, left in enumerate(ordered):
        a = masks[left]
        for right in ordered[i + 1:]:
            squared_mass += 2 * (a & masks[right]).bit_count()

    return squared_mass / (total_mass * total_mass)


def run_commission():
    cfg = load_config()

    randomizations = int(cfg["null_model"]["randomizations"])
    base_seed = int(cfg["null_model"]["base_seed"])
    max_depth = int(cfg["territory"]["max_depth"])

    if randomizations != 10000:
        raise RuntimeError("Frozen randomization count changed")
    if base_seed != 314159:
        raise RuntimeError("Frozen base seed changed")
    if max_depth != 2:
        raise RuntimeError("Frozen territory depth changed")

    prepared = prepare_commission_inputs()

    masks = precompute_territory_masks(
        prepared.adjacency,
        prepared.candidate_sources,
        max_depth=max_depth,
    )

    observed_counts = participation_counts_from_masks(
        prepared.eligible_sources,
        masks,
    )
    observed_hhi = participation_mass_hhi(observed_counts)

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
        null_values.append(hhi_from_masks(sampled, masks))

    cls = cfg["classification"]
    classification = classify_concentration(
        observed=observed_hhi,
        null_values=null_values,
        upper_p_threshold=float(
            cls["greater_than_null"]["empirical_upper_tail_p_lte"]
        ),
        lower_p_threshold=float(
            cls["less_than_null"]["empirical_lower_tail_p_lte"]
        ),
        concentration_ratio_threshold=float(
            cls["greater_than_null"]["effect_ratio_gte"]
        ),
        dispersion_ratio_threshold=float(
            cls["less_than_null"]["effect_ratio_lte"]
        ),
    )

    summary = participation_summary(
        {str(k): v for k, v in observed_counts.items()},
        source_count=len(prepared.eligible_sources),
    )

    return {
        "schema": "moscaquant.sq03f6_result/v1",
        "experiment_id": "SQ-03F.6",
        "title": "THE COMMISSION",
        "status": "COMPLETE",
        "input_artifacts": {
            "sq03f5_result": str(F5_RESULT.relative_to(ROOT)),
            "sq03f5_result_sha256": prepared.parent_result_sha256,
            "sq03f5_provenance": str(F5_PROVENANCE.relative_to(ROOT)),
            "sq03f5_provenance_sha256": prepared.parent_provenance_sha256,
        },
        "eligible_source_count": len(prepared.eligible_sources),
        "candidate_source_count": len(prepared.candidate_sources),
        "candidate_edge_count": prepared.candidate_edge_count,
        "conservative_graph_edge_count": prepared.conservative_graph_edge_count,
        "territory_parameters": cfg["territory"],
        "target_participation_rule": cfg["target_participation"],
        "primary_statistic": cfg["primary_statistic"],
        "observed_participation_mass_hhi": observed_hhi,
        "participation_summary": summary,
        "null_summary": {
            "median": median(null_values),
            "mean": mean(null_values),
            "min": min(null_values),
            "max": max(null_values),
        },
        "empirical_upper_tail_p": classification.upper_tail_p,
        "empirical_lower_tail_p": classification.lower_tail_p,
        "effect_ratio_vs_null_median": classification.effect_ratio,
        "randomizations": randomizations,
        "base_seed": base_seed,
        "classification": classification.label,
        "claim_boundary": (
            "This result concerns concentration of downstream participation "
            "within the frozen MoscaQuant model and frozen SQ-03F source set only. "
            "It does not establish literal biological command hierarchy, anatomical "
            "governing bodies, organism-level functional modules, sex-specific neural "
            "organization, consciousness, agency, intent, coordination, financial "
            "usefulness, or trading usefulness."
        ),
    }


def write_commission_result(payload):
    if OUTPUT.exists():
        raise RuntimeError(f"Refusing to overwrite existing result: {OUTPUT}")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def execute_commission_once():
    if OUTPUT.exists():
        raise RuntimeError(f"Refusing to overwrite existing result: {OUTPUT}")
    payload = run_commission()
    write_commission_result(payload)
    return payload

def main() -> None:
    payload = execute_commission_once()
    print("SQ-03F.6 THE COMMISSION complete.")
    print("result:", OUTPUT.relative_to(ROOT))
    print("eligible sources:", payload["eligible_source_count"])
    print("observed participation-mass HHI:", payload["observed_participation_mass_hhi"])
    print("null median:", payload["null_summary"]["median"])
    print("upper-tail p:", payload["empirical_upper_tail_p"])
    print("lower-tail p:", payload["empirical_lower_tail_p"])
    print("effect ratio:", payload["effect_ratio_vs_null_median"])
    print("classification:", payload["classification"])


if __name__ == "__main__":
    main()
