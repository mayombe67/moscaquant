from __future__ import annotations

from pathlib import Path
import argparse
import json
import time

import numpy as np

from brain.hybrid_runtime import HybridRuntimeConfig
from brain.sq03a_matched_runtime import build_matched_graph, run_single
from brain.sq03b_batched_engine import EdgeSwap, run_batched_edge_swaps

ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = ROOT / "artifacts" / "sidequests" / "sq03b-candidate-edges-v1.json"
FEATHER = Path.home() / "moscaquant-data" / "external" / "mq002" / "mcns_fw_edge_comp.feather"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch-size", type=int, default=64)
    ap.add_argument("--input", default="TmY14")
    args = ap.parse_args()

    if args.batch_size < 1:
        raise SystemExit("--batch-size must be >= 1")

    candidate = json.loads(CANDIDATES.read_text())
    graph = build_matched_graph(FEATHER)

    input_label = args.input
    anchors = candidate["frozen_anchors"]

    edge_rows = []
    for edge in candidate["candidate_edges"]:
        if any(m["input"] == input_label for m in edge["memberships"]):
            edge_rows.append(edge)
        if len(edge_rows) >= args.batch_size:
            break

    if len(edge_rows) < args.batch_size:
        raise RuntimeError(
            f"only found {len(edge_rows)} candidates for {input_label}"
        )

    swaps = [
        EdgeSwap(
            pre=graph.index[e["pre"]],
            post=graph.index[e["post"]],
            baseline_weight=float(e["weight_m"]) / graph.scale,
            counterfactual_weight=float(e["weight_f"]) / graph.scale,
        )
        for e in edge_rows
    ]

    cfg = HybridRuntimeConfig(
        dt_ms=1.0,
        tau_ms=20.0,
        threshold=1.0,
        reset_voltage=0.0,
    )

    anchor_idx = np.asarray([graph.index[x] for x in anchors], dtype=np.int64)

    start = time.perf_counter()
    traces_a, _ = run_batched_edge_swaps(
        matrix=graph.male,
        swaps=swaps,
        input_index=graph.index[input_label],
        anchor_indices=anchor_idx,
        frames=64,
        stimulus_frame=0,
        stimulus_amplitude=0.5,
        config=cfg,
    )
    first_seconds = time.perf_counter() - start

    start = time.perf_counter()
    traces_b, _ = run_batched_edge_swaps(
        matrix=graph.male,
        swaps=swaps,
        input_index=graph.index[input_label],
        anchor_indices=anchor_idx,
        frames=64,
        stimulus_frame=0,
        stimulus_amplitude=0.5,
        config=cfg,
    )
    replay_seconds = time.perf_counter() - start

    exact = np.array_equal(traces_a, traces_b)
    if not exact:
        raise RuntimeError("batched A/A replay mismatch")

    # Scalar parity for the first candidate only.
    e = edge_rows[0]
    scalar_matrix = graph.male.copy().tolil()
    pre = graph.index[e["pre"]]
    post = graph.index[e["post"]]
    scalar_matrix[post, pre] = np.float32(float(e["weight_f"]) / graph.scale)
    scalar_matrix = scalar_matrix.tocsr()

    scalar = run_single(
        matrix=scalar_matrix,
        graph=graph,
        input_label=input_label,
        anchor_labels=anchors,
        frames=64,
        stimulus_frame=0,
        stimulus_amplitude=0.5,
        runtime_cfg=cfg,
    )

    batched_first = traces_a[:, :, 0]
    scalar_trace = np.asarray(
        [
            [scalar["anchor_metrics"][a]["trace"][f] for a in anchors]
            for f in range(64)
        ],
        dtype=np.float32,
    )

    exact_parity = np.array_equal(batched_first, scalar_trace)
    max_abs_error = float(np.max(np.abs(batched_first - scalar_trace)))
    numerical_parity = np.allclose(
        batched_first,
        scalar_trace,
        rtol=1e-6,
        atol=1e-7,
    )

    print("SQ-03B BATCH ENGINE BENCHMARK")
    print("=" * 72)
    print("input:", input_label)
    print("batch size:", args.batch_size)
    print("frames:", 64)
    print("first batch seconds:", f"{first_seconds:.3f}")
    print("A/A batch seconds:", f"{replay_seconds:.3f}")
    print("batched A/A exact:", exact)
    print("scalar parity first candidate exact:", exact_parity)
    print("scalar parity first candidate numerical:", numerical_parity)
    print("scalar parity max abs error:", f"{max_abs_error:.12g}")

    jobs = candidate["candidate_edge_count"]
    logical_per_second = args.batch_size / first_seconds if first_seconds else 0.0
    print("logical counterfactuals/sec for this batch:", f"{logical_per_second:.3f}")
    print()
    print("ENGINEERING BENCHMARK ONLY.")
    print("No SQ-03B localization result artifact was written.")

    if not numerical_parity:
        raise SystemExit(
            "FAIL: batched engine exceeds frozen numerical-parity tolerance "
            "against scalar HybridRuntime for the first real candidate."
        )


if __name__ == "__main__":
    main()
