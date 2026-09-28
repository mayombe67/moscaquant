from __future__ import annotations

import json
from pathlib import Path

import pytest

from brain.sq10_sophon_execute import (
    AUTHORIZATION,
    EXPECTED_AUTHORIZATION_SHA256,
    EXPECTED_MANIFEST_SHA256,
    ExecutionRefusal,
    _atomic_publish_no_overwrite,
    sha256_file,
    validate_authorization_payload,
)


def test_exact_authorization_is_bound():
    assert (
        sha256_file(AUTHORIZATION)
        == EXPECTED_AUTHORIZATION_SHA256
    )

    payload = json.loads(
        AUTHORIZATION.read_text()
    )

    validate_authorization_payload(
        payload
    )


def test_manifest_identity_is_bound():
    payload = json.loads(
        AUTHORIZATION.read_text()
    )

    assert (
        payload[
            "execution_manifest_sha256"
        ]
        == EXPECTED_MANIFEST_SHA256
    )


def test_exact_16_authorized_units():
    payload = json.loads(
        AUTHORIZATION.read_text()
    )

    units = payload[
        "authorized_work_units"
    ]

    assert len(units) == 16

    assert (
        units[0]["condition_id"]
        == "sq10:000:r1"
    )

    assert (
        units[-1]["condition_id"]
        == "sq10:111:r2"
    )


def test_atomic_publication_refuses_overwrite(
    tmp_path: Path,
):
    path = tmp_path / "evidence.npz"

    path.write_bytes(b"existing")

    with pytest.raises(
        ExecutionRefusal
    ):
        _atomic_publish_no_overwrite(
            path,
            lambda handle:
                handle.write(b"replacement"),
        )

    assert (
        path.read_bytes()
        == b"existing"
    )


def test_launcher_does_not_import_analyzer():
    source = (
        Path(__file__)
        .resolve()
        .parents[2]
        / "brain/"
        "sq10_sophon_execute.py"
    ).read_text()

    assert (
        "sq10_sophon_analysis"
        not in source
    )

    assert (
        "analyze("
        not in source
    )


def test_valid_launch_seal_contract():
    from brain.sq10_sophon_execute import (
        EVIDENCE,
        EXPECTED_AUTHORIZATION_COMMIT,
        ROOT,
        validate_launch_seal_payload,
    )

    launcher_sha = "b" * 64

    payload = {
        "schema_version":
            "moscaquant.sq10-sophon-launch-seal/v1",
        "status":
            "SEALED_FOR_FROZEN_EXECUTION",
        "execution_performed":
            False,
        "authorization": {
            "path":
                "config/controls/"
                "sq10-sophon-execution-authorization-v1.json",
            "sha256":
                EXPECTED_AUTHORIZATION_SHA256,
            "git_commit":
                EXPECTED_AUTHORIZATION_COMMIT,
        },
        "execution_manifest_sha256":
            EXPECTED_MANIFEST_SHA256,
        "launcher": {
            "path":
                "brain/sq10_sophon_execute.py",
            "sha256":
                launcher_sha,
            "git_commit":
                "c" * 40,
        },
        "evidence_destination": {
            "path":
                str(
                    EVIDENCE.relative_to(
                        ROOT
                    )
                ),
            "overwrite_existing":
                False,
        },
    }

    validate_launch_seal_payload(
        payload,
        observed_launcher_sha=
            launcher_sha,
    )


def test_launch_seal_rejects_wrong_launcher_sha():
    from brain.sq10_sophon_execute import (
        EVIDENCE,
        ROOT,
        validate_launch_seal_payload,
    )

    payload = {
        "schema_version":
            "moscaquant.sq10-sophon-launch-seal/v1",
        "status":
            "SEALED_FOR_FROZEN_EXECUTION",
        "execution_performed":
            False,
        "authorization": {
            "path":
                "config/controls/"
                "sq10-sophon-execution-authorization-v1.json",
            "sha256":
                EXPECTED_AUTHORIZATION_SHA256,
        },
        "execution_manifest_sha256":
            EXPECTED_MANIFEST_SHA256,
        "launcher": {
            "path":
                "brain/sq10_sophon_execute.py",
            "sha256":
                "0" * 64,
            "git_commit":
                "c" * 40,
        },
        "evidence_destination": {
            "path":
                str(
                    EVIDENCE.relative_to(
                        ROOT
                    )
                ),
            "overwrite_existing":
                False,
        },
    }

    with pytest.raises(
        ExecutionRefusal
    ):
        validate_launch_seal_payload(
            payload,
            observed_launcher_sha=
                "1" * 64,
        )
