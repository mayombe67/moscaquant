from __future__ import annotations

import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path

import numpy as np
from scipy import sparse

from brain.sq05_two_betrayals_runner import (
    CONNECTOME,
    RETINA,
)
from brain.sq10_sophon_episode import (
    duplicate_pair_exact,
    execute_condition,
)
from brain.sq10_sophon_evidence import (
    EVIDENCE_ARRAY_KEYS,
    build_evidence_arrays,
)
from brain.sq10_sophon_independent_verify import (
    verify_evidence_arrays,
)
from brain.sq10_sophon_plan import (
    build_conditions,
)
from brain.sq10_sophon_readiness import (
    verify_body_topology,
    verify_calibration_closure,
    verify_evidence_destination,
    verify_manifest,
    verify_physical_inputs,
    verify_repo_artifacts,
    verify_repository,
    verify_runtime_semantics,
)


ROOT = Path(__file__).resolve().parents[1]

AUTHORIZATION = (
    ROOT
    / "config/controls/"
    "sq10-sophon-execution-authorization-v1.json"
)

EVIDENCE = (
    ROOT
    / "artifacts/experiments/"
    "sq10-sophon/"
    "sq10-sophon-evidence-v1.npz"
)

RECEIPT = (
    ROOT
    / "artifacts/experiments/"
    "sq10-sophon/"
    "sq10-sophon-execution-receipt-v1.json"
)

EXPECTED_AUTHORIZATION_SHA256 = (
    "6194e09f7c62bb4a3d6580445464494d"
    "b17cca6e188fbd1a999849a671f59ec2"
)

EXPECTED_AUTHORIZATION_COMMIT = (
    "1715d39e243c5960213d536baf1fa26c8c66ba9a"
)

EXPECTED_MANIFEST_SHA256 = (
    "59246348becc4d501dd6ef18b629be304"
    "a702f73ab95d2e9e1d4299d4d23b2d9"
)


class ExecutionRefusal(RuntimeError):
    pass


def refuse(message: str) -> None:
    raise ExecutionRefusal(message)


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
        refuse(
            f"git {' '.join(args)} failed:\n"
            f"{result.stdout}"
        )

    return result.stdout.strip()


def validate_authorization_payload(
    payload: dict,
) -> None:
    if (
        payload.get("status")
        != "AUTHORIZED_FOR_FROZEN_EXECUTION"
    ):
        refuse(
            "SQ-10 authorization status drift"
        )

    if (
        payload.get(
            "execution_manifest_sha256"
        )
        != EXPECTED_MANIFEST_SHA256
    ):
        refuse(
            "authorization manifest SHA drift"
        )

    boundary = payload.get(
        "execution_boundary",
        {},
    )

    if (
        boundary.get(
            "authorization_only"
        )
        is not True
    ):
        refuse(
            "authorization boundary drift"
        )

    if (
        boundary.get(
            "execution_performed"
        )
        is not False
    ):
        refuse(
            "authorization unexpectedly "
            "claims prior execution"
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
                "authorization boundary "
                f"unexpectedly grants {key}"
            )

    contract = payload.get(
        "execution_contract",
        {},
    )

    if (
        contract.get("work_unit_count")
        != 16
    ):
        refuse(
            "authorization work-unit "
            "count drift"
        )

    if contract.get("layout") != "RL":
        refuse(
            "authorization layout drift"
        )

    if (
        contract.get("frame_count")
        != 192
    ):
        refuse(
            "authorization frame-count drift"
        )

    for key in (
        "arbitrary_condition_execution",
        "manifest_regeneration_at_execution",
        "overwrite_existing_evidence",
        "implicit_resume",
    ):
        if contract.get(key) is not False:
            refuse(
                "authorization fail-closed "
                f"rule drift: {key}"
            )

    for key in (
        "all_work_units_required",
        "both_replicates_required_per_mask",
        "independent_verification_required",
        "analysis_after_verification_only",
    ):
        if contract.get(key) is not True:
            refuse(
                "authorization required "
                f"rule drift: {key}"
            )

    canonical = build_conditions()

    expected_units = [
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
        for row in canonical
    ]

    if (
        payload.get(
            "authorized_work_units"
        )
        != expected_units
    ):
        refuse(
            "authorized work-unit "
            "universe drift"
        )

    expected_ids = [
        row["condition_id"]
        for row in canonical
    ]

    if (
        contract.get(
            "authorized_condition_ids"
        )
        != expected_ids
    ):
        refuse(
            "authorized condition-ID "
            "universe drift"
        )


