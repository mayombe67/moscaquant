from __future__ import annotations

from collections import defaultdict
from pathlib import Path
import hashlib
import json
import subprocess

import numpy as np
import pandas as pd

from brain.sq03e_analyze import rebuild_pair_rows, exact_top_k
from brain.sq03f_analyze import (
    assign_equal_count_deciles,
    compute_graph_features,
    attach_features,
)

ROOT = Path(__file__).resolve().parents[1]
CFG_PATH = ROOT / "config" / "experiments" / "sq03f1_no_free_looks_v1.json"
SQ03F_RESULT = ROOT / "artifacts" / "sidequests" / "sq03f-hotspot-test-result-v1.json"
SQ03E_RESULT = ROOT / "artifacts" / "sidequests" / "sq03e-structure-destiny-result-v1.json"
SQ03B_LEDGER = ROOT / "artifacts" / "sidequests" / "sq03b-checkpoints-v1" / "results.ndjson"
FEATHER = Path.home() / "moscaquant-data" / "external" / "mq002" / "mcns_fw_edge_comp.feather"
OUTPUT = ROOT / "artifacts" / "sidequests" / "sq03f1-no-free-looks-result-v1.json"


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
        raise RuntimeError("Refusing SQ-03F.1 analysis with dirty worktree")


def median(values):
    return float(np.median(np.asarray(values, dtype=float)))


def build_candidate_edges(pair_rows, matched):
    by_edge = defaultdict(list)
    for row in pair_rows:
        by_edge[int(row["edge_id"])].append(row)

    rows = []
    for edge_id, contexts in sorted(by_edge.items()):
        a = matched.iloc[edge_id]
        pre = str(a["pre"])
        post = str(a["post"])

        for ctx in contexts:
            if str(ctx["pre"]) != pre or str(ctx["post"]) != post:
                raise RuntimeError(
                    f"candidate identity mismatch edge={edge_id}: "
                    f"{ctx['pre']}->{ctx['post']} != {pre}->{post}"
                )

        wm = float(a["weight_m"])
        wf = float(a["weight_f"])

        int_s = [c["integrated"]["total_effect_magnitude"] for c in contexts]
        int_c = [c["integrated"]["context_residual"] for c in contexts]

        rows.append({
            "edge_id": edge_id,
            "original_feather_row": int(a["original_feather_row"]),
            "pre": pre,
            "post": post,
            "weight_m": wm,
            "weight_f": wf,
            "mean_weight": (wm + wf) / 2.0,
            "total_weight": abs(wm) + abs(wf),
            "abs_weight_difference": abs(wm - wf),
            "max_integrated_S": float(max(int_s)),
            "max_integrated_C": float(max(int_c)),
            "context_count": len(contexts),
        })
    return rows


def exact_context_match_controls(rows, hotspot_rows, score_key):
    hotspot_ids = {int(r["edge_id"]) for r in hotspot_rows}
    by_stratum = defaultdict(list)

    for r in rows:
        if int(r["edge_id"]) in hotspot_ids:
            continue
        key = (
            int(r["context_count"]),
            int(r["total_weight_decile"]),
            int(r["abs_weight_difference_decile"]),
        )
        by_stratum[key].append(r)

    ordered_hotspots = sorted(
        hotspot_rows,
        key=lambda r: (-float(r[score_key]), int(r["edge_id"]))
    )

    used = set()
    pairs = []
    unmatched = []

    for h in ordered_hotspots:
        key = (
            int(h["context_count"]),
            int(h["total_weight_decile"]),
            int(h["abs_weight_difference_decile"]),
        )
        candidates = [
            c for c in by_stratum.get(key, [])
            if int(c["edge_id"]) not in used
        ]

        if not candidates:
            unmatched.append({
                "edge_id": int(h["edge_id"]),
                "context_count": int(h["context_count"]),
                "total_weight_decile": int(h["total_weight_decile"]),
                "abs_weight_difference_decile": int(h["abs_weight_difference_decile"]),
                "score": float(h[score_key]),
            })
            continue

        candidates.sort(
            key=lambda c: (
                abs(float(c["total_weight"]) - float(h["total_weight"])),
                abs(float(c["abs_weight_difference"]) - float(h["abs_weight_difference"])),
                int(c["edge_id"]),
            )
        )
        c = candidates[0]
        used.add(int(c["edge_id"]))

        if int(c["context_count"]) != int(h["context_count"]):
            raise RuntimeError("context-count exact matching violated")
        if int(c["total_weight_decile"]) != int(h["total_weight_decile"]):
            raise RuntimeError("total-weight decile matching violated")
        if int(c["abs_weight_difference_decile"]) != int(h["abs_weight_difference_decile"]):
            raise RuntimeError("abs-weight-difference decile matching violated")

        pairs.append({"hotspot": h, "control": c})

    return pairs, unmatched


