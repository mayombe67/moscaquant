from pathlib import Path
import tomllib


CONFIG = Path(
    "config/controls/"
    "mq5-er5r-way-down-in-the-hole-v1.toml"
)


def load():
    with CONFIG.open("rb") as handle:
        return tomllib.load(handle)


def test_identity_and_execution_gate():
    cfg = load()

    assert (
        cfg["experiment_id"]
        == "mq5-er5r-way-down-in-the-hole-v1"
    )

    assert (
        cfg["codename"]
        == "WAY DOWN IN THE HOLE"
    )

    assert (
        cfg["result_execution_enabled"]
        is True
    )


def test_correct_orientation_is_frozen():
    cfg = load()

    orientation = cfg["orientation"]

    assert (
        orientation["matrix_semantics"]
        == "graph[post, pre] = pre -> post"
    )

    assert (
        orientation["reverse_ancestry_storage"]
        == "csr_rows"
    )

    assert (
        orientation[
            "csc_column_reverse_ancestry_allowed"
        ]
        is False
    )

    assert (
        orientation[
            "require_executable_tiny_graph_contract"
        ]
        is True
    )


def test_historical_candidates_receive_no_special_treatment():
    cfg = load()

    h = cfg[
        "historical_candidate_neutrality"
    ]

    assert h["nodes"] == [
        1952,
        2641,
        1963,
        1944,
        23640,
    ]

    assert h["seeded"] is False
    assert h["prioritized"] is False
    assert h["required"] is False
    assert (
        h["excluded_because_historical"]
        is False
    )


def test_original_search_bounds_are_preserved():
    cfg = load()

    assert cfg["max_backward_hops"] == 3
    assert cfg["top_k"] == 5

    assert (
        cfg[
            "focused_min_affected_coverage"
        ]
        == 4
    )


def test_rasputin_remains_authoritative_boundary():
    cfg = load()

    assert (
        cfg["integrity"][
            "require_rasputin_authoritative_execution"
        ]
        is True
    )
