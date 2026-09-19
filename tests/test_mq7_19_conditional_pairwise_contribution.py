import math

from brain.mq7_19_conditional_pairwise_contribution import (
    PAIRS,
    UNIQUE_TARGETS,
    conditional_fraction,
)


def test_frozen_pair_set():
    assert PAIRS == (
        (62598, 77298),
        (62598, 79672),
        (79672, 77298),
    )


def test_unique_target_set():
    assert UNIQUE_TARGETS == (
        62598,
        77298,
        79672,
    )


def test_conditional_fraction_independent_case():
    a = 0.30
    b = 0.20
    ab = 1.0 - ((1.0 - a) * (1.0 - b))

    assert math.isclose(
        conditional_fraction(
            pair_attenuation=ab,
            conditioning_attenuation=a,
        ),
        b,
    )


def test_conditional_fraction_positive_gain_case():
    a = 0.30
    b = 0.20
    observed = 0.48

    value = conditional_fraction(
        pair_attenuation=observed,
        conditioning_attenuation=a,
    )

    assert value > b
