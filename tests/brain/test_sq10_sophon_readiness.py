from __future__ import annotations

from brain.sq10_sophon_readiness import (
    EXPECTED_MANIFEST_COMMIT,
    EXPECTED_MANIFEST_SHA256,
    SCIENCE_GIT_SHA,
    load_manifest,
    sha256_file,
    verify_body_topology,
    verify_calibration_closure,
    verify_evidence_destination,
    verify_manifest,
    verify_physical_inputs,
    verify_repo_artifacts,
    verify_runtime_semantics,
)


def test_manifest_identity_is_frozen():
    d = load_manifest()

    from brain.sq10_sophon_readiness import (
        MANIFEST,
    )

    assert (
        sha256_file(MANIFEST)
        == EXPECTED_MANIFEST_SHA256
    )

    assert (
        d["science_git_sha"]
        == SCIENCE_GIT_SHA
    )

    assert len(
        EXPECTED_MANIFEST_COMMIT
    ) == 40


def test_manifest_semantics_close():
    d = verify_manifest()

    assert (
        d["neural_execution_authorized"]
        is False
    )

    assert len(
        d["conditions"]
    ) == 16


def test_repo_artifact_hashes_close():
    d = verify_manifest()

    observed = (
        verify_repo_artifacts(d)
    )

    assert observed


def test_physical_input_hashes_close():
    d = verify_manifest()

    observed = (
        verify_physical_inputs(d)
    )

    assert (
        observed["stimulus"]
        ["frame_count"]
        == 192
    )


def test_runtime_semantics_close():
    d = verify_manifest()

    observed = (
        verify_runtime_semantics(d)
    )

    assert (
        observed["release_gain"]
        == 0.9981738484618123
    )


def test_body_topology_closes():
    d = verify_manifest()

    observed = (
        verify_body_topology(d)
    )

    assert set(observed) == {
        "A",
        "B",
        "C",
    }


def test_calibration_and_destination_close():
    d = verify_manifest()

    calibration = (
        verify_calibration_closure(d)
    )

    destination = (
        verify_evidence_destination(d)
    )

    assert (
        calibration[
            "absolute_tolerance"
        ]
        == 3.814697265625e-06
    )

    assert (
        destination[
            "exists_before_execution"
        ]
        is False
    )
