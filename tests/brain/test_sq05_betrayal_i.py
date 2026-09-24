from pathlib import Path
import tomllib

import numpy as np
from scipy import sparse

import brain.sq05_betrayal_i as b1


ROOT = Path(__file__).resolve().parents[2]
CFG = ROOT / "config/controls/sq05-betrayal-i-causal-route-lesion-v1.toml"


def load_cfg():
    with CFG.open("rb") as f:
        return tomllib.load(f)


def test_config_binds_exact_inherited_lesion():
    cfg = load_cfg()
    assert cfg["experiment"]["canonical_parent"] == "SQ-05 — TWO BETRAYALS"
    assert cfg["experiment"]["arm"] == "BETRAYAL_I_LESIONED"
    assert cfg["inherited_lesion"]["artifact_sha256"] == b1.CAUSAL_SHA256
    assert cfg["inherited_lesion"]["edge_count"] == 13
    assert cfg["inherited_lesion"]["target_count"] == 9
    assert cfg["inherited_lesion"]["historical_selection_post_hoc"] is True
    assert cfg["inherited_lesion"]["sq05_adoption"] == "prospective"


def test_execution_boundaries_are_closed():
    cfg = load_cfg()
    assert cfg["experiment"]["neural_execution_authorized"] is False
    assert cfg["experiment"]["result_execution_authorized"] is False
    assert cfg["boundaries"]["not_a_hunger_circuit_claim"] is True
    assert cfg["boundaries"]["not_a_danger_circuit_claim"] is True


def test_future_sq05_sham_is_required_but_not_selected_here():
    cfg = load_cfg()
    control = cfg["scientific_control"]
    assert control["future_sq05_sham_required"] is True
    assert control["showcase_primary_arm"] is False
    assert control["exact_sq05_sham_edges_frozen_here"] is False


def test_real_inherited_artifact_identity():
    edges, payload = b1.load_betrayal_i_edges()
    assert len(edges) == 13
    assert len(payload["targets"]) == 9
    assert payload["post_hoc"] is True
    assert payload["purpose"] == "confirmatory in-model causal intervention"


def test_adapter_applies_only_exact_frozen_edges(monkeypatch):
    baseline = sparse.csr_matrix(
        np.asarray(
            [
                [0.0, 1.0, 0.0, 0.0],
                [0.0, 0.0, 2.0, 0.0],
                [0.0, 0.0, 0.0, 3.0],
                [4.0, 0.0, 0.0, 0.0],
            ],
            dtype=np.float32,
        )
    )
    edges = [(1, 0, 1.0), (2, 1, 2.0)]
    payload = {"purpose": "confirmatory in-model causal intervention"}

    monkeypatch.setattr(b1, "load_betrayal_i_edges", lambda: (edges, payload))

    candidate, provenance = b1.build_betrayal_i(baseline)

    assert baseline.nnz == 4
    assert candidate.nnz == 2
    assert float(candidate[0, 1]) == 0.0
    assert float(candidate[1, 2]) == 0.0
    assert float(candidate[2, 3]) == 3.0
    assert float(candidate[3, 0]) == 4.0
    assert provenance["arm"] == "BETRAYAL_I_LESIONED"
    assert provenance["edge_count"] == 13
    assert provenance["historical_selection_post_hoc"] is True
    assert provenance["sq05_adoption"] == "prospective"
    assert provenance["neural_execution_authorized_here"] is False


def test_adapter_has_no_result_execution_entrypoint():
    source = (ROOT / "brain/sq05_betrayal_i.py").read_text(encoding="utf-8")
    assert "argparse" not in source
    assert 'if __name__ == "__main__"' not in source
    assert "write_result" not in source
