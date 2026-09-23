#!/usr/bin/env python3
from __future__ import annotations

import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from brain import mq5_er5_the_greek_runner as g


def main() -> None:
    print("=== AKSIS RETRY 8 — NON-RESULT PERFORMANCE PROBE ===")
    print("NO --run-frozen")
    print("NO result artifact")
    print("NO ledger mutation")
    print("NO S3 export")
    print()

    t0 = time.perf_counter()
    _original, c13, _retina, _responders = g.load_c13()
    print("load_c13_seconds:", round(time.perf_counter() - t0, 3))

    all_targets = g.AFFECTED_TARGETS + g.RETAINED_TARGETS

    t0 = time.perf_counter()
    distances = {
        int(target): g.reverse_shortest_distances(
            c13,
            int(target),
            g.MAX_BACKWARD_HOPS,
        )
        for target in all_targets
    }
    print("candidate_distance_precompute_seconds:", round(time.perf_counter() - t0, 3))

    candidates = set()
    for target in all_targets:
        candidates.update(distances[int(target)].keys())
    candidates.difference_update(
        set(g.ALL_TARGETS)
        | {11725, 29921, 11345, 47350, 10647, 51642}
    )
    candidates = sorted(candidates)
    print("candidate_count:", len(candidates))

    t0 = time.perf_counter()
    csc, to_target, branch_masks = g.build_first_hop_cache(
        c13,
        g.AFFECTED_TARGETS,
        g.MAX_BACKWARD_HOPS,
    )
    print("first_hop_cache_seconds:", round(time.perf_counter() - t0, 3))

    pair_count = 0
    branch_total = 0
    t0 = time.perf_counter()

    for node in candidates:
        for target in g.AFFECTED_TARGETS:
            if node not in distances[int(target)]:
                continue
            pair_count += 1
            branch_total += len(
                g.shortest_path_first_hops_cached(
                    csc,
                    int(node),
                    int(target),
                    to_target=to_target,
                    branch_masks=branch_masks,
                )
            )

    elapsed = time.perf_counter() - t0

    print("affected_candidate_target_pairs:", pair_count)
    print("cached_branch_scan_seconds:", round(elapsed, 3))
    print("cached_branch_memberships_total:", branch_total)
    if elapsed > 0:
        print("cached_pairs_per_second:", round(pair_count / elapsed, 1))

    print()
    print("result_execution:", False)
    print("scientific_authority_granted:", False)
    print("interpretation_allowed:", False)
    print("diagnostic_only:", True)


if __name__ == "__main__":
    main()
