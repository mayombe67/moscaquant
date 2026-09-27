from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

SCIENCE_GIT_SHA = (
    "e4a58df478d7681b612ed9deb85b5ddfe1268acc"
)

CONNECTOME_SHA256 = (
    "e00e3f2a9828c921fe1f093cc567bf45"
    "a85adad0526176be0aa1b8be09336eeb"
)

EXPECTED = {
    "prereg": (
        ROOT / "docs/experiments/"
        "sq08-three-body-problem-preregistration.md",
        "fdc3a1e8e3a4eec8e8542b740ba67de2"
        "452b59554263ba4e72c2426489336947",
    ),
    "topology_amendment": (
        ROOT / "docs/experiments/"
        "sq08-three-body-problem-topology-amendment.md",
        "7244f193b3c1a9690b453a5b055e5090"
        "d649f1fc52f943c4b170fe1c8ca580fd",
    ),
    "topology_calibration": (
        ROOT / "config/controls/"
        "sq08-three-body-topology-v1.json",
        "1f5e5bb25c9bd0a403f0f47d5b4c5870"
        "a53cfbbe0f5ebcfb945ad73d4859c075",
    ),
    "topology_frontier": (
        ROOT / "config/controls/"
        "sq08-three-body-topology-frontier-v1.json",
        "ad87e904c13698552d3e52fb58e9558ae"
        "fe4e0898a2ef6bb45b3c64652196361",
    ),
    "evidence_schema": (
        ROOT / "config/controls/"
        "sq08-three-body-evidence-schema-v1.json",
        "9f9e4465eb26b1bf5c85befcc624a0d1b"
        "9f84ffe8359281b212ff0883d47cdc2",
    ),
    "analysis_contract": (
        ROOT / "config/controls/"
        "sq08-three-body-analysis-contract-v1.json",
        "d7ba169544942504eb7ed32a3b72a248e"
        "b7611a44b8e23e7c1f4560732c78e03",
    ),
    "execution_manifest": (
        ROOT / "config/controls/"
        "sq08-three-body-execution-manifest-v1.json",
        "9a472f6548f777ceec327b8449ffcfee27"
        "d275478792a59097d28e95121c9dfe",
    ),
    "topology_freezer": (
        ROOT / "brain/sq08_three_body_topology_freezer.py",
        "466fe731c664c8207615c4b57c8f712e2"
        "b13dbfeeda7709057d9414d661535b8",
    ),
    "frontier_freezer": (
        ROOT / "brain/"
        "sq08_three_body_topology_frontier_freezer.py",
        "1c1fe51745ea5675b15ef973532ffdeab0"
        "7cad3b810573a07b5d5b323c66c08c",
    ),
    "readout": (
        ROOT / "brain/sq08_three_body_readout.py",
        "88bc82e29bcc4ffb1f9f3891bac17a293"
        "177017c47b4a73ec1210a5ad16189e9",
    ),
    "episode": (
        ROOT / "brain/sq08_three_body_episode.py",
        "489f3449c939ebe49aeef94775282bc582"
        "2f94f2f4fa577b8de1d20d22a60864",
    ),
    "evidence": (
        ROOT / "brain/sq08_three_body_evidence.py",
        "5b5349ac797b4a7fbab7b17c48214338a"
        "5d07e4415f90e19d8c0af81f966e7d4",
    ),
    "independent_verify": (
        ROOT / "brain/"
        "sq08_three_body_independent_verify.py",
        "2170e1c7454e5de277d55cdb35b7b86b"
        "3edcd794814e9604e2f3cb90b62f13dc",
    ),
    "analysis": (
        ROOT / "brain/sq08_three_body_analysis.py",
        "25c8e8754b042a8a4d4aa2620e97368f7"
        "7bf8d1481de62f1e69518cbc6ce3366",
    ),
}


class ReadinessFailure(RuntimeError):
    pass


def fail(message: str) -> None:
    raise ReadinessFailure(message)


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


