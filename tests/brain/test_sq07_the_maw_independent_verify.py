from pathlib import Path

from brain import (
    sq07_the_maw_independent_verify as v,
)


ROOT = Path(__file__).resolve().parents[2]


def test_verifier_is_independent_of_analysis_classifier():
    source = (
        ROOT
        / "brain/sq07_the_maw_independent_verify.py"
    ).read_text(encoding="utf-8")

    assert "from brain.sq07_the_maw_analysis" not in source
    assert "import brain.sq07_the_maw_analysis" not in source

    assert "from brain.sq06_silent_cartographer_runner" not in source

    assert "def symmetric_normalized_l2" in source
    assert "def classify" in source
    assert "def minimal_full13" in source


def test_independent_classifier():
    import numpy as np

    intact = np.zeros(
        (4, 5),
        dtype=np.float32,
    )

    full13 = np.ones(
        (4, 5),
        dtype=np.float32,
    )

    middle = np.full(
        (4, 5),
        0.5,
        dtype=np.float32,
    )

    assert (
        v.classify(
            intact,
            intact,
            full13,
        )
        == "EXACT_INTACT"
    )

    assert (
        v.classify(
            full13,
            intact,
            full13,
        )
        == "EXACT_FULL13"
    )

    assert (
        v.classify(
            middle,
            intact,
            full13,
        )
        == "INTERMEDIATE"
    )


def test_independent_minimality_checks_strict_submasks():
    lower = "0000000000001"
    upper = "0000000000111"

    assert (
        v.minimal_full13(
            {lower, upper}
        )
        == [lower]
    )


def test_inactive_universes_are_frozen():
    assert len(
        v.inactive_masks("LR")
    ) == 8

    assert len(
        v.inactive_masks("RL")
    ) == 1024

    assert (
        v.RL_GROUP
        in v.inactive_masks("LR")
    )

    assert (
        v.LR_GROUP
        in v.inactive_masks("RL")
    )
