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
    CFG_PATH as SQ03F1_CFG_PATH,
    SQ03F_RESULT,
    SQ03E_RESULT,
    SQ03B_LEDGER,
    FEATHER,
    assign_equal_count_deciles,
    rebuild_pair_rows,
    build_candidate_edges,
    exact_context_match_controls,
)

CFG_PATH = ROOT / "config" / "experiments" / "sq03f2_capo_test_v1.json"
SQ03F1_RESULT = ROOT / "artifacts" / "sidequests" / "sq03f1-no-free-looks-result-v1.json"
OUTPUT = ROOT / "artifacts" / "sidequests" / "sq03f2-capo-test-result-v1.json"


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
        raise RuntimeError("Refusing SQ-03F.2 analysis with dirty worktree")


def finite(x) -> bool:
    return x is not None and math.isfinite(float(x))


def median(values):
    vals = [float(v) for v in values if finite(v)]
    return float(np.median(np.asarray(vals, dtype=float))) if vals else None


def source_profiles(matched: pd.DataFrame):
    """
    Build source-level profiles over every conservative matched edge row.

    Edge identity remains the positional index of the conservative matched table.
    Parallel pre->post rows, if any, remain distinct rows.
    """
    by_source = defaultdict(list)

    for edge_id, row in matched.iterrows():
        wm = float(row["weight_m"])
        wf = float(row["weight_f"])
        mean_weight = (wm + wf) / 2.0
        by_source[str(row["pre"])].append(
            {
                "edge_id": int(edge_id),
                "post": str(row["post"]),
                "mean_weight": mean_weight,
            }
        )

    profiles = {}

    for source, edges in by_source.items():
        weights = np.asarray([e["mean_weight"] for e in edges], dtype=float)
        n = len(edges)
        total = float(weights.sum())
        ordered = np.sort(weights)[::-1]

        if total <= 0:
            raise RuntimeError(f"non-positive source total for {source}")

        profiles[source] = {
            "source_out_edge_count": n,
            "source_out_strength": total,
            "source_median_outgoing_weight": float(np.median(weights)),
            "source_max_outgoing_weight": float(weights.max()),
            "source_top1_output_share": float(ordered[:1].sum() / total),
            "source_top5_output_share": float(ordered[:5].sum() / total),
            "source_output_hhi": float(np.sum((weights / total) ** 2)),
            "_weights": weights,
            "_edge_ids": [e["edge_id"] for e in edges],
        }

    return profiles


def focal_source_features(row, profiles):
    source = str(row["pre"])
    edge_id = int(row["edge_id"])
    focal_weight = float(row["mean_weight"])

    p = profiles[source]
    n = int(p["source_out_edge_count"])
    total = float(p["source_out_strength"])

    if edge_id not in p["_edge_ids"]:
        raise RuntimeError(f"focal edge {edge_id} not present in source profile {source}")

    loo_strength = total - focal_weight
    loo_count = n - 1
    loo_mean = loo_strength / loo_count if loo_count > 0 else None

    weights = p["_weights"]
    less = int(np.sum(weights < focal_weight))
    equal = int(np.sum(weights == focal_weight))
    # Ascending midrank / N. 1.0 is strongest.
    percentile = (less + (equal + 1) / 2.0) / n

    return {
        "leave_one_edge_out_source_strength": float(loo_strength),
        "leave_one_edge_out_mean_outgoing_weight": (
            float(loo_mean) if loo_mean is not None else None
        ),
        "source_out_edge_count": n,
        "source_median_outgoing_weight": float(p["source_median_outgoing_weight"]),
        "source_max_outgoing_weight": float(p["source_max_outgoing_weight"]),
        "source_top1_output_share": float(p["source_top1_output_share"]),
        "source_top5_output_share": float(p["source_top5_output_share"]),
        "source_output_hhi": float(p["source_output_hhi"]),
        "focal_edge_output_rank_percentile": float(percentile),
        # Audit-only reproduction field:
        "source_out_strength": total,
    }


FEATURES = [
    "leave_one_edge_out_source_strength",
    "leave_one_edge_out_mean_outgoing_weight",
    "source_out_edge_count",
    "source_median_outgoing_weight",
    "source_max_outgoing_weight",
    "source_top1_output_share",
    "source_top5_output_share",
    "source_output_hhi",
    "focal_edge_output_rank_percentile",
]


def attach_source_features(rows, profiles):
    for row in rows:
        row["capo_features"] = focal_source_features(row, profiles)


