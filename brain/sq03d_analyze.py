from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
import hashlib
import json
import math
import statistics
import subprocess

ROOT = Path(__file__).resolve().parents[1]
CFG_PATH = ROOT / "config" / "experiments" / "sq03d_reciprocity_v1.json"
SQ03B_LEDGER = ROOT / "artifacts" / "sidequests" / "sq03b-checkpoints-v1" / "results.ndjson"
SQ03C_RESULT = ROOT / "artifacts" / "sidequests" / "sq03c-scalar-verification-result-v1.json"
OUTPUT = ROOT / "artifacts" / "sidequests" / "sq03d-reciprocity-result-v1.json"


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
        raise RuntimeError("Refusing SQ-03D analysis with dirty worktree")


def sign_relation(a: float, b: float) -> str:
    product = a * b
    if product < 0:
        return "OPPOSITE"
    if product > 0:
        return "SAME"
    return "ZERO_INVOLVED"


def normalized_asymmetry(a: float, b: float) -> float:
    if a == 0.0 and b == 0.0:
        return 0.0
    return abs(a + b) / (abs(a) + abs(b))


def pair_metrics(dm: float, dl: float) -> dict:
    return {
        "delta_morty": dm,
        "delta_lilith": dl,
        "context_residual": abs(dm + dl),
        "total_effect_magnitude": abs(dm) + abs(dl),
        "normalized_asymmetry": normalized_asymmetry(dm, dl),
        "sign_relation": sign_relation(dm, dl),
    }


def first_positive_relation(dm, dl) -> str:
    if dm is None and dl is None:
        return "BOTH_NULL"
    if isinstance(dm, (int, float)) and isinstance(dl, (int, float)):
        if dm == -dl:
            return "RECIPROCAL_EXACT"
        if dm == dl:
            return "SAME_EXACT"
        if dm * dl < 0:
            return "OPPOSITE_NONRECIPROCAL"
        if dm * dl > 0:
            return "SAME_DIRECTION"
        return "ZERO_INVOLVED"
    return "NONCOMPARABLE"


def quantile_sorted(xs: list[float], q: float) -> float:
    if not xs:
        return math.nan
    if len(xs) == 1:
        return float(xs[0])
    pos = (len(xs) - 1) * q
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return float(xs[lo])
    frac = pos - lo
    return float(xs[lo] * (1.0 - frac) + xs[hi] * frac)


def quantiles(xs: list[float], qs: list[float]) -> dict:
    ys = sorted(float(x) for x in xs)
    out = {}
    for q in qs:
        label = "max" if q == 1.0 else f"p{q*100:g}"
        out[label] = quantile_sorted(ys, q)
    return out


def summary(rows: list[dict], cfg: dict) -> dict:
    int_res = [r["integrated"]["context_residual"] for r in rows]
    int_mag = [r["integrated"]["total_effect_magnitude"] for r in rows]
    int_asym = [r["integrated"]["normalized_asymmetry"] for r in rows]
    peak_res = [r["peak"]["context_residual"] for r in rows]
    peak_mag = [r["peak"]["total_effect_magnitude"] for r in rows]
    peak_asym = [r["peak"]["normalized_asymmetry"] for r in rows]

    return {
        "pair_count": len(rows),
        "integrated": {
            "context_residual": quantiles(
                int_res, cfg["summaries"]["context_residual_quantiles"]
            ),
            "total_effect_magnitude": quantiles(
                int_mag, cfg["summaries"]["effect_magnitude_quantiles"]
            ),
            "normalized_asymmetry": quantiles(
                int_asym, cfg["summaries"]["normalized_asymmetry_quantiles"]
            ),
            "sign_relation_counts": dict(
                sorted(Counter(r["integrated"]["sign_relation"] for r in rows).items())
            ),
        },
        "peak": {
            "context_residual": quantiles(
                peak_res, cfg["summaries"]["context_residual_quantiles"]
            ),
            "total_effect_magnitude": quantiles(
                peak_mag, cfg["summaries"]["effect_magnitude_quantiles"]
            ),
            "normalized_asymmetry": quantiles(
                peak_asym, cfg["summaries"]["normalized_asymmetry_quantiles"]
            ),
            "sign_relation_counts": dict(
                sorted(Counter(r["peak"]["sign_relation"] for r in rows).items())
            ),
        },
        "first_positive_frame_relation_counts": dict(
            sorted(Counter(r["first_positive_frame_relation"] for r in rows).items())
        ),
    }


