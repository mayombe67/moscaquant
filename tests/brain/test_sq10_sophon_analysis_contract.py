from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

CONTRACT = (
    ROOT
    / "config/experiments/"
    "sq10-sophon-analysis-contract-draft-v1.json"
)


def load():
    return json.loads(
        CONTRACT.read_text()
    )


def test_execution_is_not_authorized():
    d = load()

    assert (
        d["neural_execution_authorized"]
        is False
    )


def test_exactly_12_matched_contrasts():
    d = load()

    contrasts = d["matched_contrasts"]

    assert len(contrasts) == 12

    assert len({
        (
            row["body"],
            row["retained"],
            row["lesioned"],
        )
        for row in contrasts
    }) == 12


def test_each_contrast_changes_only_tested_bit():
    d = load()

    bit_by_body = {
        "A": 0,
        "B": 1,
        "C": 2,
    }

    for row in d["matched_contrasts"]:
        retained = row["retained"]
        lesioned = row["lesioned"]
        bit = bit_by_body[
            row["body"]
        ]

        differing = [
            i
            for i, (a, b)
            in enumerate(
                zip(
                    retained,
                    lesioned,
                )
            )
            if a != b
        ]

        assert differing == [bit]
        assert retained[bit] == "0"
        assert lesioned[bit] == "1"


def test_each_body_has_all_four_backgrounds():
    d = load()

    contrasts = d["matched_contrasts"]

    for body in ("A", "B", "C"):
        rows = [
            row
            for row in contrasts
            if row["body"] == body
        ]

        assert len(rows) == 4


def test_primary_test_uses_p2_and_p5():
    d = load()

    primary = d["primary_test"]

    assert primary["phase"] == "P5"

    assert (
        primary[
            "source_invariance_requirement"
        ]["phase"]
        == "P2"
    )


def test_numerical_tolerance_is_not_yet_selectable():
    d = load()

    numerical = d[
        "primary_test"
    ][
        "numerical_acceptance"
    ]

    assert (
        numerical["status"]
        == "PENDING_SYNTHETIC_FLOAT32_CALIBRATION"
    )

    assert (
        numerical["absolute_tolerance"]
        is None
    )

    assert (
        numerical["relative_tolerance"]
        is None
    )

    assert (
        numerical[
            "calibration_must_precede_neural_execution"
        ]
        is True
    )


def test_no_post_result_selection():
    d = load()

    integrity = d["integrity"]

    assert (
        integrity[
            "all_12_matched_contrasts_required"
        ]
        is True
    )

    assert (
        integrity[
            "post_result_contrast_selection_forbidden"
        ]
        is True
    )

    assert (
        integrity[
            "post_result_tolerance_selection_forbidden"
        ]
        is True
    )
