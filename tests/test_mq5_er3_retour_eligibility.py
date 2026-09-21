from __future__ import annotations

import numpy as np
import pytest
from scipy import sparse

from brain import mq5_er3_retour_eligibility as retour


class FakeRuntime:
    def __init__(self, retinal_indices, relay_indices, relay_from_retina):
        self.retinal_indices = np.asarray(retinal_indices, dtype=np.int32)
        self.relay_indices = np.asarray(relay_indices, dtype=np.int32)
        self.relay_from_retina = np.asarray(
            relay_from_retina,
            dtype=np.float32,
        )


def matrix_with_edge(pre, post, weight, n=8):
    matrix = sparse.lil_matrix((n, n), dtype=np.float32)
    matrix[post, pre] = weight
    return matrix.tocsr()


def test_non_retina_relay_edge_is_intervention_addressable():
    original = matrix_with_edge(1, 4, -0.25)
    runtime = FakeRuntime(
        retinal_indices=[2],
        relay_indices=[4],
        relay_from_retina=[[-0.25]],
    )

    row = retour.classify_edge(
        original=original,
        runtime=runtime,
        pre=1,
        post=4,
        rtol=1e-6,
        atol=1e-12,
    )

    assert row["status"] == retour.ELIGIBLE
    assert row["relay_weight"] is None


def test_exact_retina_relay_duplicate_is_canceled():
    original = matrix_with_edge(2, 4, -0.25)
    runtime = FakeRuntime(
        retinal_indices=[2],
        relay_indices=[4],
        relay_from_retina=[[-0.25]],
    )

    row = retour.classify_edge(
        original=original,
        runtime=runtime,
        pre=2,
        post=4,
        rtol=1e-6,
        atol=1e-12,
    )

    assert row["status"] == retour.CANCELED
    assert row["pre_in_retina"] is True
    assert row["post_in_relay"] is True
    assert row["weight_delta"] == pytest.approx(0.0)


def test_retina_relay_representation_mismatch_aborts():
    original = matrix_with_edge(2, 4, -0.25)
    runtime = FakeRuntime(
        retinal_indices=[2],
        relay_indices=[4],
        relay_from_retina=[[-0.20]],
    )

    with pytest.raises(RuntimeError, match="representation mismatch"):
        retour.classify_edge(
            original=original,
            runtime=runtime,
            pre=2,
            post=4,
            rtol=1e-6,
            atol=1e-12,
        )


def test_frozen_negative_control_ids():
    assert retour.NO_SHOW == (116680, 12024)
    assert retour.MATCHED_CONTROL == (78481, 16087)
    assert retour.CANCELED == (
        "DETERMINISTICALLY_CANCELED_RETINA_RELAY"
    )
