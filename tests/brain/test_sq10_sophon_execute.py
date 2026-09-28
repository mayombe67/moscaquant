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
