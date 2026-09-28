from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

MANIFEST = (
    ROOT
    / "config/controls/"
    "sq11-dark-forest-execution-manifest-v1.json"
)

SCIENCE_GIT_SHA = (
    "f8efca347e4165f123f0de43019eca7d26b05dc4"
)

EXPECTED_MANIFEST_COMMIT = (
    "03ce6b4d193b5a99f18dcd2b1492768e0c3514e5"
)

EXPECTED_MANIFEST_SHA256 = (
    "f3397d6a498460ff4785df54fd7d31cd"
    "8595f5057057ca34431268e2219ee496"
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
            "SQ-11 execution manifest missing"
        )

    actual = sha256_file(
        MANIFEST
    )

    if (
        actual
        != EXPECTED_MANIFEST_SHA256
    ):
        fail(
            "SQ-11 execution manifest SHA drift: "
            f"{actual} != "
            f"{EXPECTED_MANIFEST_SHA256}"
        )

    return json.loads(
        MANIFEST.read_text(
            encoding="utf-8",
        )
    )


def verify_repository() -> dict:
    for commit, label in (
        (
            SCIENCE_GIT_SHA,
            "SQ-11 preregistration",
        ),
        (
            EXPECTED_MANIFEST_COMMIT,
            "SQ-11 execution manifest",
        ),
    ):
        git(
            "cat-file",
            "-e",
            f"{commit}^{{commit}}",
        )

        result = subprocess.run(
            [
                "git",
                "merge-base",
                "--is-ancestor",
                commit,
                "HEAD",
            ],
            cwd=ROOT,
        )

        if result.returncode != 0:
            fail(
                "HEAD does not descend from "
                f"{label}: {commit}"
            )

    dirty = git(
        "status",
        "--porcelain",
    )

    if dirty:
        fail(
            "working tree must be clean "
            "for SQ-11 readiness"
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
        d.get("schema_version")
        != "moscaquant."
        "sq11-dark-forest-execution-manifest/v1"
    ):
        fail(
            "SQ-11 manifest schema drift"
        )

    if d.get("experiment") != "SQ-11":
        fail(
            "SQ-11 manifest experiment drift"
        )

    if d.get("codename") != "DARK FOREST":
        fail(
            "SQ-11 manifest codename drift"
        )

    if (
        d.get("status")
        != "FROZEN_PRE_EXECUTION"
    ):
        fail(
            "SQ-11 manifest status drift"
        )

    if (
        d.get("science_git_sha")
        != SCIENCE_GIT_SHA
    ):
        fail(
            "SQ-11 manifest science SHA drift"
        )

    if (
        d.get(
            "neural_execution_authorized"
        )
        is not False
    ):
        fail(
            "SQ-11 manifest unexpectedly "
            "authorizes neural execution"
        )

    if (
        d.get("analysis_authorized")
        is not False
    ):
        fail(
            "SQ-11 manifest unexpectedly "
            "authorizes analysis"
        )

    boundary = d.get(
        "execution_boundary",
        {},
    )

    for key in (
        "authorization_granted",
        "execution_performed",
        "analysis_performed",
        "mechanism_interpretation_authority",
        "result_reclassification_authority",
        "tolerance_modification_authority",
        "condition_selection_authority",
    ):
        if boundary.get(key) is not False:
            fail(
                "SQ-11 execution-boundary drift: "
                f"{key}"
            )

    contract = d.get(
        "execution_contract",
        {},
    )

    exact = {
        "work_unit_count":
            16,

        "condition_masks":
            list(EXPECTED_MASKS),

        "replicates":
            list(EXPECTED_REPLICATES),

        "body_order":
            ["A", "B", "C"],

        "layout":
            "RL",

        "frame_count":
            192,

        "lesion_semantics":
            "structural BODY CSR entry omission",

        "zero_multiplication_equivalent":
            False,

        "replay_version":
            2,

        "replay_float_dtype":
            "float32",

        "replay_absolute_tolerance":
            0.0,

        "replay_relative_tolerance":
            0.0,

        "baseline_binding_required":
            True,

        "independent_verification_required":
            True,

        "persisted_reverification_required":
            True,

        "all_work_units_required":
            True,

        "both_replicates_required_per_mask":
            True,

        "arbitrary_condition_execution":
            False,

        "manifest_regeneration_at_execution":
            False,

        "overwrite_existing_evidence":
            False,

        "implicit_resume":
            False,

        "analysis_after_verification_only":
            True,
    }

    for key, expected in exact.items():
        if contract.get(key) != expected:
            fail(
                "SQ-11 execution-contract drift "
                f"{key}: "
                f"{contract.get(key)!r} != "
                f"{expected!r}"
            )

    runtime = contract.get(
        "runtime_parameters",
        {},
    )

    expected_runtime = {
        "dt_ms":
            1.0,

        "tau_ms":
            20.0,

        "threshold":
            1.0,

        "release_gain":
            0.9981738484618123,
    }

    if runtime != expected_runtime:
        fail(
            "SQ-11 runtime parameter "
            "contract drift"
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
            "SQ-11 manifest must contain "
            "exactly 16 conditions"
        )

    expected_conditions = []
    ordinal = 0

    for mask in EXPECTED_MASKS:
        for replicate in EXPECTED_REPLICATES:
            expected_conditions.append(
                {
                    "ordinal":
                        ordinal,

                    "condition_id":
                        f"sq11:{mask}:r{replicate}",

                    "mask":
                        mask,

                    "replicate":
                        replicate,

                    "edge_zeroed":
                        [
                            int(bit)
                            for bit in mask
                        ],
                }
            )

            ordinal += 1

    if conditions != expected_conditions:
        fail(
            "SQ-11 canonical condition "
            "universe drift"
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
        items = manifest.get(
            section
        )

        if not isinstance(
            items,
            dict,
        ):
            fail(
                f"SQ-11 manifest missing {section}"
            )

        for name, item in items.items():
            path = (
                ROOT
                / item["path"]
            )

            if not path.is_file():
                fail(
                    "missing frozen SQ-11 "
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
                    f"SQ-11 SHA mismatch {name}: "
                    f"{actual} != {expected}"
                )

            observed[
                f"{section}.{name}"
            ] = actual

    if (
        len(
            manifest["frozen_code"]
        )
        != 32
    ):
        fail(
            "SQ-11 frozen-code closure "
            "must contain exactly 32 artifacts"
        )

    if (
        len(
            manifest["frozen_contracts"]
        )
        != 6
    ):
        fail(
            "SQ-11 frozen-contract closure "
            "must contain exactly 6 artifacts"
        )

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
                "missing SQ-11 physical input "
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
                "SQ-11 physical input SHA "
                f"mismatch {name}: "
                f"{actual} != {expected}"
            )

        observed[name] = {
            "path":
                str(path),

            "sha256":
                actual,
        }

    #
    # Import only after frozen repository
    # artifacts have been independently
    # checked by normal readiness call order.
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
            "SQ-11 frozen stimulus "
            "frame-count drift"
        )

    if (
        stimulus.get("layout")
        != "RL"
    ):
        fail(
            "SQ-11 stimulus layout drift"
        )

    if (
        stimulus.get("frame_count")
        != 192
    ):
        fail(
            "SQ-11 stimulus manifest "
            "frame-count drift"
        )

    if (
        schedules.get("RL")
        != stimulus[
            "schedule_sha256"
        ]
    ):
        fail(
            "SQ-11 frozen RL schedule drift"
        )

    observed["stimulus"] = {
        "layout":
            "RL",

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

    from brain.sq11_dark_forest_plan import (
        MASKS,
        REPLICATES,
    )

    from brain.visual_transduction import (
        VisualTransductionConfig,
    )

    execution = manifest[
        "execution_contract"
    ]

    if FRAME_COUNT != 192:
        fail(
            "SQ-11 runtime frame-count drift"
        )

    if tuple(MASKS) != EXPECTED_MASKS:
        fail(
            "SQ-11 runtime mask-universe drift"
        )

    if tuple(REPLICATES) != (
        EXPECTED_REPLICATES
    ):
        fail(
            "SQ-11 runtime replicate drift"
        )

    expected_release_gain = (
        execution[
            "runtime_parameters"
        ][
            "release_gain"
        ]
    )

    if RELEASE_GAIN != expected_release_gain:
        fail(
            "SQ-11 release-gain drift"
        )

    config = VisualTransductionConfig(
        release_gain=RELEASE_GAIN
    )

    observed = {
        "dt_ms":
            float(config.dt_ms),

        "tau_ms":
            float(config.tau_ms),

        "threshold":
            float(config.threshold),

        "release_gain":
            float(config.release_gain),

        "frame_count":
            FRAME_COUNT,

        "layout":
            "RL",

        "replay_version":
            execution[
                "replay_version"
            ],

        "replay_float_dtype":
            execution[
                "replay_float_dtype"
            ],

        "replay_absolute_tolerance":
            execution[
                "replay_absolute_tolerance"
            ],

        "replay_relative_tolerance":
            execution[
                "replay_relative_tolerance"
            ],
    }

    expected_runtime = execution[
        "runtime_parameters"
    ]

    for key in (
        "dt_ms",
        "tau_ms",
        "threshold",
        "release_gain",
    ):
        if (
            observed[key]
            != expected_runtime[key]
        ):
            fail(
                "SQ-11 runtime semantic drift "
                f"{key}: "
                f"{observed[key]!r} != "
                f"{expected_runtime[key]!r}"
            )

    if (
        observed[
            "replay_version"
        ]
        != 2
    ):
        fail(
            "SQ-11 replay-version drift"
        )

    if (
        observed[
            "replay_float_dtype"
        ]
        != "float32"
    ):
        fail(
            "SQ-11 replay dtype drift"
        )

    if (
        observed[
            "replay_absolute_tolerance"
        ]
        != 0.0
        or observed[
            "replay_relative_tolerance"
        ]
        != 0.0
    ):
        fail(
            "SQ-11 replay tolerance "
            "must remain exactly zero"
        )

    return observed


def verify_body_topology(
    manifest: dict | None = None,
) -> dict:
    if manifest is None:
        manifest = load_manifest()

    import numpy as np
    from scipy import sparse

    from brain.sq10_sophon_episode import (
        BODY_RESPONDERS,
        BODY_SOURCES,
    )

    from brain.sq11_dark_forest_episode import (
        BODY_FLAT_POSITIONS,
        BODY_POSITIONS,
        FLAT_ENTRY_COUNT,
        PRESYNAPTIC_UNION_COUNT,
        ROW_OFFSETS,
        baseline_geometry,
    )

    connectome_path = (
        DATA_ROOT
        / manifest[
            "physical_inputs"
        ][
            "connectome"
        ][
            "logical_name"
        ]
    )

    baseline = sparse.load_npz(
        connectome_path
    ).tocsr()

    if baseline.dtype != np.float32:
        fail(
            "SQ-11 baseline connectome "
            "must remain float32"
        )

    geometry = baseline_geometry(
        baseline
    )

    if not np.array_equal(
        geometry["row_offsets"],
        ROW_OFFSETS,
    ):
        fail(
            "SQ-11 BODY row-offset drift"
        )

    if not np.array_equal(
        geometry["body_positions"],
        BODY_POSITIONS,
    ):
        fail(
            "SQ-11 BODY local-position drift"
        )

    if not np.array_equal(
        geometry[
            "body_flat_positions"
        ],
        BODY_FLAT_POSITIONS,
    ):
        fail(
            "SQ-11 BODY flat-position drift"
        )

    if (
        len(
            geometry["row_indices"]
        )
        != FLAT_ENTRY_COUNT
    ):
        fail(
            "SQ-11 BODY flat-entry-count drift"
        )

    if (
        len(
            geometry[
                "presynaptic_union_indices"
            ]
        )
        != PRESYNAPTIC_UNION_COUNT
    ):
        fail(
            "SQ-11 BODY union-count drift"
        )

    observed_body_sources = (
        geometry["row_indices"][
            geometry[
                "body_flat_positions"
            ]
        ]
    )

    if not np.array_equal(
        observed_body_sources,
        BODY_SOURCES,
    ):
        fail(
            "SQ-11 BODY source-coordinate drift"
        )

    body_weights = (
        geometry["row_weights"][
            geometry[
                "body_flat_positions"
            ]
        ]
    )

    return {
        "source_indices":
            BODY_SOURCES.tolist(),

        "responder_indices":
            BODY_RESPONDERS.tolist(),

        "row_offsets":
            geometry[
                "row_offsets"
            ].tolist(),

        "body_positions":
            geometry[
                "body_positions"
            ].tolist(),

        "body_flat_positions":
            geometry[
                "body_flat_positions"
            ].tolist(),

        "row_entry_count":
            int(
                len(
                    geometry[
                        "row_indices"
                    ]
                )
            ),

        "presynaptic_union_count":
            int(
                len(
                    geometry[
                        "presynaptic_union_indices"
                    ]
                )
            ),

        "body_edge_weight":
            [
                float(value)
                for value
                in body_weights
            ],
    }


def verify_replay_qualification_closure(
    manifest: dict | None = None,
) -> dict:
    if manifest is None:
        manifest = load_manifest()

    expected = {
        "authoritative_version":
            2,

        "status":
            "QUALIFIED_FOR_SQ11_EXECUTION",

        "synthetic_activity_cases":
            96,

        "condition_masks":
            8,

        "body_rows":
            3,

        "exact_float32_comparisons":
            2304,

        "mismatch_count":
            0,

        "absolute_tolerance":
            0.0,

        "relative_tolerance":
            0.0,

        "neural_execution_performed":
            False,

        "sq11_neural_evidence_inspected":
            False,
    }

    observed = manifest.get(
        "replay_qualification"
    )

    if observed != expected:
        fail(
            "SQ-11 replay qualification "
            "summary drift"
        )

    contracts = manifest[
        "frozen_contracts"
    ]

    result = contracts[
        "replay_qualification_result_v2"
    ]

    seal = contracts[
        "replay_qualification_seal_v2"
    ]

    if (
        sha256_file(
            ROOT / result["path"]
        )
        != result["sha256"]
    ):
        fail(
            "SQ-11 replay qualification "
            "result hash drift"
        )

    if (
        sha256_file(
            ROOT / seal["path"]
        )
        != seal["sha256"]
    ):
        fail(
            "SQ-11 replay qualification "
            "seal hash drift"
        )

    return {
        **expected,

        "result_path":
            result["path"],

        "result_sha256":
            result["sha256"],

        "seal_path":
            seal["path"],

        "seal_sha256":
            seal["sha256"],
    }


def _verify_destination(
    *,
    item: dict,
    expected_relative_path: str,
    label: str,
) -> dict:
    if (
        item.get("path")
        != expected_relative_path
    ):
        fail(
            f"SQ-11 {label} path drift"
        )

    if (
        item.get(
            "must_not_exist_before_execution"
        )
        is not True
    ):
        fail(
            f"SQ-11 {label} fail-closed "
            "existence rule drift"
        )

    if (
        item.get(
            "overwrite_existing"
        )
        is not False
    ):
        fail(
            f"SQ-11 {label} overwrite-rule drift"
        )

    path = (
        ROOT
        / expected_relative_path
    )

    if path.exists():
        fail(
            f"SQ-11 {label} already exists; "
            "implicit overwrite/resume forbidden: "
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


def verify_output_destinations(
    manifest: dict | None = None,
) -> dict:
    if manifest is None:
        manifest = load_manifest()

    evidence_relative = (
        "artifacts/experiments/"
        "sq11-dark-forest/"
        "sq11-dark-forest-evidence-v2.npz"
    )

    receipt_relative = (
        "artifacts/experiments/"
        "sq11-dark-forest/"
        "sq11-dark-forest-publication-receipt-v2.json"
    )

    evidence = _verify_destination(
        item=manifest[
            "evidence_destination"
        ],
        expected_relative_path=
            evidence_relative,
        label="evidence destination",
    )

    receipt_item = manifest[
        "publication_receipt_destination"
    ]

    if (
        receipt_item.get(
            "execution_authorized_here"
        )
        is not False
    ):
        fail(
            "SQ-11 publication receipt "
            "unexpectedly grants execution authority"
        )

    receipt = _verify_destination(
        item=receipt_item,
        expected_relative_path=
            receipt_relative,
        label="publication receipt destination",
    )

    return {
        "evidence":
            evidence,

        "publication_receipt":
            receipt,
    }


def build_readiness_report() -> dict:
    #
    # Clean repository is deliberately first.
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

    return {
        "status":
            "SQ11_READY_FOR_AUTHORIZATION",

        "experiment":
            "SQ-11",

        "codename":
            "DARK FOREST",

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

        "replay_qualification":
            qualification,

        "output_destinations":
            destinations,

        "neural_execution_performed":
            False,

        "authorization_granted":
            False,

        "analysis_performed":
            False,
    }


def main() -> None:
    report = (
        build_readiness_report()
    )

    print(
        json.dumps(
            report,
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
