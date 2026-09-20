from __future__ import annotations

from pathlib import Path
import hashlib
import json
import subprocess

from brain.sq03d1_panel_freezer import (
    allocate_stratified,
    rebuild_pairs,
    upper_sort_key,
    low_sort_key,
)

ROOT = Path(__file__).resolve().parents[1]
CFG_PATH = ROOT / "config" / "experiments" / "sq03d1_scalar_verification_v1.json"
SQ03D_RESULT = ROOT / "artifacts" / "sidequests" / "sq03d-reciprocity-result-v1.json"
SQ03B_LEDGER = ROOT / "artifacts" / "sidequests" / "sq03b-checkpoints-v1" / "results.ndjson"
OUTPUT = ROOT / "artifacts" / "sidequests" / "sq03d1-verification-panel-v1.json"


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
        raise RuntimeError("Refusing to freeze SQ-03D.1 panel with dirty worktree")


def canonical_top100(rows: list[dict]) -> list[dict]:
    return sorted(rows, key=upper_sort_key)[:100]


def comparable_row(row: dict) -> dict:
    return {
        "input": row["input"],
        "edge_id": int(row["edge_id"]),
        "anchor": row["anchor"],
        "pre": row["pre"],
        "post": row["post"],
        "integrated": row["integrated"],
        "peak": row["peak"],
    }


def main() -> int:
    require_clean_worktree()

    if OUTPUT.exists():
        raise RuntimeError(f"Refusing to overwrite existing SQ-03D.1 panel: {OUTPUT}")

    cfg = json.loads(CFG_PATH.read_text())
    sq03d = json.loads(SQ03D_RESULT.read_text())

    if cfg["status"] != "FROZEN_BEFORE_PANEL_SELECTION":
        raise RuntimeError("Unexpected SQ-03D.1 protocol status")
    if sq03d["classification"] != "AUTHORITATIVE_PAIRED_BACKGROUND_ANALYSIS":
        raise RuntimeError("Unexpected SQ-03D result classification")

    actual_ledger_hash = sha256(SQ03B_LEDGER)
    if actual_ledger_hash != sq03d["sq03b_ledger_sha256"]:
        raise RuntimeError("SQ-03B ledger hash does not match authoritative SQ-03D result")

    rows = rebuild_pairs(SQ03B_LEDGER)

    if len(rows) != int(sq03d["pair_count"]):
        raise RuntimeError(
            f"SQ-03D replay pair-count mismatch: {len(rows)} != {sq03d['pair_count']}"
        )

    replay_top100 = [comparable_row(r) for r in canonical_top100(rows)]
    stored_top100 = [comparable_row(r) for r in sq03d["top_context_residual_candidates"]]
    if replay_top100 != stored_top100:
        raise RuntimeError("SQ-03D replay top-100 ranking does not match authoritative result")

    sel = cfg["panel_selection"]

    upper = allocate_stratified(
        rows=rows,
        total=int(sel["upper_tail_pairs"]),
        minimum_per_input=int(sel["minimum_upper_per_input"]),
        sort_key=upper_sort_key,
    )

    upper_keys = {
        (r["input"], int(r["edge_id"]), r["anchor"])
        for r in upper
    }

    low = allocate_stratified(
        rows=rows,
        total=int(sel["low_tail_controls"]),
        minimum_per_input=int(sel["minimum_low_per_input"]),
        sort_key=low_sort_key,
        excluded=upper_keys,
    )

    low_keys = {
        (r["input"], int(r["edge_id"]), r["anchor"])
        for r in low
    }

    overlap = upper_keys & low_keys
    if overlap:
        raise RuntimeError(f"upper/low panel overlap: {sorted(overlap)}")

    def decorate(row: dict, panel_class: str) -> dict:
        return {
            "panel_class": panel_class,
            **comparable_row(row),
        }

    upper_out = [decorate(r, "UPPER_TAIL") for r in upper]
    low_out = [decorate(r, "LOW_TAIL_CONTROL") for r in low]

    artifact = {
        "schema": "moscaquant.sq03d1_verification_panel/v1",
        "sidequest_id": "SQ-03D.1",
        "title": "DOUBLE CHECK THE KNIFE",
        "classification": "FROZEN_VERIFICATION_PANEL",
        "source_commit": git_head(),
        "protocol_sha256": sha256(CFG_PATH),
        "sq03d_result_sha256": sha256(SQ03D_RESULT),
        "sq03b_ledger_sha256": actual_ledger_hash,
        "sq03d_replay_pair_count": len(rows),
        "sq03d_top100_replay_exact": True,
        "upper_tail_count": len(upper_out),
        "low_tail_control_count": len(low_out),
        "upper_tail": upper_out,
        "low_tail_controls": low_out,
        "claim_boundary": (
            "Panel selection only. Pair identities were deterministically recovered "
            "from the exact hashed SQ-03B ledger by replaying the frozen SQ-03D "
            "pairing/ranking logic. No SQ-03D.1 neural dynamics were executed."
        ),
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n")

    print("SQ-03D.1 — FROZEN VERIFICATION PANEL")
    print("=" * 72)
    print("source commit:", artifact["source_commit"])
    print("SQ-03D replay pairs:", artifact["sq03d_replay_pair_count"])
    print("SQ-03D top-100 replay exact:", artifact["sq03d_top100_replay_exact"])
    print("upper-tail pairs:", artifact["upper_tail_count"])
    print("low-tail controls:", artifact["low_tail_control_count"])
    print()

    for label, panel in (
        ("UPPER", upper_out),
        ("LOW", low_out),
    ):
        counts = {}
        for row in panel:
            counts[row["input"]] = counts.get(row["input"], 0) + 1
        print(label, "per input:", dict(sorted(counts.items())))
    print()

    print("UPPER-TAIL PANEL")
    for i, row in enumerate(upper_out, 1):
        print(
            f"  {i:2d}. {row['input']:10s} {row['anchor']:5s} "
            f"edge={row['edge_id']:6d} {row['pre']}->{row['post']} "
            f"C={row['integrated']['context_residual']:.12g}"
        )

    print()
    print("LOW-TAIL CONTROLS")
    for i, row in enumerate(low_out, 1):
        print(
            f"  {i:2d}. {row['input']:10s} {row['anchor']:5s} "
            f"edge={row['edge_id']:6d} {row['pre']}->{row['post']} "
            f"C={row['integrated']['context_residual']:.12g}"
        )

    print()
    print("artifact:", OUTPUT)
    print("No neural dynamics were executed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