def summarize_feature_pairs(pairs, feature):
    valid = []
    null_pairs = 0

    for p in pairs:
        h = p["hotspot"]["capo_features"][feature]
        c = p["control"]["capo_features"][feature]
        if finite(h) and finite(c):
            valid.append((float(h), float(c)))
        else:
            null_pairs += 1

    hv = [h for h, _ in valid]
    cv = [c for _, c in valid]
    diffs = [h - c for h, c in valid]

    return {
        "valid_pair_count": len(valid),
        "null_pair_count": null_pairs,
        "hotspot_median": median(hv),
        "control_median": median(cv),
        "median_paired_difference": median(diffs),
        "fraction_hotspot_gt_control": (
            sum(h > c for h, c in valid) / len(valid) if valid else None
        ),
    }


def unique_source_summary(rows):
    # Source-level metrics are identical for all focal edges except LOO and focal-rank,
    # so sensitivity reporting intentionally uses only source-intrinsic metrics.
    by_source = {}
    for r in rows:
        source = str(r["pre"])
        f = r["capo_features"]
        by_source.setdefault(
            source,
            {
                "source_out_strength": f["source_out_strength"],
                "source_out_edge_count": f["source_out_edge_count"],
                "source_median_outgoing_weight": f["source_median_outgoing_weight"],
                "source_max_outgoing_weight": f["source_max_outgoing_weight"],
                "source_top1_output_share": f["source_top1_output_share"],
                "source_top5_output_share": f["source_top5_output_share"],
                "source_output_hhi": f["source_output_hhi"],
            },
        )

    features = [
        "source_out_strength",
        "source_out_edge_count",
        "source_median_outgoing_weight",
        "source_max_outgoing_weight",
        "source_top1_output_share",
        "source_top5_output_share",
        "source_output_hhi",
    ]

    return {
        "unique_source_count": len(by_source),
        "medians": {
            feature: median([v[feature] for v in by_source.values()])
            for feature in features
        },
    }


def source_audit(hotspot_rows, control_rows):
    h_counts = Counter(str(r["pre"]) for r in hotspot_rows)
    c_counts = Counter(str(r["pre"]) for r in control_rows)

    shared_hotspot_edges = sum(
        1 for r in hotspot_rows if h_counts[str(r["pre"])] > 1
    )

    return {
        "unique_hotspot_source_count": len(h_counts),
        "unique_control_source_count": len(c_counts),
        "fraction_hotspot_edges_sharing_source": (
            shared_hotspot_edges / len(hotspot_rows) if hotspot_rows else None
        ),
        "hotspot_unique_source_sensitivity": unique_source_summary(hotspot_rows),
        "control_unique_source_sensitivity": unique_source_summary(control_rows),
    }


def reproduce_sq03f1_source_strength(pairs, expected):
    hv = [p["hotspot"]["capo_features"]["source_out_strength"] for p in pairs]
    cv = [p["control"]["capo_features"]["source_out_strength"] for p in pairs]
    diffs = [h - c for h, c in zip(hv, cv)]

    got = {
        "hotspot_median": median(hv),
        "control_median": median(cv),
        "median_paired_difference": median(diffs),
        "fraction_hotspot_gt_control": (
            sum(h > c for h, c in zip(hv, cv)) / len(pairs)
        ),
    }

    for key, value in got.items():
        if not math.isclose(
            float(value),
            float(expected[key]),
            rel_tol=1e-12,
            abs_tol=1e-12,
        ):
            raise RuntimeError(
                f"SQ-03F.1 source-out-strength reproduction failed for {key}: "
                f"{value} != {expected[key]}"
            )
    return got


def analyze_set(pairs, unmatched, expected_sq03f1):
    reproduction = reproduce_sq03f1_source_strength(
        pairs, expected_sq03f1["features"]["source_out_strength"]
    )

    hotspot_rows = [p["hotspot"] for p in pairs]
    control_rows = [p["control"] for p in pairs]

    return {
        "hotspot_count": len(pairs) + len(unmatched),
        "matched_count": len(pairs),
        "unmatched_count": len(unmatched),
        "matched_fraction": len(pairs) / (len(pairs) + len(unmatched)),
        "sq03f1_source_out_strength_reproduction": reproduction,
        "features": {
            feature: summarize_feature_pairs(pairs, feature)
            for feature in FEATURES
        },
        "source_audit": source_audit(hotspot_rows, control_rows),
        "unmatched": unmatched,
    }


