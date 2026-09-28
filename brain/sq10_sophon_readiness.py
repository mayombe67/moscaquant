from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

MANIFEST = (
    ROOT
    / "config/controls/"
    "sq10-sophon-execution-manifest-v1.json"
)

SCIENCE_GIT_SHA = (
    "af0db6776cb478e75947292236abd82b3953a778"
)

EXPECTED_MANIFEST_COMMIT = (
    "ea3a6a9a03f28c1ec165f81c55cb8ffc347816bb"
)

EXPECTED_MANIFEST_SHA256 = (
    "59246348becc4d501dd6ef18b629be304a702f73ab95d2e9e1d4299d4d23b2d9"
)

EXPECTED_MASKS = (
    "000",
    "001",
    "010",
    "011",
    "100",
    "101",
    "110",
    "111",
)

EXPECTED_REPLICATES = (1, 2)

EXPECTED_TOLERANCE = (
    3.814697265625e-06
)

DATA_ROOT = (
    Path.home()
    / "moscaquant-data"
    / "processed"
)


class ReadinessFailure(RuntimeError):
    pass


def fail(message: str) -> None:
    raise ReadinessFailure(message)


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


def load_manifest() -> dict:
    if not MANIFEST.is_file():
        fail(
            "SQ-10 execution manifest missing"
        )

    observed = sha256_file(
        MANIFEST
    )

    if (
        observed
        != EXPECTED_MANIFEST_SHA256
    ):
        fail(
            "execution manifest SHA drift: "
            f"{observed} != "
            f"{EXPECTED_MANIFEST_SHA256}"
        )

    return json.loads(
        MANIFEST.read_text(
            encoding="utf-8",
        )
    )


def verify_repository() -> dict:
    git(
        "cat-file",
        "-e",
        f"{SCIENCE_GIT_SHA}^{{commit}}",
    )

    git(
        "cat-file",
        "-e",
        (
            f"{EXPECTED_MANIFEST_COMMIT}"
            "^{commit}"
        ),
    )

    for ancestor, label in (
        (
            SCIENCE_GIT_SHA,
            "SQ-10 science freeze",
        ),
        (
            EXPECTED_MANIFEST_COMMIT,
            "SQ-10 execution manifest",
        ),
    ):
        result = subprocess.run(
            [
                "git",
                "merge-base",
                "--is-ancestor",
                ancestor,
                "HEAD",
            ],
            cwd=ROOT,
        )

        if result.returncode != 0:
            fail(
                "HEAD does not descend from "
                f"{label}: {ancestor}"
            )

    dirty = git(
        "status",
        "--porcelain",
    )

    if dirty:
        fail(
            "working tree must be clean "
            "for SQ-10 readiness"
        )

    return {
        "science_git_sha":
            SCIENCE_GIT_SHA,

        "execution_manifest_commit":
            EXPECTED_MANIFEST_COMMIT,

        "control_plane_git_sha":
            git(
                "rev-parse",
                "HEAD",
            ),

        "working_tree_clean":
            True,
    }


