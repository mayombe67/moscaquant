from __future__ import annotations

import hashlib

import numpy as np
import pytest
from scipy import sparse

import brain.sq11_dark_forest_publish as publish_module

from brain.sq11_dark_forest_publish import (
    EXPECTED_KEYS,
    PublicationRefusal,
    _atomic_publish_no_overwrite,
    publish_evidence,
    publish_receipt,
    sha256_file,
    verify_persisted_evidence,
)


def tiny_arrays():
    arrays = {}

    for index, key in enumerate(
        sorted(EXPECTED_KEYS)
    ):
        arrays[key] = np.asarray(
            [index],
            dtype=np.int64,
        )

    return arrays


def dummy_baseline():
    return sparse.csr_matrix(
        np.zeros(
            (1, 1),
            dtype=np.float32,
        )
    )


def passing_report():
    return {
        "status": "PASS",
        "baseline_binding_verified": True,
    }


@pytest.fixture
def isolated_paths(
    tmp_path,
    monkeypatch,
):
    evidence = (
        tmp_path
        / "sq11-dark-forest-evidence-v2.npz"
    )

    receipt = (
        tmp_path
        / "sq11-dark-forest-publication-receipt-v2.json"
    )

    monkeypatch.setattr(
        publish_module,
        "EVIDENCE",
        evidence,
    )

    monkeypatch.setattr(
        publish_module,
        "RECEIPT",
        receipt,
    )

    return evidence, receipt


def test_publish_evidence_round_trip(
    isolated_paths,
    monkeypatch,
):
    evidence, _receipt = isolated_paths

    monkeypatch.setattr(
        publish_module,
        "verify_evidence_arrays",
        lambda arrays, baseline=None:
            passing_report(),
    )

    arrays = tiny_arrays()

    evidence_sha, report = (
        publish_evidence(
            arrays,
            baseline=dummy_baseline(),
        )
    )

    assert evidence.is_file()

    assert evidence_sha == (
        sha256_file(evidence)
    )

    assert report == passing_report()

    with np.load(
        evidence,
        allow_pickle=False,
    ) as payload:
        assert set(payload.files) == (
            EXPECTED_KEYS
        )

        for key in EXPECTED_KEYS:
            np.testing.assert_array_equal(
                payload[key],
                arrays[key],
            )


def test_existing_evidence_is_never_overwritten(
    isolated_paths,
    monkeypatch,
):
    evidence, _receipt = isolated_paths

    evidence.write_bytes(
        b"DO-NOT-TOUCH"
    )

    original_sha = hashlib.sha256(
        evidence.read_bytes()
    ).hexdigest()

    monkeypatch.setattr(
        publish_module,
        "verify_evidence_arrays",
        lambda arrays, baseline=None:
            passing_report(),
    )

    with pytest.raises(
        PublicationRefusal,
        match="refusing to overwrite",
    ):
        publish_evidence(
            tiny_arrays(),
            baseline=dummy_baseline(),
        )

    assert hashlib.sha256(
        evidence.read_bytes()
    ).hexdigest() == original_sha


def test_failed_verification_prevents_publication(
    isolated_paths,
    monkeypatch,
):
    evidence, _receipt = isolated_paths

    monkeypatch.setattr(
        publish_module,
        "verify_evidence_arrays",
        lambda arrays, baseline=None: {
            "status": "FAIL",
            "baseline_binding_verified": True,
        },
    )

    with pytest.raises(
        PublicationRefusal,
        match="did not return PASS",
    ):
        publish_evidence(
            tiny_arrays(),
            baseline=dummy_baseline(),
        )

    assert not evidence.exists()


def test_persisted_mismatch_is_refused(
    isolated_paths,
    monkeypatch,
):
    evidence, _receipt = isolated_paths

    monkeypatch.setattr(
        publish_module,
        "verify_evidence_arrays",
        lambda arrays, baseline=None:
            passing_report(),
    )

    arrays = tiny_arrays()

    publish_module._publish_evidence_to(
        evidence,
        arrays,
    )

    expected = {
        key: value.copy()
        for key, value in arrays.items()
    }

    changed_key = sorted(
        EXPECTED_KEYS
    )[0]

    expected[
        changed_key
    ][0] += 1

    with pytest.raises(
        PublicationRefusal,
        match="persisted SQ-11 evidence mismatch",
    ):
        verify_persisted_evidence(
            evidence,
            expected,
            baseline=dummy_baseline(),
        )


def test_receipt_must_deny_execution_authority(
    isolated_paths,
):
    _evidence, receipt = isolated_paths

    with pytest.raises(
        PublicationRefusal,
        match="must explicitly deny execution authority",
    ):
        publish_receipt(
            {
                "execution_authorized_here":
                    True,
            }
        )

    assert not receipt.exists()


def test_receipt_is_no_overwrite(
    isolated_paths,
):
    _evidence, receipt = isolated_paths

    payload = {
        "execution_authorized_here":
            False,
        "status":
            "published",
    }

    first_sha = publish_receipt(
        payload
    )

    assert first_sha == (
        sha256_file(receipt)
    )

    original = receipt.read_bytes()

    with pytest.raises(
        PublicationRefusal,
        match="refusing to overwrite",
    ):
        publish_receipt(
            payload
        )

    assert receipt.read_bytes() == original


def test_failed_writer_leaves_no_output_or_temp(
    tmp_path,
):
    target = (
        tmp_path
        / "failure.bin"
    )

    def bad_writer(handle):
        handle.write(
            b"partial"
        )

        raise RuntimeError(
            "synthetic writer failure"
        )

    with pytest.raises(
        RuntimeError,
        match="synthetic writer failure",
    ):
        _atomic_publish_no_overwrite(
            target,
            bad_writer,
        )

    assert not target.exists()

    leftovers = list(
        tmp_path.glob(
            ".failure.bin.*.tmp"
        )
    )

    assert leftovers == []
