import json
from pathlib import Path

import numpy as np
from scipy import sparse

from brain.hybrid_runtime import HybridRuntimeConfig
from brain.sq03a_matched_runtime import (
    MatchedGraph,
    exact_replay_equal,
    frozen_labels,
    load_protocol,
    run_single,
)

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "config" / "experiments" / "sq03a_other_fly_v1.json"
SMOKE = ROOT / "config" / "experiments" / "sq03a_smoke_v1.json"


def tiny_graph():
    labels = ("A", "B", "C")
    index = {x: i for i, x in enumerate(labels)}

    # row=post, col=pre:
    # A -> B, B -> C
    matrix = sparse.csr_matrix(
        (
            np.asarray([0.5, 0.5], dtype=np.float32),
            (
                np.asarray([1, 2]),
                np.asarray([0, 1]),
            ),
        ),
        shape=(3, 3),
        dtype=np.float32,
    )
    return MatchedGraph(
        labels=labels,
        index=index,
        male=matrix,
        female=matrix.copy(),
        edge_count=2,
        scale=1.0,
    )


def test_frozen_protocol_labels_are_exact():
    protocol = load_protocol(PROTOCOL)
    inputs, anchors = frozen_labels(protocol)
    assert len(inputs) == 12
    assert set(anchors) == {"DNc02", "DNp27", "DNp30"}
    assert "TmY14" in inputs


def test_smoke_is_explicitly_non_authoritative():
    cfg = json.loads(SMOKE.read_text())
    assert cfg["status"] == "ENGINEERING_SMOKE_ONLY"
    assert cfg["authoritative_result"] is False
    assert "not an SQ-03A scientific result" in cfg["claim_boundary"]


def test_matrix_orientation_propagates_pre_to_post():
    graph = tiny_graph()
    cfg = HybridRuntimeConfig(
        dt_ms=1.0,
        tau_ms=20.0,
        threshold=1.0,
        reset_voltage=0.0,
    )
    result = run_single(
        graph.male,
        graph,
        input_label="A",
        anchor_labels=["B", "C"],
        frames=4,
        stimulus_frame=0,
        stimulus_amplitude=0.5,
        runtime_cfg=cfg,
    )
    # Stimulus enters A at frame 0. B must become positive later.
    assert result["anchor_metrics"]["B"]["first_positive_frame"] is not None


def test_exact_replay_is_bitwise_stable_on_fixture():
    graph = tiny_graph()
    cfg = HybridRuntimeConfig()
    kwargs = dict(
        matrix=graph.male,
        graph=graph,
        input_label="A",
        anchor_labels=["B", "C"],
        frames=8,
        stimulus_frame=0,
        stimulus_amplitude=0.5,
        runtime_cfg=cfg,
    )
    a = run_single(**kwargs)
    b = run_single(**kwargs)
    assert exact_replay_equal(a, b)


def test_male_female_identity_when_weights_identical():
    graph = tiny_graph()
    cfg = HybridRuntimeConfig()
    common = dict(
        graph=graph,
        input_label="A",
        anchor_labels=["B", "C"],
        frames=8,
        stimulus_frame=0,
        stimulus_amplitude=0.5,
        runtime_cfg=cfg,
    )
    male = run_single(matrix=graph.male, **common)
    female = run_single(matrix=graph.female, **common)
    assert exact_replay_equal(male, female)
