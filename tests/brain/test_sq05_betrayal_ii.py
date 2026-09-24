from pathlib import Path
import tomllib

import numpy as np
from scipy import sparse

import brain.sq05_betrayal_ii as b2

ROOT = Path(__file__).resolve().parents[2]
CFG = ROOT / "config/controls/sq05-betrayal-ii-strict-topology-null-v1.toml"


def load_cfg():
    with CFG.open("rb") as f:
        return tomllib.load(f)


def test_config_binds_betrayal_ii_to_warthog_1x():
    cfg = load_cfg()
    assert cfg["experiment"]["canonical_parent"] == "SQ-05 — TWO BETRAYALS"
    assert cfg["experiment"]["arm"] == "BETRAYAL_II_SHUFFLED"
    assert cfg["backend"]["accepted_swaps_per_eligible_edge"] == 1.0
    assert cfg["backend"]["max_attempt_multiplier"] == 20
    assert cfg["warthog_authority"]["required_classification"] == (
        "CURRENT_1X_ADEQUATE_FOR_SQ05"
    )
    assert cfg["experiment"]["neural_execution_authorized"] is False
    assert cfg["experiment"]["result_execution_authorized"] is False


def test_config_leaves_future_sq05_seed_unselected():
    cfg = load_cfg()
    policy = cfg["seed_policy"]
    assert policy["exact_seed_frozen_here"] is False
    assert policy["seed_count_frozen_here"] is False
    assert policy["fresh_seed_required"] is True


def test_warthog_and_backend_dependencies_are_exact():
    authority = b2.assert_betrayal_ii_dependencies()
    assert authority["warthog_classification"] == (
        "CURRENT_1X_ADEQUATE_FOR_SQ05"
    )
    assert authority["accepted_swaps_per_eligible_edge"] == 1.0


def test_historical_seeds_are_rejected():
    for seed in (20263000, 20263019, 20264000, 20264001, 20264002):
        try:
            b2._validate_future_sq05_seed(seed)
        except ValueError:
            pass
        else:
            raise AssertionError(f"historical seed unexpectedly accepted: {seed}")


def test_fresh_seed_validation_is_strict():
    assert b2._validate_future_sq05_seed(20265000) == 20265000
    for bad in (-1, True, 1.5, "20265000"):
        try:
            b2._validate_future_sq05_seed(bad)
        except (TypeError, ValueError):
            pass
        else:
            raise AssertionError(f"invalid seed unexpectedly accepted: {bad!r}")


def test_adapter_forces_exact_1x_constructor_and_verifier(monkeypatch):
    baseline = sparse.eye(3, dtype=np.float32, format="csr")
    signs = np.ones(3, dtype=np.float32)
    protected = np.asarray([], dtype=np.int32)
    captured = {}

    monkeypatch.setattr(
        b2, "assert_betrayal_ii_dependencies", lambda: {"authority": "test"}
    )

    def fake_constructor(
        original,
        transmitter_sign,
        protected_indices,
        seed,
        *,
        accepted_swaps_per_eligible_edge,
        max_attempt_multiplier,
    ):
        captured["seed"] = seed
        captured["depth"] = accepted_swaps_per_eligible_edge
        captured["max_attempt_multiplier"] = max_attempt_multiplier
        return original.copy(), object()

    def fake_verifier(original, candidate, transmitter_sign, protected_indices):
        captured["verifier_called"] = True
        return {"all_test_invariants": True, "no_new_self_edges": True}

    monkeypatch.setattr(
        b2, "build_strict_matched_control_native", fake_constructor
    )
    monkeypatch.setattr(
        b2, "verify_strict_matched_control_scalable", fake_verifier
    )

    _, _, invariants, provenance = b2.build_betrayal_ii(
        baseline, signs, protected, seed=20265000
    )

    assert captured == {
        "seed": 20265000,
        "depth": 1.0,
        "max_attempt_multiplier": 20,
        "verifier_called": True,
    }
    assert all(invariants.values())
    assert provenance["arm"] == "BETRAYAL_II_SHUFFLED"
    assert provenance["sq05_seed"] == 20265000
    assert provenance["neural_execution_authorized_here"] is False
    assert provenance["result_execution_authorized_here"] is False


def test_adapter_has_no_result_execution_entrypoint():
    source = (ROOT / "brain/sq05_betrayal_ii.py").read_text(encoding="utf-8")
    assert "argparse" not in source
    assert 'if __name__ == "__main__"' not in source
    assert "write_result" not in source
