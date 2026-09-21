#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path.cwd().resolve()
DATA_ROOT = Path.home() / "moscaquant-data"

ARTIFACT = DATA_ROOT / "experiments" / "mq5-ts-topology-specificity-v1.json"
EXPECTED_ARTIFACT_SHA256 = "903bff56fba99580b93db2a875f4c1996e3976a018bb26d306ef61baf73b2811"
OUTPUT = ROOT / "artifacts" / "mq5-ts-claude-review-bundle.md"

FILES = [
    ROOT / "CHARTER.md",
    ROOT / "ROADMAP.md",
    ROOT / "docs" / "KNOWN_CONFOUNDS.md",
    ROOT / "docs" / "experiments" / "mq5-ts-topology-specificity-protocol.md",
    ROOT / "docs" / "experiments" / "mq5-ts-topology-specificity-results.md",
    ROOT / "docs" / "experiments" / "mq5-ts-randomized-ensemble-implementation.md",
    ROOT / "docs" / "experiments" / "mq5-ts-arm-c-native-backend-hardening.md",
    ROOT / "docs" / "retrospectives" / "MOSCAQUANT_EXPERIMENTAL_HIGHLIGHT_REEL.md",
    ROOT / "config" / "controls" / "mq5-ts-topology-specificity-v1.toml",
    ROOT / "brain" / "mq5_ts_metrics.py",
    ROOT / "brain" / "mq5_ts_harness.py",
    ROOT / "brain" / "mq5_ts_runtime.py",
    ROOT / "brain" / "mq5_ts_duplicate_replay.py",
    ROOT / "brain" / "mq5_ts_randomized_ensemble.py",
    ROOT / "brain" / "mq5_ts_strict_shuffle.py",
    ROOT / "brain" / "mq5_ts_strict_shuffle_native.py",
    ROOT / "brain" / "mq5_ts_strict_shuffle_verify.py",
]

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def git(args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    return result.stdout.strip()

if not ARTIFACT.exists():
    raise SystemExit(f"missing result artifact: {ARTIFACT}")

artifact_sha = sha256_file(ARTIFACT)
if artifact_sha != EXPECTED_ARTIFACT_SHA256:
    raise SystemExit(
        "result artifact hash mismatch:\n"
        f"expected {EXPECTED_ARTIFACT_SHA256}\n"
        f"actual   {artifact_sha}"
    )

payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

missing = [str(path) for path in FILES if not path.exists()]
if missing:
    raise SystemExit("missing review-bundle files:\n" + "\n".join(missing))

summary = {
    "artifact": payload.get("artifact"),
    "artifact_sha256": artifact_sha,
    "execution_commit": payload.get("execution_commit"),
    "a_d_gate_sha256": payload.get("a_d_gate_sha256"),
    "arm_B_seed_count_expected": payload["arm_B"].get("seed_count_expected"),
    "arm_B_seed_count_completed": payload["arm_B"].get("seed_count_completed"),
    "arm_B_exact_reproductions": payload["arm_B"].get("exact_response_pattern_reproductions"),
    "arm_C_seed_count_expected": payload["arm_C"].get("seed_count_expected"),
    "arm_C_seed_count_completed": payload["arm_C"].get("seed_count_completed"),
    "arm_C_exact_reproductions": payload["arm_C"].get("exact_response_pattern_reproductions"),
    "arm_C_classification": payload["arm_C"].get("classification"),
    "financial_semantics_used": payload.get("financial_semantics_used"),
}

sections = [
"""# MoscaQuant MQ-5.TS — External Methodology Review Bundle

## Purpose

This bundle is intended for an independent critical review of MoscaQuant's
MQ-5.TS topology-specificity experiment.

Please review this as a scientific/methodological audit, not as a request to
agree with the project's conclusions.

## Questions for the reviewer

1. Does the preregistered Arm C null genuinely isolate specific wiring beyond
   the structural statistics it preserves?
2. Are the exact-reproduction criteria scientifically coherent and faithfully
   implemented?
3. Does `0 / 20` exact reproduction support the frozen classification without
   stronger claims than the design warrants?
4. Are there implementation details that could accidentally make Arm C more
   destructive than its protocol states?
5. Is the A/D positive-control gate sufficient to show that the measurement
   stack can detect a known topology intervention?
6. Are there unaddressed multiple-comparison, stopping-rule, seed-selection,
   determinism, or artifact-provenance problems?
7. Does the result justify saying that the specific directed wiring arrangement
   contributes materially within the frozen model?
8. What scientifically useful null family or robustness test would be the
   strongest next challenge?
9. Which project claims should be weakened, strengthened, or left exactly as
   written?
10. Please distinguish bugs, methodological limitations, alternative
    interpretations, and future experiments.

Do not assume financial meaning. Financial semantics are explicitly unassigned.
""",
    "## Frozen result summary\n\n```json\n"
    + json.dumps(summary, indent=2, sort_keys=True)
    + "\n```\n",
    "## Repository provenance\n\n"
    f"- HEAD: `{git(['rev-parse', 'HEAD'])}`\n"
    f"- HEAD description: `{git(['log', '-1', '--oneline'])}`\n"
    "- working tree status at bundle creation:\n\n```text\n"
    + (git(["status", "--short"]) or "<clean>")
    + "\n```\n",
]

for path in FILES:
    relative = path.relative_to(ROOT)
    suffix = path.suffix.lower()
    fence = "python" if suffix == ".py" else "toml" if suffix == ".toml" else "markdown"
    sections.append(
        "\n" + "=" * 88
        + f"\n\n# FILE: {relative}\n\n"
        + f"SHA-256: `{sha256_file(path)}`\n\n"
        + f"```{fence}\n"
        + path.read_text(encoding="utf-8")
        + "\n```\n"
    )

sections.append(
    "\n" + "=" * 88
    + "\n\n# FROZEN RESULT ARTIFACT\n\n"
    + f"Path: `{ARTIFACT}`\n\n"
    + f"SHA-256: `{artifact_sha}`\n\n"
    + "```json\n"
    + json.dumps(payload, indent=2, sort_keys=True)
    + "\n```\n"
)

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text("\n".join(sections), encoding="utf-8")

print("wrote", OUTPUT)
print("artifact SHA-256:", artifact_sha)
print("bundle SHA-256:", sha256_file(OUTPUT))
print()
print("Give this file to Claude and ask for a hostile-but-fair methodology review.")
