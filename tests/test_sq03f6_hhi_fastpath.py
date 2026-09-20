import random

import pytest

import brain.sq03f6_analyze as f6


def direct_hhi(sources, masks):
    counts = f6.participation_counts_from_masks(sources, masks)
    return f6.participation_mass_hhi(counts)


def test_fast_hhi_matches_direct_simple_case():
    masks = {
        "a": 0b0011,
        "b": 0b0110,
        "c": 0b0100,
    }
    sources = ["a", "b", "c"]
    assert f6.hhi_from_masks(sources, masks) == pytest.approx(
        direct_hhi(sources, masks)
    )


def test_fast_hhi_matches_direct_disjoint_case():
    masks = {
        "a": 0b0001,
        "b": 0b0010,
        "c": 0b0100,
        "d": 0b1000,
    }
    sources = list(masks)
    assert f6.hhi_from_masks(sources, masks) == pytest.approx(
        direct_hhi(sources, masks)
    )


def test_fast_hhi_matches_direct_fully_overlapping_case():
    masks = {
        "a": 0b1111,
        "b": 0b1111,
        "c": 0b1111,
    }
    sources = list(masks)
    assert f6.hhi_from_masks(sources, masks) == pytest.approx(
        direct_hhi(sources, masks)
    )


def test_fast_hhi_matches_direct_randomized_synthetic_cases():
    rng = random.Random(314159)

    for _ in range(100):
        source_count = rng.randint(2, 12)
        bit_count = rng.randint(8, 64)

        masks = {}
        for i in range(source_count):
            mask = 0
            for bit in range(bit_count):
                if rng.random() < 0.2:
                    mask |= 1 << bit
            if mask == 0:
                mask = 1 << rng.randrange(bit_count)
            masks[str(i)] = mask

        sources = list(masks)
        assert f6.hhi_from_masks(sources, masks) == pytest.approx(
            direct_hhi(sources, masks),
            rel=1e-12,
            abs=1e-15,
        )


def test_fast_hhi_rejects_empty_selection():
    with pytest.raises(ValueError, match="At least one source"):
        f6.hhi_from_masks([], {})


def test_fast_hhi_rejects_zero_mass():
    with pytest.raises(ValueError, match="No positive downstream participation mass"):
        f6.hhi_from_masks(["a", "b"], {"a": 0, "b": 0})
