from __future__ import annotations

from brain.sq10_sophon_authorization import (
    EXPECTED_READINESS_COMMIT,
    EXPECTED_READINESS_SHA256,
    assemble_authorization,
)
from brain.sq10_sophon_readiness import (
    load_manifest,
    sha256_file,
)


def synthetic_payload():
    manifest = load_manifest()

    return assemble_authorization(
        manifest=manifest,

        control_plane_sha=
            "a" * 40,

        repo_artifacts={
            "test": "hash",
        },

        physical_inputs={
            "test": {
                "sha256": "hash",
            },
        },

        runtime={
            "dt_ms": 1.0,
            "tau_ms": 20.0,
            "threshold": 1.0,
            "release_gain":
                0.9981738484618123,
        },

        body_topology={
            "A": {},
            "B": {},
            "C": {},
        },

        calibration={
            "absolute_tolerance":
                3.814697265625e-06,
            "relative_tolerance":
                0.0,
        },

        evidence_destination={
            "exists_before_execution":
                False,
            "overwrite_existing":
                False,
        },
    )


def test_readiness_revision_is_bound():
    from brain.sq10_sophon_authorization import (
        READINESS,
    )

    assert (
        len(
            EXPECTED_READINESS_COMMIT
        )
        == 40
    )

    assert (
        sha256_file(READINESS)
        == EXPECTED_READINESS_SHA256
    )


def test_authorization_contains_exact_cube():
    d = synthetic_payload()

    assert (
        len(
            d["authorized_work_units"]
        )
        == 16
    )

    ids = [
        row["condition_id"]
        for row in
        d["authorized_work_units"]
    ]

    assert len(set(ids)) == 16

    assert ids[0] == "sq10:000:r1"
    assert ids[-1] == "sq10:111:r2"


def test_authorization_is_execution_only():
    d = synthetic_payload()

    boundary = d[
        "execution_boundary"
    ]

    assert (
        boundary[
            "authorization_only"
        ]
        is True
    )

    assert (
        boundary[
            "execution_performed"
        ]
        is False
    )

    assert (
        boundary[
            "analysis_authority"
        ]
        is False
    )

    assert (
        boundary[
            "mechanism_interpretation_authority"
        ]
        is False
    )

    assert (
        boundary[
            "result_reclassification_authority"
        ]
        is False
    )

    assert (
        boundary[
            "tolerance_modification_authority"
        ]
        is False
    )


def test_authorization_remains_fail_closed():
    d = synthetic_payload()

    contract = d[
        "execution_contract"
    ]

    assert (
        contract[
            "arbitrary_condition_execution"
        ]
        is False
    )

    assert (
        contract[
            "overwrite_existing_evidence"
        ]
        is False
    )

    assert (
        contract[
            "implicit_resume"
        ]
        is False
    )

    assert (
        contract[
            "all_work_units_required"
        ]
        is True
    )

    assert (
        contract[
            "independent_verification_required"
        ]
        is True
    )


def test_manifest_identity_is_bound():
    d = synthetic_payload()

    assert (
        len(
            d[
                "execution_manifest_sha256"
            ]
        )
        == 64
    )
