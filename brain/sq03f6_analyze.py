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

def main() -> None:
    prepared = prepare_commission_inputs()
    print("SQ-03F.6 execution adapter validation passed.")
    print("eligible sources:", len(prepared.eligible_sources))
    print("candidate sources:", len(prepared.candidate_sources))
    print("candidate edges:", prepared.candidate_edge_count)
    print("conservative graph edges:", prepared.conservative_graph_edge_count)
    raise SystemExit(
        "SQ-03F.6 result-bearing execution remains disabled in this commit."
    )


if __name__ == "__main__":
    main()
