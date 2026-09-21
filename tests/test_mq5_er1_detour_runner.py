from __future__ import annotations

import numpy as np
from scipy import sparse

from brain.mq5_er1_detour_runner import (
    _push_top_candidate,
    classify_family,
    score_target_streaming,
)


def test_factorized_edge_score_matches_explicit_time_series():
    weight = -0.5
    a = np.asarray([0.0, 0.2, 0.4, 0.1])
    c = np.asarray([0.0, 0.5, 0.1, 0.3])
    lesion = np.asarray([0.0, 0.25, 0.2, 0.1])

    explicit_divergence = np.abs(
        weight * c - weight * a
    ).sum()
    explicit_persistence = np.abs(
        weight * lesion
    ).sum()

    factorized_divergence = (
        abs(weight) * np.abs(c - a).sum()
    )
    factorized_persistence = (
        abs(weight) * np.abs(lesion).sum()
    )

    assert np.isclose(
        explicit_divergence,
        factorized_divergence,
    )
    assert np.isclose(
        explicit_persistence,
        factorized_persistence,
    )
    assert np.isclose(
        explicit_divergence * explicit_persistence,
        factorized_divergence * factorized_persistence,
    )


def test_streaming_score_zeroes_frozen_lesioned_edge():
    matrix = np.zeros((4, 4), dtype=np.float32)
    matrix[3, 1] = 0.5
    matrix[3, 2] = 0.25
    csr = sparse.csr_matrix(matrix)

    divergence = np.asarray(
        [0.0, 2.0, 1.0, 0.0],
        dtype=np.float64,
    )
    persistence = np.asarray(
        [0.0, 2.0, 2.0, 0.0],
        dtype=np.float64,
    )

    result = score_target_streaming(
        original=csr,
        lesioned_edges={(1, 3)},
        target=3,
        onset=2,
        divergence_snapshot=divergence,
        lesion_snapshot=persistence,
    )

    edges = {
        (
            row["presynaptic"],
            row["postsynaptic"],
        )
        for row in result["top_candidates"]
    }

    assert (1, 3) not in edges
    assert (2, 3) in edges


def test_heap_tie_order_prefers_nearer_then_lower_post_then_lower_pre():
    heap = []

    rows = [
        {
            "score": 1.0,
            "hop_from_target": 2,
            "postsynaptic": 9,
            "presynaptic": 7,
        },
        {
            "score": 1.0,
            "hop_from_target": 1,
            "postsynaptic": 9,
            "presynaptic": 8,
        },
        {
            "score": 1.0,
            "hop_from_target": 1,
            "postsynaptic": 8,
            "presynaptic": 9,
        },
        {
            "score": 1.0,
            "hop_from_target": 1,
            "postsynaptic": 8,
            "presynaptic": 3,
        },
    ]

    for row in rows:
        row = {
            "target": 55,
            "onset_frame": 1,
            "encoding_divergence_l1": 1.0,
            "lesion_persistence_l1": 1.0,
            **row,
        }
        _push_top_candidate(heap, row)

    ordered = [item[1] for item in heap]
    ordered.sort(
        key=lambda row: (
            -row["score"],
            row["hop_from_target"],
            row["postsynaptic"],
            row["presynaptic"],
        )
    )

    assert [
        (
            r["hop_from_target"],
            r["postsynaptic"],
            r["presynaptic"],
        )
        for r in ordered
    ] == [
        (1, 8, 3),
        (1, 8, 9),
        (1, 9, 8),
        (2, 9, 7),
    ]


def test_classification_focused_only_on_three_target_edge_recurrence():
    shared = {
        "presynaptic": 7,
        "postsynaptic": 8,
        "score": 1.0,
        "hop_from_target": 1,
        "onset_frame": 1,
        "encoding_divergence_l1": 1.0,
        "lesion_persistence_l1": 1.0,
    }

    by_target = {}
    for target in [55, 92, 656, 126002, 137122]:
        rows = []
        if target in {55, 92, 656}:
            rows.append({"target": target, **shared})
        by_target[target] = {
            "top_candidates": rows,
        }

    assert classify_family(by_target) == "FOCUSED_DETOUR_CANDIDATES"
