from __future__ import annotations

import numpy as np
import pytest

from brain.sq10_sophon_episode import (
    BODY_RESPONDERS,
    BODY_SOURCES,
    RESULT_KEYS,
    condition_edge_zeroed,
    validate_condition,
    validate_result,
)
from brain.sq10_sophon_plan import (
    MASKS,
    REPLICATES,
    build_conditions,
    condition_id,
)


def valid_result():
    return {
        "source_voltage_pre_step":
            np.zeros(
                (192, 3),
                dtype=np.float32,
            ),
        "source_spikes_pre_step":
            np.zeros(
                (192, 3),
                dtype=np.uint8,
            ),
        "source_effective_activity_pre_synaptic":
            np.zeros(
                (192, 3),
                dtype=np.float32,
            ),
        "responder_voltage_pre_threshold":
            np.zeros(
                (192, 3),
                dtype=np.float32,
            ),
        "responder_fired":
            np.zeros(
                (192, 3),
                dtype=np.uint8,
            ),
        "responder_voltage_post_reset":
            np.zeros(
                (192, 3),
                dtype=np.float32,
            ),
        "responder_spikes_post_commit":
            np.zeros(
                (192, 3),
                dtype=np.uint8,
            ),
        "body_edge_weight":
            np.ones(
                3,
                dtype=np.float32,
            ),
        "condition_edge_zeroed":
            np.zeros(
                3,
                dtype=np.uint8,
            ),
    }


def test_sq10_cube_and_replicates_are_exact():
    assert MASKS == (
        "000",
        "001",
        "010",
        "011",
        "100",
        "101",
        "110",
        "111",
    )

    assert REPLICATES == (1, 2)


def test_sq10_condition_ids_are_distinct_from_sq08():
    assert (
        condition_id("000", 1)
        == "sq10:000:r1"
    )

    assert (
        condition_id("111", 2)
        == "sq10:111:r2"
    )


def test_sq10_plan_contains_exactly_16_conditions():
    conditions = build_conditions()

    assert len(conditions) == 16

    assert [
        row["ordinal"]
        for row in conditions
    ] == list(range(16))

    assert len({
        row["condition_id"]
        for row in conditions
    }) == 16


def test_condition_zeroed_vector_matches_mask():
    np.testing.assert_array_equal(
        condition_edge_zeroed("000"),
        np.asarray(
            [0, 0, 0],
            dtype=np.uint8,
        ),
    )

    np.testing.assert_array_equal(
        condition_edge_zeroed("101"),
        np.asarray(
            [1, 0, 1],
            dtype=np.uint8,
        ),
    )

    np.testing.assert_array_equal(
        condition_edge_zeroed("111"),
        np.asarray(
            [1, 1, 1],
            dtype=np.uint8,
        ),
    )


def test_body_coordinate_order_is_frozen():
    np.testing.assert_array_equal(
        BODY_SOURCES,
        np.asarray(
            [
                65084,
                128590,
                135589,
            ],
            dtype=np.int64,
        ),
    )

    np.testing.assert_array_equal(
        BODY_RESPONDERS,
        np.asarray(
            [
                137122,
                317,
                126002,
            ],
            dtype=np.int64,
        ),
    )


def test_validate_condition_accepts_canonical_row():
    row = build_conditions()[11]

    assert (
        validate_condition(row)
        == row
    )


def test_validate_condition_rejects_sq08_namespace():
    row = build_conditions()[0]
    row = dict(row)

    row["condition_id"] = (
        "sq08:000:r1"
    )

    with pytest.raises(
        ValueError,
        match="condition ID mismatch",
    ):
        validate_condition(row)


def test_result_contract_is_exact():
    result = valid_result()

    validate_result(result)

    assert set(result) == set(
        RESULT_KEYS
    )


def test_result_shape_drift_is_rejected():
    result = valid_result()

    result[
        "source_voltage_pre_step"
    ] = np.zeros(
        (191, 3),
        dtype=np.float32,
    )

    with pytest.raises(
        RuntimeError,
        match="shape drift",
    ):
        validate_result(result)


def test_result_dtype_drift_is_rejected():
    result = valid_result()

    result[
        "responder_fired"
    ] = np.zeros(
        (192, 3),
        dtype=np.float32,
    )

    with pytest.raises(
        RuntimeError,
        match="dtype drift",
    ):
        validate_result(result)


def test_nonfinite_measurement_is_rejected():
    result = valid_result()

    result[
        "responder_voltage_pre_threshold"
    ][0, 0] = np.nan

    with pytest.raises(
        RuntimeError,
        match="non-finite",
    ):
        validate_result(result)