def load_authorization() -> dict:
    if not AUTHORIZATION.is_file():
        refuse(
            "SQ-10 execution "
            "authorization missing"
        )

    actual = sha256_file(
        AUTHORIZATION
    )

    if (
        actual
        != EXPECTED_AUTHORIZATION_SHA256
    ):
        refuse(
            "authorization SHA drift: "
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
        (
            f"{EXPECTED_AUTHORIZATION_COMMIT}"
            "^{commit}"
        ),
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
            "frozen SQ-10 authorization commit"
        )


def verify_execution_preconditions() -> dict:
    authorization = (
        load_authorization()
    )

    verify_authorization_commit()

    #
    # Re-run the complete readiness closure
    # immediately before execution.
    #
    repository = verify_repository()
    manifest = verify_manifest()

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

    body = (
        verify_body_topology(
            manifest
        )
    )

    calibration = (
        verify_calibration_closure(
            manifest
        )
    )

    destination = (
        verify_evidence_destination(
            manifest
        )
    )

    if EVIDENCE.exists():
        refuse(
            "SQ-10 evidence already exists"
        )

    if RECEIPT.exists():
        refuse(
            "SQ-10 execution receipt "
            "already exists"
        )

    if (
        Path(
            destination["path"]
        ).resolve()
        != EVIDENCE.resolve()
    ):
        refuse(
            "authorized evidence "
            "destination drift"
        )

    return {
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
        "calibration":
            calibration,
    }


def load_frozen_neural_inputs():
    baseline = sparse.load_npz(
        CONNECTOME
    ).tocsr()

    if baseline.dtype != np.float32:
        refuse(
            "baseline connectome "
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
                "retina artifact lacks "
                "neuron_index"
            )

        retinal_indices = np.asarray(
            retina["neuron_index"],
            dtype=np.int32,
        ).copy()

    if retinal_indices.ndim != 1:
        refuse(
            "retinal indices must be 1D"
        )

    if len(retinal_indices) == 0:
        refuse(
            "retinal index set is empty"
        )

    return (
        baseline,
        retinal_indices,
    )


