from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from scipy import sparse

import brain.sq07_the_maw_episode as e


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "brain/sq07_the_maw_episode.py"


def fake_result(value: float = 0.0) -> dict:
    return {
        "positive_voltage": np.full(
            (192, 1191),
            value,
            dtype=np.float32,
        ),
        "spikes": np.zeros(
            (192, 1191),
            dtype=np.uint8,
        ),
        "channel_mean_positive_voltage": np.full(
            (3, 192),
            value,
            dtype=np.float64,
        ),
        "channel_positive_fraction": np.zeros(
            (3, 192),
            dtype=np.float64,
        ),
        "channel_spike_count": np.zeros(
            (3, 192),
            dtype=np.int32,
        ),
        "channel_spike_rate": np.zeros(
            (3, 192),
            dtype=np.float64,
        ),
    }


def condition(mask13="0000000000000", layout="LR", replicate=1):
    ordinal = (
        int(mask13, 2) * 4
        + (0 if layout == "LR" else 2)
        + replicate - 1
    )

    return {
        "ordinal": ordinal,
        "condition_id": f"sq07:{mask13}:{layout}:r{replicate}",
        "mask13": mask13,
        "layout": layout,
        "replicate": replicate,
    }


def test_condition_coordinates_reproduce_planner_order():
    assert e.expected_ordinal("0000000000000", "LR", 1) == 0
    assert e.expected_ordinal("0000000000000", "LR", 2) == 1
    assert e.expected_ordinal("0000000000000", "RL", 1) == 2
    assert e.expected_ordinal("0000000000000", "RL", 2) == 3

    assert e.expected_ordinal("0000000000001", "LR", 1) == 4
    assert e.expected_ordinal("1111111111111", "RL", 2) == 32767


def test_condition_identity_validation_is_fail_closed():
    good = condition(
        mask13="0101010101010",
        layout="RL",
        replicate=2,
    )

    assert e.validate_condition(good) == good

    bad = dict(good)
    bad["ordinal"] += 1

    with pytest.raises(ValueError, match="ordinal mismatch"):
        e.validate_condition(bad)

    bad = dict(good)
    bad["condition_id"] = "wrong"

    with pytest.raises(ValueError, match="ID mismatch"):
        e.validate_condition(bad)


def test_episode_result_contract_accepts_exact_frozen_shapes_and_dtypes():
    e.validate_episode_result(fake_result())


def test_episode_result_contract_rejects_shape_drift():
    result = fake_result()
    result["positive_voltage"] = np.zeros(
        (191, 1191),
        dtype=np.float32,
    )

    with pytest.raises(e.Refusal, match="shape drift"):
        e.validate_episode_result(result)


def test_episode_result_contract_rejects_dtype_drift():
    result = fake_result()
    result["spikes"] = result["spikes"].astype(np.int32)

    with pytest.raises(e.Refusal, match="dtype drift"):
        e.validate_episode_result(result)


def test_execute_condition_runs_exactly_one_topology_and_episode(monkeypatch):
    e.verify_frozen_dependencies.cache_clear()

    monkeypatch.setattr(
        e,
        "verify_frozen_dependencies",
        lambda: {"status": "synthetic"},
    )

    baseline = sparse.eye(4, format="csr", dtype=np.float64)

    candidate = baseline.copy()

    topology = {
        "artifact": "synthetic",
        "mask13": "0000000000000",
    }

    calls = {
        "subset": 0,
        "stimuli": 0,
        "episode": 0,
    }

    def fake_subset(matrix, mask13):
        calls["subset"] += 1
        assert matrix is baseline
        assert mask13 == "0000000000000"
        return candidate, topology

    stimuli = tuple(object() for _ in range(192))

    def fake_stimuli(layout):
        calls["stimuli"] += 1
        assert layout == "LR"
        return stimuli

    result = fake_result(0.25)

    def fake_episode(
        matrix,
        retinal_indices,
        dn_indices,
        channel_positions,
        supplied_stimuli,
    ):
        calls["episode"] += 1
        assert matrix is candidate
        assert supplied_stimuli is stimuli
        return result

    monkeypatch.setattr(e, "build_mask_subset", fake_subset)
    monkeypatch.setattr(e, "build_stimuli", fake_stimuli)
    monkeypatch.setattr(e, "run_episode", fake_episode)

    evidence = e.execute_condition(
        baseline=baseline,
        retinal_indices=np.asarray([0, 1], dtype=np.int32),
        dn_indices=np.arange(1191, dtype=np.int32),
        channel_positions={
            "DN-C0": np.asarray([0], dtype=np.int32),
            "DN-C1": np.asarray([1], dtype=np.int32),
            "DN-C2": np.asarray([2], dtype=np.int32),
        },
        condition=condition(),
    )

    assert calls == {
        "subset": 1,
        "stimuli": 1,
        "episode": 1,
    }

    assert evidence["condition"] == condition()
    assert evidence["topology_provenance"] == topology
    assert evidence["result"] is result
    assert evidence["timing"]["elapsed_seconds"] >= 0.0


def test_duplicate_pair_exact_inherits_all_six_sq05_arrays():
    first = {
        "condition": condition(replicate=1),
        "result": fake_result(1.0),
    }
    second = {
        "condition": condition(replicate=2),
        "result": fake_result(1.0),
    }

    assert e.duplicate_pair_exact(first, second) is True

    second["result"]["channel_spike_count"][0, 0] = 1

    assert e.duplicate_pair_exact(first, second) is False


def test_duplicate_pair_rejects_coordinate_mismatch():
    first = {
        "condition": condition(layout="LR", replicate=1),
        "result": fake_result(),
    }

    second = {
        "condition": condition(layout="RL", replicate=2),
        "result": fake_result(),
    }

    assert e.duplicate_pair_exact(first, second) is False


def test_source_has_no_shard_runner_cli_or_result_analysis():
    source = SOURCE.read_text(encoding="utf-8")

    forbidden = [
        "argparse",
        "--run-frozen",
        "shard_plan(",
        "for shard in",
        "EXACT_INTACT",
        "EXACT_FULL13",
        "INTERMEDIATE",
        "minimal_recapitulator",
        "inactive_subset_closure",
        "write_manifest",
        "np.save",
        "np.savez",
    ]

    for token in forbidden:
        assert token not in source
