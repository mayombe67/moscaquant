from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

from brain.sq11_dark_forest_readiness import (
    EXPECTED_MANIFEST_SHA256,
    SCIENCE_GIT_SHA,
    verify_body_topology,
    verify_manifest,
    verify_output_destinations,
    verify_physical_inputs,
    verify_replay_qualification_closure,
    verify_repo_artifacts,
    verify_repository,
    verify_runtime_semantics,
)


ROOT = Path(__file__).resolve().parents[1]

OUTPUT = (
    ROOT
    / "config/controls/"
    "sq11-dark-forest-execution-authorization-v1.json"
)

READINESS = (
    ROOT
    / "brain/"
    "sq11_dark_forest_readiness.py"
)

EXPECTED_READINESS_COMMIT = (
    "37c1dba5f88df123bca92e6bc6da009ed9c63707"
)

EXPECTED_READINESS_SHA256 = (
    "078fe3b1114a50ce3c859ea43c015f2fc9c8e068a32d0bc56129acd231db6674"
)


class AuthorizationFailure(RuntimeError):
    pass


def fail(message: str) -> None:
    raise AuthorizationFailure(message)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()

    with path.open("rb") as handle:
        for block in iter(
            lambda: handle.read(
                8 * 1024 * 1024
            ),
            b"",
        ):
            h.update(block)

    return h.hexdigest()


def git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    if result.returncode != 0:
        fail(
            f"git {' '.join(args)} failed:\n"
            f"{result.stdout}"
        )

    return result.stdout.strip()


def verify_readiness_revision() -> str:
    actual = sha256_file(
        READINESS
    )

    if (
        actual
        != EXPECTED_READINESS_SHA256
    ):
        fail(
            "SQ-11 readiness source SHA drift: "
            f"{actual} != "
            f"{EXPECTED_READINESS_SHA256}"
        )

    git(
        "cat-file",
        "-e",
        f"{EXPECTED_READINESS_COMMIT}^{{commit}}",
    )

    result = subprocess.run(
        [
            "git",
            "merge-base",
            "--is-ancestor",
            EXPECTED_READINESS_COMMIT,
            "HEAD",
        ],
        cwd=ROOT,
    )

    if result.returncode != 0:
        fail(
            "HEAD does not descend from "
            "reviewed SQ-11 readiness revision"
        )

    return git(
        "rev-parse",
        "HEAD",
    )