def main() -> int:
    require_clean_worktree()

    if OUTPUT.exists():
        raise RuntimeError(f"Refusing to overwrite existing SQ-03F.2 result: {OUTPUT}")

    cfg = json.loads(CFG_PATH.read_text())
    if cfg["status"] != "FROZEN_BEFORE_ANALYSIS":
        raise RuntimeError("Unexpected SQ-03F.2 protocol status")

    if sha256(SQ03F1_RESULT) != cfg["parent"]["sq03f1_result_sha256"]:
        raise RuntimeError("SQ-03F.1 parent hash mismatch")

    sq03f1 = json.loads(SQ03F1_RESULT.read_text())
    sq03f = json.loads(SQ03F_RESULT.read_text())
    sq03e = json.loads(SQ03E_RESULT.read_text())

    pair_rows = rebuild_pair_rows(SQ03B_LEDGER)

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

    if len(rows) != int(sq03f["candidate_edge_count"]):
        raise RuntimeError("candidate universe differs from SQ-03F")

    total_bin = assign_equal_count_deciles(rows, lambda r: r["total_weight"])
    diff_bin = assign_equal_count_deciles(rows, lambda r: r["abs_weight_difference"])
    for r in rows:
        r["total_weight_decile"] = total_bin[int(r["edge_id"])]
        r["abs_weight_difference_decile"] = diff_bin[int(r["edge_id"])]

    profiles = source_profiles(matched)
    attach_source_features(rows, profiles)

    frac = float(sq03f["hotspot_fraction"])
    hot_s = exact_top_k(rows, lambda r: r["max_integrated_S"], frac)
    hot_c = exact_top_k(rows, lambda r: r["max_integrated_C"], frac)

    # Reproduce the frozen top ranking identities before matching.
    if [int(r["edge_id"]) for r in hot_s[:100]] != [
        int(r["edge_id"]) for r in sq03e["top100_dynamic_S"]
    ]:
        raise RuntimeError("S hotspot ranking mismatch")
    if [int(r["edge_id"]) for r in hot_c[:100]] != [
        int(r["edge_id"]) for r in sq03e["top100_dynamic_C"]
    ]:
        raise RuntimeError("C hotspot ranking mismatch")

    s_pairs, s_unmatched = exact_context_match_controls(
        rows, hot_s, "max_integrated_S"
    )
    c_pairs, c_unmatched = exact_context_match_controls(
        rows, hot_c, "max_integrated_C"
    )

    # Exact matched counts must agree with SQ-03F.1.
    if len(s_pairs) != int(sq03f1["S_hotspots"]["matched_count"]):
        raise RuntimeError("S matched-count mismatch vs SQ-03F.1")
    if len(c_pairs) != int(sq03f1["C_hotspots"]["matched_count"]):
        raise RuntimeError("C matched-count mismatch vs SQ-03F.1")

    s_result = analyze_set(s_pairs, s_unmatched, sq03f1["S_hotspots"])
    c_result = analyze_set(c_pairs, c_unmatched, sq03f1["C_hotspots"])

    artifact = {
        "schema": "moscaquant.sq03f2_result/v1",
        "sidequest_id": "SQ-03F.2",
        "title": "THE CAPO TEST",
        "classification": "AUTHORITATIVE_SOURCE_LEVEL_HOTSPOT_DECOMPOSITION",
        "source_commit": git_head(),
        "protocol_sha256": sha256(CFG_PATH),
        "sq03f1_result_sha256": sha256(SQ03F1_RESULT),
        "sq03f_result_sha256": sha256(SQ03F_RESULT),
        "sq03e_result_sha256": sha256(SQ03E_RESULT),
        "sq03b_ledger_sha256": sha256(SQ03B_LEDGER),
        "aligned_edges_sha256": sha256(FEATHER),
        "candidate_edge_count": len(rows),
        "conservative_graph_edge_count": len(matched),
        "source_profile_count": len(profiles),
        "S_hotspots": s_result,
        "C_hotspots": c_result,
        "claim_boundary": cfg["claim_boundary"],
        "family_model": cfg["family_model"],
        "implementation_note": (
            "Feature summaries omit a matched pair only when either side is null/non-finite; "
            "valid/null pair counts are recorded for every feature."
        ),
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n")

    print("SQ-03F.2 — THE CAPO TEST")
    print("=" * 72)
    print("candidate edges:", len(rows))
    print("conservative graph edges:", len(matched))
    print("source profiles:", len(profiles))
    print()

    for label, result in (("S", s_result), ("C", c_result)):
        print(f"{label} HOTSPOTS")
        print(
            "  matched:",
            f"{result['matched_count']}/{result['hotspot_count']}",
            f"({result['matched_fraction']:.4f})",
        )
        print("  SQ-03F.1 source-strength reproduction: True")
        print(
            "  unique sources:",
            f"hot={result['source_audit']['unique_hotspot_source_count']}",
            f"ctl={result['source_audit']['unique_control_source_count']}",
            "shared-hotspot-edge fraction="
            f"{result['source_audit']['fraction_hotspot_edges_sharing_source']:.6f}",
        )

        for feature in FEATURES:
            rec = result["features"][feature]
            print(
                f"  {feature:38s} "
                f"hot={rec['hotspot_median']!s:>14} "
                f"ctl={rec['control_median']!s:>14} "
                f"medΔ={rec['median_paired_difference']!s:>14} "
                f"P(hot>ctl)={rec['fraction_hotspot_gt_control']!s} "
                f"n={rec['valid_pair_count']}"
            )
        print()

    print("artifact:", OUTPUT)
    print("No new neural dynamics were executed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
