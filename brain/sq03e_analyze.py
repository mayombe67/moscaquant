from __future__ import annotations

from collections import defaultdict
from pathlib import Path
import hashlib
import json
import math
import subprocess

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CFG_PATH = ROOT / "config" / "experiments" / "sq03e_structure_destiny_v1.json"
SQ03B_LEDGER = ROOT / "artifacts" / "sidequests" / "sq03b-checkpoints-v1" / "results.ndjson"
FEATHER = Path.home() / "moscaquant-data" / "external" / "mq002" / "mcns_fw_edge_comp.feather"
OUTPUT = ROOT / "artifacts" / "sidequests" / "sq03e-structure-destiny-result-v1.json"


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
        raise RuntimeError("Refusing SQ-03E analysis with dirty worktree")


def normalized_asymmetry(a: float, b: float) -> float:
    if a == 0.0 and b == 0.0:
        return 0.0
    return abs(a + b) / (abs(a) + abs(b))


def pair_metrics(dm: float, dl: float) -> dict:
    return {
        "context_residual": abs(dm + dl),
        "total_effect_magnitude": abs(dm) + abs(dl),
    }


def rebuild_pair_rows(ledger_path: Path) -> list[dict]:
    observations = {}

    with ledger_path.open(encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise RuntimeError(f"invalid JSON on SQ-03B ledger line {lineno}") from exc

            for anchor in row["relevant_anchors"]:
                delta = row["anchor_results"][anchor]["delta"]
                key = (row["input"], int(row["edge_id"]), anchor)
                slot = observations.setdefault(key, {})

                subject = row["subject"]
                if subject in slot:
                    raise RuntimeError(f"duplicate subject for paired observation {key}: {subject}")

                slot[subject] = {
                    "pre": row["pre"],
                    "post": row["post"],
                    "integrated": float(delta["integrated_positive_voltage_delta"]),
                    "peak": float(delta["peak_voltage_delta"]),
                }

    rows = []
    for (input_label, edge_id, anchor), pair in observations.items():
        if set(pair) != {"MORTY", "LILITH"}:
            raise RuntimeError(
                f"unpaired observation {(input_label, edge_id, anchor)}: {sorted(pair)}"
            )

        m = pair["MORTY"]
        l = pair["LILITH"]

        if m["pre"] != l["pre"] or m["post"] != l["post"]:
            raise RuntimeError(
                f"structural identity mismatch for {(input_label, edge_id, anchor)}"
            )

        rows.append({
            "input": input_label,
            "edge_id": edge_id,
            "anchor": anchor,
            "pre": m["pre"],
            "post": m["post"],
            "integrated": pair_metrics(m["integrated"], l["integrated"]),
            "peak": pair_metrics(m["peak"], l["peak"]),
        })

    rows.sort(key=lambda r: (r["edge_id"], r["input"], r["anchor"]))
    return rows


def average_ranks(values: np.ndarray) -> np.ndarray:
    s = pd.Series(values)
    return s.rank(method="average").to_numpy(dtype=float)


def spearman_no_p(x, y):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)

    finite = np.isfinite(x) & np.isfinite(y)
    x = x[finite]
    y = y[finite]

    if len(x) < 2:
        return None, int(len(x))

    rx = average_ranks(x)
    ry = average_ranks(y)

    if np.all(rx == rx[0]) or np.all(ry == ry[0]):
        return None, int(len(x))

    corr = float(np.corrcoef(rx, ry)[0, 1])
    return corr, int(len(x))