def summarize_feature_pairs(pairs, feature):
    hv = [float(p["hotspot"]["features"][feature]) for p in pairs]
    cv = [float(p["control"]["features"][feature]) for p in pairs]
    diffs = [h - c for h, c in zip(hv, cv)]

    return {
        "hotspot_median": median(hv),
        "control_median": median(cv),
        "median_paired_difference": median(diffs),
        "fraction_hotspot_gt_control": (
            sum(h > c for h, c in zip(hv, cv)) / len(pairs)
            if pairs else None
        ),
    }


def summarize_matching(pairs, unmatched, total_hotspots):
    features = [
        "source_out_degree",
        "target_in_degree",
        "source_output_fraction",
        "target_input_fraction",
        "source_out_strength",
        "target_in_strength",
        "endpoint_degree_product",
    ]

    context_ok = all(
        int(p["hotspot"]["context_count"]) == int(p["control"]["context_count"])
        for p in pairs
    )
    bins_ok = all(
        int(p["hotspot"]["total_weight_decile"]) == int(p["control"]["total_weight_decile"])
        and int(p["hotspot"]["abs_weight_difference_decile"])
        == int(p["control"]["abs_weight_difference_decile"])
        for p in pairs
    )

    return {
        "hotspot_count": total_hotspots,
        "matched_count": len(pairs),
        "unmatched_count": len(unmatched),
        "matched_fraction": len(pairs) / total_hotspots if total_hotspots else 0.0,
        "context_count_exact_match_check": context_ok,
        "structural_bin_exact_match_check": bins_ok,
        "features": {f: summarize_feature_pairs(pairs, f) for f in features},
        "negative_controls": {
            "context_count": {
                "hotspot_median": median([p["hotspot"]["context_count"] for p in pairs]),
                "control_median": median([p["control"]["context_count"] for p in pairs]),
                "median_paired_difference": median([
                    p["hotspot"]["context_count"] - p["control"]["context_count"]
                    for p in pairs
                ]),
            },
            "abs_weight_difference": {
                "hotspot_median": median([
                    p["hotspot"]["abs_weight_difference"] for p in pairs
                ]),
                "control_median": median([
                    p["control"]["abs_weight_difference"] for p in pairs
                ]),
                "median_paired_difference": median([
                    p["hotspot"]["abs_weight_difference"]
                    - p["control"]["abs_weight_difference"]
                    for p in pairs
                ]),
            },
        },
        "unmatched_first100": unmatched[:100],
    }


