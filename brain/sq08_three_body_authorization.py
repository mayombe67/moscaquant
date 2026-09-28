from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

from brain.sq08_three_body_readiness import (
    EXPECTED,
    SCIENCE_GIT_SHA,
    verify_artifacts,
    verify_manifest,
    verify_repository,
)


ROOT = Path(__file__).resolve().parents[1]

OUTPUT = (
    ROOT
    / "config/controls/"
    "sq08-three-body-execution-authorization-v1.json"
)

EXPECTED_CONTROL_PLANE_ANCESTOR = (
    "e232fd2a103db762180422f638bafe13519da38a"
)


class AuthorizationFailure(RuntimeError):
    pass


def fail(message: str) -> None:
    raise AuthorizationFailure(message)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()

    with path.open("rb") as handle:
        for block in iter(
            lambda: handle.read(8 * 1024 * 1024),
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


def verify_control_plane_ancestry() -> str:
    result = subprocess.run(
        [
            "git",
            "merge-base",
            "--is-ancestor",
            EXPECTED_CONTROL_PLANE_ANCESTOR,
            "HEAD",
        ],
        cwd=ROOT,
    )

    if result.returncode != 0:
        fail(
            "current HEAD does not descend from "
            "reviewed SQ-08 readiness revision"
        )

    return git(
        "rev-parse",
        "HEAD",
    )


def build_authorization() -> dict:
    repository = verify_repository()
    artifacts = verify_artifacts()
    manifest = verify_manifest()

    control_plane_sha = (
        verify_control_plane_ancestry()
    )

    if repository[
        "working_tree_clean"
    ] is not True:
        fail(
            "authorization requires clean tree"
        )

    if (
        repository[
            "science_git_sha"
        ]
        != SCIENCE_GIT_SHA
    ):
        fail(
            "science identity drift"
        )

    conditions = manifest[
        "conditions"
    ]

    if len(conditions) != 16:
        fail(
            "authorization requires exactly "
            "16 work units"
        )

    condition_ids = [
        row["condition_id"]
        for row in conditions
    ]

    if len(set(condition_ids)) != 16:
        fail(
            "authorization condition IDs "
            "must be unique"
        )

    return {
        "schema_version": (
            "moscaquant."
            "sq08-three-body-execution-authorization/v1"
        ),

        "experiment": "SQ-08",

        "codename":
            "THREE BODY PROBLEM",

        "status":
            "AUTHORIZED_FOR_FROZEN_EXECUTION",

        "science_git_sha":
            SCIENCE_GIT_SHA,

        "control_plane_git_sha":
            control_plane_sha,

        "execution_manifest_sha256":
            EXPECTED[
                "execution_manifest"
            ][1],

        "frozen_artifact_hashes":
            artifacts,

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
            "work_unit_count": 16,

            "authorized_condition_ids":
                condition_ids,

            "arbitrary_condition_execution":
                False,

            "manifest_regeneration_at_execution":
                False,

            "overwrite_existing_evidence":
                False,

            "implicit_resume":
                False,

            "all_work_units_required":
                True,

            "independent_verification_required":
                True,
        },

        "execution_boundary": {
            "authorization_only":
                True,

            "analysis_authority":
                False,

            "mechanism_interpretation_authority":
                False,

            "result_reclassification_authority":
                False,
        },
    }


def main() -> None:
    payload = build_authorization()

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
        "SQ-08 execution authorization frozen"
    )

    print(
        "science git sha:",
        payload["science_git_sha"],
    )

    print(
        "control plane git sha:",
        payload["control_plane_git_sha"],
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
        "output:",
        OUTPUT.relative_to(ROOT),
    )

    print(
        "output sha256:",
        sha256_file(OUTPUT),
    )


if __name__ == "__main__":
    main()
