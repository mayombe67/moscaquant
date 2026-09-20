import json
import random

import pandas as pd
import pytest

import brain.sq03f5_analyze as f5


def test_adjacency_from_matched_is_directed_and_deduplicated():
    frame = pd.DataFrame({
        "pre": ["1", "1", "1", "2"],
        "post": ["2", "2", "3", "4"],
    })
    assert f5.adjacency_from_matched(frame) == {
        "1": ("2", "3"),
        "2": ("4",),
    }


def test_sample_matched_sources_preserves_count_and_strata():
    observed = ["a", "c"]
    universe = ["a", "b", "c", "d"]
    strata = {"a": 0, "b": 0, "c": 1, "d": 1}
    sample = f5.sample_matched_sources(observed, universe, strata, random.Random(123))
    assert sample == ["b", "d"]


def test_build_result_payload_schema(monkeypatch):
    prepared = f5.PreparedInputs(
        eligible_sources=("10", "20"),
        candidate_sources=("10", "20", "30"),
        adjacency={"10": ("30",), "20": ("30",)},
        candidate_edge_count=7,
        conservative_graph_edge_count=9,
    )
    monkeypatch.setattr(f5, "load_config", lambda: {
        "territory": {"direction": "downstream", "max_depth": 2},
        "null_model": {"randomizations": 10000, "base_seed": 314159},
    })
    monkeypatch.setattr(f5, "load_f4_result", lambda: {"classification": "TEST_PARENT"})
    monkeypatch.setattr(f5, "sha256", lambda _path: "abc")

    result = f5.build_result_payload(
        prepared=prepared,
        territory_sizes={"10": 1, "20": 1},
        pairwise_overlap=[{
            "source_a": "10", "source_b": "20",
            "intersection": 1, "union": 1, "jaccard": 1.0,
        }],
        observed=1.0,
        null_values=[0.25, 0.50],
        classification=f5.Classification(
            "GREATER_THAN_NULL_DOWNSTREAM_CONVERGENCE", 0.01, 1.0, 2.0
        ),
        derived_streams=[314159],
    )
    assert result["schema"] == "moscaquant.sq03f5_result/v1"
    assert result["eligible_sources"] == ["10", "20"]
    assert result["candidate_source_count"] == 3
    assert result["randomizations"] == 10000
    assert result["classification"] == "GREATER_THAN_NULL_DOWNSTREAM_CONVERGENCE"
    assert "financial usefulness" in result["claim_boundary"]


def test_write_result_refuses_overwrite(tmp_path, monkeypatch):
    output = tmp_path / "result.json"
    output.write_text("{}")
    monkeypatch.setattr(f5, "OUTPUT", output)
    with pytest.raises(RuntimeError, match="Refusing to overwrite"):
        f5.write_result({"x": 1})


def test_write_result_is_stable_json(tmp_path, monkeypatch):
    output = tmp_path / "result.json"
    monkeypatch.setattr(f5, "OUTPUT", output)
    f5.write_result({"b": 2, "a": 1})
    assert json.loads(output.read_text()) == {"a": 1, "b": 2}
