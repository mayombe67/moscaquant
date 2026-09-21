from __future__ import annotations

import numpy as np
import pytest
from scipy import sparse

from brain import mq5_er3_retour_runner as retour


class FakeEligibility:
    def __init__(self, rejected):
        self.rejected = {
            (int(pre), int(post))
            for pre, post in rejected
        }
        self.canceled_candidate_checks = 0

    def keep_mask(
        self,
        *,
        post,
        pres,
        weights,
        eligible,
    ):
        del weights
        keep = np.ones(
            len(eligible),
            dtype=bool,
        )
        for i, local_idx in enumerate(
            eligible.tolist()
        ):
            edge = (
                int(pres[int(local_idx)]),
                int(post),
            )
            if edge in self.rejected:
                keep[i] = False
                self.canceled_candidate_checks += 1
        return keep


def make_graph():
    # row = postsynaptic, col = presynaptic
    matrix = sparse.lil_matrix(
        (8, 8),
        dtype=np.float32,
    )
    matrix[7, 1] = 2.0
    matrix[7, 2] = 1.5
    matrix[1, 3] = 1.0
    matrix[2, 4] = 1.0
    return matrix.tocsr()


def test_frozen_contract():
    assert retour.EXPERIMENT_ID == (
        "mq5-er3-retour-v1"
    )
    assert retour.CODENAME == "RETOUR"
    assert retour.FINANCIAL_SEMANTICS == (
        "NOT ASSIGNED"
    )
    assert retour.MAX_BACKWARD_HOPS == 3
    assert retour.TOP_K_PER_TARGET == 5
    assert retour.FOCUSED_MIN_TARGETS == 3


def test_frozen_target_sets():
    assert retour.AFFECTED_TARGETS == (
        55, 92, 656, 126002, 137122
    )
    assert retour.RETAINED_TARGETS == (
        51, 129, 317, 1273
    )


def test_canceled_candidate_is_not_emitted_but_ancestry_survives():
    graph = make_graph()
    divergence = np.ones(
        8,
        dtype=np.float64,
    )
    lesion = np.ones(
        8,
        dtype=np.float64,
    )

    result = retour.score_target_streaming(
        original=graph,
        lesioned_edges=set(),
        target=7,
        onset=0,
        divergence_snapshot=divergence,
        lesion_snapshot=lesion,
        eligibility_index=FakeEligibility(
            rejected={(1, 7)}
        ),
        max_backward_hops=2,
    )

    edges = {
        (
            row["presynaptic"],
            row["postsynaptic"],
        )
        for row in result["top_candidates"]
    }

    assert (1, 7) not in edges
    # Traversal still proceeds through node 1,
    # so its parent remains discoverable.
    assert (3, 1) in edges


def test_negative_controls_must_be_absent():
    by_target = {
        target: {
            "top_candidates": []
        }
        for target in retour.ALL_TRACE_TARGETS
    }
    retour.verify_negative_control_absence(
        by_target
    )

    by_target[55]["top_candidates"] = [
        {
            "presynaptic": retour.NO_SHOW[0],
            "postsynaptic": retour.NO_SHOW[1],
        }
    ]

    with pytest.raises(
        RuntimeError,
        match="THE NO-SHOW",
    ):
        retour.verify_negative_control_absence(
            by_target
        )


def test_retour_recurrence_classification():
    by_target = {
        target: {
            "top_candidates": []
        }
        for target in retour.ALL_TRACE_TARGETS
    }

    assert (
        retour.classify_family(by_target)
        == "NO_CLEAR_RETOUR_CANDIDATES"
    )

    edge = {
        "presynaptic": 10,
        "postsynaptic": 20,
    }

    for target in (55, 92):
        by_target[target][
            "top_candidates"
        ] = [
            {
                **edge,
                "target": target,
            }
        ]

    assert (
        retour.classify_family(by_target)
        == "DIFFUSE_RETOUR_CANDIDATES"
    )

    by_target[656][
        "top_candidates"
    ] = [
        {
            **edge,
            "target": 656,
        }
    ]

    assert (
        retour.classify_family(by_target)
        == "FOCUSED_RETOUR_CANDIDATES"
    )


def test_execution_gate_refuses_when_disabled():
    protocol = {
        "experiment_id": retour.EXPERIMENT_ID,
        "codename": retour.CODENAME,
        "financial_semantics": (
            retour.FINANCIAL_SEMANTICS
        ),
        "frames": 192,
        "max_backward_hops": 3,
        "top_k_per_target": 5,
        "result_execution_enabled": False,
        "affected_targets": list(
            retour.AFFECTED_TARGETS
        ),
        "retained_dependency_comparisons": list(
            retour.RETAINED_TARGETS
        ),
        "all_targets": list(
            retour.ALL_TRACE_TARGETS
        ),
        "classification": {
            "focused_min_recurrence_targets": 3,
            "focused_label": (
                "FOCUSED_RETOUR_CANDIDATES"
            ),
            "diffuse_label": (
                "DIFFUSE_RETOUR_CANDIDATES"
            ),
            "none_label": (
                "NO_CLEAR_RETOUR_CANDIDATES"
            ),
        },
    }

    with pytest.raises(
        RuntimeError,
        match="result_execution_enabled is false",
    ):
        retour.execution_gate(protocol)
