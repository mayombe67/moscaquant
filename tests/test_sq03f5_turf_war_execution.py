import random

import pytest

import brain.sq03f5_analyze as f5


def test_bitmask_jaccard_matches_set_jaccard():
    a = (1 << 0) | (1 << 1)
    b = (1 << 1) | (1 << 2)
    assert f5.bitmask_jaccard(a, b) == pytest.approx(1 / 3)


def test_territory_bitmask_matches_existing_territory():
    adjacency = {
        "1": ("2", "3"),
        "2": ("4", "1"),
        "3": ("5",),
        "4": ("6",),
        "5": (),
    }
    bits = f5.build_node_bit_index(adjacency)
    mask = f5.territory_bitmask(adjacency, "1", max_depth=2, node_bits=bits)

    expected = f5.territory(adjacency, "1", max_depth=2)
    decoded = {node for node, idx in bits.items() if mask & (1 << idx)}
    assert decoded == expected == {"2", "3", "4", "5"}


def test_mean_pairwise_mask_statistic_matches_set_version():
    territories = {
        "10": {"1", "2"},
        "20": {"2", "3"},
        "30": {"2"},
    }
    nodes = sorted(set().union(*territories.values()))
    bits = {node: i for i, node in enumerate(nodes)}
    masks = {
        source: sum(1 << bits[n] for n in vals)
        for source, vals in territories.items()
    }

    set_value, _ = f5.mean_pairwise_jaccard(territories)
    mask_value = f5.mean_pairwise_jaccard_masks(territories.keys(), masks)
    assert mask_value == pytest.approx(set_value)


def test_observed_pairwise_mask_components():
    masks = {"a": 0b0011, "b": 0b0110}
    value, pairs = f5.observed_pairwise_from_masks(["a", "b"], masks)
    assert value == pytest.approx(1 / 3)
    assert pairs[0]["intersection"] == 1
    assert pairs[0]["union"] == 3
    assert pairs[0]["jaccard"] == pytest.approx(1 / 3)


def test_execute_once_refuses_existing_output(tmp_path, monkeypatch):
    output = tmp_path / "result.json"
    output.write_text("{}")
    monkeypatch.setattr(f5, "OUTPUT", output)

    with pytest.raises(RuntimeError, match="Refusing to overwrite"):
        f5.execute_once()


def test_run_experiment_uses_frozen_randomization_count(monkeypatch):
    cfg = {
        "territory": {"max_depth": 2},
        "null_model": {"randomizations": 9999, "base_seed": 314159},
    }
    monkeypatch.setattr(f5, "load_config", lambda: cfg)

    with pytest.raises(RuntimeError, match="Frozen randomization count changed"):
        f5.run_experiment()


def test_run_experiment_uses_frozen_seed(monkeypatch):
    cfg = {
        "territory": {"max_depth": 2},
        "null_model": {"randomizations": 10000, "base_seed": 123},
    }
    monkeypatch.setattr(f5, "load_config", lambda: cfg)

    with pytest.raises(RuntimeError, match="Frozen base seed changed"):
        f5.run_experiment()


def test_sampling_is_deterministic_for_base_seed():
    observed = ["a", "c"]
    universe = ["a", "b", "c", "d", "e", "f"]
    strata = {
        "a": 0, "b": 0, "e": 0,
        "c": 1, "d": 1, "f": 1,
    }

    r1 = random.Random(314159)
    r2 = random.Random(314159)

    seq1 = [
        f5.sample_matched_sources(observed, universe, strata, r1)
        for _ in range(20)
    ]
    seq2 = [
        f5.sample_matched_sources(observed, universe, strata, r2)
        for _ in range(20)
    ]
    assert seq1 == seq2
