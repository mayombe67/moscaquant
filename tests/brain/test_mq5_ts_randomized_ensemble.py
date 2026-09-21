from __future__ import annotations

import numpy as np

from brain.mq5_ts_randomized_ensemble import (
    classify_arm_c,
    exact_reproduction_against_a,
)


class FakeResult:
    def __init__(
        self,
        responders,
        onsets,
        fingerprint,
    ):
        self.responder_identity = {
            "responder_indices": list(responders),
            "responder_count": len(responders),
        }
        self.first_positive_onsets = dict(onsets)
        self.positive_voltage_fingerprint = list(fingerprint)


def test_classification_boundaries():
    kwargs = {
        "completed_count": 20,
        "expected_count": 20,
        "max_for_supported": 1,
        "min_for_frequent": 10,
    }

    assert classify_arm_c(0, **kwargs) == (
        "TOPOLOGY-SPECIFIC RESPONSE PATTERN SUPPORTED"
    )
    assert classify_arm_c(1, **kwargs) == (
        "TOPOLOGY-SPECIFIC RESPONSE PATTERN SUPPORTED"
    )
    assert classify_arm_c(2, **kwargs) == "MIXED TOPOLOGY SPECIFICITY"
    assert classify_arm_c(9, **kwargs) == "MIXED TOPOLOGY SPECIFICITY"
    assert classify_arm_c(10, **kwargs) == (
        "STRICT NULL FREQUENTLY REPRODUCES RESPONSE"
    )
    assert classify_arm_c(20, **kwargs) == (
        "STRICT NULL FREQUENTLY REPRODUCES RESPONSE"
    )


def test_incomplete_arm_c_refuses_classification():
    assert classify_arm_c(
        0,
        completed_count=19,
        expected_count=20,
        max_for_supported=1,
        min_for_frequent=10,
    ) == "INCOMPLETE_DUE_TO_FAILED_ARM_C_BUILDS"


def test_exact_reproduction_requires_all_three_matches():
    a = FakeResult(
        responders=[1, 2],
        onsets={1: 10, 2: 12},
        fingerprint=[0.0, 1.0, 2.0],
    )

    identical = FakeResult(
        responders=[1, 2],
        onsets={1: 10, 2: 12},
        fingerprint=[0.0, 1.0, 2.0],
    )

    report = exact_reproduction_against_a(
        a,
        identical,
        fingerprint_tolerance=1e-9,
    )

    assert report["exact_response_pattern_reproduction"]

    onset_changed = FakeResult(
        responders=[1, 2],
        onsets={1: 10, 2: 13},
        fingerprint=[0.0, 1.0, 2.0],
    )

    report = exact_reproduction_against_a(
        a,
        onset_changed,
        fingerprint_tolerance=1e-9,
    )

    assert not report["exact_response_pattern_reproduction"]
    assert not report["onset_vector_match"]

    fingerprint_changed = FakeResult(
        responders=[1, 2],
        onsets={1: 10, 2: 12},
        fingerprint=[0.0, 1.0, 2.01],
    )

    report = exact_reproduction_against_a(
        a,
        fingerprint_changed,
        fingerprint_tolerance=1e-9,
    )

    assert not report["exact_response_pattern_reproduction"]
    assert not report["fingerprint_match"]


def test_fingerprint_tolerance_boundary_counts_as_match():
    a = FakeResult(
        responders=[1],
        onsets={1: 10},
        fingerprint=[1.0],
    )

    candidate = FakeResult(
        responders=[1],
        onsets={1: 10},
        fingerprint=[1.0 + 1e-10],
    )

    report = exact_reproduction_against_a(
        a,
        candidate,
        fingerprint_tolerance=1e-9,
    )

    assert report["fingerprint_match"]
    assert report["exact_response_pattern_reproduction"]