def verify_manifest() -> dict:
    d = load_manifest()

    if (
        d.get("status")
        != "FROZEN_PRE_EXECUTION"
    ):
        fail(
            "manifest status drift"
        )

    if (
        d.get("science_git_sha")
        != SCIENCE_GIT_SHA
    ):
        fail(
            "manifest science SHA drift"
        )

    if (
        d.get(
            "neural_execution_authorized"
        )
        is not False
    ):
        fail(
            "manifest unexpectedly "
            "authorizes neural execution"
        )

    boundary = d.get(
        "execution_boundary",
        {},
    )

    if (
        boundary.get(
            "authorization_granted"
        )
        is not False
    ):
        fail(
            "manifest authorization "
            "boundary drift"
        )

    contract = d.get(
        "execution_contract",
        {},
    )

    if (
        contract.get("layout")
        != "RL"
    ):
        fail(
            "stimulus layout drift"
        )

    if (
        contract.get("frame_count")
        != 192
    ):
        fail(
            "frame-count drift"
        )

    if (
        contract.get(
            "condition_masks"
        )
        != list(EXPECTED_MASKS)
    ):
        fail(
            "Boolean cube drift"
        )

    if (
        contract.get("replicates")
        != list(EXPECTED_REPLICATES)
    ):
        fail(
            "replicate contract drift"
        )

    if (
        contract.get(
            "work_unit_count"
        )
        != 16
    ):
        fail(
            "work-unit count drift"
        )

    conditions = d.get(
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
            "manifest must contain "
            "exactly 16 conditions"
        )

    expected_ids = [
        f"sq10:{mask}:r{replicate}"
        for mask in EXPECTED_MASKS
        for replicate
        in EXPECTED_REPLICATES
    ]

    observed_ids = [
        row.get("condition_id")
        for row in conditions
    ]

    if observed_ids != expected_ids:
        fail(
            "condition identity/order drift"
        )

    if (
        len(set(observed_ids))
        != 16
    ):
        fail(
            "duplicate condition ID"
        )

    for ordinal, row in enumerate(
        conditions
    ):
        if (
            row.get("ordinal")
            != ordinal
        ):
            fail(
                "condition ordinal drift"
            )

        mask = row.get("mask")

        if (
            row.get("edge_zeroed")
            != {
                "A": int(mask[0]),
                "B": int(mask[1]),
                "C": int(mask[2]),
            }
        ):
            fail(
                "lesion semantics drift: "
                f"{row.get('condition_id')}"
            )

    return d


def verify_repo_artifacts(
    manifest: dict | None = None,
) -> dict:
    if manifest is None:
        manifest = load_manifest()

    observed = {}

    for section in (
        "frozen_code",
        "frozen_contracts",
    ):
        for name, item in (
            manifest[
                section
            ].items()
        ):
            path = (
                ROOT
                / item["path"]
            )

            if not path.is_file():
                fail(
                    "missing frozen repo "
                    f"artifact: {name}"
                )

            actual = sha256_file(
                path
            )

            expected = item[
                "sha256"
            ]

            if actual != expected:
                fail(
                    f"SHA mismatch {name}: "
                    f"{actual} != {expected}"
                )

            observed[
                f"{section}.{name}"
            ] = actual

    return observed


def verify_physical_inputs(
    manifest: dict | None = None,
) -> dict:
    if manifest is None:
        manifest = load_manifest()

    physical = manifest[
        "physical_inputs"
    ]

    observed = {}

    for name in (
        "connectome",
        "retina",
        "relay",
        "graded",
    ):
        item = physical[name]

        path = (
            DATA_ROOT
            / item["logical_name"]
        )

        if not path.is_file():
            fail(
                "missing physical input "
                f"{name}: {path}"
            )

        actual = sha256_file(
            path
        )

        expected = item[
            "sha256"
        ]

        if actual != expected:
            fail(
                f"physical input SHA "
                f"mismatch {name}: "
                f"{actual} != {expected}"
            )

        observed[name] = {
            "path": str(path),
            "sha256": actual,
        }

    #
    # Import only after the repository hashes
    # have been independently validated by
    # the normal readiness call order.
    #
    from brain.sq05_stimulus import (
        TOTAL_FRAMES,
        assert_frozen_stimulus,
    )

    schedules = (
        assert_frozen_stimulus()
    )

    stimulus = physical[
        "stimulus"
    ]

    if TOTAL_FRAMES != 192:
        fail(
            "stimulus frame-count drift"
        )

    if (
        schedules.get("RL")
        != stimulus[
            "schedule_sha256"
        ]
    ):
        fail(
            "frozen RL schedule drift"
        )

    observed["stimulus"] = {
        "layout": "RL",
        "frame_count":
            TOTAL_FRAMES,
        "schedule_sha256":
            schedules["RL"],
    }

    return observed


