from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import numpy as np
from scipy import sparse

from brain.mq3_2_causal_intervention import zero_edges


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = Path(
    os.environ.get("MOSCAQUANT_DATA_ROOT", str(Path.home() / "moscaquant-data"))
).expanduser().resolve()

CAUSAL_ARTIFACT = DATA_ROOT / "processed/mq3-2-first-onset-causal-edges-v1.json"
MQ32_OPERATOR_SOURCE = ROOT / "brain/mq3_2_causal_intervention.py"

CAUSAL_SHA256 = "23cc19a39c30e554671bdf92b904865311d2f7df4dd9ef82af1eaf66638c3a2b"
MQ32_OPERATOR_SOURCE_SHA256 = "007aa507ac22b07811bff5ae8102a0916c88549aa3011fa22fa57c70598c6a87"
EDGE_COUNT = 13
TARGET_COUNT = 9


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_betrayal_i_edges() -> tuple[list[tuple[int, int, float]], dict]:
    if not CAUSAL_ARTIFACT.is_file():
        raise RuntimeError(f"missing BETRAYAL I causal artifact: {CAUSAL_ARTIFACT}")
    if _sha256_file(CAUSAL_ARTIFACT) != CAUSAL_SHA256:
        raise RuntimeError("BETRAYAL I causal artifact SHA mismatch")
    if _sha256_file(MQ32_OPERATOR_SOURCE) != MQ32_OPERATOR_SOURCE_SHA256:
        raise RuntimeError("BETRAYAL I lesion-operator source SHA mismatch")

    payload = json.loads(CAUSAL_ARTIFACT.read_text(encoding="utf-8"))
    if payload.get("artifact") != "mq3-2-first-onset-causal-edges-v1":
        raise RuntimeError("unexpected BETRAYAL I causal artifact id")
    if payload.get("post_hoc") is not True:
        raise RuntimeError("historical lesion-selection provenance drift")
    if payload.get("purpose") != "confirmatory in-model causal intervention":
        raise RuntimeError("historical lesion purpose drift")

    edges = [
        (
            int(edge["presynaptic"]),
            int(edge["postsynaptic"]),
            float(edge["weight"]),
        )
        for edge in payload.get("edges", [])
    ]
    if len(edges) != EDGE_COUNT:
        raise RuntimeError(f"expected {EDGE_COUNT} BETRAYAL I edges")
    if len(payload.get("targets", [])) != TARGET_COUNT:
        raise RuntimeError(f"expected {TARGET_COUNT} BETRAYAL I targets")
    return edges, payload


def _verify_exact_lesion(
    baseline: sparse.csr_matrix,
    lesioned: sparse.csr_matrix,
    edges: list[tuple[int, int, float]],
) -> None:
    if baseline.shape != lesioned.shape:
        raise RuntimeError("BETRAYAL I changed connectome shape")

    if lesioned.nnz != baseline.nnz - len(edges):
        raise RuntimeError("BETRAYAL I changed unexpected edge count")

    expected_pairs = {(int(pre), int(post)) for pre, post, _ in edges}

    diff = (baseline != lesioned).tocoo()
    observed_pairs = {
        (int(col), int(row))
        for row, col in zip(diff.row, diff.col)
    }
    if observed_pairs != expected_pairs:
        raise RuntimeError(
            "BETRAYAL I modified edges outside exact frozen lesion set"
        )

    for pre, post, expected_weight in edges:
        before = float(baseline[post, pre])
        after = float(lesioned[post, pre])
        if not np.isclose(before, expected_weight, rtol=1e-6, atol=1e-12):
            raise RuntimeError(f"BETRAYAL I baseline weight mismatch {pre}->{post}")
        if after != 0.0:
            raise RuntimeError(f"BETRAYAL I failed to zero {pre}->{post}")


def build_betrayal_i(
    baseline: sparse.csr_matrix,
):
    """Apply the exact inherited 13-edge MQ-3.2 causal-route lesion."""
    edges, payload = load_betrayal_i_edges()
    lesioned = zero_edges(baseline, edges)
    _verify_exact_lesion(baseline, lesioned, edges)

    provenance = {
        "arm": "BETRAYAL_I_LESIONED",
        "scope": "inherited_validated_causal_route_lesion",
        "causal_artifact_sha256": CAUSAL_SHA256,
        "mq3_2_operator_source_sha256": MQ32_OPERATOR_SOURCE_SHA256,
        "edge_count": EDGE_COUNT,
        "target_count": TARGET_COUNT,
        "historical_selection_post_hoc": True,
        "historical_purpose": payload["purpose"],
        "sq05_adoption": "prospective",
        "neural_execution_authorized_here": False,
        "result_execution_authorized_here": False,
    }
    return lesioned, provenance
