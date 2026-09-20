from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
import hashlib
import json
import math
import subprocess

import numpy as np
import pandas as pd

from brain.sq03e_analyze import exact_top_k
from brain.sq03f1_analyze import (
    ROOT,
    SQ03F_RESULT,
    SQ03E_RESULT,
    SQ03B_LEDGER,
    FEATHER,
    assign_equal_count_deciles,
    rebuild_pair_rows,
    build_candidate_edges,
)

CFG_PATH = ROOT / "config" / "experiments" / "sq03f3_made_men_v1.json"
SQ03F2_RESULT = ROOT / "artifacts" / "sidequests" / "sq03f2-capo-test-result-v1.json"
OUTPUT = ROOT / "artifacts" / "sidequests" / "sq03f3-made-men-result-v1.json"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git_head() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()


def require_clean_worktree() -> None:
    status = subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    )
    if status.strip():
        raise RuntimeError("Refusing SQ-03F.3 analysis with dirty worktree")


def percentile_rank(null_values, observed):
    arr = np.asarray(null_values, dtype=float)
    return float(np.mean(arr <= float(observed)))


def quantile(null_values, q):
    return float(np.quantile(np.asarray(null_values, dtype=float), q))


def observed_metrics(selected_rows, contexts_by_edge):
    counts = Counter(str(r["pre"]) for r in selected_rows)
    total = len(selected_rows)
    unique_sources = len(counts)

    repeated_fraction = (
        sum(1 for r in selected_rows if counts[str(r["pre"])] >= 2) / total
        if total else 0.0
    )

    values = np.asarray(list(counts.values()), dtype=float)
    shares = values / values.sum()

    context_sets = defaultdict(set)
    for r in selected_rows:
        source = str(r["pre"])
        for sig in contexts_by_edge[int(r["edge_id"])]:
            context_sets[source].add(sig)

    distinct_context_counts = [len(v) for v in context_sets.values()]

    return {
        "unique_hotspot_source_count": unique_sources,
        "fraction_hotspot_edges_repeated_source": repeated_fraction,
        "max_hotspot_edges_one_source": int(values.max()) if len(values) else 0,
        "source_count_hhi": float(np.sum(shares ** 2)) if len(shares) else 0.0,
        "median_hotspot_edges_per_source": float(np.median(values)) if len(values) else 0.0,
        "top1_source_share": float(np.sort(shares)[-1]) if len(shares) else 0.0,
        "top5_source_share": float(np.sort(shares)[-5:].sum()) if len(shares) else 0.0,
        "sources_with_2plus_context_signatures": sum(x >= 2 for x in distinct_context_counts),
        "max_distinct_context_signatures_one_source": max(distinct_context_counts) if distinct_context_counts else 0,
    }


def context_signatures(pair_rows):
    by_edge = defaultdict(set)
    for row in pair_rows:
        edge_id = int(row["edge_id"])
        by_edge[edge_id].add((str(row["input"]), str(row["anchor"])))
    return by_edge


def opportunity_audit(rows, contexts_by_edge):
    out = defaultdict(lambda: {
        "candidate_edge_count": 0,
        "sum_context_count": 0,
        "contexts": set(),
    })

    for r in rows:
        source = str(r["pre"])
        d = out[source]
        d["candidate_edge_count"] += 1
        d["sum_context_count"] += int(r["context_count"])
        d["contexts"].update(contexts_by_edge[int(r["edge_id"])])

    edge_counts = [v["candidate_edge_count"] for v in out.values()]
    context_sums = [v["sum_context_count"] for v in out.values()]
    distinct_contexts = [len(v["contexts"]) for v in out.values()]

    return {
        "source_count": len(out),
        "candidate_edge_count_per_source": {
            "median": float(np.median(edge_counts)),
            "max": int(max(edge_counts)),
        },
        "sum_candidate_context_count_per_source": {
            "median": float(np.median(context_sums)),
            "max": int(max(context_sums)),
        },
        "distinct_candidate_context_signatures_per_source": {
            "median": float(np.median(distinct_contexts)),
            "max": int(max(distinct_contexts)),
        },
    }