def main() -> int:
    require_clean_worktree()

    if OUTPUT.exists():
        raise RuntimeError(f"Refusing to overwrite existing SQ-03F.1 result: {OUTPUT}")

    cfg = json.loads(CFG_PATH.read_text())
    if cfg["status"] != "FROZEN_BEFORE_ANALYSIS":
        raise RuntimeError("Unexpected SQ-03F.1 protocol status")

    if sha256(SQ03F_RESULT) != cfg["parent"]["sq03f_result_sha256"]:
        raise RuntimeError("SQ-03F parent hash mismatch")

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
        raise RuntimeError("SQ-03F.1 candidate universe differs from SQ-03F")

    total_bin = assign_equal_count_deciles(rows, lambda r: r["total_weight"])
    diff_bin = assign_equal_count_deciles(rows, lambda r: r["abs_weight_difference"])
    for r in rows:
        r["total_weight_decile"] = total_bin[int(r["edge_id"])]
        r["abs_weight_difference_decile"] = diff_bin[int(r["edge_id"])]

    attach_features(rows, compute_graph_features(matched))

    frac = float(sq03f["hotspot_fraction"])
    hot_s = exact_top_k(rows, lambda r: r["max_integrated_S"], frac)
    hot_c = exact_top_k(rows, lambda r: r["max_integrated_C"], frac)

    if len(hot_s) != int(sq03f["hotspot_k"]) or len(hot_c) != int(sq03f["hotspot_k"]):
        raise RuntimeError("SQ-03F.1 hotspot k differs from SQ-03F")

    # Reuse exact SQ-03F memberships by reproducing the frozen SQ-03E rankings.
    sq03e_s_ids = [int(r["edge_id"]) for r in sq03e["top100_dynamic_S"]]
    sq03e_c_ids = [int(r["edge_id"]) for r in sq03e["top100_dynamic_C"]]
    if [int(r["edge_id"]) for r in hot_s[:100]] != sq03e_s_ids:
        raise RuntimeError("SQ-03F.1 S hotspot ranking mismatch")
    if [int(r["edge_id"]) for r in hot_c[:100]] != sq03e_c_ids:
        raise RuntimeError("SQ-03F.1 C hotspot ranking mismatch")

    s_pairs, s_unmatched = exact_context_match_controls(
        rows, hot_s, "max_integrated_S"
    )
    c_pairs, c_unmatched = exact_context_match_controls(
        rows, hot_c, "max_integrated_C"
    )

    s_summary = summarize_matching(s_pairs, s_unmatched, len(hot_s))
    c_summary = summarize_matching(c_pairs, c_unmatched, len(hot_c))

    artifact = {
        "schema": "moscaquant.sq03f1_result/v1",
        "sidequest_id": "SQ-03F.1",
        "title": "NO FREE LOOKS",
        "classification": "AUTHORITATIVE_CONTEXT_MATCHED_HOTSPOT_RESULT",
        "source_commit": git_head(),
        "protocol_sha256": sha256(CFG_PATH),
        "sq03f_result_sha256": sha256(SQ03F_RESULT),
        "sq03e_result_sha256": sha256(SQ03E_RESULT),
        "sq03b_ledger_sha256": sha256(SQ03B_LEDGER),
        "aligned_edges_sha256": sha256(FEATHER),
        "candidate_edge_count": len(rows),
        "hotspot_k": len(hot_s),
        "S_hotspots": s_summary,
        "C_hotspots": c_summary,
        "claim_boundary": cfg["claim_boundary"],
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n")

    print("SQ-03F.1 — NO FREE LOOKS")
    print("=" * 72)
    print("candidate edges:", artifact["candidate_edge_count"])
    print("hotspot k:", artifact["hotspot_k"])
    print()

    for label, summary in (("S", s_summary), ("C", c_summary)):
        print(f"{label} HOTSPOTS")
        print(
            "  matched:",
            f"{summary['matched_count']}/{summary['hotspot_count']}",
            f"({summary['matched_fraction']:.4f})",
        )
        print(
            "  exact context-count match:",
            summary["context_count_exact_match_check"],
        )
        print(
            "  exact structural-bin match:",
            summary["structural_bin_exact_match_check"],
        )

        for feature, rec in summary["features"].items():
            print(
                f"  {feature:28s} "
                f"hot={rec['hotspot_median']:.12g} "
                f"ctl={rec['control_median']:.12g} "
                f"medΔ={rec['median_paired_difference']:.12g} "
                f"P(hot>ctl)={rec['fraction_hotspot_gt_control']:.6f}"
            )

        nc = summary["negative_controls"]["context_count"]
        print(
            "  negative-control context_count "
            f"hot={nc['hotspot_median']:.12g} "
            f"ctl={nc['control_median']:.12g} "
            f"medΔ={nc['median_paired_difference']:.12g}"
        )
        print()

    print("artifact:", OUTPUT)
    print("No new neural dynamics were executed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
