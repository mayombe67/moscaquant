import importlib
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "experiments" / "sq02_ghost_market_v1.json"
RUNNER = ROOT / "brain" / "sq02_ghost_market.py"


def test_sq02_runner_exists_and_imports():
    assert RUNNER.exists()
    module = importlib.import_module("brain.sq02_ghost_market")
    assert module.DT_MS == 1.0
    assert module.FRAME_COUNT == 16
    assert module.CONDITION == "A"


def test_sq02_runner_precommits_implementation_choices():
    module = importlib.import_module("brain.sq02_ghost_market")

    assert module.EXTREME_ROW == 0
    assert module.EXTREME_FEATURE_COLUMN == 1
    assert module.MUTATION_OBSERVATION == module.OBSERVATIONS // 2


def test_stage_a_mutations_are_exact_and_deterministic():
    module = importlib.import_module("brain.sq02_ghost_market")
    base = np.arange(42, dtype=np.float32).reshape(6, 7)

    assert module.mutate_feature_tensor(base, "BASELINE_VALID").shape == (6, 7)

    nan_case = module.mutate_feature_tensor(base, "FEATURE_NAN")
    assert np.isnan(nan_case[0, 0])

    pos_inf = module.mutate_feature_tensor(base, "FEATURE_POS_INF")
    assert np.isposinf(pos_inf[0, 0])

    neg_inf = module.mutate_feature_tensor(base, "FEATURE_NEG_INF")
    assert np.isneginf(neg_inf[0, 0])

    assert module.mutate_feature_tensor(base, "FEATURE_SHORT_ROW").shape == (6, 6)
    assert module.mutate_feature_tensor(base, "FEATURE_LONG_ROW").shape == (6, 8)


def test_stage_b_sequence_mutations_are_exact():
    module = importlib.import_module("brain.sq02_ghost_market")
    count = max(module.MUTATION_OBSERVATION + 2, 6)
    observations = [
        np.full((6, 7), i, dtype=np.float32)
        for i in range(count)
    ]

    # Temporarily exercise the mutation helper with its actual frozen midpoint only
    # when our synthetic list is long enough for that index.
    observations = [
        np.full((6, 7), i, dtype=np.float32)
        for i in range(module.OBSERVATIONS)
    ]
    idx = module.MUTATION_OBSERVATION

    baseline = module.mutate_observation_sequence(observations, "SEQUENCE_BASELINE")
    duplicate = module.mutate_observation_sequence(observations, "SEQUENCE_DUPLICATE_FRAME")
    dropped = module.mutate_observation_sequence(observations, "SEQUENCE_DROP_FRAME")
    reversed_ = module.mutate_observation_sequence(observations, "SEQUENCE_REVERSED")
    frozen = module.mutate_observation_sequence(observations, "SEQUENCE_FROZEN")

    assert len(baseline) == module.OBSERVATIONS
    assert len(duplicate) == module.OBSERVATIONS + 1
    assert np.array_equal(duplicate[idx], observations[idx])
    assert np.array_equal(duplicate[idx + 1], observations[idx])
    assert len(dropped) == module.OBSERVATIONS - 1
    assert np.array_equal(reversed_[0], observations[-1])
    assert all(np.array_equal(item, observations[idx]) for item in frozen)


def test_stage_c_extremes_target_precommitted_momentum_cell():
    module = importlib.import_module("brain.sq02_ghost_market")
    base = np.ones((6, 7), dtype=np.float32)

    x10 = module.mutate_finite_extreme(base, "EXTREME_X10")
    x100 = module.mutate_finite_extreme(base, "EXTREME_X100")
    zero = module.mutate_finite_extreme(base, "ZERO_VECTOR")

    assert x10[0, 1] == np.float32(10.0)
    assert x100[0, 1] == np.float32(100.0)
    assert np.count_nonzero(x10 != base) == 1
    assert np.count_nonzero(x100 != base) == 1
    assert np.count_nonzero(zero) == 0


def test_runner_matches_frozen_protocol_matrix():
    module = importlib.import_module("brain.sq02_ghost_market")
    data = json.loads(CONFIG.read_text())

    ids = {
        stage["id"]: {item["id"] for item in stage["variants"]}
        for stage in data["stages"]
    }

    assert ids["A"] == {
        "BASELINE_VALID",
        "FEATURE_NAN",
        "FEATURE_POS_INF",
        "FEATURE_NEG_INF",
        "FEATURE_SHORT_ROW",
        "FEATURE_LONG_ROW",
    }
    assert ids["B"] == {
        "SEQUENCE_BASELINE",
        "SEQUENCE_DUPLICATE_FRAME",
        "SEQUENCE_DROP_FRAME",
        "SEQUENCE_REVERSED",
        "SEQUENCE_FROZEN",
    }
    assert ids["C"] == {
        "EXTREME_X10",
        "EXTREME_X100",
        "ZERO_VECTOR",
    }

    assert module.DT_MS == 1.0
