from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib
import json

import numpy as np
from scipy import sparse
import pyarrow.feather as feather

from brain.hybrid_runtime import HybridRuntime, HybridRuntimeConfig


@dataclass(frozen=True)
class MatchedGraph:
    labels: tuple[str, ...]
    index: dict[str, int]
    male: sparse.csr_matrix
    female: sparse.csr_matrix
    edge_count: int
    scale: float


def load_protocol(path: Path) -> dict:
    cfg = json.loads(path.read_text())
    if cfg["sidequest_id"] != "SQ-03A":
        raise RuntimeError("Unexpected sidequest config")
    if cfg["status"] != "FROZEN_BEFORE_NEURAL_EXECUTION":
        raise RuntimeError("SQ-03A protocol is not frozen before execution")
    return cfg


def frozen_labels(protocol: dict) -> tuple[list[str], list[str]]:
    inputs = list(
        protocol["frozen_input_panel_rule"]["expected_labels_from_qualification"]
    )
    anchors = [x["label"] for x in protocol["frozen_output_anchors"]]
    if len(inputs) != len(set(inputs)):
        raise RuntimeError("Duplicate frozen input label")
    if len(anchors) != len(set(anchors)):
        raise RuntimeError("Duplicate frozen anchor label")
    return inputs, anchors


def build_matched_graph(feather_path: Path) -> MatchedGraph:
    table = feather.read_table(
        feather_path,
        columns=["pre", "post", "weight_m", "weight_f", "verdict_corr"],
    )

    pre = table["pre"].combine_chunks().to_pylist()
    post = table["post"].combine_chunks().to_pylist()
    wm = table["weight_m"].combine_chunks().to_pylist()
    wf = table["weight_f"].combine_chunks().to_pylist()
    verdict = table["verdict_corr"].combine_chunks().to_pylist()

    rows = []
    cols = []
    male_data = []
    female_data = []
    node_set: set[str] = set()

    accepted = []
    for a, b, m, f, v in zip(pre, post, wm, wf, verdict):
        if a is None or b is None:
            continue
        if v != "isomorphic" or m <= 0 or f <= 0:
            continue
        accepted.append((str(a), str(b), float(m), float(f)))
        node_set.add(str(a))
        node_set.add(str(b))

    labels = tuple(sorted(node_set))
    index = {label: i for i, label in enumerate(labels)}

    # HybridRuntime computes connectome @ presynaptic_activity.
    # Therefore matrix[row=post, col=pre] is the synaptic orientation.
    for a, b, m, f in accepted:
        rows.append(index[b])
        cols.append(index[a])
        male_data.append(m)
        female_data.append(f)

    shape = (len(labels), len(labels))
    male_raw = sparse.csr_matrix(
        (np.asarray(male_data, dtype=np.float32), (rows, cols)),
        shape=shape,
        dtype=np.float32,
    )
    female_raw = sparse.csr_matrix(
        (np.asarray(female_data, dtype=np.float32), (rows, cols)),
        shape=shape,
        dtype=np.float32,
    )

    male_rowsum = np.asarray(abs(male_raw).sum(axis=1)).ravel()
    female_rowsum = np.asarray(abs(female_raw).sum(axis=1)).ravel()
    scale = float(max(male_rowsum.max(initial=0.0), female_rowsum.max(initial=0.0)))
    if not np.isfinite(scale) or scale <= 0:
        raise RuntimeError("Invalid common structural normalization scale")

    male = (male_raw / np.float32(scale)).tocsr()
    female = (female_raw / np.float32(scale)).tocsr()

    if not np.array_equal(male.indptr, female.indptr):
        raise RuntimeError("Male/female sparsity row structure differs")
    if not np.array_equal(male.indices, female.indices):
        raise RuntimeError("Male/female sparsity column structure differs")

    return MatchedGraph(
        labels=labels,
        index=index,
        male=male,
        female=female,
        edge_count=len(accepted),
        scale=scale,
    )


def assert_frozen_labels_present(
    graph: MatchedGraph,
    input_labels: list[str],
    anchor_labels: list[str],
) -> None:
    missing_inputs = [x for x in input_labels if x not in graph.index]
    missing_anchors = [x for x in anchor_labels if x not in graph.index]
    if missing_inputs or missing_anchors:
        raise RuntimeError(
            f"Frozen-label resolution failed: inputs={missing_inputs} "
            f"anchors={missing_anchors}"
        )


def runtime_config_from_dict(cfg: dict) -> HybridRuntimeConfig:
    return HybridRuntimeConfig(
        dt_ms=float(cfg["dt_ms"]),
        tau_ms=float(cfg["tau_ms"]),
        threshold=float(cfg["threshold"]),
        reset_voltage=float(cfg["reset_voltage"]),
    )


def run_single(
    matrix: sparse.csr_matrix,
    graph: MatchedGraph,
    input_label: str,
    anchor_labels: list[str],
    frames: int,
    stimulus_frame: int,
    stimulus_amplitude: float,
    runtime_cfg: HybridRuntimeConfig,
) -> dict:
    if frames <= 0:
        raise ValueError("frames must be > 0")
    if not 0 <= stimulus_frame < frames:
        raise ValueError("stimulus frame outside run")

    runtime = HybridRuntime(matrix, config=runtime_cfg)
    input_idx = graph.index[input_label]
    anchor_idx = np.asarray([graph.index[x] for x in anchor_labels], dtype=np.int64)

    traces = np.zeros((frames, len(anchor_labels)), dtype=np.float32)

    for frame in range(frames):
        stimulus = None
        if frame == stimulus_frame:
            stimulus = np.zeros(len(graph.labels), dtype=np.float32)
            stimulus[input_idx] = np.float32(stimulus_amplitude)

        runtime.step(stimulus)
        traces[frame] = runtime.voltage[anchor_idx]

    metrics = {}
    for j, label in enumerate(anchor_labels):
        trace = traces[:, j]
        positive = np.flatnonzero(trace > 0)
        metrics[label] = {
            "first_positive_frame": int(positive[0]) if len(positive) else None,
            "peak_voltage": float(trace.max(initial=0.0)),
            "integrated_positive_voltage": float(np.clip(trace, 0.0, None).sum()),
            "trace": [float(x) for x in trace],
        }

    digest = hashlib.sha256(traces.tobytes()).hexdigest()

    return {
        "input_label": input_label,
        "frames": frames,
        "stimulus_frame": stimulus_frame,
        "stimulus_amplitude": stimulus_amplitude,
        "anchor_metrics": metrics,
        "trace_sha256": digest,
    }


def exact_replay_equal(a: dict, b: dict) -> bool:
    return a["trace_sha256"] == b["trace_sha256"] and a["anchor_metrics"] == b["anchor_metrics"]
