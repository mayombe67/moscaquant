from __future__ import annotations

import argparse
import json
import time

import numpy as np

from brain.mq5_er1_detour_runner import (
    ALL_TRACE_TARGETS,
    C_BASELINE_ONSETS,
    load_inputs,
    score_target_streaming,
)

MAX_BACKWARD_HOPS = 3


def run_benchmark() -> dict:
    original, _lesioned, _retina, _responders, causal_edges = load_inputs()

    population_size = int(original.shape[0])

    synthetic_divergence = np.ones(population_size, dtype=np.float64)
    synthetic_persistence = np.ones(population_size, dtype=np.float64)

    lesioned_edge_set = {
        (int(pre), int(post))
        for pre, post, _weight in causal_edges
    }

    targets = {}
    total_start = time.perf_counter()

    for target in ALL_TRACE_TARGETS:
        start = time.perf_counter()

        result = score_target_streaming(
            original=original,
            lesioned_edges=lesioned_edge_set,
            target=int(target),
            onset=int(C_BASELINE_ONSETS[int(target)]),
            divergence_snapshot=synthetic_divergence,
            lesion_snapshot=synthetic_persistence,
            max_backward_hops=MAX_BACKWARD_HOPS,
        )

        elapsed = time.perf_counter() - start

        targets[str(target)] = {
            "target": int(target),
            "edge_visits": int(result["edge_visits"]),
            "elapsed_seconds": float(elapsed),
            "candidate_count_internal": len(result["top_candidates"]),
        }

    total_elapsed = time.perf_counter() - total_start

    return {
        "benchmark": "mq5-er1-detour-3hop-synthetic-stress-v1",
        "kind": "ENGINEERING BENCHMARK — NON-RESULT",
        "max_backward_hops": MAX_BACKWARD_HOPS,
        "synthetic_activity_inputs": True,
        "uses_parent_dynamic_activity": False,
        "candidate_identities_emitted": False,
        "authoritative": False,
        "scientific_result": False,
        "total_elapsed_seconds": float(total_elapsed),
        "targets": targets,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", action="store_true", required=True)
    parser.parse_args()

    print(json.dumps(
        run_benchmark(),
        indent=2,
        sort_keys=True,
        allow_nan=False,
    ))


if __name__ == "__main__":
    main()
