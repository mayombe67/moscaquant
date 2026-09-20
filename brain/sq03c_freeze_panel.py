from __future__ import annotations

from pathlib import Path
import json
import subprocess

from brain.sq03c_panel_freezer import freeze_panel, sha256

ROOT = Path(__file__).resolve().parents[1]
CFG_PATH = ROOT / "config" / "experiments" / "sq03c_scalar_verification_v1.json"
SQ03B_RESULT = ROOT / "artifacts" / "sidequests" / "sq03b-mechanistic-localization-result-v1.json"
SQ03B_LEDGER = ROOT / "artifacts" / "sidequests" / "sq03b-checkpoints-v1" / "results.ndjson"
OUTPUT = ROOT / "artifacts" / "sidequests" / "sq03c-verification-panel-v1.json"


def git_head() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()


def require_clean_worktree() -> None:
    status = subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    )
    if status.strip():
        raise RuntimeError(
            "Refusing to freeze SQ-03C verification panel with dirty worktree."
        )


def main() -> int:
    require_clean_worktree()

    if OUTPUT.exists():
        raise RuntimeError(f"Refusing to overwrite SQ-03C panel: {OUTPUT}")

    cfg = json.loads(CFG_PATH.read_text())

    if cfg["status"] != "FROZEN_BEFORE_PANEL_SELECTION":
        raise RuntimeError("Unexpected SQ-03C protocol status")

    expected_result_hash = cfg["parents"]["sq03b_result_sha256"]
    expected_ledger_hash = cfg["parents"]["sq03b_ledger_sha256"]

    actual_result_hash = sha256(SQ03B_RESULT)
    actual_ledger_hash = sha256(SQ03B_LEDGER)

    if actual_result_hash != expected_result_hash:
        raise RuntimeError(
            "SQ-03B result hash mismatch; refusing SQ-03C panel selection"
        )
    if actual_ledger_hash != expected_ledger_hash:
        raise RuntimeError(
            "SQ-03B ledger hash mismatch; refusing SQ-03C panel selection"
        )

    frozen = freeze_panel(SQ03B_LEDGER, cfg)

    artifact = {
        "schema": "moscaquant.sq03c_verification_panel/v1",
        "sidequest_id": "SQ-03C",
        "title": "CHECK THE RECEIPTS",
        "classification": "FROZEN_VERIFICATION_PANEL",
        "source_commit": git_head(),
        "protocol_sha256": sha256(CFG_PATH),
        "sq03b_result_sha256": actual_result_hash,
        "sq03b_ledger_sha256": actual_ledger_hash,
        "selection_rule": cfg["panel_selection"],
        **frozen,
        "claim_boundary": (
            "Panel selection only. The panel was derived deterministically "
            "from the completed SQ-03B ledger under the frozen SQ-03C rule. "
            "No SQ-03C neural dynamics were executed."
        ),
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n")

    print("SQ-03C — FROZEN VERIFICATION PANEL")
    print("=" * 72)
    print("source commit:", artifact["source_commit"])
    print("selected jobs:", artifact["selected_job_count"])
    print("upper-tail jobs:", artifact["upper_tail_job_count"])
    print("low-tail controls:", artifact["low_tail_control_job_count"])
    print()

    for s in artifact["strata"]:
        print(
            f"{s['input']:10s} {s['subject']:6s} "
            f"source={s['source_job_count']:6d} "
            f"upper={s['upper_tail_count']:2d} "
            f"low={s['low_tail_control_count']:2d}"
        )

    print()
    print("artifact:", OUTPUT)
    print("No neural dynamics were executed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
