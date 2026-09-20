from __future__ import annotations

from collections import defaultdict
from pathlib import Path
import hashlib
import json
import math
import subprocess

import numpy as np
import pandas as pd

from brain.sq03e_analyze import rebuild_pair_rows, equal_count_bins, exact_top_k

ROOT = Path(__file__).resolve().parents[1]
CFG_PATH = ROOT / "config" / "experiments" / "sq03f_hotspot_test_v1.json"
SQ03E_RESULT = ROOT / "artifacts" / "sidequests" / "sq03e-structure-destiny-result-v1.json"
SQ03B_LEDGER = ROOT / "artifacts" / "sidequests" / "sq03b-checkpoints-v1" / "results.ndjson"
FEATHER = Path.home() / "moscaquant-data" / "external" / "mq002" / "mcns_fw_edge_comp.feather"
OUTPUT = ROOT / "artifacts" / "sidequests" / "sq03f-hotspot-test-result-v1.json"


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
        raise RuntimeError("Refusing SQ-03F analysis with dirty worktree")


def assign_equal_count_deciles(rows, value_fn):
    ordered = sorted(rows, key=lambda r: (float(value_fn(r)), int(r["edge_id"])))
    n = len(ordered)
    mapping = {}
    for i, row in enumerate(ordered):
        mapping[int(row["edge_id"])] = min((i * 10) // n, 9) + 1
    return mapping


def median(values):
    return float(np.median(np.asarray(values, dtype=float)))


def build_candidate_edges(pair_rows, matched):
    by_edge = defaultdict(list)
    for row in pair_rows:
        by_edge[int(row["edge_id"])].append(row)

    rows = []
    for edge_id, contexts in sorted(by_edge.items()):
        if edge_id < 0 or edge_id >= len(matched):
            raise RuntimeError(f"edge_id out of matched-table bounds: {edge_id}")

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
        total_weight = abs(wm) + abs(wf)
        abs_diff = abs(wm - wf)

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
            "total_weight": total_weight,
            "abs_weight_difference": abs_diff,
            "max_integrated_S": float(max(int_s)),
            "max_integrated_C": float(max(int_c)),
            "context_count": len(contexts),
        })
    return rows


def compute_graph_features(matched):
    out_neighbors = defaultdict(set)
    in_neighbors = defaultdict(set)
    out_strength = defaultdict(float)
    in_strength = defaultdict(float)

    for row in matched.itertuples(index=False):
        pre = str(row.pre)
        post = str(row.post)
        w = (float(row.weight_m) + float(row.weight_f)) / 2.0

        out_neighbors[pre].add(post)
        in_neighbors[post].add(pre)
        out_strength[pre] += w
        in_strength[post] += w

    return out_neighbors, in_neighbors, out_strength, in_strength


def attach_features(rows, graph_features):
    out_neighbors, in_neighbors, out_strength, in_strength = graph_features

    for r in rows:
        pre = r["pre"]
        post = r["post"]
        w = r["mean_weight"]

        so_deg = len(out_neighbors[pre])
        ti_deg = len(in_neighbors[post])
        so_strength = float(out_strength[pre])
        ti_strength = float(in_strength[post])

        r["features"] = {
            "source_out_degree": so_deg,
            "target_in_degree": ti_deg,
            "source_output_fraction": (w / so_strength) if so_strength else 0.0,
            "target_input_fraction": (w / ti_strength) if ti_strength else 0.0,
            "source_out_strength": so_strength,
            "target_in_strength": ti_strength,
            "endpoint_degree_product": so_deg * ti_deg,
            "context_count": r["context_count"],
        }