def assemble_authorization(
    *,
    manifest: dict,
    control_plane_sha: str,
    repo_artifacts: dict,
    physical_inputs: dict,
    runtime: dict,
    body_topology: dict,
    replay_qualification: dict,
    output_destinations: dict,
) -> dict:
    conditions = manifest[
        "conditions"
    ]

    if len(conditions) != 16:
        fail(
            "SQ-11 authorization requires "
            "exactly 16 work units"
        )

    condition_ids = [
        row["condition_id"]
        for row in conditions
    ]

    if len(set(condition_ids)) != 16:
        fail(
            "SQ-11 authorization condition "
            "IDs must be unique"
        )

    return {
        "schema_version":
            "moscaquant."
            "sq11-dark-forest-execution-authorization/v1",

        "experiment":
            "SQ-11",

        "codename":
            "DARK FOREST",

        "status":
            "AUTHORIZED_FOR_FROZEN_EXECUTION",

        "science_git_sha":
            SCIENCE_GIT_SHA,

        "execution_manifest_sha256":
            EXPECTED_MANIFEST_SHA256,

        "readiness": {
            "git_commit":
                EXPECTED_READINESS_COMMIT,

            "source_sha256":
                EXPECTED_READINESS_SHA256,
        },

        "control_plane_git_sha":
            control_plane_sha,

        "authorized_work_units": [
            {
                "ordinal":
                    row["ordinal"],

                "condition_id":
                    row["condition_id"],

                "mask":
                    row["mask"],

                "replicate":
                    row["replicate"],

                "edge_zeroed":
                    row["edge_zeroed"],
            }
            for row in conditions
        ],

        "execution_contract": {
            "work_unit_count":
                16,

            "authorized_condition_ids":
                condition_ids,

            "layout":
                "RL",

            "frame_count":
                192,

            "replay_version":
                2,

            "replay_float_dtype":
                "float32",

            "replay_absolute_tolerance":
                0.0,

            "replay_relative_tolerance":
                0.0,

            "structural_lesion_required":
                True,

            "zero_multiplication_equivalent":
                False,

            "baseline_binding_required":
                True,

            "arbitrary_condition_execution":
                False,

            "manifest_regeneration_at_execution":
                False,

            "overwrite_existing_evidence":
                False,

            "overwrite_existing_receipt":
                False,

            "implicit_resume":
                False,

            "all_work_units_required":
                True,

            "both_replicates_required_per_mask":
                True,

            "independent_verification_required":
                True,

            "persisted_reverification_required":
                True,

            "analysis_after_verification_only":
                True,
        },

        "verified_dependency_closure": {
            "repo_artifact_hashes":
                repo_artifacts,

            "physical_inputs":
                physical_inputs,

            "runtime_parameters":
                runtime,

            "body_topology":
                body_topology,

            "replay_qualification":
                replay_qualification,

            "output_destinations":
                output_destinations,
        },

        "execution_boundary": {
            "authorization_only":
                True,

            "execution_performed":
                False,

            "analysis_authority":
                False,

            "mechanism_interpretation_authority":
                False,

            "result_reclassification_authority":
                False,

            "tolerance_modification_authority":
                False,

            "condition_selection_authority":
                False,
        },
    }


def build_authorization() -> dict:
    #
    # Clean control plane first.
    #
    repository = (
        verify_repository()
    )

    manifest = (
        verify_manifest()
    )

    repo_artifacts = (
        verify_repo_artifacts(
            manifest
        )
    )

    physical_inputs = (
        verify_physical_inputs(
            manifest
        )
    )

    runtime = (
        verify_runtime_semantics(
            manifest
        )
    )

    body_topology = (
        verify_body_topology(
            manifest
        )
    )

    replay_qualification = (
        verify_replay_qualification_closure(
            manifest
        )
    )

    output_destinations = (
        verify_output_destinations(
            manifest
        )
    )

    control_plane_sha = (
        verify_readiness_revision()
    )

    if (
        repository[
            "working_tree_clean"
        ]
        is not True
    ):
        fail(
            "SQ-11 authorization requires "
            "clean working tree"
        )

    return assemble_authorization(
        manifest=manifest,
        control_plane_sha=
            control_plane_sha,
        repo_artifacts=
            repo_artifacts,
        physical_inputs=
            physical_inputs,
        runtime=runtime,
        body_topology=
            body_topology,
        replay_qualification=
            replay_qualification,
        output_destinations=
            output_destinations,
    )


def main() -> None:
    if OUTPUT.exists():
        fail(
            "SQ-11 authorization artifact "
            "already exists; overwrite forbidden"
        )

    payload = (
        build_authorization()
    )

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT.write_text(
        json.dumps(
            payload,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    print(
        "SQ-11 DARK FOREST frozen "
        "execution authorization created"
    )

    print(
        "science git sha:",
        payload[
            "science_git_sha"
        ],
    )

    print(
        "control plane git sha:",
        payload[
            "control_plane_git_sha"
        ],
    )

    print(
        "manifest sha256:",
        payload[
            "execution_manifest_sha256"
        ],
    )

    print(
        "authorized work units:",
        len(
            payload[
                "authorized_work_units"
            ]
        ),
    )

    print(
        "execution performed:",
        payload[
            "execution_boundary"
        ][
            "execution_performed"
        ],
    )

    print(
        "output:",
        OUTPUT.relative_to(ROOT),
    )

    print(
        "output sha256:",
        sha256_file(OUTPUT),
    )


if __name__ == "__main__":
    main()
