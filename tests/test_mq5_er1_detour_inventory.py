from scipy import sparse
import numpy as np

from brain.mq5_er1_detour_inventory import (
    count_target_cone,
    inventory_connectome,
)


def toy_matrix():
    matrix = np.zeros((8, 8), dtype=np.float32)
    matrix[7, 5] = 1.0
    matrix[5, 3] = 1.0
    matrix[3, 1] = 1.0
    matrix[6, 5] = 1.0
    return sparse.csr_matrix(matrix)


def test_count_target_cone_reports_exact_hops_without_edge_objects():
    result = count_target_cone(
        toy_matrix(),
        7,
        max_hops=3,
        edge_visit_cap=100,
    )

    assert result["truncated_by_engineering_cap"] is False
    assert [row["edge_visits"] for row in result["hops"]] == [1, 1, 1]
    assert [
        row["unique_presynaptic_count"]
        for row in result["hops"]
    ] == [1, 1, 1]
    assert result["cumulative_edge_visits"] == 3


def test_inventory_keeps_targets_separate_and_does_not_run_neural_runtime():
    result = inventory_connectome(
        toy_matrix(),
        affected_targets=(7,),
        retained_targets=(6,),
        max_hops=3,
        edge_visit_cap=100,
    )

    assert result["any_target_truncated"] is False
    assert set(result["targets"]) == {"6", "7"}
    assert result["targets"]["7"]["cumulative_edge_visits"] == 3
    assert result["targets"]["6"]["cumulative_edge_visits"] == 3


def test_engineering_cap_reports_truncation_without_changing_rule():
    result = count_target_cone(
        toy_matrix(),
        7,
        max_hops=3,
        edge_visit_cap=1,
    )

    assert result["truncated_by_engineering_cap"] is True
    assert result["engineering_edge_visit_cap"] == 1
    assert result["hops"][-1]["hop"] == 2