def verify_runtime_semantics(
    manifest: dict | None = None,
) -> dict:
    if manifest is None:
        manifest = load_manifest()

    from brain.sq05_two_betrayals_runner import (
        FRAME_COUNT,
        RELEASE_GAIN,
    )

    from brain.sq10_sophon_plan import (
        MASKS,
        REPLICATES,
    )

    from brain.visual_transduction import (
        VisualTransductionConfig,
    )

    execution = manifest[
        "execution_contract"
    ]

    if (
        tuple(MASKS)
        != EXPECTED_MASKS
    ):
        fail(
            "SQ-10 plan mask drift"
        )

    if (
        tuple(REPLICATES)
        != EXPECTED_REPLICATES
    ):
        fail(
            "SQ-10 plan replicate drift"
        )

    if FRAME_COUNT != 192:
        fail(
            "runner frame-count drift"
        )

    runtime = execution[
        "runtime_parameters"
    ]

    cfg = (
        VisualTransductionConfig()
    )

    expected_base = {
        "dt_ms":
            float(cfg.dt_ms),

        "tau_ms":
            float(cfg.tau_ms),

        "threshold":
            float(cfg.threshold),

        "release_gain":
            float(RELEASE_GAIN),
    }

    if runtime != expected_base:
        fail(
            "effective runtime "
            "parameter drift: "
            f"{runtime} != {expected_base}"
        )

    return expected_base


def verify_body_topology(
    manifest: dict | None = None,
) -> dict:
    if manifest is None:
        manifest = load_manifest()

    import numpy as np
    from scipy import sparse

    from brain.sq08_three_body_episode import (
        resolve_body_edges,
    )

    body = manifest[
        "body_edges"
    ]

    matrix_path = (
        DATA_ROOT
        / manifest[
            "physical_inputs"
        ][
            "connectome"
        ][
            "logical_name"
        ]
    )

    matrix = sparse.load_npz(
        matrix_path
    ).tocsr()

    if matrix.dtype != np.float32:
        fail(
            "connectome dtype drift"
        )

    observed = {}

    for label, edge in zip(
        ("A", "B", "C"),
        resolve_body_edges(),
    ):
        source = int(edge[0])
        responder = int(edge[1])
        weight = float(
            np.float32(
                edge[2]
            )
        )

        expected = body[label]

        if (
            source
            != expected["source"]
            or responder
            != expected["responder"]
            or weight
            != expected[
                "frozen_weight"
            ]
        ):
            fail(
                f"BODY {label} identity drift"
            )

        row = matrix.getrow(
            responder
        )

        hits = np.flatnonzero(
            row.indices
            == source
        )

        if len(hits) != 1:
            fail(
                f"BODY {label} edge "
                "multiplicity drift"
            )

        position = int(
            hits[0]
        )

        if (
            row.nnz
            != expected[
                "responder_row_nnz"
            ]
        ):
            fail(
                f"BODY {label} row "
                "geometry drift"
            )

        if (
            position
            != expected[
                "source_csr_position"
            ]
        ):
            fail(
                f"BODY {label} CSR "
                "position drift"
            )

        csr_weight = float(
            np.float32(
                row.data[position]
            )
        )

        if csr_weight != weight:
            fail(
                f"BODY {label} CSR "
                "weight drift"
            )

        observed[label] = {
            "source": source,
            "responder":
                responder,
            "frozen_weight":
                weight,
            "row_nnz":
                int(row.nnz),
            "source_csr_position":
                position,
        }

    return observed


