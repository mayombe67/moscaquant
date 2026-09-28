from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import tempfile

import numpy as np
from scipy import sparse

from brain.sq11_dark_forest_independent_verify import (
    EXPECTED_KEYS,
    verify_evidence_arrays,
)


ROOT = Path(__file__).resolve().parents[1]

EVIDENCE = (
    ROOT
    / "artifacts"
    / "experiments"
    / "sq11-dark-forest"
    / "sq11-dark-forest-evidence-v2.npz"
)

RECEIPT = (
    ROOT
    / "artifacts"
    / "experiments"
    / "sq11-dark-forest"
    / "sq11-dark-forest-publication-receipt-v2.json"
)


class PublicationRefusal(RuntimeError):
    pass


def refuse(message: str) -> None:
    raise PublicationRefusal(message)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(
                8 * 1024 * 1024
            ),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


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
        # Match SQ-10 semantics:
        # hard-link publication is atomic and
        # fails rather than replacing a file
        # that appeared during execution.
        #
        try:
            os.link(
                temp,
                path,
            )
        except FileExistsError:
            refuse(
                "output appeared during "
                f"publication: {path}"
            )

        dir_fd = os.open(
            path.parent,
            os.O_RDONLY,
        )

        try:
            os.fsync(
                dir_fd
            )
        finally:
            os.close(
                dir_fd
            )

    finally:
        try:
            temp.unlink()
        except FileNotFoundError:
            pass


def validate_for_publication(
    arrays: dict[str, np.ndarray],
    *,
    baseline: sparse.csr_matrix,
) -> dict:
    if set(arrays) != EXPECTED_KEYS:
        refuse(
            "SQ-11 publication "
            "evidence key-set drift"
        )

    #
    # Crucially, publication requires the
    # independent verifier WITH frozen-baseline
    # binding, not merely internal replay.
    #
    report = verify_evidence_arrays(
        arrays,
        baseline=baseline,
    )

    if (
        report.get("status")
        != "PASS"
    ):
        refuse(
            "SQ-11 independent verification "
            "did not return PASS"
        )

    if (
        report.get(
            "baseline_binding_verified"
        )
        is not True
    ):
        refuse(
            "SQ-11 baseline binding "
            "was not verified"
        )

    return report


def _publish_evidence_to(
    path: Path,
    arrays: dict[str, np.ndarray],
) -> str:
    def writer(handle):
        np.savez_compressed(
            handle,
            **arrays,
        )

    _atomic_publish_no_overwrite(
        path,
        writer,
    )

    return sha256_file(
        path
    )


def verify_persisted_evidence(
    path: Path,
    expected: dict[str, np.ndarray],
    *,
    baseline: sparse.csr_matrix,
) -> dict:
    if not path.is_file():
        refuse(
            "persisted SQ-11 evidence "
            f"is missing: {path}"
        )

    with np.load(
        path,
        allow_pickle=False,
    ) as payload:
        observed = {
            key: payload[key]
            for key in payload.files
        }

    if set(observed) != EXPECTED_KEYS:
        refuse(
            "persisted SQ-11 evidence "
            "key-set drift"
        )

    for key in EXPECTED_KEYS:
        if not np.array_equal(
            observed[key],
            expected[key],
        ):
            refuse(
                "persisted SQ-11 evidence "
                f"mismatch: {key}"
            )

    #
    # Independent verification AGAIN,
    # now against bytes reloaded from disk,
    # and AGAIN bound to the frozen baseline.
    #
    return validate_for_publication(
        observed,
        baseline=baseline,
    )


def publish_evidence(
    arrays: dict[str, np.ndarray],
    *,
    baseline: sparse.csr_matrix,
) -> tuple[str, dict]:
    #
    # First pass is entirely in-memory.
    #
    validate_for_publication(
        arrays,
        baseline=baseline,
    )

    evidence_sha = (
        _publish_evidence_to(
            EVIDENCE,
            arrays,
        )
    )

    #
    # Second pass is against persisted bytes.
    #
    persisted_report = (
        verify_persisted_evidence(
            EVIDENCE,
            arrays,
            baseline=baseline,
        )
    )

    return (
        evidence_sha,
        persisted_report,
    )


def publish_receipt(
    payload: dict,
) -> str:
    if not isinstance(
        payload,
        dict,
    ):
        raise TypeError(
            "SQ-11 publication receipt "
            "must be a dict"
        )

    if payload.get(
        "execution_authorized_here"
    ) is not False:
        refuse(
            "SQ-11 publication receipt "
            "must explicitly deny "
            "execution authority"
        )

    encoded = (
        json.dumps(
            payload,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    ).encode(
        "utf-8"
    )

    def writer(handle):
        handle.write(
            encoded
        )

    _atomic_publish_no_overwrite(
        RECEIPT,
        writer,
    )

    return sha256_file(
        RECEIPT
    )