def build_strata(rows):
    strata = defaultdict(list)
    for r in rows:
        key = (
            int(r["context_count"]),
            int(r["total_weight_decile"]),
            int(r["abs_weight_difference_decile"]),
        )
        strata[key].append(r)
    return strata


def hotspot_counts_by_stratum(hotspot_rows):
    counts = Counter()
    for r in hotspot_rows:
        key = (
            int(r["context_count"]),
            int(r["total_weight_decile"]),
            int(r["abs_weight_difference_decile"]),
        )
        counts[key] += 1
    return counts


def randomize(strata, hotspot_counts, iterations, seed, contexts_by_edge):
    rng = np.random.default_rng(seed)

    metric_names = [
        "unique_hotspot_source_count",
        "fraction_hotspot_edges_repeated_source",
        "max_hotspot_edges_one_source",
        "source_count_hhi",
        "median_hotspot_edges_per_source",
        "top1_source_share",
        "top5_source_share",
        "sources_with_2plus_context_signatures",
        "max_distinct_context_signatures_one_source",
    ]
    nulls = {name: [] for name in metric_names}

    strata_items = []
    for key in sorted(hotspot_counts):
        n_hot = int(hotspot_counts[key])
        universe = strata[key]
        if n_hot > len(universe):
            raise RuntimeError(f"hotspot count exceeds stratum universe for {key}")
        edge_indices = np.arange(len(universe))
        strata_items.append((universe, edge_indices, n_hot))

    for _ in range(iterations):
        selected = []
        for universe, edge_indices, n_hot in strata_items:
            picks = rng.choice(edge_indices, size=n_hot, replace=False)
            selected.extend(universe[int(i)] for i in picks)

        metrics = observed_metrics(selected, contexts_by_edge)
        for name in metric_names:
            nulls[name].append(metrics[name])

    return nulls


def summarize_randomization(observed, nulls):
    out = {}
    for name, obs in observed.items():
        vals = nulls[name]
        med = quantile(vals, 0.5)
        out[name] = {
            "observed": obs,
            "null_median": med,
            "null_p05": quantile(vals, 0.05),
            "null_p95": quantile(vals, 0.95),
            "observed_over_null_median": (
                float(obs) / med if med not in (0, 0.0) else None
            ),
            "descriptive_null_percentile_rank": percentile_rank(vals, obs),
        }
    return out


