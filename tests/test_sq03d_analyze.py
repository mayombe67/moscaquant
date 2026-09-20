from brain.sq03d_analyze import (
    first_positive_relation,
    normalized_asymmetry,
    pair_metrics,
    sign_relation,
)


def test_exact_reciprocity_has_zero_residual_and_asymmetry():
    got = pair_metrics(3.0, -3.0)
    assert got["context_residual"] == 0.0
    assert got["normalized_asymmetry"] == 0.0
    assert got["sign_relation"] == "OPPOSITE"


def test_same_direction_is_maximally_asymmetric():
    got = pair_metrics(2.0, 3.0)
    assert got["context_residual"] == 5.0
    assert got["normalized_asymmetry"] == 1.0
    assert got["sign_relation"] == "SAME"


def test_unequal_opposite_direction_has_partial_asymmetry():
    got = pair_metrics(4.0, -1.0)
    assert got["context_residual"] == 3.0
    assert got["total_effect_magnitude"] == 5.0
    assert got["normalized_asymmetry"] == 0.6


def test_double_zero_is_defined_as_zero_asymmetry():
    assert normalized_asymmetry(0.0, 0.0) == 0.0
    assert sign_relation(0.0, 0.0) == "ZERO_INVOLVED"


def test_first_positive_relation_preserves_null():
    assert first_positive_relation(None, None) == "BOTH_NULL"
    assert first_positive_relation(2, -2) == "RECIPROCAL_EXACT"
    assert first_positive_relation(2, 2) == "SAME_EXACT"


def test_noncomparable_first_positive_relation():
    assert first_positive_relation("one_only", 0) == "NONCOMPARABLE"
