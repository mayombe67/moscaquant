from __future__ import annotations

import numpy as np
import pytest

from brain.sq08_three_body_evidence import (
    Refusal,
    assemble_arrays,
    validate_sidecar_arrays,
)
from brain.sq08_three_body_episode import (
    RESULT_KEYS,
)
from brain.sq08_three_body_plan import (
    build_conditions,
)


def synthetic_result() -> dict:
    return {
        "positive_voltage":
            np.zeros(
                (192, 1191),
                dtype=np.float32,
            ),

        "spikes":
            np.zeros(
                (192, 1191),
                dtype=np.uint8,
            ),

        "body_responder_voltage":
            np.zeros(
                (192, 3),
                dtype=np.float32,
            ),

        "body_responder_spikes":
            np.zeros(
                (192, 3),
                dtype=np.uint8,
            ),

        "frontier_voltage":
            np.zeros(
                (192, 18),
                dtype=np.float32,
            ),

        "frontier_spikes":
            np.zeros(
                (192, 18),
                dtype=np.uint8,
            ),

        "channel_mean_positive_voltage":
            np.zeros(
                (3, 192),
                dtype=np.float64,
            ),

        "channel_positive_fraction":
            np.zeros(
                (3, 192),
                dtype=np.float64,
            ),

        "channel_spike_count":
            np.zeros(
                (3, 192),
                dtype=np.int32,
            ),

        "channel_spike_rate":
            np.zeros(
                (3, 192),
                dtype=np.float64,
            ),
    }


def synthetic_records():
    records = []

    for condition in build_conditions():
        records.append({
            "condition": dict(condition),

            "topology_provenance": {
                "synthetic": True,
            },

            "result":
                synthetic_result(),

            "timing": {
                "started_at_utc":
                    "2026-01-01T00:00:00Z",
                "completed_at_utc":
                    "2026-01-01T00:00:01Z",
                "elapsed_seconds":
                    1.0,
            },
        })

    return records


def test_result_key_contract_matches_evidence():
    assert set(
        synthetic_result()
    ) == set(
        RESULT_KEYS
    )


def test_complete_evidence_shape_contract():
    arrays, exact, count = (
        assemble_arrays(
            records=synthetic_records(),
            dn_indices=np.arange(
                1191,
                dtype=np.int32,
            ),
        )
    )

    assert exact is True
    assert count == 8

    validate_sidecar_arrays(
        arrays
    )

    assert arrays[
        "primary_positive_voltage"
    ].shape == (
        16,
        192,
        1191,
    )

    assert arrays[
        "body_responder_voltage"
    ].shape == (
        16,
        192,
        3,
    )

    assert arrays[
        "frontier_voltage"
    ].shape == (
        16,
        192,
        18,
    )


def test_duplicate_mismatch_fails_closed():
    records = synthetic_records()

    records[1][
        "result"
    ][
        "frontier_voltage"
    ][0, 0] = 1.0

    with pytest.raises(
        Refusal
    ):
        assemble_arrays(
            records=records,
            dn_indices=np.arange(
                1191,
                dtype=np.int32,
            ),
        )


def test_condition_order_mismatch_fails_closed():
    records = synthetic_records()

    records[0], records[1] = (
        records[1],
        records[0],
    )

    with pytest.raises(
        Refusal
    ):
        assemble_arrays(
            records=records,
            dn_indices=np.arange(
                1191,
                dtype=np.int32,
            ),
        )


def test_frontier_coordinate_drift_fails_closed():
    arrays, _exact, _count = (
        assemble_arrays(
            records=synthetic_records(),
            dn_indices=np.arange(
                1191,
                dtype=np.int32,
            ),
        )
    )

    arrays[
        "frontier_indices"
    ][0] = 999

    with pytest.raises(
        Refusal
    ):
        validate_sidecar_arrays(
            arrays
        )