def magnitude_deciles(rows: list[dict]) -> list[dict]:
    ordered = sorted(
        rows,
        key=lambda r: (
            r["integrated"]["total_effect_magnitude"],
            r["input"],
            r["anchor"],
            r["edge_id"],
        ),
    )
    n = len(ordered)
    buckets = []
    for d in range(10):
        start = (n * d) // 10
        end = (n * (d + 1)) // 10
        part = ordered[start:end]
        if not part:
            continue
        buckets.append({
            "decile": d + 1,
            "pair_count": len(part),
            "min_total_effect_magnitude": part[0]["integrated"]["total_effect_magnitude"],
            "max_total_effect_magnitude": part[-1]["integrated"]["total_effect_magnitude"],
            "median_context_residual": statistics.median(
                r["integrated"]["context_residual"] for r in part
            ),
            "median_normalized_asymmetry": statistics.median(
                r["integrated"]["normalized_asymmetry"] for r in part
            ),
            "opposite_sign_fraction": (
                sum(r["integrated"]["sign_relation"] == "OPPOSITE" for r in part)
                / len(part)
            ),
        })
    return buckets


def load_sq03c_verified_pair_keys() -> set[tuple[str, int, str]]:
    if not SQ03C_RESULT.exists():
        return set()

    data = json.loads(SQ03C_RESULT.read_text())
    by_job = defaultdict(set)

    for row in data["results"]:
        if not row.get("aa_exact", False):
            continue
        if not row.get("all_metrics_agree_with_sq03b", False):
            continue
        key = (row["input"], int(row["edge_id"]))
        by_job[key].add(row["subject"])

    both = {
        key for key, subjects in by_job.items()
        if subjects == {"MORTY", "LILITH"}
    }

    pair_keys = set()
    for row in data["results"]:
        job_key = (row["input"], int(row["edge_id"]))
        if job_key not in both:
            continue
        for anchor in row["relevant_anchors"]:
            pair_keys.add((row["input"], int(row["edge_id"]), anchor))
    return pair_keys


