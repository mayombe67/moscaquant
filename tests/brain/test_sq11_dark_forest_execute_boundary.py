from __future__ import annotations

import copy
import json

import pytest

import brain.sq11_dark_forest_execute as execute


def authorization_payload():
    return json.loads(
        execute.AUTHORIZATION.read_text(
            encoding="utf-8",
        )
    )


def valid_launch_seal(
    launcher_sha: str,
) -> dict:
    return {
        "schema_version":
            "moscaquant."
            "sq11-dark-forest-launch-seal/v1",

        "experiment":
            "SQ-11",

        "codename":
            "DARK FOREST",

        "status":
            "SEALED_FOR_FROZEN_EXECUTION",

        "authorization": {
            "path":
                str(
                    execute.AUTHORIZATION.relative_to(
                        execute.ROOT
                    )
                ),
            "sha256":
                execute.EXPECTED_AUTHORIZATION_SHA256,
            "git_commit":
                execute.EXPECTED_AUTHORIZATION_COMMIT,
        },

        "execution_manifest_sha256":
            execute.EXPECTED_MANIFEST_SHA256,

        "launcher": {
            "path":
                str(
                    execute.Path(
                        execute.__file__
                    ).relative_to(
                        execute.ROOT
                    )
                ),
            "sha256":
                launcher_sha,
            "git_commit":
                "synthetic-launcher-commit",
        },

        "destinations": {
            "evidence": {
                "path":
                    str(
                        execute.EVIDENCE.relative_to(
                            execute.ROOT
                        )
                    ),
                "overwrite_existing":
                    False,
            },

            "publication_receipt": {
                "path":
                    str(
                        execute.RECEIPT.relative_to(
                            execute.ROOT
                        )
                    ),
                "overwrite_existing":
                    False,
            },
        },

        "execution_boundary": {
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
        },
    }


def test_frozen_authorization_payload_passes():
    execute.validate_authorization_payload(
        authorization_payload()
    )


def test_prior_execution_claim_is_refused():
    payload = authorization_payload()

    payload[
        "execution_boundary"
    ][
        "execution_performed"
    ] = True

    with pytest.raises(
        execute.ExecutionRefusal,
        match="prior execution",
    ):
        execute.validate_authorization_payload(
            payload
        )


def test_nonzero_replay_tolerance_is_refused():
    payload = authorization_payload()

    payload[
        "execution_contract"
    ][
        "replay_absolute_tolerance"
    ] = 1.0e-6

    with pytest.raises(
        execute.ExecutionRefusal,
        match="replay_absolute_tolerance",
    ):
        execute.validate_authorization_payload(
            payload
        )


def test_valid_launch_seal_contract_passes():
    sha = execute.sha256_file(
        execute.Path(
            execute.__file__
        )
    )

    execute.validate_launch_seal_payload(
        valid_launch_seal(sha),
        observed_launcher_sha=sha,
    )


def test_launcher_sha_drift_is_refused():
    sha = execute.sha256_file(
        execute.Path(
            execute.__file__
        )
    )

    payload = valid_launch_seal(
        "0" * 64
    )

    with pytest.raises(
        execute.ExecutionRefusal,
        match="launcher SHA drift",
    ):
        execute.validate_launch_seal_payload(
            payload,
            observed_launcher_sha=sha,
        )


def test_launch_seal_cannot_grant_analysis():
    sha = execute.sha256_file(
        execute.Path(
            execute.__file__
        )
    )

    payload = valid_launch_seal(sha)

    payload[
        "execution_boundary"
    ][
        "analysis_authority"
    ] = True

    with pytest.raises(
        execute.ExecutionRefusal,
        match="execution boundary drift",
    ):
        execute.validate_launch_seal_payload(
            payload,
            observed_launcher_sha=sha,
        )
