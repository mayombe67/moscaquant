from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
from scipy import sparse

import brain.sq05_betrayal_i as b1
from brain.mq3_2_causal_intervention import zero_edges


ROOT = Path(__file__).resolve().parents[1]

REGISTRY = ROOT / "config/controls/sq07-the-maw-edge-registry-v1.json"
SQ05_BETRAYAL_I_SOURCE = ROOT / "brain/sq05_betrayal_i.py"
MQ32_OPERATOR_SOURCE = ROOT / "brain/mq3_2_causal_intervention.py"

EXPECTED_REGISTRY_SHA256 = (
    "0e9502f3147d2f833d00ce2c05af258b973f7391a43c9d89f695556d8823dedd"
)
EXPECTED_SQ05_BETRAYAL_I_SHA256 = (
    "c62767cac434f380104c8da5cd9b73dcee89fefbeea0a0efe17ca9bd812c8664"
)
EXPECTED_MQ32_OPERATOR_SHA256 = (
    "007aa507ac22b07811bff5ae8102a0916c88549aa3011fa22fa57c70598c6a87"
)

MASK_WIDTH = 13
INTACT_MASK = "0000000000000"
FULL13_MASK = "1111111111111"
LR_GROUP_MASK = "1111111111000"
RL_GROUP_MASK = "0000000000111"


class Refusal(RuntimeError):
    pass


def refuse(message: str) -> None:
    raise Refusal(message)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            h.update(chunk)

    return h.hexdigest()


def validate_mask(mask13: str) -> None:
    if not isinstance(mask13, str):
        raise ValueError("SQ-07 mask must be a string")

    if len(mask13) != MASK_WIDTH:
        raise ValueError(
            f"SQ-07 mask must contain exactly {MASK_WIDTH} characters"
        )

    if set(mask13) - {"0", "1"}:
        raise ValueError("SQ-07 mask may contain only 0 and 1")


def _load_registry() -> dict:
    if not REGISTRY.is_file():
        refuse(f"missing SQ-07 edge registry: {REGISTRY}")

    actual = sha256_file(REGISTRY)

    if actual != EXPECTED_REGISTRY_SHA256:
        refuse(
            "SQ-07 edge-registry SHA mismatch: "
            f"{actual} != {EXPECTED_REGISTRY_SHA256}"
        )

    payload = json.loads(REGISTRY.read_text(encoding="utf-8"))

    if payload.get("artifact") != "sq07-the-maw-edge-registry-v1":
        refuse("unexpected SQ-07 edge-registry artifact id")

    edges = payload.get("edges")

    if not isinstance(edges, list) or len(edges) != MASK_WIDTH:
        refuse("SQ-07 edge-registry count drift")

    for i, row in enumerate(edges):
        if row.get("edge_index") != i:
            refuse(f"SQ-07 edge-index drift at {i}")

        if row.get("edge_id") != f"E{i:02d}":
            refuse(f"SQ-07 edge-id drift at {i}")

        expected_group = "LR_OBSERVED" if i < 10 else "RL_OBSERVED"

        if row.get("sq06_group") != expected_group:
            refuse(f"SQ-07 group-coordinate drift at E{i:02d}")

    mask_contract = payload.get("mask_contract", {})

    if mask_contract.get("length") != MASK_WIDTH:
        refuse("SQ-07 registry mask-width drift")

    if (
        mask_contract.get("character_index_semantics")
        != "mask13[i] corresponds to edges[i]"
    ):
        refuse("SQ-07 registry mask-coordinate semantics drift")

    return payload


def verify_frozen_dependencies() -> dict:
    paths = {
        "registry": (REGISTRY, EXPECTED_REGISTRY_SHA256),
        "sq05_betrayal_i": (
            SQ05_BETRAYAL_I_SOURCE,
            EXPECTED_SQ05_BETRAYAL_I_SHA256,
        ),
        "mq32_zero_edge_operator": (
            MQ32_OPERATOR_SOURCE,
            EXPECTED_MQ32_OPERATOR_SHA256,
        ),
    }

    observed = {}

    for name, (path, expected) in paths.items():
        if not path.is_file():
            refuse(f"missing frozen SQ-07 dependency {name}: {path}")

        actual = sha256_file(path)

        if actual != expected:
            refuse(
                f"SQ-07 frozen dependency SHA mismatch for {name}: "
                f"{actual} != {expected}"
            )

        observed[name] = actual

    payload = _load_registry()

    historical_edges, historical_payload = b1.load_betrayal_i_edges()

    if len(historical_edges) != MASK_WIDTH:
        refuse("SQ-07 inherited FULL13 edge-count drift")

    if historical_payload.get("post_hoc") is not True:
        refuse("SQ-07 historical lesion provenance drift")

    if (
        historical_payload.get("purpose")
        != "confirmatory in-model causal intervention"
    ):
        refuse("SQ-07 historical lesion purpose drift")

    return {
        "dependencies": observed,
        "historical_causal_artifact_sha256": b1.CAUSAL_SHA256,
        "edge_count": MASK_WIDTH,
        "registry_artifact": payload["artifact"],
    }


