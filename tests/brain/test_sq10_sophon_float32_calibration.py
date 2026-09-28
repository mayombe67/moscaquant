from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy import sparse

from brain.sq10_sophon_float32_calibration import (
    CONTRACT,
    background_pattern,
    float32_p5,
    power_of_two_ceiling,
    remove_csr_position,
)


def test_contract_forbids_neural_execution():
    d = json.loads(
        CONTRACT.read_text()
    )

    assert (
        d["neural_execution_authorized"]
        is False
    )

    assert (
        d["tolerance_rule"]
        [
            "rule_frozen_before_calibration"
        ]
        is True
    )


def test_expected_case_count_is_frozen():
    d = json.loads(
        CONTRACT.read_text()
    )

    expected = (
        3
        * len(
            d["synthetic_activity"]
            ["background_patterns"]
        )
        * len(
            d["synthetic_activity"]
            ["source_levels_float32"]
        )
        * len(
            d["synthetic_membrane_state"]
            ["pre_step_voltage_float32"]
        )
        * len(
            d["synthetic_membrane_state"]
            ["direct_stimulus_float32"]
        )
    )

    assert expected == 5760

    assert (
        d["expected_case_count"]
        == expected
    )


def test_background_patterns_are_bounded():
    d = json.loads(
        CONTRACT.read_text()
    )

    for name in (
        d["synthetic_activity"]
        ["background_patterns"]
    ):
        values = background_pattern(
            name,
            1000,
        )

        assert values.dtype == np.float32
        assert np.all(values >= 0.0)
        assert np.all(values <= 1.0)


def test_remove_csr_position_removes_only_one_term():
    row = sparse.csr_matrix(
        np.asarray(
            [[1.0, 2.0, 3.0, 4.0]],
            dtype=np.float32,
        )
    )

    result = remove_csr_position(
        row,
        2,
    )

    np.testing.assert_array_equal(
        result.toarray(),
        np.asarray(
            [[1.0, 2.0, 0.0, 4.0]],
            dtype=np.float32,
        ),
    )

    assert result.nnz == 3


def test_float32_p5_matches_declared_order():
    got = float32_p5(
        pre_voltage=np.float32(0.5),
        synaptic=np.float32(0.25),
        stimulus=np.float32(0.125),
        decay=0.95,
    )

    expected = np.asarray(
        [0.5],
        dtype=np.float32,
    )

    expected *= 0.95
    expected += np.float32(0.25)
    expected += np.float32(0.125)

    assert got == expected[0]


def test_power_of_two_ceiling():
    assert (
        power_of_two_ceiling(
            1.0e-7
        )
        == 2.0 ** -23
    )

    assert (
        power_of_two_ceiling(
            2.0 ** -20
        )
        == 2.0 ** -20
    )
