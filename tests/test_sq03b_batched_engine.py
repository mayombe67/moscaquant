import numpy as np
from scipy import sparse

from brain.hybrid_runtime import HybridRuntime, HybridRuntimeConfig
from brain.sq03b_batched_engine import EdgeSwap, run_batched_edge_swaps


def scalar_run(matrix, input_index, anchors, frames, amp, cfg):
    rt = HybridRuntime(matrix, config=cfg)
    traces = np.zeros((frames, len(anchors)), dtype=np.float32)
    for f in range(frames):
        stim = None
        if f == 0:
            stim = np.zeros(matrix.shape[0], dtype=np.float32)
            stim[input_index] = np.float32(amp)
        rt.step(stim)
        traces[f] = rt.voltage[anchors]
    return traces


def fixture():
    # A -> B -> C and A -> C.
    # Matrix orientation is [post, pre].
    matrix = sparse.csr_matrix(
        (
            np.asarray([0.2, 0.3, 0.1], dtype=np.float32),
            (
                np.asarray([1, 2, 2]),
                np.asarray([0, 1, 0]),
            ),
        ),
        shape=(3, 3),
        dtype=np.float32,
    )
    return matrix


def test_single_batched_swap_matches_scalar_matrix_replacement_exactly():
    matrix = fixture()
    cfg = HybridRuntimeConfig()
    swap = EdgeSwap(pre=0, post=1, baseline_weight=0.2, counterfactual_weight=0.4)

    batched, _ = run_batched_edge_swaps(
        matrix, [swap], 0, np.asarray([1, 2]), 8, 0, 0.5, cfg
    )

    altered = matrix.copy().tolil()
    altered[1, 0] = np.float32(0.4)
    altered = altered.tocsr()

    scalar = scalar_run(altered, 0, np.asarray([1, 2]), 8, 0.5, cfg)
    assert np.allclose(
        batched[:, :, 0],
        scalar,
        rtol=1e-6,
        atol=1e-7,
    )


def test_two_independent_swaps_match_two_scalar_runs():
    matrix = fixture()
    cfg = HybridRuntimeConfig()
    swaps = [
        EdgeSwap(pre=0, post=1, baseline_weight=0.2, counterfactual_weight=0.4),
        EdgeSwap(pre=0, post=2, baseline_weight=0.1, counterfactual_weight=0.25),
    ]

    batched, _ = run_batched_edge_swaps(
        matrix, swaps, 0, np.asarray([1, 2]), 8, 0, 0.5, cfg
    )

    for j, (post, value) in enumerate(((1, 0.4), (2, 0.25))):
        altered = matrix.copy().tolil()
        altered[post, 0] = np.float32(value)
        altered = altered.tocsr()
        scalar = scalar_run(altered, 0, np.asarray([1, 2]), 8, 0.5, cfg)
        assert np.allclose(
            batched[:, :, j],
            scalar,
            rtol=1e-6,
            atol=1e-7,
        )


def test_batched_replay_is_exact():
    matrix = fixture()
    cfg = HybridRuntimeConfig()
    swaps = [
        EdgeSwap(pre=0, post=1, baseline_weight=0.2, counterfactual_weight=0.4),
        EdgeSwap(pre=0, post=2, baseline_weight=0.1, counterfactual_weight=0.25),
    ]
    kwargs = dict(
        matrix=matrix,
        swaps=swaps,
        input_index=0,
        anchor_indices=np.asarray([1, 2]),
        frames=8,
        stimulus_frame=0,
        stimulus_amplitude=0.5,
        config=cfg,
    )
    a, _ = run_batched_edge_swaps(**kwargs)
    b, _ = run_batched_edge_swaps(**kwargs)
    assert np.array_equal(a, b)