def resolve_registry_edges() -> tuple[tuple[int, int, float], ...]:
    verify_frozen_dependencies()

    payload = _load_registry()
    historical_edges, _ = b1.load_betrayal_i_edges()

    historical_by_pair = {
        (int(pre), int(post)): (int(pre), int(post), float(weight))
        for pre, post, weight in historical_edges
    }

    if len(historical_by_pair) != MASK_WIDTH:
        refuse("SQ-07 inherited FULL13 contains duplicate edge coordinates")

    resolved = []

    for row in payload["edges"]:
        target = row["target_edge"]

        pair = (
            int(target["presynaptic"]),
            int(target["postsynaptic"]),
        )

        if pair not in historical_by_pair:
            refuse(
                f"SQ-07 registry edge absent from frozen FULL13 lesion: {pair}"
            )

        resolved.append(historical_by_pair[pair])

    resolved_pairs = {
        (pre, post)
        for pre, post, _ in resolved
    }

    historical_pairs = set(historical_by_pair)

    if resolved_pairs != historical_pairs:
        refuse("SQ-07 registry does not exactly equal frozen FULL13 edge set")

    if len(resolved) != len(resolved_pairs):
        refuse("SQ-07 registry contains duplicate target coordinates")

    return tuple(resolved)


def selected_edges_for_mask(
    mask13: str,
    resolved_edges: tuple[tuple[int, int, float], ...] | None = None,
) -> tuple[tuple[int, int, float], ...]:
    validate_mask(mask13)

    edges = resolve_registry_edges() if resolved_edges is None else resolved_edges

    if len(edges) != MASK_WIDTH:
        refuse("SQ-07 resolved edge universe must contain exactly 13 edges")

    return tuple(
        edge
        for bit, edge in zip(mask13, edges)
        if bit == "1"
    )


def verify_exact_mask_subset(
    baseline: sparse.csr_matrix,
    candidate: sparse.csr_matrix,
    selected_edges: tuple[tuple[int, int, float], ...],
) -> None:
    if baseline.shape != candidate.shape:
        refuse("SQ-07 subset operator changed connectome shape")

    expected_nnz = baseline.nnz - len(selected_edges)

    if candidate.nnz != expected_nnz:
        refuse(
            "SQ-07 subset operator changed unexpected edge count: "
            f"{candidate.nnz} != {expected_nnz}"
        )

    expected_pairs = {
        (int(pre), int(post))
        for pre, post, _ in selected_edges
    }

    if len(expected_pairs) != len(selected_edges):
        refuse("SQ-07 selected subset contains duplicate edge coordinates")

    diff = (baseline != candidate).tocoo()

    observed_pairs = {
        (int(col), int(row))
        for row, col in zip(diff.row, diff.col)
    }

    if observed_pairs != expected_pairs:
        refuse("SQ-07 subset operator changed unexpected edge identities")

    for pre, post, expected_weight in selected_edges:
        before = float(baseline[post, pre])
        after = float(candidate[post, pre])

        if not np.isclose(
            before,
            expected_weight,
            rtol=1e-6,
            atol=1e-12,
        ):
            refuse(
                f"SQ-07 baseline weight mismatch for {pre}->{post}: "
                f"{before} != {expected_weight}"
            )

        if after != 0.0:
            refuse(f"SQ-07 failed to zero {pre}->{post}")


def build_mask_subset(
    baseline: sparse.csr_matrix,
    mask13: str,
    resolved_edges: tuple[tuple[int, int, float], ...] | None = None,
) -> tuple[sparse.csr_matrix, dict]:
    validate_mask(mask13)

    edges = resolve_registry_edges() if resolved_edges is None else resolved_edges

    selected = selected_edges_for_mask(mask13, edges)

    candidate = zero_edges(
        baseline,
        selected,
    )

    verify_exact_mask_subset(
        baseline,
        candidate,
        selected,
    )

    selected_indices = [
        i
        for i, bit in enumerate(mask13)
        if bit == "1"
    ]

    provenance = {
        "artifact": "sq07-the-maw-mask-subset-v1",
        "mask13": mask13,
        "selected_edge_count": len(selected),
        "selected_edge_indices": selected_indices,
        "selected_edge_ids": [
            f"E{i:02d}"
            for i in selected_indices
        ],
        "edge_registry_sha256": EXPECTED_REGISTRY_SHA256,
        "sq05_betrayal_i_source_sha256": EXPECTED_SQ05_BETRAYAL_I_SHA256,
        "mq32_zero_edge_operator_sha256": EXPECTED_MQ32_OPERATOR_SHA256,
        "historical_causal_artifact_sha256": b1.CAUSAL_SHA256,
        "neural_execution_authorized_here": False,
        "result_execution_authorized_here": False,
    }

    return candidate, provenance