def equal_count_bins(rows: list[dict], value_key, bins: int = 10) -> list[list[dict]]:
    ordered = sorted(rows, key=lambda r: (value_key(r), int(r["edge_id"])))
    n = len(ordered)
    out = [[] for _ in range(bins)]

    for i, row in enumerate(ordered):
        b = min((i * bins) // n, bins - 1)
        out[b].append(row)

    return out


def finite_values(rows, fn):
    vals = []
    for r in rows:
        v = fn(r)
        if v is not None and math.isfinite(float(v)):
            vals.append(float(v))
    return vals


def summarize_deciles(rows: list[dict], structural_key) -> list[dict]:
    bins = equal_count_bins(rows, structural_key, 10)
    out = []

    for i, group in enumerate(bins, 1):
        sdiff = [structural_key(r) for r in group]
        dyn_s = [r["dynamic"]["max_integrated_total_effect_magnitude"] for r in group]
        dyn_c = [r["dynamic"]["max_integrated_context_residual"] for r in group]

        out.append({
            "decile": i,
            "edge_count": len(group),
            "structural_min": float(min(sdiff)),
            "structural_max": float(max(sdiff)),
            "dynamic_s_median": float(np.median(dyn_s)),
            "dynamic_s_max": float(max(dyn_s)),
            "dynamic_c_median": float(np.median(dyn_c)),
            "dynamic_c_max": float(max(dyn_c)),
        })

    return out


def exact_top_k(rows: list[dict], value_key, fraction: float) -> list[dict]:
    n = len(rows)
    k = int(math.ceil(n * fraction))
    return sorted(
        rows,
        key=lambda r: (-float(value_key(r)), int(r["edge_id"]))
    )[:k]


def overlap_summary(a: list[dict], b: list[dict]) -> dict:
    sa = {int(r["edge_id"]) for r in a}
    sb = {int(r["edge_id"]) for r in b}
    inter = sa & sb
    union = sa | sb

    return {
        "set_a_count": len(sa),
        "set_b_count": len(sb),
        "overlap_count": len(inter),
        "jaccard": (len(inter) / len(union)) if union else 0.0,
        "overlap_edge_ids_first100": sorted(inter)[:100],
    }


def main() -> int:
    require_clean_worktree()

    if OUTPUT.exists():
        raise RuntimeError(f"Refusing to overwrite existing SQ-03E result: {OUTPUT}")

    cfg = json.loads(CFG_PATH.read_text())

    if cfg["status"] != "FROZEN_BEFORE_ANALYSIS":
        raise RuntimeError("Unexpected SQ-03E protocol status")

    if sha256(SQ03B_LEDGER) != cfg["parents"]["sq03b_ledger_sha256"]:
        raise RuntimeError("SQ-03B ledger hash mismatch")

    if sha256(FEATHER) != cfg["parents"]["aligned_edges_sha256"]:
        raise RuntimeError("Aligned Feather hash mismatch")

    pair_rows = rebuild_pair_rows(SQ03B_LEDGER)

    by_edge = defaultdict(list)
    for row in pair_rows:
        by_edge[int(row["edge_id"])].append(row)

    aligned = pd.read_feather(FEATHER)

    required_columns = {
        "pre", "post", "weight_m", "weight_f", "t", "p_corr", "verdict_corr"
    }
    missing = required_columns - set(aligned.columns)
    if missing:
        raise RuntimeError(f"Aligned Feather missing required columns: {sorted(missing)}")

    conservative_mask = (
        (aligned["verdict_corr"] == "isomorphic")
        & (aligned["weight_m"] > 0)
        & (aligned["weight_f"] > 0)
    )
    matched = aligned.loc[conservative_mask].copy()
    matched["original_feather_row"] = matched.index.astype(int)
    matched = matched.reset_index(drop=True)

    edge_rows = []

    for edge_id, contexts in sorted(by_edge.items()):
        if edge_id < 0 or edge_id >= len(matched):
            raise RuntimeError(f"edge_id out of conservative matched-table bounds: {edge_id}")

        a = matched.iloc[edge_id]

        pre = str(a["pre"])
        post = str(a["post"])

        for ctx in contexts:
            if str(ctx["pre"]) != pre or str(ctx["post"]) != post:
                raise RuntimeError(
                    f"aligned-edge identity mismatch edge={edge_id}: "
                    f"ledger={ctx['pre']}->{ctx['post']} feather={pre}->{post}"
                )

        wm = float(a["weight_m"])
        wf = float(a["weight_f"])

        if not math.isfinite(wm) or not math.isfinite(wf):
            raise RuntimeError(f"nonfinite primary weight field on edge {edge_id}")

        abs_diff = abs(wm - wf)
        total_weight = abs(wm) + abs(wf)
        relative_diff = abs_diff / total_weight if total_weight > 0 else 0.0

        int_s = [
            c["integrated"]["total_effect_magnitude"] for c in contexts
        ]
        int_c = [
            c["integrated"]["context_residual"] for c in contexts
        ]
        peak_s = [
            c["peak"]["total_effect_magnitude"] for c in contexts
        ]
        peak_c = [
            c["peak"]["context_residual"] for c in contexts
        ]

        t_raw = a["t"]
        p_raw = a["p_corr"]

        t_val = float(t_raw) if pd.notna(t_raw) else None
        p_val = float(p_raw) if pd.notna(p_raw) else None

        edge_rows.append({
            "edge_id": edge_id,
            "original_feather_row": int(a["original_feather_row"]),
            "pre": pre,
            "post": post,
            "structure": {
                "weight_m": wm,
                "weight_f": wf,
                "abs_weight_difference": abs_diff,
                "total_weight": total_weight,
                "relative_weight_difference": relative_diff,
                "t": t_val,
                "abs_t": abs(t_val) if t_val is not None and math.isfinite(t_val) else None,
                "p_corr": p_val if p_val is not None and math.isfinite(p_val) else None,
                "verdict_corr": str(a["verdict_corr"]),
            },
            "dynamic": {
                "max_integrated_total_effect_magnitude": float(max(int_s)),
                "max_integrated_context_residual": float(max(int_c)),
                "max_peak_total_effect_magnitude": float(max(peak_s)),
                "max_peak_context_residual": float(max(peak_c)),
                "median_integrated_total_effect_magnitude": float(np.median(int_s)),
                "context_count": len(contexts),
            },
        })

    def x(name):
        return [r["structure"][name] for r in edge_rows]

    def y(name):
        return [r["dynamic"][name] for r in edge_rows]

    associations = {}

    for label, xv, yv in [
        (
            "abs_weight_difference_vs_max_integrated_S",
            x("abs_weight_difference"),
            y("max_integrated_total_effect_magnitude"),
        ),
        (
            "abs_weight_difference_vs_max_integrated_C",
            x("abs_weight_difference"),
            y("max_integrated_context_residual"),
        ),
        (
            "abs_t_vs_max_integrated_S",
            x("abs_t"),
            y("max_integrated_total_effect_magnitude"),
        ),
        (
            "abs_t_vs_max_integrated_C",
            x("abs_t"),
            y("max_integrated_context_residual"),
        ),
    ]:
        rho, n = spearman_no_p(xv, yv)
        associations[label] = {"spearman_rho": rho, "finite_pair_count": n}

    structural_deciles = summarize_deciles(
        edge_rows,
        lambda r: r["structure"]["abs_weight_difference"],
    )

    total_weight_bins = equal_count_bins(
        edge_rows,
        lambda r: r["structure"]["total_weight"],
        10,
    )

    within_weight_bins = []
    for i, group in enumerate(total_weight_bins, 1):
        rho_s, n_s = spearman_no_p(
            [r["structure"]["abs_weight_difference"] for r in group],
            [r["dynamic"]["max_integrated_total_effect_magnitude"] for r in group],
        )
        rho_c, n_c = spearman_no_p(
            [r["structure"]["abs_weight_difference"] for r in group],
            [r["dynamic"]["max_integrated_context_residual"] for r in group],
        )
        within_weight_bins.append({
            "bin": i,
            "edge_count": len(group),
            "total_weight_min": float(min(r["structure"]["total_weight"] for r in group)),
            "total_weight_max": float(max(r["structure"]["total_weight"] for r in group)),
            "rho_absdiff_vs_S": rho_s,
            "rho_absdiff_vs_C": rho_c,
            "finite_pairs_S": n_s,
            "finite_pairs_C": n_c,
        })

    top_fraction = float(cfg["analyses"]["extreme_overlap"]["top_fraction"])

    top_structural = exact_top_k(
        edge_rows,
        lambda r: r["structure"]["abs_weight_difference"],
        top_fraction,
    )
    top_dynamic_s = exact_top_k(
        edge_rows,
        lambda r: r["dynamic"]["max_integrated_total_effect_magnitude"],
        top_fraction,
    )
    top_dynamic_c = exact_top_k(
        edge_rows,
        lambda r: r["dynamic"]["max_integrated_context_residual"],
        top_fraction,
    )

    overlap_s = overlap_summary(top_structural, top_dynamic_s)
    overlap_c = overlap_summary(top_structural, top_dynamic_c)

    top_structural_100 = top_structural[:100]
    top_dynamic_s_100 = top_dynamic_s[:100]
    top_dynamic_c_100 = top_dynamic_c[:100]

    verdict_counts = {}
    for row in edge_rows:
        verdict = row["structure"]["verdict_corr"]
        verdict_counts[verdict] = verdict_counts.get(verdict, 0) + 1

    artifact = {
        "schema": "moscaquant.sq03e_result/v1",
        "sidequest_id": "SQ-03E",
        "title": "STRUCTURE IS NOT DESTINY",
        "classification": "AUTHORITATIVE_STRUCTURE_DYNAMICS_CENSUS",
        "source_commit": git_head(),
        "protocol_sha256": sha256(CFG_PATH),
        "sq03b_ledger_sha256": sha256(SQ03B_LEDGER),
        "aligned_edges_sha256": sha256(FEATHER),
        "pair_observation_count": len(pair_rows),
        "unique_edge_count": len(edge_rows),
        "conservative_matched_edge_table_count": len(matched),
        "edge_id_indexing": (
            'zero-based position after verdict_corr=="isomorphic" and '
            'weight_m>0 and weight_f>0, preserving original Feather order'
        ),
        "verdict_corr_counts": dict(sorted(verdict_counts.items())),
        "rank_associations": associations,
        "structural_difference_deciles": structural_deciles,
        "within_total_weight_bins": within_weight_bins,
        "top_fraction": top_fraction,
        "top_k": len(top_structural),
        "top1pct_structural_vs_dynamic_S": overlap_s,
        "top1pct_structural_vs_dynamic_C": overlap_c,
        "top100_structural_abs_difference": top_structural_100,
        "top100_dynamic_S": top_dynamic_s_100,
        "top100_dynamic_C": top_dynamic_c_100,
        "claim_boundary": cfg["claim_boundary"],
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n")

    print("SQ-03E — STRUCTURE IS NOT DESTINY")
    print("=" * 72)
    print("pair observations:", artifact["pair_observation_count"])
    print("unique edges:", artifact["unique_edge_count"])
    print("verdict_corr counts:", artifact["verdict_corr_counts"])
    print()

    print("SPEARMAN RANK ASSOCIATIONS")
    for label, rec in artifact["rank_associations"].items():
        print(
            f"  {label:48s} rho={rec['spearman_rho']} "
            f"n={rec['finite_pair_count']}"
        )
    print()

    print("TOP-1% OVERLAP")
    print("  k:", artifact["top_k"])
    print(
        "  structural vs dynamic S:",
        f"overlap={overlap_s['overlap_count']} "
        f"jaccard={overlap_s['jaccard']:.6f}",
    )
    print(
        "  structural vs dynamic C:",
        f"overlap={overlap_c['overlap_count']} "
        f"jaccard={overlap_c['jaccard']:.6f}",
    )
    print()

    print("STRUCTURAL-DIFFERENCE DECILES")
    for d in structural_deciles:
        print(
            f"  D{d['decile']:02d} n={d['edge_count']:6d} "
            f"|dw|=[{d['structural_min']:.6g},{d['structural_max']:.6g}] "
            f"medianS={d['dynamic_s_median']:.12g} "
            f"maxS={d['dynamic_s_max']:.12g} "
            f"medianC={d['dynamic_c_median']:.12g} "
            f"maxC={d['dynamic_c_max']:.12g}"
        )
    print()

    print("WITHIN TOTAL-WEIGHT BINS")
    for b in within_weight_bins:
        print(
            f"  B{b['bin']:02d} n={b['edge_count']:6d} "
            f"rho(|dw|,S)={b['rho_absdiff_vs_S']} "
            f"rho(|dw|,C)={b['rho_absdiff_vs_C']}"
        )

    print()
    print("artifact:", OUTPUT)
    print("No new neural dynamics were executed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