def main() -> int:
    require_clean_worktree()

    if OUTPUT.exists():
        raise RuntimeError(f"Refusing to overwrite existing SQ-03D result: {OUTPUT}")

    cfg = json.loads(CFG_PATH.read_text())

    if cfg["status"] != "FROZEN_BEFORE_ANALYSIS":
        raise RuntimeError("Unexpected SQ-03D protocol status")

    actual_ledger_hash = sha256(SQ03B_LEDGER)
    if actual_ledger_hash != cfg["parents"]["sq03b_ledger_sha256"]:
        raise RuntimeError("SQ-03B ledger hash mismatch")

    observations = {}

    with SQ03B_LEDGER.open(encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            if not line.strip():
                continue
            row = json.loads(line)

            for anchor in row["relevant_anchors"]:
                delta = row["anchor_results"][anchor]["delta"]
                key = (row["input"], int(row["edge_id"]), anchor)
                slot = observations.setdefault(key, {})

                subject = row["subject"]
                if subject in slot:
                    raise RuntimeError(
                        f"Duplicate subject for paired observation {key}: {subject}"
                    )

                slot[subject] = {
                    "peak": float(delta["peak_voltage_delta"]),
                    "integrated": float(delta["integrated_positive_voltage_delta"]),
                    "first_positive": delta["first_positive_frame_delta"],
                    "pre": row["pre"],
                    "post": row["post"],
                }

    expected_subjects = set(cfg["pairing"]["subjects_required"])
    rows = []

    for (input_label, edge_id, anchor), pair in observations.items():
        if set(pair) != expected_subjects:
            raise RuntimeError(
                f"Unpaired SQ-03D observation {(input_label, edge_id, anchor)}: "
                f"{sorted(pair)}"
            )

        m = pair["MORTY"]
        l = pair["LILITH"]

        if m["pre"] != l["pre"] or m["post"] != l["post"]:
            raise RuntimeError(
                f"Structural identity mismatch for {(input_label, edge_id, anchor)}"
            )

        rows.append({
            "input": input_label,
            "edge_id": edge_id,
            "anchor": anchor,
            "pre": m["pre"],
            "post": m["post"],
            "integrated": pair_metrics(m["integrated"], l["integrated"]),
            "peak": pair_metrics(m["peak"], l["peak"]),
            "first_positive_frame_relation": first_positive_relation(
                m["first_positive"], l["first_positive"]
            ),
        })

    rows.sort(key=lambda r: (r["input"], r["anchor"], r["edge_id"]))

    verified_keys = load_sq03c_verified_pair_keys()
    verified_rows = [
        r for r in rows if (r["input"], r["edge_id"], r["anchor"]) in verified_keys
    ]

    strata = defaultdict(list)
    for row in rows:
        strata[(row["input"], row["anchor"])].append(row)

    ranking = sorted(
        rows,
        key=lambda r: (
            -r["integrated"]["context_residual"],
            -r["peak"]["context_residual"],
            -r["integrated"]["total_effect_magnitude"],
            r["edge_id"],
        ),
    )

    artifact = {
        "schema": "moscaquant.sq03d_result/v1",
        "sidequest_id": "SQ-03D",
        "title": "THE SAME KNIFE CUTS DIFFERENTLY",
        "classification": "AUTHORITATIVE_PAIRED_BACKGROUND_ANALYSIS",
        "source_commit": git_head(),
        "protocol_sha256": sha256(CFG_PATH),
        "sq03b_ledger_sha256": actual_ledger_hash,
        "sq03c_result_sha256": sha256(SQ03C_RESULT) if SQ03C_RESULT.exists() else None,
        "pair_count": len(rows),
        "sq03c_verified_pair_count": len(verified_rows),
        "global_summary": summary(rows, cfg),
        "magnitude_deciles": magnitude_deciles(rows),
        "strata": [
            {
                "input": key[0],
                "anchor": key[1],
                **summary(group, cfg),
            }
            for key, group in sorted(strata.items())
        ],
        "sq03c_verified_subset_summary": (
            summary(verified_rows, cfg) if verified_rows else None
        ),
        "top_context_residual_candidates": ranking[:100],
        "claim_boundary": cfg["claim_boundary"],
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n")

    g = artifact["global_summary"]["integrated"]
    print("SQ-03D — THE SAME KNIFE CUTS DIFFERENTLY")
    print("=" * 72)
    print("paired observations:", artifact["pair_count"])
    print("SQ-03C scalar-verified paired observations:", artifact["sq03c_verified_pair_count"])
    print()
    print("INTEGRATED POSITIVE VOLTAGE — CONTEXT RESIDUAL")
    for k, v in g["context_residual"].items():
        print(f"  {k:6s} {v:.12g}")
    print()
    print("INTEGRATED POSITIVE VOLTAGE — NORMALIZED ASYMMETRY")
    for k, v in g["normalized_asymmetry"].items():
        print(f"  {k:6s} {v:.12g}")
    print()
    print("INTEGRATED SIGN RELATIONS")
    for k, v in g["sign_relation_counts"].items():
        print(f"  {k:16s} {v}")
    print()
    print("TOP 10 CONTEXT-RESIDUAL PAIRS")
    for i, row in enumerate(ranking[:10], 1):
        print(
            f"  {i:2d}. {row['input']:10s} {row['anchor']:5s} "
            f"edge={row['edge_id']:6d} {row['pre']}->{row['post']} "
            f"C={row['integrated']['context_residual']:.12g} "
            f"S={row['integrated']['total_effect_magnitude']:.12g} "
            f"A={row['integrated']['normalized_asymmetry']:.6f}"
        )
    print()
    print("artifact:", OUTPUT)
    print("No new neural dynamics were executed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
