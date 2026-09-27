from __future__ import annotations

from brain.sq08_three_body_authorization import (
    EXPECTED_CONTROL_PLANE_ANCESTOR,
)
from brain.sq08_three_body_readiness import (
    SCIENCE_GIT_SHA,
)


def test_authorization_science_identity():
    assert SCIENCE_GIT_SHA == (
        "e4a58df478d7681b612ed9deb85b5ddfe1268acc"
    )


def test_authorization_descends_from_reviewed_readiness():
    assert (
        EXPECTED_CONTROL_PLANE_ANCESTOR
        == "e232fd2a103db762180422f638bafe13519da38a"
    )
