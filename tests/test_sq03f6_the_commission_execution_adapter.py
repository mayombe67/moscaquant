import brain.sq03f6_analyze as f6


def test_commission_result_skeleton_is_non_result_bearing():
    prepared = f6.PreparedCommissionInputs(
        eligible_sources=("a", "b"),
        candidate_sources=("a", "b", "c"),
        adjacency={"a": ("x",), "b": ("x",)},
        candidate_edge_count=7,
        conservative_graph_edge_count=9,
        parent_result_sha256="result-hash",
        parent_provenance_sha256="prov-hash",
    )
    row = f6.commission_result_skeleton(prepared)
    assert row["schema"] == "moscaquant.sq03f6_result/v1"
    assert row["status"] == "NOT_EXECUTED"
    assert row["eligible_source_count"] == 2
    assert row["candidate_source_count"] == 3
    assert row["input_artifacts"]["sq03f5_result_sha256"] == "result-hash"


def test_parent_paths_match_frozen_config():
    cfg = f6.load_config()
    assert cfg["input"]["authoritative_sq03f5_result"] == (
        "artifacts/sidequests/sq03f5-turf-war-result-v1.json"
    )
    assert cfg["input"]["authoritative_sq03f5_provenance"] == (
        "artifacts/sidequests/sq03f5-turf-war-provenance-v1.json"
    )


def test_parent_result_and_provenance_are_bound():
    f5 = f6.load_f5_result()
    prov = f6.load_f5_provenance()
    assert f5["schema"] == "moscaquant.sq03f5_result/v1"
    assert f5["status"] == "COMPLETE"
    assert prov["schema"] == "moscaquant.sq03f5_provenance/v1"
    assert prov["result_sha256"] == f6.sha256(f6.F5_RESULT)


def test_reconstructed_commission_inputs_match_parent():
    prepared = f6.prepare_commission_inputs()
    parent = f6.load_f5_result()
    assert len(prepared.eligible_sources) == 42
    assert len(prepared.candidate_sources) == parent["candidate_source_count"]
    assert prepared.candidate_edge_count == parent["candidate_edge_count"]
    assert prepared.conservative_graph_edge_count == parent["conservative_graph_edge_count"]
    assert tuple(sorted(parent["eligible_sources"])) == prepared.eligible_sources


def test_inherited_territory_contract_matches_f5():
    parent = f6.load_f5_result()
    territory = parent["territory_parameters"]
    assert territory["direction"] == "downstream"
    assert territory["max_depth"] == 2
    assert territory["exclude_source_nodes"] is True
    assert territory["collapse_repeated_nodes"] is True
