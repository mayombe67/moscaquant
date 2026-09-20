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
    rebuild_pair_rows,
    build_candidate_edges,
)
from brain.sq03f2_analyze import source_profiles
from brain.sq03f3_analyze import context_signatures

CFG_PATH = ROOT / "config" / "experiments" / "sq03f4_sit_down_v1.json"
SQ03F3_RESULT = ROOT / "artifacts" / "sidequests" / "sq03f3-made-men-result-v1.json"
OUTPUT = ROOT / "artifacts" / "sidequests" / "sq03f4-sit-down-result-v1.json"


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
        raise RuntimeError("Refusing SQ-03F.4 analysis with dirty worktree")


def finite(x) -> bool:
    return x is not None and math.isfinite(float(x))


def median(values):
    vals = [float(v) for v in values if finite(v)]
    return float(np.median(vals)) if vals else None


def equal_count_bins(records, key, bins=10):
    ordered = sorted(records, key=lambda r: (float(r[key]), str(r["source"])))
    n = len(ordered)
    out = {}
    for rank, row in enumerate(ordered):
        b = min(bins, (rank * bins) // n + 1)
        out[str(row["source"])] = int(b)
    return out


def build_source_opportunities(candidate_rows, contexts_by_edge):
    d = defaultdict(lambda: {
        "candidate_edge_count": 0,
        "sum_candidate_context_count": 0,
        "contexts": set(),
    })
    for row in candidate_rows:
        source = str(row["pre"])
        x = d[source]
        x["candidate_edge_count"] += 1
        x["sum_candidate_context_count"] += int(row["context_count"])
        x["contexts"].update(contexts_by_edge[int(row["edge_id"])])

    records = []
    for source, x in d.items():
        records.append({
            "source": source,
            "candidate_edge_count": int(x["candidate_edge_count"]),
            "sum_candidate_context_count": int(x["sum_candidate_context_count"]),
            "distinct_candidate_context_signature_count": int(len(x["contexts"])),
        })

    edge_bins = equal_count_bins(records, "candidate_edge_count")
    sum_bins = equal_count_bins(records, "sum_candidate_context_count")
    ctx_bins = equal_count_bins(records, "distinct_candidate_context_signature_count")

    for row in records:
        source = row["source"]
        row["candidate_edge_count_decile"] = edge_bins[source]
        row["sum_candidate_context_count_decile"] = sum_bins[source]
        row["distinct_candidate_context_signature_count_decile"] = ctx_bins[source]

    return {r["source"]: r for r in records}


def build_source_features(matched, profiles):
    targets = defaultdict(set)
    for _, row in matched.iterrows():
        targets[str(row["pre"])].add(str(row["post"]))

    out = {}
    for source, p in profiles.items():
        count = int(p["source_out_edge_count"])
        strength = float(p["source_out_strength"])
        target_count = len(targets[source])
        out[source] = {
            "source_out_strength": strength,
            "source_mean_outgoing_weight": strength / count,
            "source_max_outgoing_weight": float(p["source_max_outgoing_weight"]),
            "source_out_edge_count": count,
            "source_median_outgoing_weight": float(p["source_median_outgoing_weight"]),
            "source_top1_output_share": float(p["source_top1_output_share"]),
            "source_top5_output_share": float(p["source_top5_output_share"]),
            "source_output_hhi": float(p["source_output_hhi"]),
            "distinct_downstream_target_count": int(target_count),
            "source_target_diversity_ratio": float(target_count / count),
        }
    return out


PRIMARY = [
    "source_out_strength",
    "source_mean_outgoing_weight",
    "source_max_outgoing_weight",
    "source_out_edge_count",
]

SECONDARY = [
    "source_median_outgoing_weight",
    "source_top1_output_share",
    "source_top5_output_share",
    "source_output_hhi",
    "distinct_downstream_target_count",
    "source_target_diversity_ratio",
]


def made_sources(candidate_sources, hotspot_rows):
    counts = Counter(str(r["pre"]) for r in hotspot_rows)
    k = int(math.ceil(len(candidate_sources) * 0.01))
    eligible = [
        (source, int(counts.get(source, 0)))
        for source in candidate_sources
        if counts.get(source, 0) > 0
    ]
    eligible.sort(key=lambda x: (-x[1], x[0]))
    if len(eligible) < k:
        raise RuntimeError(f"only {len(eligible)} hotspot-producing sources for k={k}")
    return [s for s, _ in eligible[:k]], counts, k


def exact_match_controls(made, opportunities, hotspot_counts):
    made_set = set(made)
    available = set(opportunities) - made_set
    pairs = []
    unmatched = []

    made_order = sorted(
        made,
        key=lambda s: (-int(hotspot_counts.get(s, 0)), s),
    )

    for source in made_order:
        m = opportunities[source]
        key = (
            m["candidate_edge_count_decile"],
            m["sum_candidate_context_count_decile"],
            m["distinct_candidate_context_signature_count_decile"],
        )

        candidates = []
        for ctl in available:
            c = opportunities[ctl]
            ckey = (
                c["candidate_edge_count_decile"],
                c["sum_candidate_context_count_decile"],
                c["distinct_candidate_context_signature_count_decile"],
            )
            if ckey != key:
                continue
            candidates.append((
                abs(m["candidate_edge_count"] - c["candidate_edge_count"]),
                abs(m["sum_candidate_context_count"] - c["sum_candidate_context_count"]),
                abs(
                    m["distinct_candidate_context_signature_count"]
                    - c["distinct_candidate_context_signature_count"]
                ),
                ctl,
            ))

        if not candidates:
            unmatched.append(source)
            continue

        candidates.sort()
        ctl = candidates[0][3]
        available.remove(ctl)
        pairs.append((source, ctl))

    return pairs, unmatched


def summarize_pairs(pairs, source_features, feature):
    vals = []
    for made, ctl in pairs:
        a = source_features[made][feature]
        b = source_features[ctl][feature]
        if finite(a) and finite(b):
            vals.append((float(a), float(b)))

    av = [a for a, _ in vals]
    bv = [b for _, b in vals]
    diffs = [a - b for a, b in vals]
    return {
        "valid_pair_count": len(vals),
        "made_source_median": median(av),
        "matched_control_median": median(bv),
        "median_paired_difference": median(diffs),
        "fraction_made_gt_control": (
            sum(a > b for a, b in vals) / len(vals) if vals else None
        ),
    }


def audit_bins(pairs, opportunities):
    for made, ctl in pairs:
        m = opportunities[made]
        c = opportunities[ctl]
        for key in (
            "candidate_edge_count_decile",
            "sum_candidate_context_count_decile",
            "distinct_candidate_context_signature_count_decile",
        ):
            if m[key] != c[key]:
                return False
    return True


def analyze_set(made, counts, k, opportunities, source_features):
    pairs, unmatched = exact_match_controls(made, opportunities, counts)
    summaries = {
        feature: summarize_pairs(pairs, source_features, feature)
        for feature in PRIMARY + SECONDARY
    }

    return {
        "made_source_k": k,
        "matched_count": len(pairs),
        "unmatched_count": len(unmatched),
        "exact_opportunity_bin_check": audit_bins(pairs, opportunities),
        "made_sources": [
            {
                "source": s,
                "hotspot_edge_count": int(counts[s]),
                "opportunity": opportunities[s],
            }
            for s in made
        ],
        "unmatched_sources": unmatched,
        "feature_summaries": summaries,
    }


def main() -> int:
    require_clean_worktree()

    if OUTPUT.exists():
        raise RuntimeError(f"Refusing to overwrite existing result: {OUTPUT}")

    cfg = json.loads(CFG_PATH.read_text())
    if cfg["status"] != "FROZEN_BEFORE_ANALYSIS":
        raise RuntimeError("Unexpected SQ-03F.4 protocol status")
    if sha256(SQ03F3_RESULT) != cfg["parent"]["sq03f3_result_sha256"]:
        raise RuntimeError("SQ-03F.3 parent hash mismatch")

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

    candidate_rows = build_candidate_edges(pair_rows, matched)
    candidate_sources = sorted({str(r["pre"]) for r in candidate_rows})

    opportunities = build_source_opportunities(candidate_rows, contexts_by_edge)
    if set(candidate_sources) != set(opportunities):
        raise RuntimeError("candidate source opportunity universe mismatch")

    profiles = source_profiles(matched)
    source_features = build_source_features(matched, profiles)

    missing_profiles = sorted(set(candidate_sources) - set(source_features))
    if missing_profiles:
        raise RuntimeError(
            f"candidate sources missing conservative source profiles: {missing_profiles[:10]}"
        )

    frac = float(sq03f["hotspot_fraction"])
    hot_s = exact_top_k(candidate_rows, lambda r: r["max_integrated_S"], frac)
    hot_c = exact_top_k(candidate_rows, lambda r: r["max_integrated_C"], frac)

    if [int(r["edge_id"]) for r in hot_s[:100]] != [
        int(r["edge_id"]) for r in sq03e["top100_dynamic_S"]
    ]:
        raise RuntimeError("S hotspot ranking mismatch")
    if [int(r["edge_id"]) for r in hot_c[:100]] != [
        int(r["edge_id"]) for r in sq03e["top100_dynamic_C"]
    ]:
        raise RuntimeError("C hotspot ranking mismatch")

    made_s, counts_s, k_s = made_sources(candidate_sources, hot_s)
    made_c, counts_c, k_c = made_sources(candidate_sources, hot_c)

    if k_s != k_c:
        raise RuntimeError("S/C made-source k mismatch")

    result_s = analyze_set(
        made_s, counts_s, k_s, opportunities, source_features
    )
    result_c = analyze_set(
        made_c, counts_c, k_c, opportunities, source_features
    )

    overlap = sorted(set(made_s) & set(made_c))

    artifact = {
        "schema": "moscaquant.sq03f4_result/v1",
        "sidequest_id": "SQ-03F.4",
        "title": "THE SIT-DOWN",
        "classification": "AUTHORITATIVE_SOURCE_LEVEL_MATCHED_RECURRENCE_PHENOTYPE",
        "source_commit": git_head(),
        "protocol_sha256": sha256(CFG_PATH),
        "sq03f3_result_sha256": sha256(SQ03F3_RESULT),
        "sq03f_result_sha256": sha256(SQ03F_RESULT),
        "sq03e_result_sha256": sha256(SQ03E_RESULT),
        "sq03b_ledger_sha256": sha256(SQ03B_LEDGER),
        "aligned_edges_sha256": sha256(FEATHER),
        "candidate_edge_count": len(candidate_rows),
        "candidate_source_count": len(candidate_sources),
        "conservative_graph_edge_count": len(matched),
        "made_source_k": k_s,
        "S_hotspots": result_s,
        "C_hotspots": result_c,
        "S_C_made_source_overlap": {
            "count": len(overlap),
            "fraction_of_k": len(overlap) / k_s if k_s else None,
            "sources": overlap,
        },
        "claim_boundary": cfg["claim_boundary"],
        "family_model": cfg["family_model"],
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n")

    print("SQ-03F.4 — THE SIT-DOWN")
    print("=" * 72)
    print("candidate edges:", len(candidate_rows))
    print("candidate sources:", len(candidate_sources))
    print("made-source k:", k_s)
    print(
        "S/C made overlap:",
        f"{len(overlap)}/{k_s}",
        f"({len(overlap)/k_s:.4f})" if k_s else "",
    )
    print()

    for label, result in (("S", result_s), ("C", result_c)):
        print(f"{label} MADE SOURCES")
        print(
            "  matched:",
            f"{result['matched_count']}/{result['made_source_k']}",
            "unmatched:",
            result["unmatched_count"],
        )
        print(
            "  exact opportunity bins:",
            result["exact_opportunity_bin_check"],
        )
        for feature in PRIMARY + SECONDARY:
            x = result["feature_summaries"][feature]
            print(
                f"  {feature:38s} "
                f"made={x['made_source_median']!s:>12} "
                f"ctl={x['matched_control_median']!s:>12} "
                f"medΔ={x['median_paired_difference']!s:>12} "
                f"P(made>ctl)={x['fraction_made_gt_control']!s}"
            )
        print()

    print("artifact:", OUTPUT)
    print("No new neural dynamics were executed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
