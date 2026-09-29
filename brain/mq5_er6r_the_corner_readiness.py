"""Read-only readiness inventory. Cannot qualify or authorize THE CORNER."""
from __future__ import annotations

import json

from brain import mq5_er6r_the_corner as corner
from brain import mq5_er6r_the_corner_runner as runner


def inspect_readiness() -> dict:
    stage = corner.load_frozen_stage()
    inputs = {
        name: {"path": str(path), "present": path.is_file()}
        for name, path in runner.INPUTS.items()
    }
    missing = [name for name, entry in inputs.items() if not entry["present"]]
    blockers = [f"missing_input:{name}" for name in missing]
    if runner._git("status", "--porcelain"):
        blockers.append("worktree_not_clean")
    if not runner.OUTPUT.parent.is_dir():
        blockers.append("result_directory_missing")
    if runner.OUTPUT.exists():
        blockers.append("result_already_exists_do_not_rerun")
    if not runner.QUALIFICATION.is_file():
        blockers.append("runner_qualification_missing")
    if not runner.AUTHORIZATION.is_file():
        blockers.append("neural_execution_authorization_missing")
    # Presence is not validity, and this tool neither hashes large data nor
    # exercises a write path. Never emit a qualification status from inventory.
    return {
        "schema_version": "moscaquant.mq5-er6r-the-corner-readiness/v1",
        "stage_id": stage["stage_id"],
        "status": "INVENTORY_ONLY_NOT_EXECUTION_QUALIFICATION",
        "git_sha": runner._git("rev-parse", "HEAD"),
        "candidate_node": stage["candidate_node"],
        "matched_control_node": stage["matched_control_node"],
        "inputs": inputs,
        "observed_blockers": blockers,
        "pending_verification": [
            "source_and_input_sha_bindings",
            "RASPUTIN_runtime_image_and_execution_path_acceptance",
            "durable_output_creation_and_handoff",
            "sealed_qualification_and_separate_execution_authorization",
        ],
        "authoritative_neural_execution": False,
        "qualification_granted": False,
        "execution_authorized": False,
    }


def main() -> None:
    print(json.dumps(inspect_readiness(), sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
