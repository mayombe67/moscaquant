from __future__ import annotations

from collections import defaultdict
from pathlib import Path
import hashlib
import json


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def summarize_job(row: dict) -> dict:
    peak_max = 0.0
    integrated_max = 0.0

    for result in row["anchor_results"].values():
        delta = result["delta"]
        peak_max = max(peak_max, abs(float(delta["peak_voltage_delta"])))
        integrated_max = max(
            integrated_max,
            abs(float(delta["integrated_positive_voltage_delta"])),
        )

    return {
        "input": row["input"],
        "subject": row["subject"],
        "edge_id": int(row["edge_id"]),
        "pre": row["pre"],
        "post": row["post"],
        "baseline_weight": float(row["baseline_weight"]),
        "counterfactual_weight": float(row["counterfactual_weight"]),
        "relevant_anchors": list(row["relevant_anchors"]),
        "sq03b_anchor_results": row["anchor_results"],
        "sq03b_max_abs_peak_voltage_delta": peak_max,
        "sq03b_max_abs_integrated_positive_voltage_delta": integrated_max,
    }


def select_stratum(
    rows: list[dict],
    top_integrated_n: int,
    top_peak_n: int,
    lower_n: int,
) -> dict:
    if len(rows) < max(top_integrated_n, top_peak_n, lower_n):
        raise RuntimeError("stratum is too small for frozen SQ-03C panel rule")

    summarized = [summarize_job(r) for r in rows]

    integrated_ranked = sorted(
        summarized,
        key=lambda r: (
            -r["sq03b_max_abs_integrated_positive_voltage_delta"],
            -r["sq03b_max_abs_peak_voltage_delta"],
            r["edge_id"],
        ),
    )

    peak_ranked = sorted(
        summarized,
        key=lambda r: (
            -r["sq03b_max_abs_peak_voltage_delta"],
            -r["sq03b_max_abs_integrated_positive_voltage_delta"],
            r["edge_id"],
        ),
    )

    lower_ranked = sorted(
        summarized,
        key=lambda r: (
            r["sq03b_max_abs_integrated_positive_voltage_delta"],
            r["sq03b_max_abs_peak_voltage_delta"],
            r["edge_id"],
        ),
    )

    upper_roles: dict[int, set[str]] = defaultdict(set)
    by_edge = {r["edge_id"]: r for r in summarized}

    for r in integrated_ranked[:top_integrated_n]:
        upper_roles[r["edge_id"]].add("TOP_INTEGRATED")
    for r in peak_ranked[:top_peak_n]:
        upper_roles[r["edge_id"]].add("TOP_PEAK")

    lower_ids = [r["edge_id"] for r in lower_ranked[:lower_n]]

    overlap = set(upper_roles).intersection(lower_ids)
    if overlap:
        raise RuntimeError(
            f"upper/lower SQ-03C panel overlap in stratum: {sorted(overlap)}"
        )

    selected = []

    for edge_id in sorted(upper_roles):
        r = dict(by_edge[edge_id])
        r["panel_class"] = "UPPER_TAIL"
        r["selection_roles"] = sorted(upper_roles[edge_id])
        selected.append(r)

    for edge_id in lower_ids:
        r = dict(by_edge[edge_id])
        r["panel_class"] = "LOW_TAIL_CONTROL"
        r["selection_roles"] = ["LOW_INTEGRATED_THEN_PEAK"]
        selected.append(r)

    selected.sort(
        key=lambda r: (
            0 if r["panel_class"] == "UPPER_TAIL" else 1,
            r["edge_id"],
        )
    )

    return {
        "source_job_count": len(rows),
        "upper_tail_count": sum(
            1 for r in selected if r["panel_class"] == "UPPER_TAIL"
        ),
        "low_tail_control_count": sum(
            1 for r in selected if r["panel_class"] == "LOW_TAIL_CONTROL"
        ),
        "selected": selected,
    }


def freeze_panel(ledger_path: Path, cfg: dict) -> dict:
    strata = defaultdict(list)

    with ledger_path.open(encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise RuntimeError(
                    f"invalid JSON in SQ-03B ledger line {lineno}"
                ) from exc

            key = (row["input"], row["subject"])
            strata[key].append(row)

    expected_inputs = cfg["strata"]["expected_inputs"]
    expected_subjects = cfg["strata"]["expected_subjects"]
    expected_keys = {
        (input_label, subject)
        for input_label in expected_inputs
        for subject in expected_subjects
    }

    if set(strata) != expected_keys:
        missing = sorted(expected_keys - set(strata))
        unexpected = sorted(set(strata) - expected_keys)
        raise RuntimeError(
            f"SQ-03C strata mismatch: missing={missing} unexpected={unexpected}"
        )

    sel = cfg["panel_selection"]
    top_integrated_n = int(
        sel["upper_tail_per_stratum"][
            "top_by_abs_integrated_positive_voltage_delta"
        ]
    )
    top_peak_n = int(
        sel["upper_tail_per_stratum"]["top_by_abs_peak_voltage_delta"]
    )
    lower_n = int(sel["lower_tail_controls_per_stratum"])

    strata_records = []
    all_selected = []

    for input_label in expected_inputs:
        for subject in expected_subjects:
            key = (input_label, subject)
            result = select_stratum(
                strata[key],
                top_integrated_n=top_integrated_n,
                top_peak_n=top_peak_n,
                lower_n=lower_n,
            )
            record = {
                "input": input_label,
                "subject": subject,
                **result,
            }
            strata_records.append(record)

            for selected in result["selected"]:
                all_selected.append({
                    "input": input_label,
                    "subject": subject,
                    **selected,
                })

    panel_keys = [
        (r["input"], r["subject"], int(r["edge_id"]))
        for r in all_selected
    ]
    if len(panel_keys) != len(set(panel_keys)):
        raise RuntimeError("duplicate SQ-03C panel job key detected")

    return {
        "strata": strata_records,
        "selected_jobs": all_selected,
        "selected_job_count": len(all_selected),
        "upper_tail_job_count": sum(
            1 for r in all_selected if r["panel_class"] == "UPPER_TAIL"
        ),
        "low_tail_control_job_count": sum(
            1 for r in all_selected if r["panel_class"] == "LOW_TAIL_CONTROL"
        ),
    }
