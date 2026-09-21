#!/usr/bin/env python3
from pathlib import Path
import hashlib
import json
import subprocess
import tomllib

ROOT = Path.cwd().resolve()

CONFIG = ROOT / "config/controls/mq5-er-encoding-robustness-v1.toml"
ENCODING_ARTIFACT = ROOT / "artifacts/mq5-er-encoding-real-artifact-verification-v1.json"
CLAUDE_BUNDLE = ROOT / "artifacts/mq5-ts-claude-review-bundle.md"

EXPECTED_ENCODING_SHA = "15340cae365c291424f88ac3206e7ddc3f16885a52e89aece96d347bba741acb"

REQUIRED_TRACKED = (
    "config/controls/mq5-er-encoding-robustness-v1.toml",
    "artifacts/mq5-er-encoding-real-artifact-verification-v1.json",
    "brain/mq5_er_encoder.py",
    "brain/mq5_er_real_artifact_verify.py",
    "brain/mq5_er_neural_runner.py",
    "tests/brain/test_mq5_er_encoder.py",
    "tests/brain/test_mq5_er_real_artifact_verify.py",
    "tests/brain/test_mq5_er_neural_runner.py",
    "docs/experiments/mq5-er-encoding-robustness-protocol.md",
    "docs/experiments/mq5-er-encoding-robustness-amendment-v1.md",
    "docs/experiments/mq5-er-response-classification-contract-v1.md",
    "docs/experiments/mq5-er-response-contract-amendment-v1.md",
    "docs/experiments/mq5-er-neural-runner-implementation.md",
)

EXPECTED_RUNNER_FREEZE = "37cccff"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git(*args: str) -> str:
    cp = subprocess.run(
        ["git", *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    if cp.returncode != 0:
        raise RuntimeError(
            f"git {' '.join(args)} failed:\n{cp.stdout}"
        )
    return cp.stdout.strip()


def main() -> None:
    if not (ROOT / ".git").exists():
        raise SystemExit("Run from MoscaQuant repository root.")

    if not CONFIG.exists():
        raise SystemExit(f"missing config: {CONFIG}")

    if not ENCODING_ARTIFACT.exists():
        raise SystemExit(
            f"missing encoding artifact: {ENCODING_ARTIFACT}"
        )

    with CONFIG.open("rb") as f:
        cfg = tomllib.load(f)

    checks = {}

    head = git("rev-parse", "HEAD")
    checks["head"] = head

    runner_freeze = git(
        "rev-parse",
        f"{EXPECTED_RUNNER_FREEZE}^{{commit}}",
    )
    checks["runner_freeze_commit"] = runner_freeze

    ancestor_check = subprocess.run(
        [
            "git",
            "merge-base",
            "--is-ancestor",
            runner_freeze,
            head,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    checks["runner_freeze_is_ancestor"] = (
        ancestor_check.returncode == 0
    )

    tracked = set(git("ls-files").splitlines())
    missing_tracked = [
        path for path in REQUIRED_TRACKED
        if path not in tracked
    ]
    checks["required_tracked_files_missing"] = missing_tracked

    actual_encoding_sha = sha256_file(ENCODING_ARTIFACT)
    checks["encoding_artifact_sha256"] = actual_encoding_sha
    checks["encoding_artifact_sha_matches"] = (
        actual_encoding_sha == EXPECTED_ENCODING_SHA
    )

    checks["result_execution_enabled"] = bool(
        cfg["execution"]["result_execution_enabled"]
    )
    checks["preservation_tolerances_frozen"] = bool(
        cfg["classification"]["preservation_tolerances_frozen"]
    )

    status = git("status", "--porcelain")
    status_lines = [
        line for line in status.splitlines()
        if line.strip()
    ]
    checks["git_status_lines"] = status_lines

    only_expected_bundle_dirty = (
        status_lines
        == ["?? artifacts/mq5-ts-claude-review-bundle.md"]
    )
    checks["only_expected_claude_bundle_untracked"] = (
        only_expected_bundle_dirty
    )

    checks["claude_bundle_present"] = CLAUDE_BUNDLE.exists()

    safe_hold = (
        checks["runner_freeze_is_ancestor"]
        and checks["encoding_artifact_sha_matches"]
        and not missing_tracked
        and checks["preservation_tolerances_frozen"]
        and not checks["result_execution_enabled"]
        and only_expected_bundle_dirty
    )
    checks["safe_pre_audit_hold_state"] = bool(safe_hold)

    print("=" * 88)
    print("MQ-5.ER PRE-AUDIT LAUNCH READINESS CHECK")
    print("=" * 88)
    print("HEAD:", head)
    print(
        "Runner freeze is ancestor:",
        checks["runner_freeze_is_ancestor"],
    )
    print("Encoding artifact SHA OK:", checks["encoding_artifact_sha_matches"])
    print("Required tracked files missing:", missing_tracked)
    print("Classification frozen:", checks["preservation_tolerances_frozen"])
    print("Result execution enabled:", checks["result_execution_enabled"])
    print("Claude bundle present:", checks["claude_bundle_present"])
    print("Only expected bundle untracked:", only_expected_bundle_dirty)
    print()
    print("SAFE PRE-AUDIT HOLD STATE:", safe_hold)

    if checks["result_execution_enabled"]:
        raise SystemExit(
            "FAIL: result_execution_enabled must remain false before audit resolution."
        )

    if not safe_hold:
        raise SystemExit(
            "FAIL: pre-audit hold state is not clean enough for handoff."
        )

    print()
    print("PASS")
    print("NO NEURAL RESULT EXECUTED.")
    print("MQ-5.ER REMAINS BLOCKED PENDING MQ-5.TS AUDIT.")


if __name__ == "__main__":
    main()
