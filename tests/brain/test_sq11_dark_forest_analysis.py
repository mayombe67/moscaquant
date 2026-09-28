from __future__ import annotations

import numpy as np

from brain.sq11_dark_forest_analysis import (
    classify_contrast,
)


def test_exact_float32_direct_term():
    classification, residual = (
        classify_contrast(
            divergence_exists=True,
            body_source_exact=True,
            row_source_exact=True,
            runtime_delta=np.float64(
                1.25
            ),
            direct_term_f32=np.float32(
                1.25
            ),
        )
    )

    assert (
        classification
        == "DIRECT_TERM_EXACT_FLOAT32"
    )

    assert residual == 0.0


def test_float32_rounding_path():
    classification, residual = (
        classify_contrast(
            divergence_exists=True,
            body_source_exact=True,
            row_source_exact=True,
            runtime_delta=np.float64(
                1.2500001
            ),
            direct_term_f32=np.float32(
                1.25
            ),
        )
    )

    assert (
        classification
        == (
            "DIRECT_TERM_WITH_"
            "FLOAT32_ROUNDING_PATH"
        )
    )

    assert residual != 0.0


def test_source_divergence_wins():
    classification, residual = (
        classify_contrast(
            divergence_exists=True,
            body_source_exact=False,
            row_source_exact=True,
            runtime_delta=np.float64(
                1.0
            ),
            direct_term_f32=np.float32(
                1.0
            ),
        )
    )

    assert (
        classification
        == (
            "SOURCE_STATE_DIVERGES_"
            "BEFORE_OR_AT_P3"
        )
    )

    assert residual is None


def test_no_p3_divergence():
    classification, residual = (
        classify_contrast(
            divergence_exists=False,
            body_source_exact=True,
            row_source_exact=True,
            runtime_delta=None,
            direct_term_f32=None,
        )
    )

    assert (
        classification
        == "NO_P3_DIVERGENCE"
    )

    assert residual is None
