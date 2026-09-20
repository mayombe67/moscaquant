from brain.sq03c_panel_freezer import select_stratum


def row(edge_id, peak, integrated):
    return {
        "input": "X",
        "subject": "MORTY",
        "edge_id": edge_id,
        "pre": f"P{edge_id}",
        "post": f"Q{edge_id}",
        "baseline_weight": 1.0,
        "counterfactual_weight": 2.0,
        "relevant_anchors": ["DN"],
        "anchor_results": {
            "DN": {
                "delta": {
                    "peak_voltage_delta": peak,
                    "integrated_positive_voltage_delta": integrated,
                    "first_positive_frame_delta": 0,
                }
            }
        },
    }


def test_upper_union_is_deduplicated():
    rows = [
        row(1, 10, 10),
        row(2, 9, 1),
        row(3, 1, 9),
        row(4, 0.5, 0.5),
        row(5, 0.4, 0.4),
        row(6, 0.3, 0.3),
    ]
    got = select_stratum(rows, 2, 2, 1)
    upper = [x for x in got["selected"] if x["panel_class"] == "UPPER_TAIL"]
    assert {x["edge_id"] for x in upper} == {1, 2, 3}
    assert got["upper_tail_count"] == 3


def test_low_tail_selection_is_deterministic():
    rows = [
        row(1, 10, 10),
        row(2, 3, 3),
        row(3, 0.2, 0.1),
        row(4, 0.1, 0.1),
        row(5, 0.1, 0.1),
    ]
    got = select_stratum(rows, 1, 1, 2)
    low = [x for x in got["selected"] if x["panel_class"] == "LOW_TAIL_CONTROL"]
    assert [x["edge_id"] for x in low] == [4, 5]


def test_integrated_tie_breaks_by_peak_then_edge_id():
    rows = [
        row(1, 2, 5),
        row(2, 3, 5),
        row(3, 3, 5),
        row(4, 0.1, 0.1),
    ]
    got = select_stratum(rows, 2, 1, 1)
    upper = [x for x in got["selected"] if x["panel_class"] == "UPPER_TAIL"]
    assert {x["edge_id"] for x in upper} == {2, 3}