def execute_authorized_cube(
    *,
    baseline,
    retinal_indices,
) -> list[dict]:
    conditions = build_conditions()

    if len(conditions) != 16:
        refuse(
            "runtime condition universe "
            "is not exactly 16"
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

        #
        # As soon as each deterministic pair
        # exists, fail immediately if it does
        # not reproduce exactly.
        #
        if (
            condition["replicate"] == 2
        ):
            first = episodes[-2]
            second = episodes[-1]

            if not duplicate_pair_exact(
                first,
                second,
            ):
                refuse(
                    "deterministic duplicate "
                    "mismatch for "
                    f"{condition['mask']}"
                )

            print(
                "        duplicate exact: PASS"
            )

    if len(episodes) != 16:
        refuse(
            "execution did not produce "
            "exactly 16 episodes"
        )

    return episodes


def verify_evidence_in_memory(
    episodes: list[dict],
) -> dict[str, np.ndarray]:
    arrays = build_evidence_arrays(
        episodes
    )

    if set(arrays) != set(
        EVIDENCE_ARRAY_KEYS
    ):
        refuse(
            "packed evidence key-set drift"
        )

    #
    # Independent verifier must pass
    # before evidence publication.
    #
    verify_evidence_arrays(
        arrays
    )

    return arrays


def _atomic_publish_no_overwrite(
    path: Path,
    writer,
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    if path.exists():
        refuse(
            "refusing to overwrite "
            f"existing output: {path}"
        )

    fd, temp_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=path.parent,
    )

    temp = Path(temp_name)

    try:
        with os.fdopen(
            fd,
            "wb",
        ) as handle:
            writer(handle)

            handle.flush()
            os.fsync(
                handle.fileno()
            )

        #
        # Hard-link publication is atomic
        # and refuses EEXIST instead of
        # replacing a destination that
        # appeared during execution.
        #
        try:
            os.link(
                temp,
                path,
            )
        except FileExistsError:
            refuse(
                "output appeared during "
                f"execution: {path}"
            )

        dir_fd = os.open(
            path.parent,
            os.O_RDONLY,
        )

        try:
            os.fsync(dir_fd)
        finally:
            os.close(dir_fd)

    finally:
        try:
            temp.unlink()
        except FileNotFoundError:
            pass


def publish_evidence(
    arrays: dict[str, np.ndarray],
) -> str:
    def writer(handle):
        np.savez_compressed(
            handle,
            **arrays,
        )

    _atomic_publish_no_overwrite(
        EVIDENCE,
        writer,
    )

    return sha256_file(
        EVIDENCE
    )


def verify_persisted_evidence(
    expected: dict[str, np.ndarray],
) -> None:
    with np.load(
        EVIDENCE,
        allow_pickle=False,
    ) as payload:
        observed = {
            key: payload[key]
            for key in payload.files
        }

    if set(observed) != set(
        EVIDENCE_ARRAY_KEYS
    ):
        refuse(
            "persisted evidence "
            "key-set drift"
        )

    for key in EVIDENCE_ARRAY_KEYS:
        if not np.array_equal(
            observed[key],
            expected[key],
        ):
            refuse(
                "persisted evidence "
                f"mismatch: {key}"
            )

    #
    # Independent verification again,
    # this time against the actual bytes
    # reloaded from disk.
    #
    verify_evidence_arrays(
        observed
    )


def publish_receipt(
    payload: dict,
) -> str:
    encoded = (
        json.dumps(
            payload,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    ).encode("utf-8")

    def writer(handle):
        handle.write(encoded)

    _atomic_publish_no_overwrite(
        RECEIPT,
        writer,
    )

    return sha256_file(
        RECEIPT
    )


def main() -> None:
    preflight = (
        verify_execution_preconditions()
    )

    print(
        "SQ-10 authorization verified"
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

    episodes = (
        execute_authorized_cube(
            baseline=baseline,
            retinal_indices=
                retinal_indices,
        )
    )

    arrays = (
        verify_evidence_in_memory(
            episodes
        )
    )

    print()
    print(
        "pre-publication independent "
        "verification: PASS"
    )

    evidence_sha = (
        publish_evidence(
            arrays
        )
    )

    verify_persisted_evidence(
        arrays
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
            "sq10-sophon-execution-receipt/v1",

        "experiment":
            "SQ-10",

        "codename":
            "SOPHON",

        "status":
            "FROZEN_EXECUTION_COMPLETE",

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

        "launcher": {
            "path":
                str(
                    Path(__file__).relative_to(
                        ROOT
                    )
                ),
            "sha256":
                launcher_sha,
        },

        "work_units_executed":
            16,

        "all_deterministic_duplicate_pairs_exact":
            True,

        "independent_verification": {
            "pre_publication":
                "PASS",
            "post_publication":
                "PASS",
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
    print("SQ-10 FROZEN EXECUTION COMPLETE")
    print("evidence sha256:", evidence_sha)
    print("receipt sha256:", receipt_sha)
    print("analysis performed: False")


if __name__ == "__main__":
    main()