def main() -> int:
    require_clean_worktree()

    if OUTPUT.exists():
        raise RuntimeError(f"Refusing to overwrite existing SQ-03F.3 result: {OUTPUT}")

    cfg = json.loads(CFG_PATH.read_text())
    if cfg["status"] != "FROZEN_BEFORE_ANALYSIS":
        raise RuntimeError("Unexpected SQ-03F.3 protocol status")

    if sha256(SQ03F2_RESULT) != cfg["parent"]["sq03f2_result_sha256"]:
        raise RuntimeError("SQ-03F.2 parent hash mismatch")

    sq03f = json.loads(SQ03F_RESULT.read_text())
    sq03e = json.loads(SQ03E_RESULT.read_text())

    pair_rows = rebuild_pair_rows(SQ03B_LEDGER)
    contexts_by_edge = context_signatures(pair_rows)

    aligned = pd.read_feather(FEATHER)
    mask = (
        (aligned["verdict_corr"] == "isomorphic")
        & (aligned["weight_m"] > 0)
        & (aligned["weight_f"] > 0)
    )
    matched = aligned.loc[mask].copy()
    matched["original_feather_row"] = matched.index.astype(int)
    matched = matched.reset_index(drop=True)

    rows = build_candidate_edges(pair_rows, matched)

    if len(rows) != int(cfg["universe"]["candidate_edges"]):
        raise RuntimeError("candidate universe differs from frozen SQ-03F.3 protocol")

    total_bin = assign_equal_count_deciles(rows, lambda r: r["total_weight"])
    diff_bin = assign_equal_count_deciles(rows, lambda r: r["abs_weight_difference"])
    for r in rows:
        r["total_weight_decile"] = total_bin[int(r["edge_id"])]
        r["abs_weight_difference_decile"] = diff_bin[int(r["edge_id"])]

    frac = float(sq03f["hotspot_fraction"])
    hot_s = exact_top_k(rows, lambda r: r["max_integrated_S"], frac)
    hot_c = exact_top_k(rows, lambda r: r["max_integrated_C"], frac)

    # Frozen identity gate.
    if [int(r["edge_id"]) for r in hot_s[:100]] != [
        int(r["edge_id"]) for r in sq03e["top100_dynamic_S"]
    ]:
        raise RuntimeError("S hotspot ranking mismatch")
    if [int(r["edge_id"]) for r in hot_c[:100]] != [
        int(r["edge_id"]) for r in sq03e["top100_dynamic_C"]
    ]:
        raise RuntimeError("C hotspot ranking mismatch")

    strata = build_strata(rows)

    iterations = int(cfg["null_model"]["iterations"])
    seed = int(cfg["null_model"]["seed"])

    obs_s = observed_metrics(hot_s, contexts_by_edge)
    obs_c = observed_metrics(hot_c, contexts_by_edge)

    s_counts = hotspot_counts_by_stratum(hot_s)
    c_counts = hotspot_counts_by_stratum(hot_c)

    null_s = randomize(strata, s_counts, iterations, seed, contexts_by_edge)
    null_c = randomize(strata, c_counts, iterations, seed + 1, contexts_by_edge)

    result_s = summarize_randomization(obs_s, null_s)
    result_c = summarize_randomization(obs_c, null_c)

    artifact = {
        "schema": "moscaquant.sq03f3_result/v1",
        "sidequest_id": "SQ-03F.3",
        "title": "MADE MEN",
        "classification": "AUTHORITATIVE_SOURCE_RECURRENCE_RANDOMIZATION_RESULT",
        "source_commit": git_head(),
        "protocol_sha256": sha256(CFG_PATH),
        "sq03f2_result_sha256": sha256(SQ03F2_RESULT),
        "sq03f_result_sha256": sha256(SQ03F_RESULT),
        "sq03e_result_sha256": sha256(SQ03E_RESULT),
        "sq03b_ledger_sha256": sha256(SQ03B_LEDGER),
        "aligned_edges_sha256": sha256(FEATHER),
        "candidate_edge_count": len(rows),
        "hotspot_k": len(hot_s),
        "null_model": {
            "iterations": iterations,
            "seed_S": seed,
            "seed_C": seed + 1,
            "strata": cfg["null_model"]["strata"],
        },
        "opportunity_audit": opportunity_audit(rows, contexts_by_edge),
        "S_hotspots": {
            "observed_metrics": obs_s,
            "randomization": result_s,
            "hotspot_stratum_count": len(s_counts),
        },
        "C_hotspots": {
            "observed_metrics": obs_c,
            "randomization": result_c,
            "hotspot_stratum_count": len(c_counts),
        },
        "claim_boundary": cfg["claim_boundary"],
        "family_model": cfg["family_model"],
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n")

    print("SQ-03F.3 — MADE MEN")
    print("=" * 72)
    print("candidate edges:", len(rows))
    print("hotspot k:", len(hot_s))
    print("randomizations per hotspot set:", iterations)
    print()

    for label, obs, result in (
        ("S", obs_s, result_s),
        ("C", obs_c, result_c),
    ):
        print(f"{label} HOTSPOTS")
        for name in obs:
            rec = result[name]
            print(
                f"  {name:42s} "
                f"obs={rec['observed']!s:>12} "
                f"null50={rec['null_median']!s:>12} "
                f"[{rec['null_p05']!s}, {rec['null_p95']!s}] "
                f"pct={rec['descriptive_null_percentile_rank']:.6f}"
            )
        print()

    print("artifact:", OUTPUT)
    print("No new neural dynamics were executed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
