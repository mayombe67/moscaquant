import pytest

import brain.sq03f6_analyze as f6


def test_participation_counts_from_masks():
    masks = {
        "a": 0b0011,
        "b": 0b0110,
        "c": 0b0100,
    }
    counts = f6.participation_counts_from_masks(["a", "b", "c"], masks)
    assert counts == {0: 1, 1: 2, 2: 2}


def test_hhi_from_masks_matches_direct_counts():
    masks = {
        "a": 0b0011,
        "b": 0b0110,
    }
    counts = f6.participation_counts_from_masks(["a", "b"], masks)
    assert f6.hhi_from_masks(["a", "b"], masks) == pytest.approx(
        f6.participation_mass_hhi(counts)
    )


def test_execute_commission_refuses_existing_output(tmp_path, monkeypatch):
    output = tmp_path / "result.json"
    output.write_text("{}")
    monkeypatch.setattr(f6, "OUTPUT", output)
    with pytest.raises(RuntimeError, match="Refusing to overwrite"):
        f6.execute_commission_once()


def test_run_commission_checks_frozen_randomization_count(monkeypatch):
    monkeypatch.setattr(
        f6,
        "load_config",
        lambda: {
            "territory": {"max_depth": 2},
            "null_model": {"randomizations": 9999, "base_seed": 314159},
        },
    )
    with pytest.raises(RuntimeError, match="Frozen randomization count changed"):
        f6.run_commission()


def test_run_commission_checks_frozen_seed(monkeypatch):
    monkeypatch.setattr(
        f6,
        "load_config",
        lambda: {
            "territory": {"max_depth": 2},
            "null_model": {"randomizations": 10000, "base_seed": 123},
        },
    )
    with pytest.raises(RuntimeError, match="Frozen base seed changed"):
        f6.run_commission()


def test_run_commission_checks_frozen_depth(monkeypatch):
    monkeypatch.setattr(
        f6,
        "load_config",
        lambda: {
            "territory": {"max_depth": 3},
            "null_model": {"randomizations": 10000, "base_seed": 314159},
        },
    )
    with pytest.raises(RuntimeError, match="Frozen territory depth changed"):
        f6.run_commission()
