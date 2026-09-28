from __future__ import annotations

import numpy as np
import pytest
from scipy import sparse

from brain.sq08_three_body_episode import (
    BODY_EDGE_INDICES,
    RESULT_KEYS,
    build_body_lesion,
    selected_body_edges,
    validate_condition,
)


def test_body_edge_indices_are_frozen():
    assert BODY_EDGE_INDICES == (
        10,
        11,
        12,
    )


def test_mask_zero_means_retained():
    assert selected_body_edges("000") == ()


def test_mask_one_means_zeroed():
    selected = selected_body_edges("101")

    assert [
        (int(pre), int(post))
        for pre, post, _weight in selected
    ] == [
        (65084, 137122),
        (135589, 126002),
    ]


def test_full_mask_selects_exact_three_body_core():
    selected = selected_body_edges("111")

    assert [
        (int(pre), int(post))
        for pre, post, _weight in selected
    ] == [
        (65084, 137122),
        (128590, 317),
        (135589, 126002),
    ]


def test_condition_contract_requires_explicit_lesion_coordinates():
    condition = {
        "ordinal": 10,
        "condition_id": "sq08:101:r1",
        "mask": "101",
        "replicate": 1,
        "edge_zeroed": {
            "A": 1,
            "B": 0,
            "C": 1,
        },
    }

    assert validate_condition(
        condition
    ) == condition


def test_condition_refuses_semantic_drift():
    condition = {
        "ordinal": 10,
        "condition_id": "sq08:101:r1",
        "mask": "101",
        "replicate": 1,
        "edge_zeroed": {
            "A": 0,
            "B": 1,
            "C": 0,
        },
    }

    with pytest.raises(ValueError):
        validate_condition(condition)


def test_episode_result_contract_contains_mechanistic_arrays():
    assert "body_responder_voltage" in RESULT_KEYS
    assert "body_responder_spikes" in RESULT_KEYS
    assert "frontier_voltage" in RESULT_KEYS
    assert "frontier_spikes" in RESULT_KEYS
