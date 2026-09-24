from __future__ import annotations

import hashlib
import json
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SHAM = ROOT / "config/controls/sq05-betrayal-i-sham-v1.json"
PREREG = ROOT / "config/controls/sq05-two-betrayals-core-prereg-v1.toml"

EXPECTED_SHAM_CANONICAL = "4a96cc329bb98a6cce66315280d80dcf9389c1ea7e39934b5d40d31ab4cc6879"
EXPECTED_SEEDS = list(range(20265100, 20265120))
EXPECTED_RESPONDERS = [51, 55, 92, 129, 317, 656, 1273, 126002, 137122]


def canonical_edge_digest(edges):
    payload = [
        {
            "presynaptic": int(row["presynaptic"]),
            "postsynaptic": int(row["postsynaptic"]),
            "weight": float(row["weight"]),
        }
        for row in edges
    ]
    raw = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def load_prereg():
    with PREREG.open("rb") as f:
        return tomllib.load(f)


def test_sham_is_exact_historical_edge_set():
    payload = json.loads(SHAM.read_text(encoding="utf-8"))
    assert payload["artifact"] == "sq05-betrayal-i-sham-v1"
    assert payload["edge_count"] == 13
    assert len(payload["edges"]) == 13
    assert payload["selection"]["derive_at_execution"] is False
    assert payload["canonical_edge_set_sha256"] == EXPECTED_SHAM_CANONICAL
    assert canonical_edge_digest(payload["edges"]) == EXPECTED_SHAM_CANONICAL


def test_fresh_seed_block_is_exact_and_disjoint():
    cfg = load_prereg()
    randomization = cfg["betrayal_ii_randomization"]
    assert randomization["seed_count"] == 20
    assert randomization["seeds"] == EXPECTED_SEEDS
    assert 20265000 not in randomization["seeds"]
    assert not (set(range(20263000, 20263020)) & set(randomization["seeds"]))
    assert not ({20264000, 20264001, 20264002} & set(randomization["seeds"]))
    assert randomization["no_early_stopping"] is True
    assert randomization["no_failed_seed_replacement"] is True
    assert randomization["reuse_each_seed_topology_for_both_layouts"] is True


def test_primary_population_is_outcome_independent():
    cfg = load_prereg()
    pop = cfg["primary_population"]
    assert pop["selection_basis"] == "pre-existing anatomy-only consensus"
    assert pop["included_clusters"] == ["DN-C0", "DN-C1", "DN-C2"]
    assert pop["assigned_neuron_count"] == 1191
    assert pop["excluded_unassigned_count"] == 123
    assert pop["post_result_population_selection_forbidden"] is True


def test_primary_fingerprint_and_layouts_are_fixed():
    cfg = load_prereg()
    fp = cfg["primary_fingerprint"]
    layouts = cfg["layouts"]
    assert fp["quantity"] == "positive_membrane_voltage"
    assert fp["shape_per_layout"] == "192x1191"
    assert fp["layouts"] == ["LR", "RL"]
    assert layouts["classification_requires_both"] is True
    assert layouts["one_layout_only_forbidden"] is True


def test_cue_transition_status_is_precommitted():
    cfg = load_prereg()
    transition = cfg["cue_transition"]
    assert transition["a_reference_frames"] == [80, 95]
    assert transition["b_blocks"] == [
        "96..111",
        "112..127",
        "128..143",
        "144..159",
        "160..175",
        "176..191",
    ]
    assert transition["numeric_tolerance"] == 1e-12


def test_betrayal_i_is_compared_to_sham_in_both_layouts():
    cfg = load_prereg()
    rule = cfg["betrayal_i_classification"]
    assert rule["comparison"] == "distance_from_INTACT_primary_fingerprint"
    assert rule["rule_both_layouts"] == "LESION_EFFECT_EXCEEDS_SHAM_BOTH_LAYOUTS"
    assert rule["rule_one_layout"] == "LAYOUT_DEPENDENT_LESION_EFFECT"
    assert rule["rule_neither"] == "LESION_NOT_SEPARATED_FROM_SHAM"


def test_betrayal_ii_exact_reproduction_rule_is_fixed():
    cfg = load_prereg()
    exact = cfg["betrayal_ii_exact_reproduction"]
    cls = cfg["betrayal_ii_classification"]
    assert exact["normalized_l2_max"] == 1e-9
    assert exact["max_abs_max"] == 1e-12
    assert exact["requires_both_layouts"] is True
    assert cls["rare_exact_min"] == 0
    assert cls["rare_exact_max"] == 1
    assert cls["mixed_exact_min"] == 2
    assert cls["mixed_exact_max"] == 9
    assert cls["frequent_exact_min"] == 10
    assert cls["frequent_exact_max"] == 20
    assert cls["population_significance_claim"] is False


def test_accepted_nine_are_secondary_only():
    cfg = load_prereg()
    secondary = cfg["lesion_specific_secondary"]
    assert secondary["accepted_responder_indices"] == EXPECTED_RESPONDERS
    assert secondary["responder_count"] == 9
    assert secondary["primary_endpoint"] is False


def test_execution_remains_closed():
    cfg = load_prereg()
    exp = cfg["experiment"]
    boundary = cfg["execution_boundary"]
    assert exp["neural_execution_authorized"] is False
    assert exp["topology_construction_authorized"] is False
    assert exp["result_execution_authorized"] is False
    assert boundary["capacity_assessment_required_before_execution"] is True
    assert boundary["authoritative_runner_not_frozen_here"] is True
    assert boundary["result_schema_not_frozen_here"] is True
    assert boundary["execution_authorization_not_frozen_here"] is True


def test_no_single_overall_winner():
    cfg = load_prereg()
    interpretation = cfg["interpretation"]
    assert interpretation["single_overall_winner_forbidden"] is True
    assert interpretation["report_cue_transition_status_separately"] is True
    assert interpretation["report_betrayal_i_status_separately"] is True
    assert interpretation["report_betrayal_ii_status_separately"] is True