def verify_calibration_closure(
    manifest: dict | None = None,
) -> dict:
    if manifest is None:
        manifest = load_manifest()

    contracts = manifest[
        "frozen_contracts"
    ]

    seal_path = (
        ROOT
        / contracts[
            "calibration_seal"
        ][
            "path"
        ]
    )

    artifact_path = (
        ROOT
        / contracts[
            "calibration_artifact"
        ][
            "path"
        ]
    )

    analysis_path = (
        ROOT
        / contracts[
            "analysis_contract"
        ][
            "path"
        ]
    )

    calibration_contract_path = (
        ROOT
        / contracts[
            "calibration_contract"
        ][
            "path"
        ]
    )

    seal = json.loads(
        seal_path.read_text()
    )

    artifact = json.loads(
        artifact_path.read_text()
    )

    analysis = json.loads(
        analysis_path.read_text()
    )

    if (
        seal[
            "calibration_artifact"
        ][
            "sha256"
        ]
        != sha256_file(
            artifact_path
        )
    ):
        fail(
            "calibration artifact "
            "seal mismatch"
        )

    if (
        seal[
            "calibration_contract"
        ][
            "sha256"
        ]
        != sha256_file(
            calibration_contract_path
        )
    ):
        fail(
            "calibration contract "
            "seal mismatch"
        )

    calibrated = artifact[
        "calibration"
    ]

    if (
        calibrated[
            "frozen_absolute_tolerance"
        ]
        != EXPECTED_TOLERANCE
    ):
        fail(
            "calibrated absolute "
            "tolerance drift"
        )

    if (
        calibrated[
            "frozen_relative_tolerance"
        ]
        != 0.0
    ):
        fail(
            "calibrated relative "
            "tolerance drift"
        )

    numerical = manifest[
        "numerical_acceptance"
    ]

    if (
        numerical[
            "absolute_tolerance"
        ]
        != EXPECTED_TOLERANCE
        or numerical[
            "relative_tolerance"
        ]
        != 0.0
    ):
        fail(
            "manifest numerical "
            "acceptance drift"
        )

    analysis_numerical = (
        analysis[
            "primary_test"
        ][
            "numerical_acceptance"
        ]
    )

    if (
        analysis_numerical[
            "absolute_tolerance"
        ]
        != EXPECTED_TOLERANCE
        or analysis_numerical[
            "relative_tolerance"
        ]
        != 0.0
    ):
        fail(
            "analysis-contract "
            "tolerance drift"
        )

    if (
        seal["integrity"][
            "calibration_preceded_neural_execution"
        ]
        is not True
    ):
        fail(
            "calibration chronology "
            "seal drift"
        )

    return {
        "absolute_tolerance":
            EXPECTED_TOLERANCE,

        "relative_tolerance":
            0.0,

        "calibration_artifact_sha256":
            sha256_file(
                artifact_path
            ),

        "calibration_seal_sha256":
            sha256_file(
                seal_path
            ),
    }


def verify_evidence_destination(
    manifest: dict | None = None,
) -> dict:
    if manifest is None:
        manifest = load_manifest()

    destination = manifest[
        "evidence_destination"
    ]

    path = (
        ROOT
        / destination["path"]
    )

    if (
        destination[
            "must_not_exist_before_execution"
        ]
        is not True
    ):
        fail(
            "evidence destination "
            "fail-closed rule drift"
        )

    if (
        destination[
            "overwrite_existing"
        ]
        is not False
    ):
        fail(
            "evidence overwrite "
            "rule drift"
        )

    if path.exists():
        fail(
            "SQ-10 evidence destination "
            "already exists; implicit "
            "overwrite/resume forbidden: "
            f"{path}"
        )

    return {
        "path":
            str(path),

        "exists_before_execution":
            False,

        "overwrite_existing":
            False,
    }


def main() -> None:
    #
    # Repository cleanliness is intentionally
    # first. No readiness claim can be made
    # from an uncommitted control plane.
    #
    repository = (
        verify_repository()
    )

    manifest = (
        verify_manifest()
    )

    artifacts = (
        verify_repo_artifacts(
            manifest
        )
    )

    physical = (
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

    evidence = (
        verify_evidence_destination(
            manifest
        )
    )

    report = {
        "status":
            "SQ10_READY_FOR_AUTHORIZATION",

        "experiment":
            "SQ-10",

        "codename":
            "SOPHON",

        "repository":
            repository,

        "execution_manifest_sha256":
            EXPECTED_MANIFEST_SHA256,

        "work_unit_count":
            len(
                manifest[
                    "conditions"
                ]
            ),

        "repo_artifact_hashes":
            artifacts,

        "physical_inputs":
            physical,

        "runtime_parameters":
            runtime,

        "body_topology":
            body,

        "numerical_calibration":
            calibration,

        "evidence_destination":
            evidence,

        "neural_execution_performed":
            False,

        "authorization_granted":
            False,

        "analysis_performed":
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
