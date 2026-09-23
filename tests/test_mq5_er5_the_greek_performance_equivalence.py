from __future__ import annotations

import numpy as np
from scipy import sparse

from brain import mq5_er5_the_greek_runner as greek


def _matrix(seed: int, n: int = 10) -> sparse.csr_matrix:
    rng = np.random.default_rng(seed)
    dense = (rng.random((n, n)) < 0.24).astype(np.float64)
    np.fill_diagonal(dense, 0.0)
    return sparse.csr_matrix(dense)


def test_cached_first_hops_matches_frozen_reference_exhaustively_on_small_graphs():
    for seed in range(12):
        graph = _matrix(seed)
        targets = tuple(range(graph.shape[0]))

        for max_hops in (1, 2, 3):
            csc, to_target, branch_masks = greek.build_first_hop_cache(
                graph,
                targets,
                max_hops,
            )

            for candidate in range(graph.shape[0]):
                for target in targets:
                    expected = greek.shortest_path_first_hops(
                        graph,
                        candidate,
                        target,
                        max_hops,
                    )
                    actual = greek.shortest_path_first_hops_cached(
                        csc,
                        candidate,
                        target,
                        to_target=to_target,
                        branch_masks=branch_masks,
                    )
                    assert actual == expected, (
                        seed,
                        max_hops,
                        candidate,
                        target,
                        expected,
                        actual,
                    )


def test_cached_path_does_not_call_frozen_reference(monkeypatch):
    graph = _matrix(999)
    targets = tuple(range(graph.shape[0]))
    csc, to_target, branch_masks = greek.build_first_hop_cache(
        graph,
        targets,
        3,
    )

    def forbidden(*args, **kwargs):
        raise AssertionError("frozen reference path was invoked")

    monkeypatch.setattr(greek, "shortest_path_first_hops", forbidden)

    greek.shortest_path_first_hops_cached(
        csc,
        0,
        1,
        to_target=to_target,
        branch_masks=branch_masks,
    )
