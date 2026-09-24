from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
from scipy import sparse

from brain.mq3_2_causal_intervention import zero_edges
from brain.sq05_betrayal_i import load_betrayal_i_edges


ROOT = Path(__file__).resolve().parents[1]

GROUPS = ROOT / "config/controls/sq06-orientation-edge-groups-v1.json"
SHAM = ROOT / "config/controls/sq05-betrayal-i-sham-v1.json"
MQ32_OPERATOR = ROOT / "brain/mq3_2_causal_intervention.py"

EXPECTED_GROUPS_SHA256 = "2fac74225e9874dfe13f919bfc47062065ba85b1ed1b61cce424f9a2c777c38d"
EXPECTED_SHAM_SHA256 = "d43488defc7b27705fe6765db50c8519c65cdaf6ac9a4443aa599c9dd1879f0d"
EXPECTED_OPERATOR_SHA256 = "007aa507ac22b07811bff5ae8102a0916c88549aa3011fa22fa57c70598c6a87"

GROUP_NAMES = ("LR_OBSERVED", "RL_OBSERVED")
EXPECTED_GROUP_SIZES = {"LR_OBSERVED": 10, "RL_OBSERVED": 3}
EXPECTED_RESPONDERS = {
    "LR_OBSERVED": {51, 55, 92, 129, 656, 1273},
    "RL_OBSERVED": {317, 126002, 137122},
}


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _load_frozen_group_payload() -> dict:
    if _sha256_file(GROUPS) != EXPECTED_GROUPS_SHA256:
        raise RuntimeError("SQ-06 orientation-group artifact SHA mismatch")
    if _sha256_file(SHAM) != EXPECTED_SHAM_SHA256:
        raise RuntimeError("SQ-06 inherited sham artifact SHA mismatch")
    if _sha256_file(MQ32_OPERATOR) != EXPECTED_OPERATOR_SHA256:
        raise RuntimeError("SQ-06 zero-edge operator source SHA mismatch")

    payload = json.loads(GROUPS.read_text(encoding="utf-8"))
    if payload.get("artifact") != "sq06-orientation-edge-groups-v1":
        raise RuntimeError("unexpected SQ-06 group artifact id")
    if payload.get("derivation", {}).get("independent_discovery") is not False:
        raise RuntimeError("SQ-06 outcome-derived provenance drift")
    if payload.get("derivation", {}).get("sq05_reinterpretation") is not False:
        raise RuntimeError("SQ-06 may not reinterpret SQ-05")

    groups = payload.get("groups", {})
    if tuple(sorted(groups)) != tuple(sorted(GROUP_NAMES)):
        raise RuntimeError("unexpected SQ-06 orientation group names")

    return payload


def _load_full_sham_edges() -> list[tuple[int, int, float]]:
    payload = json.loads(SHAM.read_text(encoding="utf-8"))
    if payload.get("artifact") != "sq05-betrayal-i-sham-v1":
        raise RuntimeError("unexpected inherited sham artifact id")
    if payload.get("edge_count") != 13:
        raise RuntimeError("unexpected inherited sham edge count")
    if payload.get("selection", {}).get("derive_at_execution") is not False:
        raise RuntimeError("SQ-06 sham derivation at execution is forbidden")
    return [
        (
            int(row["presynaptic"]),
            int(row["postsynaptic"]),
            float(row["weight"]),
        )
        for row in payload["edges"]
    ]


def resolve_group_edges(
    group_name: str,
) -> tuple[list[tuple[int, int, float]], list[tuple[int, int, float]], dict]:
    if group_name not in GROUP_NAMES:
        raise ValueError(f"unknown SQ-06 orientation group: {group_name}")

    payload = _load_frozen_group_payload()
    target_full, _ = load_betrayal_i_edges()
    sham_full = _load_full_sham_edges()

    target_by_pair = {(pre, post): (pre, post, weight) for pre, post, weight in target_full}
    sham_by_pair = {(pre, post): (pre, post, weight) for pre, post, weight in sham_full}

    rows = payload["groups"][group_name]
    if len(rows) != EXPECTED_GROUP_SIZES[group_name]:
        raise RuntimeError(f"{group_name} edge count drift")

    responders = {int(row["accepted_responder"]) for row in rows}
    if responders != EXPECTED_RESPONDERS[group_name]:
        raise RuntimeError(f"{group_name} responder set drift")

    target_edges = []
    sham_edges = []
    for row in rows:
        target_pair = (
            int(row["target_edge"]["presynaptic"]),
            int(row["target_edge"]["postsynaptic"]),
        )
        sham_pair = (
            int(row["matched_sham_edge"]["presynaptic"]),
            int(row["matched_sham_edge"]["postsynaptic"]),
        )

        if target_pair[0] != sham_pair[0]:
            raise RuntimeError("matched sham presynaptic identity drift")
        if target_pair not in target_by_pair:
            raise RuntimeError(f"target pair absent from frozen 13-edge lesion: {target_pair}")
        if sham_pair not in sham_by_pair:
            raise RuntimeError(f"sham pair absent from frozen 13-edge sham: {sham_pair}")

        target_edges.append(target_by_pair[target_pair])
        sham_edges.append(sham_by_pair[sham_pair])

    return target_edges, sham_edges, payload


def verify_exact_zero_subset(
    baseline: sparse.csr_matrix,
    candidate: sparse.csr_matrix,
    edges: list[tuple[int, int, float]],
) -> None:
    if baseline.shape != candidate.shape:
        raise RuntimeError("SQ-06 subset operator changed connectome shape")
    if candidate.nnz != baseline.nnz - len(edges):
        raise RuntimeError("SQ-06 subset operator changed unexpected edge count")

    expected_pairs = {(int(pre), int(post)) for pre, post, _ in edges}
    diff = (baseline != candidate).tocoo()
    observed_pairs = {(int(col), int(row)) for row, col in zip(diff.row, diff.col)}
    if observed_pairs != expected_pairs:
        raise RuntimeError("SQ-06 subset operator changed unexpected edge identities")

    for pre, post, expected_weight in edges:
        before = float(baseline[post, pre])
        after = float(candidate[post, pre])
        if not np.isclose(before, expected_weight, rtol=1e-6, atol=1e-12):
            raise RuntimeError(f"SQ-06 baseline weight mismatch {pre}->{post}")
        if after != 0.0:
            raise RuntimeError(f"SQ-06 failed to zero {pre}->{post}")


def build_orientation_group(
    baseline: sparse.csr_matrix,
    group_name: str,
    control: str,
) -> tuple[sparse.csr_matrix, dict]:
    if control not in ("TARGETED", "SHAM"):
        raise ValueError("control must be TARGETED or SHAM")

    targeted, sham, payload = resolve_group_edges(group_name)
    selected = targeted if control == "TARGETED" else sham

    candidate = zero_edges(baseline, selected)
    verify_exact_zero_subset(baseline, candidate, selected)

    provenance = {
        "group": group_name,
        "control": control,
        "edge_count": len(selected),
        "group_artifact_sha256": EXPECTED_GROUPS_SHA256,
        "inherited_sham_sha256": EXPECTED_SHAM_SHA256,
        "zero_edge_operator_sha256": EXPECTED_OPERATOR_SHA256,
        "outcome_derived_from_sq05": True,
        "future_use": "prospective_validation",
        "sq05_reinterpretation": False,
        "neural_execution_authorized_here": False,
        "result_execution_authorized_here": False,
        "source_artifact": payload["artifact"],
    }
    return candidate, provenance
