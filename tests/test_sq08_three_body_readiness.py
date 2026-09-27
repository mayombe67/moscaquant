from __future__ import annotations

from brain.sq08_three_body_readiness import (
    CONNECTOME_SHA256,
    EXPECTED,
    SCIENCE_GIT_SHA,
)


def test_science_freeze_identity():
    assert SCIENCE_GIT_SHA == (
        "e4a58df478d7681b612ed9deb85b5ddfe1268acc"
    )


def test_authoritative_manifest_identity():
    assert (
        EXPECTED[
            "execution_manifest"
        ][1]
        == (
            "9a472f6548f777ceec327b8449ffcfee27"
            "d275478792a59097d28e95121c9dfe"
        )
    )


def test_connectome_identity():
    assert CONNECTOME_SHA256 == (
        "e00e3f2a9828c921fe1f093cc567bf45"
        "a85adad0526176be0aa1b8be09336eeb"
    )


def test_readiness_pins_core_science_artifacts():
    for key in (
        "prereg",
        "topology_amendment",
        "topology_calibration",
        "topology_frontier",
        "evidence_schema",
        "analysis_contract",
        "execution_manifest",
        "readout",
        "episode",
        "evidence",
        "independent_verify",
        "analysis",
    ):
        assert key in EXPECTED
