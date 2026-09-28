from __future__ import annotations

import numpy as np

from brain.sq08_three_body_analysis import (
    MASKS,
    classify_three_way,
    factorial_terms,
    first_nonzero_frame,
    frontier_report,
)


def constant_cube(
    *,
    shape,
    main_a=0.0,
    main_b=0.0,
    main_c=0.0,
    ab=0.0,
    ac=0.0,
    bc=0.0,
    abc=0.0,
):
    base = np.zeros(
        shape,
        dtype=np.float64,
    )

    result = {}

    for mask in MASKS:
        a = int(mask[0])
        b = int(mask[1])
        c = int(mask[2])

        value = (
            base
            + a * main_a
            + b * main_b
            + c * main_c
            + a * b * ab
            + a * c * ac
            + b * c * bc
            + a * b * c * abc
        )

        result[mask] = np.array(
            value,
            copy=True,
        )

    return result


def test_factorial_recovers_main_effects():
    cube = constant_cube(
        shape=(2, 3),
        main_a=1.0,
        main_b=2.0,
        main_c=3.0,
    )

    terms = factorial_terms(
        cube
    )

    assert np.all(
        terms["M_A"] == 1.0
    )

    assert np.all(
        terms["M_B"] == 2.0
    )

    assert np.all(
        terms["M_C"] == 3.0
    )


def test_factorial_recovers_pairwise_terms():
    cube = constant_cube(
        shape=(2, 3),
        ab=4.0,
        ac=5.0,
        bc=6.0,
    )

    terms = factorial_terms(
        cube
    )

    assert np.all(
        terms["I_AB"] == 4.0
    )

    assert np.all(
        terms["I_AC"] == 5.0
    )

    assert np.all(
        terms["I_BC"] == 6.0
    )


def test_factorial_recovers_three_way_term():
    cube = constant_cube(
        shape=(2, 3),
        abc=7.0,
    )

    terms = factorial_terms(
        cube
    )

    assert np.all(
        terms["I_ABC"] == 7.0
    )


def test_pairwise_complete_cube_is_exact_zero():
    cube = constant_cube(
        shape=(192, 18),
        main_a=1.0,
        main_b=2.0,
        main_c=3.0,
        ab=4.0,
        ac=5.0,
        bc=6.0,
        abc=0.0,
    )

    report = classify_three_way(
        cube
    )

    assert (
        report["classification"]
        == "THREE_WAY_EXACT_ZERO"
    )

    assert (
        report["max_abs_difference"]
        == 0.0
    )


def test_true_three_way_term_is_nonzero():
    cube = constant_cube(
        shape=(192, 18),
        abc=1e-4,
    )

    report = classify_three_way(
        cube
    )

    assert (
        report["classification"]
        == "THREE_WAY_NONZERO"
    )


def test_first_nonzero_frame_uses_exact_numeric_value():
    trace = np.zeros(
        192,
        dtype=np.float64,
    )

    trace[47] = 1e-30

    assert (
        first_nonzero_frame(
            trace
        )
        == 47
    )


def test_zero_trajectory_has_no_first_frame():
    trace = np.zeros(
        192,
        dtype=np.float64,
    )

    assert (
        first_nonzero_frame(
            trace
        )
        is None
    )


def test_frontier_reports_all_18_nodes():
    cube = constant_cube(
        shape=(192, 18),
        abc=0.0,
    )

    report = frontier_report(
        cube
    )

    assert report["node_count"] == 18
    assert len(report["nodes"]) == 18

    assert all(
        row["first_nonzero_frame"] is None
        for row in report["nodes"]
    )


def test_frontier_does_not_select_only_active_nodes():
    cube = constant_cube(
        shape=(192, 18),
        abc=0.0,
    )

    cube["111"][25, 3] = 1.0

    report = frontier_report(
        cube
    )

    assert report["node_count"] == 18
    assert len(report["nodes"]) == 18
