from __future__ import annotations

import numpy as np
import pytest

from oracle.d6_darkness import (
    DARKNESS_VERSION,
    DEFAULT_DURATION_TRANSITIONS,
    DEFAULT_RETAINED_AMPLITUDE,
    DarknessError,
    apply_darkness,
    build_darkness,
    is_darkness_active,
)
from oracle.reinforcement import ReinforcementCondition


def test_darkness_defaults_are_frozen():
    intervention = build_darkness(
        current_generation=5,
    )

    assert intervention.schema_version == DARKNESS_VERSION

    assert (
        intervention.condition
        is ReinforcementCondition.SC_02_DARKNESS
    )

    assert (
        intervention.retained_amplitude
        == DEFAULT_RETAINED_AMPLITUDE
        == 0.25
    )

    assert (
        intervention.duration_transitions
        == DEFAULT_DURATION_TRANSITIONS
        == 10
    )


def test_darkness_window_is_exact():
    intervention = build_darkness(
        current_generation=5,
    )

    assert not is_darkness_active(
        intervention,
        generation=4,
    )

    assert is_darkness_active(
        intervention,
        generation=5,
    )

    assert is_darkness_active(
        intervention,
        generation=14,
    )

    assert not is_darkness_active(
        intervention,
        generation=15,
    )


def test_darkness_retains_exactly_quarter_amplitude():
    stimulus = np.asarray(
        [0.0, 1.0, 2.0, 4.0],
        dtype=np.float32,
    )

    intervention = build_darkness(
        current_generation=0,
    )

    transformed = apply_darkness(
        stimulus=stimulus,
        intervention=intervention,
        generation=0,
    )

    np.testing.assert_allclose(
        transformed,
        stimulus * 0.25,
    )


def test_darkness_preserves_spatial_pattern():
    stimulus = np.asarray(
        [1.0, 2.0, 4.0, 8.0],
        dtype=np.float32,
    )

    intervention = build_darkness(
        current_generation=0,
    )

    transformed = apply_darkness(
        stimulus=stimulus,
        intervention=intervention,
        generation=0,
    )

    original_ratio = stimulus / stimulus.sum()
    transformed_ratio = transformed / transformed.sum()

    np.testing.assert_allclose(
        transformed_ratio,
        original_ratio,
    )


def test_darkness_does_not_modify_original_stimulus():
    stimulus = np.asarray(
        [1.0, 2.0, 3.0],
        dtype=np.float32,
    )

    original = stimulus.copy()

    intervention = build_darkness(
        current_generation=0,
    )

    transformed = apply_darkness(
        stimulus=stimulus,
        intervention=intervention,
        generation=0,
    )

    np.testing.assert_array_equal(
        stimulus,
        original,
    )

    assert transformed is not stimulus


def test_darkness_recovers_immediately():
    stimulus = np.asarray(
        [1.0, 2.0, 3.0],
        dtype=np.float32,
    )

    intervention = build_darkness(
        current_generation=0,
    )

    transformed = apply_darkness(
        stimulus=stimulus,
        intervention=intervention,
        generation=10,
    )

    np.testing.assert_array_equal(
        transformed,
        stimulus,
    )


def test_darkness_rejects_non_finite_stimulus():
    intervention = build_darkness(
        current_generation=0,
    )

    stimulus = np.asarray(
        [1.0, np.nan],
        dtype=np.float32,
    )

    with pytest.raises(
        DarknessError,
        match="non-finite",
    ):
        apply_darkness(
            stimulus=stimulus,
            intervention=intervention,
            generation=0,
        )
