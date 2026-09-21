from __future__ import annotations

import json

import pytest

from brain.mq5_ts_duplicate_replay import (
    canonical_payload,
    exact_duplicate_report,
)


def test_canonical_payload_is_key_order_independent():
    a = {
        "z": 3,
        "a": {
            "b": 2,
            "a": 1,
        },
    }

    b = {
        "a": {
            "a": 1,
            "b": 2,
        },
        "z": 3,
    }

    assert canonical_payload(a) == canonical_payload(b)


def test_exact_duplicate_report_accepts_identical_payloads():
    first = {
        "voltage": [
            [0.0, 0.1],
            [0.2, 0.3],
        ],
        "onsets": {
            "1": 1,
            "2": 2,
        },
    }

    second = json.loads(
        json.dumps(first)
    )

    report = exact_duplicate_report(
        first,
        second,
    )

    assert report["exact_payload_equal"]
    assert (
        report["first_sha256"]
        == report["second_sha256"]
    )
    assert (
        report["first_size_bytes"]
        == report["second_size_bytes"]
    )


def test_exact_duplicate_report_detects_single_float_change():
    first = {
        "voltage": [
            0.1,
            0.2,
        ]
    }

    second = {
        "voltage": [
            0.1,
            0.2000000001,
        ]
    }

    report = exact_duplicate_report(
        first,
        second,
    )

    assert not report["exact_payload_equal"]
    assert (
        report["first_sha256"]
        != report["second_sha256"]
    )


def test_canonical_payload_rejects_nan():
    with pytest.raises(
        ValueError
    ):
        canonical_payload(
            {
                "x": float("nan")
            }
        )
