from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import numpy as np
from scipy import sparse

from brain.sq05_two_betrayals_runner import (
    CONNECTOME,
    RETINA,
)
from brain.sq11_dark_forest_episode import (
    duplicate_pair_exact,
    execute_condition,
)
from brain.sq11_dark_forest_evidence import (
    EVIDENCE_ARRAY_KEYS,
    build_evidence_arrays,
)
from brain.sq11_dark_forest_independent_verify import (
    EXPECTED_KEYS,
    verify_evidence_arrays,
)
from brain.sq11_dark_forest_plan import (
    build_conditions,
)
from brain.sq11_dark_forest_publish import (
    EVIDENCE,
    RECEIPT,
    publish_evidence,
    publish_receipt,
)
from brain.sq11_dark_forest_readiness import (
    EXPECTED_MANIFEST_SHA256,
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

AUTHORIZATION = (
    ROOT
    / "config/controls/"
    "sq11-dark-forest-execution-authorization-v1.json"
)

LAUNCH_SEAL = (
    ROOT
    / "config/controls/"
    "sq11-dark-forest-launch-seal-v1.json"
)

EXPECTED_AUTHORIZATION_SHA256 = (
    "7fde9c5bfb7e5d8caabd62fe90bfc610"
    "10e232db1d2a34dc4c88abfd86041578"
)

EXPECTED_AUTHORIZATION_COMMIT = (
    "ca11b692b207e4e4dd51323b9e656ed07ad836bc"
)


class ExecutionRefusal(RuntimeError):
    pass


def refuse(message: str) -> None:
    raise ExecutionRefusal(message)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()

    with path.open("rb") as handle:
        for block in iter(
            lambda: handle.read(8 * 1024 * 1024),
            b"",
        ):
            h.update(block)

    return h.hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    if result.returncode != 0:
        refuse(
            f"git {' '.join(args)} failed:\n"
            f"{result.stdout}"
        )

    return result.stdout.strip()


def _canonical_authorized_units() -> list[dict]:
    return [
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
        for row in build_conditions()
    ]


def validate_authorization_payload(
    payload: dict,
) -> None:
    if (
        payload.get("schema_version")
        != "moscaquant."
        "sq11-dark-forest-execution-authorization/v1"
    ):
        refuse(
            "SQ-11 authorization schema drift"
        )

    if (
        payload.get("experiment") != "SQ-11"
        or payload.get("codename") != "DARK FOREST"
    ):
        refuse(
            "SQ-11 authorization identity drift"
        )

    if (
        payload.get("status")
        != "AUTHORIZED_FOR_FROZEN_EXECUTION"
    ):
        refuse(
            "SQ-11 authorization status drift"
        )

    if (
        payload.get(
            "execution_manifest_sha256"
        )
        != EXPECTED_MANIFEST_SHA256
    ):
        refuse(
            "SQ-11 authorization manifest "
            "SHA drift"
        )

    if (
        payload.get("authorized_work_units")
        != _canonical_authorized_units()
    ):
        refuse(
            "SQ-11 authorized work-unit "
            "universe drift"
        )

    boundary = payload.get(
        "execution_boundary",
        {},
    )

    if (
        boundary.get("authorization_only")
        is not True
    ):
        refuse(
            "SQ-11 authorization boundary drift"
        )

    if (
        boundary.get("execution_performed")
        is not False
    ):
        refuse(
            "SQ-11 authorization claims "
            "prior execution"
        )

    for key in (
        "analysis_authority",
        "mechanism_interpretation_authority",
        "result_reclassification_authority",
        "tolerance_modification_authority",
        "condition_selection_authority",
    ):
        if boundary.get(key) is not False:
            refuse(
                "SQ-11 authorization "
                f"unexpectedly grants {key}"
            )

    contract = payload.get(
        "execution_contract",
        {},
    )

    exact = {
        "work_unit_count":
            16,
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
    }

    for key, expected in exact.items():
        if contract.get(key) != expected:
            refuse(
                "SQ-11 authorization contract "
                f"drift: {key}"
            )

    expected_ids = [
        row["condition_id"]
        for row in build_conditions()
    ]

    if (
        contract.get(
            "authorized_condition_ids"
        )
        != expected_ids
    ):
        refuse(
            "SQ-11 authorized condition-ID "
            "order drift"
        )


def load_authorization() -> dict:
    if not AUTHORIZATION.is_file():
        refuse(
            "SQ-11 authorization missing"
        )

    actual = sha256_file(
        AUTHORIZATION
    )

    if (
        actual
        != EXPECTED_AUTHORIZATION_SHA256
    ):
        refuse(
            "SQ-11 authorization SHA drift: "
            f"{actual} != "
            f"{EXPECTED_AUTHORIZATION_SHA256}"
        )

    payload = json.loads(
        AUTHORIZATION.read_text(
            encoding="utf-8",
        )
    )

    validate_authorization_payload(
        payload
    )

    return payload


def verify_authorization_commit() -> None:
    git(
        "cat-file",
        "-e",
        f"{EXPECTED_AUTHORIZATION_COMMIT}^{{commit}}",
    )

    result = subprocess.run(
        [
            "git",
            "merge-base",
            "--is-ancestor",
            EXPECTED_AUTHORIZATION_COMMIT,
            "HEAD",
        ],
        cwd=ROOT,
    )

    if result.returncode != 0:
        refuse(
            "HEAD does not descend from "
            "frozen SQ-11 authorization"
        )


def validate_launch_seal_payload(
    payload: dict,
    *,
    observed_launcher_sha: str,
) -> None:
    expected_keys = {
        "schema_version",
        "experiment",
        "codename",
        "status",
        "authorization",
        "execution_manifest_sha256",
        "launcher",
        "destinations",
        "execution_boundary",
    }

    if set(payload) != expected_keys:
        refuse(
            "SQ-11 launch-seal key-set drift"
        )

    if (
        payload.get("schema_version")
        != "moscaquant."
        "sq11-dark-forest-launch-seal/v1"
    ):
        refuse(
            "SQ-11 launch-seal schema drift"
        )

    if (
        payload.get("experiment") != "SQ-11"
        or payload.get("codename") != "DARK FOREST"
        or payload.get("status")
        != "SEALED_FOR_FROZEN_EXECUTION"
    ):
        refuse(
            "SQ-11 launch-seal identity drift"
        )

    authorization = payload.get(
        "authorization",
        {},
    )

    if authorization != {
        "path":
            str(
                AUTHORIZATION.relative_to(ROOT)
            ),
        "sha256":
            EXPECTED_AUTHORIZATION_SHA256,
        "git_commit":
            EXPECTED_AUTHORIZATION_COMMIT,
    }:
        refuse(
            "SQ-11 launch-seal "
            "authorization binding drift"
        )

    if (
        payload.get(
            "execution_manifest_sha256"
        )
        != EXPECTED_MANIFEST_SHA256
    ):
        refuse(
            "SQ-11 launch-seal manifest drift"
        )

    launcher = payload.get(
        "launcher",
        {},
    )

    if (
        launcher.get("path")
        != str(
            Path(__file__).relative_to(ROOT)
        )
    ):
        refuse(
            "SQ-11 launch-seal launcher "
            "path drift"
        )

    if (
        launcher.get("sha256")
        != observed_launcher_sha
    ):
        refuse(
            "SQ-11 launch-seal launcher "
            "SHA drift"
        )

    if not isinstance(
        launcher.get("git_commit"),
        str,
    ):
        refuse(
            "SQ-11 launch-seal launcher "
            "commit missing"
        )

    destinations = payload.get(
        "destinations",
        {},
    )

    expected_destinations = {
        "evidence": {
            "path":
                str(EVIDENCE.relative_to(ROOT)),
            "overwrite_existing":
                False,
        },
        "publication_receipt": {
            "path":
                str(RECEIPT.relative_to(ROOT)),
            "overwrite_existing":
                False,
        },
    }

    if destinations != expected_destinations:
        refuse(
            "SQ-11 launch-seal destination drift"
        )

    boundary = payload.get(
        "execution_boundary",
        {},
    )

    if boundary != {
        "launch_only":
            True,
        "execution_performed":
            False,
        "analysis_authority":
            False,
        "tolerance_modification_authority":
            False,
        "condition_selection_authority":
            False,
    }:
        refuse(
            "SQ-11 launch-seal execution "
            "boundary drift"
        )


def verify_launch_seal() -> dict:
    if not LAUNCH_SEAL.is_file():
        refuse(
            "SQ-11 launch seal missing"
        )

    payload = json.loads(
        LAUNCH_SEAL.read_text(
            encoding="utf-8",
        )
    )

    launcher_sha = sha256_file(
        Path(__file__)
    )

    validate_launch_seal_payload(
        payload,
        observed_launcher_sha=
            launcher_sha,
    )

    launcher_commit = payload[
        "launcher"
    ][
        "git_commit"
    ]

    git(
        "cat-file",
        "-e",
        f"{launcher_commit}^{{commit}}",
    )

    result = subprocess.run(
        [
            "git",
            "merge-base",
            "--is-ancestor",
            launcher_commit,
            "HEAD",
        ],
        cwd=ROOT,
    )

    if result.returncode != 0:
        refuse(
            "HEAD does not descend from "
            "sealed SQ-11 launcher revision"
        )

    #
    # Bind the seal's SHA to the actual bytes
    # stored at that exact Git commit.
    #
    relative = str(
        Path(__file__).relative_to(ROOT)
    )

    committed = subprocess.run(
        [
            "git",
            "show",
            f"{launcher_commit}:{relative}",
        ],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    if committed.returncode != 0:
        refuse(
            "cannot read sealed launcher "
            "from Git commit"
        )

    if (
        sha256_bytes(committed.stdout)
        != launcher_sha
    ):
        refuse(
            "sealed launcher commit/byte "
            "binding mismatch"
        )

    return payload


def verify_execution_preconditions() -> dict:
    #
    # Launch seal is deliberately first.
    #
    launch_seal = (
        verify_launch_seal()
    )

    authorization = (
        load_authorization()
    )

    verify_authorization_commit()

    #
    # Rerun complete readiness closure
    # immediately before neural execution.
    #
    repository = verify_repository()
    manifest = verify_manifest()

    repo_artifacts = (
        verify_repo_artifacts(manifest)
    )

    physical_inputs = (
        verify_physical_inputs(manifest)
    )

    runtime = (
        verify_runtime_semantics(manifest)
    )

    body = (
        verify_body_topology(manifest)
    )

    qualification = (
        verify_replay_qualification_closure(
            manifest
        )
    )

    destinations = (
        verify_output_destinations(
            manifest
        )
    )

    if EVIDENCE.exists():
        refuse(
            "SQ-11 evidence already exists"
        )

    if RECEIPT.exists():
        refuse(
            "SQ-11 publication receipt "
            "already exists"
        )

    if (
        Path(
            destinations[
                "evidence"
            ][
                "path"
            ]
        ).resolve()
        != EVIDENCE.resolve()
    ):
        refuse(
            "SQ-11 authorized evidence "
            "destination drift"
        )

    if (
        Path(
            destinations[
                "publication_receipt"
            ][
                "path"
            ]
        ).resolve()
        != RECEIPT.resolve()
    ):
        refuse(
            "SQ-11 authorized receipt "
            "destination drift"
        )

    return {
        "launch_seal":
            launch_seal,
        "authorization":
            authorization,
        "repository":
            repository,
        "manifest":
            manifest,
        "repo_artifacts":
            repo_artifacts,
        "physical_inputs":
            physical_inputs,
        "runtime":
            runtime,
        "body":
            body,
        "qualification":
            qualification,
    }


def load_frozen_neural_inputs():
    baseline = sparse.load_npz(
        CONNECTOME
    ).tocsr()

    if baseline.dtype != np.float32:
        refuse(
            "SQ-11 baseline connectome "
            "must be float32"
        )

    with np.load(
        RETINA,
        allow_pickle=False,
    ) as retina:
        if (
            "neuron_index"
            not in retina.files
        ):
            refuse(
                "SQ-11 retina artifact lacks "
                "neuron_index"
            )

        retinal_indices = np.asarray(
            retina["neuron_index"],
            dtype=np.int32,
        ).copy()

    if retinal_indices.ndim != 1:
        refuse(
            "SQ-11 retinal indices "
            "must be 1D"
        )

    if len(retinal_indices) == 0:
        refuse(
            "SQ-11 retinal index set "
            "is empty"
        )

    return (
        baseline,
        retinal_indices,
    )


def execute_authorized_cube(
    *,
    baseline,
    retinal_indices,
    authorization: dict,
) -> list[dict]:
    conditions = build_conditions()

    if len(conditions) != 16:
        refuse(
            "SQ-11 runtime condition "
            "universe is not exactly 16"
        )

    if (
        authorization[
            "authorized_work_units"
        ]
        != _canonical_authorized_units()
    ):
        refuse(
            "SQ-11 runtime authorization "
            "universe drift"
        )

    episodes = []

    for index, condition in enumerate(
        conditions
    ):
        print(
            f"[{index + 1:02d}/16] "
            f"{condition['condition_id']}"
        )

        episode = execute_condition(
            baseline=baseline,
            retinal_indices=
                retinal_indices,
            condition=condition,
        )

        episodes.append(
            episode
        )

        if condition["replicate"] == 2:
            if not duplicate_pair_exact(
                episodes[-2],
                episodes[-1],
            ):
                refuse(
                    "SQ-11 deterministic "
                    "duplicate mismatch for "
                    f"{condition['mask']}"
                )

            print(
                "        duplicate exact: PASS"
            )

    if len(episodes) != 16:
        refuse(
            "SQ-11 execution did not "
            "produce exactly 16 episodes"
        )

    return episodes


def verify_evidence_in_memory(
    episodes: list[dict],
    *,
    baseline,
) -> dict[str, np.ndarray]:
    arrays = build_evidence_arrays(
        episodes
    )

    if (
        set(arrays)
        != set(EVIDENCE_ARRAY_KEYS)
        or set(arrays)
        != set(EXPECTED_KEYS)
    ):
        refuse(
            "SQ-11 packed evidence "
            "key-set drift"
        )

    report = verify_evidence_arrays(
        arrays,
        baseline=baseline,
    )

    if report.get("status") != "PASS":
        refuse(
            "SQ-11 independent verifier "
            "did not return PASS"
        )

    if (
        report.get(
            "baseline_binding_verified"
        )
        is not True
    ):
        refuse(
            "SQ-11 independent verifier "
            "did not verify baseline binding"
        )

    return arrays


def main() -> None:
    preflight = (
        verify_execution_preconditions()
    )

    print(
        "SQ-11 DARK FOREST "
        "authorization + launch seal verified"
    )
    print(
        "authorized work units: 16"
    )
    print(
        "evidence destination:",
        EVIDENCE.relative_to(ROOT),
    )
    print()

    baseline, retinal_indices = (
        load_frozen_neural_inputs()
    )

    episodes = execute_authorized_cube(
        baseline=baseline,
        retinal_indices=
            retinal_indices,
        authorization=
            preflight["authorization"],
    )

    arrays = verify_evidence_in_memory(
        episodes,
        baseline=baseline,
    )

    print()
    print(
        "pre-publication independent "
        "verification: PASS"
    )

    evidence_sha, persisted_report = (
        publish_evidence(
            arrays,
            baseline=baseline,
        )
    )

    if (
        persisted_report.get("status")
        != "PASS"
        or persisted_report.get(
            "baseline_binding_verified"
        )
        is not True
    ):
        refuse(
            "SQ-11 persisted independent "
            "verification failed"
        )

    print(
        "post-publication independent "
        "verification: PASS"
    )

    launcher_sha = sha256_file(
        Path(__file__)
    )

    receipt = {
        "schema_version":
            "moscaquant."
            "sq11-dark-forest-execution-receipt/v1",

        "experiment":
            "SQ-11",

        "codename":
            "DARK FOREST",

        "status":
            "FROZEN_EXECUTION_COMPLETE",

        #
        # Required by the frozen publisher:
        # this receipt records execution;
        # it does not grant execution authority.
        #
        "execution_authorized_here":
            False,

        "science_git_sha":
            preflight[
                "authorization"
            ][
                "science_git_sha"
            ],

        "execution_control_plane_git_sha":
            git(
                "rev-parse",
                "HEAD",
            ),

        "authorization": {
            "path":
                str(
                    AUTHORIZATION.relative_to(
                        ROOT
                    )
                ),
            "sha256":
                EXPECTED_AUTHORIZATION_SHA256,
            "git_commit":
                EXPECTED_AUTHORIZATION_COMMIT,
        },

        "execution_manifest_sha256":
            EXPECTED_MANIFEST_SHA256,

        "launch_seal": {
            "path":
                str(
                    LAUNCH_SEAL.relative_to(
                        ROOT
                    )
                ),
            "sha256":
                sha256_file(
                    LAUNCH_SEAL
                ),
        },

        "launcher": {
            "path":
                str(
                    Path(__file__).relative_to(
                        ROOT
                    )
                ),
            "sha256":
                launcher_sha,
            "git_commit":
                preflight[
                    "launch_seal"
                ][
                    "launcher"
                ][
                    "git_commit"
                ],
        },

        "work_units_executed":
            16,

        "all_deterministic_duplicate_pairs_exact":
            True,

        "replay": {
            "version":
                2,
            "dtype":
                "float32",
            "absolute_tolerance":
                0.0,
            "relative_tolerance":
                0.0,
            "structural_lesion_semantics":
                True,
        },

        "independent_verification": {
            "pre_publication":
                "PASS",
            "post_publication":
                "PASS",
            "baseline_binding_verified":
                True,
        },

        "evidence": {
            "path":
                str(
                    EVIDENCE.relative_to(
                        ROOT
                    )
                ),
            "sha256":
                evidence_sha,
            "overwrite_performed":
                False,
        },

        "analysis": {
            "performed":
                False,
            "authorized_here":
                False,
        },
    }

    receipt_sha = publish_receipt(
        receipt
    )

    print()
    print(
        "SQ-11 DARK FOREST "
        "FROZEN EXECUTION COMPLETE"
    )
    print(
        "evidence sha256:",
        evidence_sha,
    )
    print(
        "receipt sha256:",
        receipt_sha,
    )
    print(
        "analysis performed: False"
    )


if __name__ == "__main__":
    main()
