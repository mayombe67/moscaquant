import numpy as np

from brain.sq12_resonance_cascade_gate import (
    mismatch_report,
)


def test_gate_report_closed():
    zero = np.zeros(
        (192, 3),
        dtype=np.uint8,
    )

    canonical = {
        mask: zero.copy()
        for mask in (
            "000",
            "001",
            "010",
            "011",
            "100",
            "101",
            "110",
            "111",
        )
    }

    report = mismatch_report(
        canonical
    )

    assert (
        report[
            "all_masks_exact_to_000"
        ]
        is True
    )

    assert (
        report[
            "total_mismatches_vs_000"
        ]
        == 0
    )


def test_gate_report_detects_open_path():
    zero = np.zeros(
        (192, 3),
        dtype=np.uint8,
    )

    canonical = {
        mask: zero.copy()
        for mask in (
            "000",
            "001",
            "010",
            "011",
            "100",
            "101",
            "110",
            "111",
        )
    }

    canonical["010"][125, 1] = 1

    report = mismatch_report(
        canonical
    )

    assert (
        report[
            "all_masks_exact_to_000"
        ]
        is False
    )

    assert (
        report["by_mask"]["010"][
            "first_mismatch"
        ]
        == {
            "frame": 125,
            "body_position": 1,
        }
    )