def match_controls(rows, hotspot_rows, score_key):
    hotspot_ids = {int(r["edge_id"]) for r in hotspot_rows}
    by_bin = defaultdict(list)

    for r in rows:
        if int(r["edge_id"]) in hotspot_ids:
            continue
        key = (r["total_weight_decile"], r["abs_weight_difference_decile"])
        by_bin[key].append(r)

    for key in by_bin:
        by_bin[key].sort(key=lambda r: int(r["edge_id"]))

    ordered_hotspots = sorted(
        hotspot_rows,
        key=lambda r: (-float(r[score_key]), int(r["edge_id"]))
    )

    used = set()
    pairs = []
    unmatched = []

    for h in ordered_hotspots:
        key = (h["total_weight_decile"], h["abs_weight_difference_decile"])
        candidates = [
            c for c in by_bin.get(key, [])
            if int(c["edge_id"]) not in used
        ]

        if not candidates:
            unmatched.append({
                "edge_id": int(h["edge_id"]),
                "score": float(h[score_key]),
                "bin": list(key),
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
        "context_count",
    ]

    return {
        "hotspot_count": total_hotspots,
        "matched_count": len(pairs),
        "unmatched_count": len(unmatched),
        "matched_fraction": len(pairs) / total_hotspots if total_hotspots else 0.0,
        "features": {
            f: summarize_feature_pairs(pairs, f)
            for f in features
        },
        "negative_control_abs_weight_difference": {
            "hotspot_median": median(
                [p["hotspot"]["abs_weight_difference"] for p in pairs]
            ),
            "control_median": median(
                [p["control"]["abs_weight_difference"] for p in pairs]
            ),
            "median_paired_difference": median([
                p["hotspot"]["abs_weight_difference"]
                - p["control"]["abs_weight_difference"]
                for p in pairs
            ]),
        },
        "unmatched": unmatched[:100],
        "pairs_first100": [
            {
                "hotspot_edge_id": int(p["hotspot"]["edge_id"]),
                "control_edge_id": int(p["control"]["edge_id"]),
                "hotspot_pre": p["hotspot"]["pre"],
                "hotspot_post": p["hotspot"]["post"],
                "control_pre": p["control"]["pre"],
                "control_post": p["control"]["post"],
                "total_weight_decile": p["hotspot"]["total_weight_decile"],
                "abs_weight_difference_decile": p["hotspot"]["abs_weight_difference_decile"],
            }
            for p in pairs[:100]
        ],
    }


def main() -> int:
    require_clean_worktree()

    if OUTPUT.exists():
        raise RuntimeError(f"Refusing to overwrite existing SQ-03F result: {OUTPUT}")

    cfg = json.loads(CFG_PATH.read_text())
    if cfg["status"] != "FROZEN_BEFORE_ANALYSIS":
        raise RuntimeError("Unexpected SQ-03F protocol status")

    if sha256(SQ03E_RESULT) != cfg["parent"]["sq03e_result_sha256"]:
        raise RuntimeError("SQ-03E parent artifact hash mismatch")

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

    if len(rows) != int(sq03e["unique_edge_count"]):
        raise RuntimeError(
            f"candidate edge count mismatch vs SQ-03E: {len(rows)} "
            f"!= {sq03e['unique_edge_count']}"
        )

    total_bin = assign_equal_count_deciles(rows, lambda r: r["total_weight"])
    diff_bin = assign_equal_count_deciles(rows, lambda r: r["abs_weight_difference"])

    for r in rows:
        r["total_weight_decile"] = total_bin[int(r["edge_id"])]
        r["abs_weight_difference_decile"] = diff_bin[int(r["edge_id"])]

    attach_features(rows, compute_graph_features(matched))

    frac = float(cfg["hotspots"]["fraction"])
    hot_s = exact_top_k(rows, lambda r: r["max_integrated_S"], frac)
    hot_c = exact_top_k(rows, lambda r: r["max_integrated_C"], frac)

    expected_k = int(sq03e["top_k"])
    if len(hot_s) != expected_k or len(hot_c) != expected_k:
        raise RuntimeError("SQ-03F hotspot k does not reproduce SQ-03E top-k")

    # Cross-check exact top-100 identities against SQ-03E authoritative artifact.
    sq03e_s_ids = [int(r["edge_id"]) for r in sq03e["top100_dynamic_S"]]
    sq03e_c_ids = [int(r["edge_id"]) for r in sq03e["top100_dynamic_C"]]

    if [int(r["edge_id"]) for r in hot_s[:100]] != sq03e_s_ids:
        raise RuntimeError("SQ-03F S-hotspot ranking does not reproduce SQ-03E top-100")
    if [int(r["edge_id"]) for r in hot_c[:100]] != sq03e_c_ids:
        raise RuntimeError("SQ-03F C-hotspot ranking does not reproduce SQ-03E top-100")

    s_pairs, s_unmatched = match_controls(rows, hot_s, "max_integrated_S")
    c_pairs, c_unmatched = match_controls(rows, hot_c, "max_integrated_C")

    s_summary = summarize_matching(s_pairs, s_unmatched, len(hot_s))
    c_summary = summarize_matching(c_pairs, c_unmatched, len(hot_c))

    artifact = {
        "schema": "moscaquant.sq03f_result/v1",
        "sidequest_id": "SQ-03F",
        "title": "HOTSPOT TEST",
        "classification": "AUTHORITATIVE_DYNAMIC_HOTSPOT_NETWORK_POSITION_RESULT",
        "source_commit": git_head(),
        "protocol_sha256": sha256(CFG_PATH),
        "sq03e_result_sha256": sha256(SQ03E_RESULT),
        "sq03b_ledger_sha256": sha256(SQ03B_LEDGER),
        "aligned_edges_sha256": sha256(FEATHER),
        "candidate_edge_count": len(rows),
        "conservative_matched_graph_edge_count": len(matched),
        "hotspot_fraction": frac,
        "hotspot_k": expected_k,
        "sq03e_top100_S_reproduced": True,
        "sq03e_top100_C_reproduced": True,
        "S_hotspots": s_summary,
        "C_hotspots": c_summary,
        "claim_boundary": cfg["claim_boundary"],
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n")

    print("SQ-03F — HOTSPOT TEST")
    print("=" * 72)
    print("candidate edges:", artifact["candidate_edge_count"])
    print("conservative graph edges:", artifact["conservative_matched_graph_edge_count"])
    print("hotspot k:", artifact["hotspot_k"])
    print("SQ-03E top-100 S reproduced:", artifact["sq03e_top100_S_reproduced"])
    print("SQ-03E top-100 C reproduced:", artifact["sq03e_top100_C_reproduced"])
    print()

    for label, summary in (("S", s_summary), ("C", c_summary)):
        print(f"{label} HOTSPOTS")
        print(
            "  matched:",
            f"{summary['matched_count']}/{summary['hotspot_count']}",
            f"({summary['matched_fraction']:.4f})",
        )
        for feature, rec in summary["features"].items():
            print(
                f"  {feature:28s} "
                f"hot={rec['hotspot_median']:.12g} "
                f"ctl={rec['control_median']:.12g} "
                f"medΔ={rec['median_paired_difference']:.12g} "
                f"P(hot>ctl)={rec['fraction_hotspot_gt_control']:.6f}"
            )
        neg = summary["negative_control_abs_weight_difference"]
        print(
            "  negative-control |dw|       "
            f"hot={neg['hotspot_median']:.12g} "
            f"ctl={neg['control_median']:.12g} "
            f"medΔ={neg['median_paired_difference']:.12g}"
        )
        print()

    print("artifact:", OUTPUT)
    print("No new neural dynamics were executed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
