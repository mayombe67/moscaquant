from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tempfile
import tomllib
from pathlib import Path

from brain.mq5_er1_detour_runner import (
    AFFECTED_TARGETS,
    ALL_TRACE_TARGETS,
    C_BASELINE_ONSETS,
    EXPECTED_PARENT_SHA256,
    RETAINED_TARGETS,
    build_stimuli,
    classify_family,
    load_inputs,
    load_parent_result,
    score_target_streaming,
    verify_known_replay,
)
from config.paths import data_path


CONFIG = Path("config/controls/mq5-er1-detour-laptop-pilot-v1.toml")
OUTPUT = data_path(
    "experiments",
    "mq5-er1-detour-laptop-pilot-r2-v1.json",
)
MAX_BACKWARD_HOPS = 2


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load_config() -> dict:
    with CONFIG.open("rb") as handle:
        return tomllib.load(handle)


def git_status_porcelain() -> str:
    completed = subprocess.run(
        ["git", "status", "--porcelain"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stdout)
    return completed.stdout


def git_head() -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stdout)
    return completed.stdout.strip()


def execution_gate(protocol: dict) -> str:
    if protocol["experiment"]["authoritative"]:
        raise RuntimeError("pilot must remain non-authoritative")

    if int(protocol["scope"]["max_backward_hops"]) != 2:
        raise RuntimeError("pilot hop depth is not frozen at 2")

    for key in (
        "may_amend_parent_protocol",
        "may_supply_roadblock_candidates",
        "may_tune_thresholds",
        "may_create_causal_claims",
    ):
        if protocol["restrictions"][key]:
            raise RuntimeError(f"pilot restriction violated: {key}")

    if not protocol["execution"]["result_execution_enabled"]:
        raise RuntimeError(
            "DETOUR LAPTOP PILOT EXECUTION REFUSED: "
            "result_execution_enabled is false"
        )

    if git_status_porcelain().strip():
        raise RuntimeError(
            "DETOUR LAPTOP PILOT EXECUTION REFUSED: working tree not clean"
        )

    if OUTPUT.exists():
        raise RuntimeError(
            f"pilot result artifact already exists: {OUTPUT}"
        )

    return git_head()


def run_pilot() -> dict:
    load_parent_result()
    protocol = load_config()
    head = execution_gate(protocol)

    original, lesioned, retina, responders, causal_edges = load_inputs()
    a_stimuli, c_stimuli, a_sha, c_sha = build_stimuli()

    with tempfile.TemporaryDirectory(
        prefix="mq5-er1-detour-laptop-pilot-"
    ) as temp:
        replay = verify_known_replay(
            original=original,
            lesioned=lesioned,
            retinal_indices=retina,
            responders=responders,
            a_stimuli=a_stimuli,
            c_stimuli=c_stimuli,
            scratch_dir=Path(temp),
        )

        lesioned_edge_set = {
            (int(pre), int(post))
            for pre, post, _weight in causal_edges
        }

        by_target = {}

        for target in ALL_TRACE_TARGETS:
            onset = C_BASELINE_ONSETS[int(target)]
            by_target[int(target)] = score_target_streaming(
                original=original,
                lesioned_edges=lesioned_edge_set,
                target=int(target),
                onset=int(onset),
                divergence_snapshot=replay[
                    "divergence_snapshots"
                ][int(onset)],
                lesion_snapshot=replay[
                    "lesion_snapshots"
                ][int(onset)],
                max_backward_hops=MAX_BACKWARD_HOPS,
            )

        payload = {
            "experiment": "mq5-er1-detour-laptop-pilot-r2-v1",
            "parent_experiment": "mq5-er1-detour-v1",
            "status": "ENGINEERING PILOT — NON-AUTHORITATIVE",
            "authoritative": False,
            "git_head": head,
            "parent_result_sha256": EXPECTED_PARENT_SHA256,
            "arm_a_stimulus_sha256": a_sha,
            "arm_c_stimulus_sha256": c_sha,
            "max_backward_hops": MAX_BACKWARD_HOPS,
            "affected_targets": list(AFFECTED_TARGETS),
            "retained_dependency_targets": list(RETAINED_TARGETS),
            "classification": classify_family(by_target),
            "targets": {
                str(k): v
                for k, v in sorted(by_target.items())
            },
            "may_supply_roadblock_candidates": False,
            "may_amend_parent_protocol": False,
            "causal_claims_authorized": False,
            "financial_semantics": "NOT ASSIGNED",
        }

        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(
            json.dumps(
                payload,
                indent=2,
                sort_keys=True,
                allow_nan=False,
            )
            + "\n",
            encoding="utf-8",
        )

        payload["result_artifact"] = str(OUTPUT)
        payload["result_sha256"] = sha256_file(OUTPUT)
        return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--run-pilot",
        action="store_true",
        required=True,
    )
    parser.parse_args()

    print(json.dumps(
        run_pilot(),
        indent=2,
        sort_keys=True,
        allow_nan=False,
    ))


if __name__ == "__main__":
    main()
