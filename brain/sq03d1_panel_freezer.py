from __future__ import annotations

from collections import defaultdict
from pathlib import Path
import json
import math


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
    }


def rebuild_pairs(ledger_path: Path) -> list[dict]:
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
                    "peak": float(delta["peak_voltage_delta"]),
                    "integrated": float(delta["integrated_positive_voltage_delta"]),
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
                f"structural mismatch for {(input_label, edge_id, anchor)}"
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

    rows.sort(key=lambda r: (r["input"], r["anchor"], r["edge_id"]))
    return rows


def upper_sort_key(r: dict):
    return (
        -r["integrated"]["context_residual"],
        -r["peak"]["context_residual"],
        -r["integrated"]["total_effect_magnitude"],
        r["edge_id"],
        r["input"],
        r["anchor"],
    )


def low_sort_key(r: dict):
    return (
        r["integrated"]["context_residual"],
        r["integrated"]["total_effect_magnitude"],
        r["peak"]["context_residual"],
        r["edge_id"],
        r["input"],
        r["anchor"],
    )


def allocate_stratified(
    rows: list[dict],
    total: int,
    minimum_per_input: int,
    sort_key,
    excluded: set[tuple[str, int, str]] | None = None,
) -> list[dict]:
    excluded = excluded or set()
    eligible = [
        r for r in rows
        if (r["input"], int(r["edge_id"]), r["anchor"]) not in excluded
    ]
    ranked = sorted(eligible, key=sort_key)

    by_input = defaultdict(list)
    for row in ranked:
        by_input[row["input"]].append(row)

    inputs = sorted(by_input)
    if total < minimum_per_input * len(inputs):
        raise RuntimeError("panel total is too small for required stratification")

    selected = []
    selected_keys = set()

    # Seed each input.
    for input_label in inputs:
        pool = by_input[input_label]
        if len(pool) < minimum_per_input:
            raise RuntimeError(
                f"not enough eligible rows for input {input_label}: {len(pool)}"
            )
        for row in pool[:minimum_per_input]:
            key = (row["input"], int(row["edge_id"]), row["anchor"])
            selected.append(row)
            selected_keys.add(key)

    # Fill globally.
    for row in ranked:
        if len(selected) >= total:
            break
        key = (row["input"], int(row["edge_id"]), row["anchor"])
        if key in selected_keys:
            continue
        selected.append(row)
        selected_keys.add(key)

    if len(selected) != total:
        raise RuntimeError(f"could not fill panel: selected {len(selected)} of {total}")

    return selected