def verify_repository() -> dict:
    git(
        "cat-file",
        "-e",
        f"{SCIENCE_GIT_SHA}^{{commit}}",
    )

    result = subprocess.run(
        [
            "git",
            "merge-base",
            "--is-ancestor",
            SCIENCE_GIT_SHA,
            "HEAD",
        ],
        cwd=ROOT,
    )

    if result.returncode != 0:
        fail(
            "HEAD does not descend from frozen "
            "SQ-08 science commit"
        )

    dirty = git(
        "status",
        "--porcelain",
    )

    if dirty:
        fail(
            "working tree must be clean before "
            "SQ-08 authorization"
        )

    return {
        "science_git_sha":
            SCIENCE_GIT_SHA,
        "control_plane_git_sha":
            git("rev-parse", "HEAD"),
        "working_tree_clean":
            True,
    }


def verify_artifacts() -> dict:
    observed = {}

    for name, (path, expected) in EXPECTED.items():
        if not path.is_file():
            fail(
                f"missing frozen artifact: {name}"
            )

        actual = sha256_file(
            path
        )

        if actual != expected:
            fail(
                f"SHA mismatch {name}: "
                f"{actual} != {expected}"
            )

        observed[name] = actual

    return observed


def verify_manifest() -> dict:
    path = EXPECTED[
        "execution_manifest"
    ][0]

    payload = json.loads(
        path.read_text(
            encoding="utf-8",
        )
    )

    if (
        payload.get("status")
        != "FROZEN_PRE_EXECUTION"
    ):
        fail(
            "execution manifest status drift"
        )

    if (
        payload.get("science_git_sha")
        != SCIENCE_GIT_SHA
    ):
        fail(
            "manifest science SHA drift"
        )

    contract = payload.get(
        "execution_contract",
        {},
    )

    masks = [
        "000",
        "001",
        "010",
        "011",
        "100",
        "101",
        "110",
        "111",
    ]

    if contract.get(
        "condition_masks"
    ) != masks:
        fail(
            "Boolean cube drift"
        )

    if contract.get(
        "replicates"
    ) != [1, 2]:
        fail(
            "replicate contract drift"
        )

    if contract.get(
        "work_unit_count"
    ) != 16:
        fail(
            "work-unit count drift"
        )

    conditions = payload.get(
        "conditions"
    )

    if (
        not isinstance(
            conditions,
            list,
        )
        or len(conditions) != 16
    ):
        fail(
            "manifest condition count drift"
        )

    expected_ids = [
        f"sq08:{mask}:r{replicate}"
        for mask in masks
        for replicate in (1, 2)
    ]

    observed_ids = [
        row.get("condition_id")
        for row in conditions
    ]

    if observed_ids != expected_ids:
        fail(
            "condition identity/order drift"
        )

    for row in conditions:
        mask = row.get("mask")

        if row.get(
            "edge_zeroed"
        ) != {
            "A": int(mask[0]),
            "B": int(mask[1]),
            "C": int(mask[2]),
        }:
            fail(
                "lesion semantics drift for "
                f"{row.get('condition_id')}"
            )

    frozen = payload.get(
        "frozen_inputs",
        {},
    )

    if (
        frozen.get(
            "connectome_sha256"
        )
        != CONNECTOME_SHA256
    ):
        fail(
            "connectome SHA drift"
        )

    if (
        frozen.get(
            "topology_calibration_sha256"
        )
        != EXPECTED[
            "topology_calibration"
        ][1]
    ):
        fail(
            "calibration SHA drift"
        )

    if (
        frozen.get(
            "topology_frontier_sha256"
        )
        != EXPECTED[
            "topology_frontier"
        ][1]
    ):
        fail(
            "frontier SHA drift"
        )

    if (
        frozen.get(
            "evidence_schema_sha256"
        )
        != EXPECTED[
            "evidence_schema"
        ][1]
    ):
        fail(
            "evidence-schema SHA drift"
        )

    return payload


def main() -> None:
    repository = (
        verify_repository()
    )

    artifacts = (
        verify_artifacts()
    )

    manifest = (
        verify_manifest()
    )

    report = {
        "status":
            "SQ08_READY_FOR_AUTHORIZATION",

        "repository":
            repository,

        "manifest_sha256":
            EXPECTED[
                "execution_manifest"
            ][1],

        "artifact_hashes":
            artifacts,

        "work_unit_count":
            manifest[
                "execution_contract"
            ][
                "work_unit_count"
            ],

        "neural_execution_performed":
            False,
    }

    print(
        json.dumps(
            report,
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
