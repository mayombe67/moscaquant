from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy import sparse

from brain.hybrid_runtime import HybridRuntimeConfig


@dataclass(frozen=True)
class EdgeSwap:
    pre: int
    post: int
    baseline_weight: float
    counterfactual_weight: float


def run_batched_edge_swaps(
    matrix: sparse.csr_matrix,
    swaps: list[EdgeSwap],
    input_index: int,
    anchor_indices: np.ndarray,
    frames: int,
    stimulus_frame: int,
    stimulus_amplitude: float,
    config: HybridRuntimeConfig,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Execute independent single-edge counterfactuals in parallel columns.

    Column j is one independent neural simulation. Every column uses the same
    baseline sparse matrix. The one-edge counterfactual for that column is
    applied as an exact synaptic-current correction:

        delta_w * effective_activity[pre, j]

    added to post in that same column.

    Returns:
      anchor_traces: [frames, anchors, jobs]
      final_voltage: [neurons, jobs]
    """
    if not swaps:
        raise ValueError("at least one swap is required")

    matrix = matrix.tocsr()
    n = matrix.shape[0]
    jobs = len(swaps)

    voltage = np.zeros((n, jobs), dtype=np.float32)
    spikes = np.zeros((n, jobs), dtype=np.float32)

    decay = np.float32(np.exp(-config.dt_ms / config.tau_ms))
    threshold = np.float32(config.threshold)
    reset = np.float32(config.reset_voltage)

    pre_idx = np.asarray([s.pre for s in swaps], dtype=np.int64)
    post_idx = np.asarray([s.post for s in swaps], dtype=np.int64)
    delta = np.asarray(
        [s.counterfactual_weight - s.baseline_weight for s in swaps],
        dtype=np.float32,
    )
    cols = np.arange(jobs, dtype=np.int64)

    anchor_indices = np.asarray(anchor_indices, dtype=np.int64)
    traces = np.zeros(
        (frames, len(anchor_indices), jobs),
        dtype=np.float32,
    )

    for frame in range(frames):
        graded = np.clip(voltage, 0.0, threshold) / threshold
        activity = np.maximum(spikes, graded).astype(np.float32, copy=False)

        synaptic = np.asarray(matrix @ activity, dtype=np.float32)

        # Per-column exact one-edge replacement.
        synaptic[post_idx, cols] += delta * activity[pre_idx, cols]

        voltage *= decay
        voltage += synaptic

        if frame == stimulus_frame:
            voltage[input_index, :] += np.float32(stimulus_amplitude)

        fired = voltage >= threshold
        spikes.fill(0.0)
        spikes[fired] = 1.0
        voltage[fired] = reset

        traces[frame] = voltage[anchor_indices]

    return traces, voltage


def summarize_anchor_traces(
    traces: np.ndarray,
    anchor_labels: list[str],
) -> list[dict]:
    """
    Convert [frames, anchors, jobs] traces to one metrics dict per job.
    """
    if traces.ndim != 3:
        raise ValueError("expected [frames, anchors, jobs] traces")

    frames, anchors, jobs = traces.shape
    if anchors != len(anchor_labels):
        raise ValueError("anchor label count mismatch")

    results = []
    for j in range(jobs):
        metrics = {}
        for a, label in enumerate(anchor_labels):
            trace = traces[:, a, j]
            positive = np.flatnonzero(trace > 0)
            metrics[label] = {
                "first_positive_frame": int(positive[0]) if len(positive) else None,
                "peak_voltage": float(trace.max(initial=0.0)),
                "integrated_positive_voltage": float(
                    np.clip(trace, 0.0, None).sum()
                ),
            }
        results.append(metrics)

    return results
