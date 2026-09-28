from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from brain.sq10_sophon_episode import (
    RESULT_KEYS,
    condition_edge_zeroed,
)
from brain.sq10_sophon_evidence import (
    EVIDENCE_ARRAY_KEYS,
    build_evidence_arrays,
    derive_edge_quantities,
)
from brain.sq10_sophon_independent_verify import (
    VerificationRefusal,
    verify_evidence_arrays,
)
from brain.sq10_sophon_plan import (
    build_conditions,
)


ROOT = Path(__file__).resolve().parents[2]

SCHEMA = (
    ROOT
    / "config/experiments/"
    "sq10-sophon-evidence-schema-draft-v1.json"
)


def synthetic_episodes():
    episodes = []

    weights = np.asarray(
        [0.25, 1.5, 0.5],
        dtype=np.float32,
    )

    for condition in build_conditions():
        mask_value = int(
            condition["mask"],
            2,
        )

        scalar = np.float32(
            0.1
            + mask_value * 0.01
        )

        float_frame = np.full(
            (192, 3),
            scalar,
            dtype=np.float32,
        )

        zero_frame = np.zeros(
            (192, 3),
            dtype=np.uint8,
        )

        result = {
            "source_voltage_pre_step":
                float_frame.copy(),
            "source_spikes_pre_step":
                zero_frame.copy(),
            "source_effective_activity_pre_synaptic":
                float_frame.copy(),
            "responder_voltage_pre_threshold":
                float_frame.copy(),
            "responder_fired":
                zero_frame.copy(),
            "responder_voltage_post_reset":
                float_frame.copy(),
            "responder_spikes_post_commit":
                zero_frame.copy(),
            "body_edge_weight":
                weights.copy(),
            "condition_edge_zeroed":
                condition_edge_zeroed(
                    condition["mask"]
                ),
        }

        assert set(result) == set(
            RESULT_KEYS
        )

        episodes.append(
            {
                "condition":
                    dict(condition),
                "topology_provenance": {
                    "artifact":
                        "synthetic-test",
                },
                "result":
                    result,
                "execution_authorized_here":
                    False,
            }
        )

    return episodes


def test_schema_array_set_matches_packer():
    schema = json.loads(
        SCHEMA.read_text()
    )

    assert set(
        schema["arrays"]
    ) == set(
        EVIDENCE_ARRAY_KEYS
    )


def test_build_and_independently_verify_evidence():
    arrays = build_evidence_arrays(
        synthetic_episodes()
    )

    result = verify_evidence_arrays(
        arrays
    )

    assert result == {
        "status": "VERIFIED",
        "episode_count": 16,
        "mask_count": 8,
        "duplicate_pair_count": 8,
        "frame_count": 192,
        "body_pair_count": 3,
    }


def test_edge_derivations_follow_mask_semantics():
    arrays = build_evidence_arrays(
        synthetic_episodes()
    )

    derived = derive_edge_quantities(
        arrays
    )

    #
    # Episode 10 is mask 101 / replicate 1.
    #
    i = 10

    potential = derived[
        "potential_direct_edge_drive"
    ][i]

    actual = derived[
        "actual_direct_edge_contribution"
    ][i]

    removed = derived[
        "removed_direct_edge_contribution"
    ][i]

    np.testing.assert_array_equal(
        actual[:, 0],
        np.zeros(
            192,
            dtype=np.float64,
        ),
    )

    np.testing.assert_array_equal(
        actual[:, 2],
        np.zeros(
            192,
            dtype=np.float64,
        ),
    )

    np.testing.assert_array_equal(
        removed[:, 1],
        np.zeros(
            192,
            dtype=np.float64,
        ),
    )

    np.testing.assert_array_equal(
        actual + removed,
        potential,
    )


def test_packer_rejects_duplicate_drift():
    episodes = synthetic_episodes()

    episodes[1][
        "result"
    ][
        "source_voltage_pre_step"
    ][0, 0] += np.float32(0.01)

    with pytest.raises(
        RuntimeError,
        match="deterministic duplicate",
    ):
        build_evidence_arrays(
            episodes
        )


def test_packer_rejects_execution_authority():
    episodes = synthetic_episodes()

    episodes[0][
        "execution_authorized_here"
    ] = True

    with pytest.raises(
        RuntimeError,
        match="execution-authorized",
    ):
        build_evidence_arrays(
            episodes
        )


def test_independent_verifier_rejects_coordinate_drift():
    arrays = build_evidence_arrays(
        synthetic_episodes()
    )

    arrays[
        "source_indices"
    ][0] = 123

    with pytest.raises(
        VerificationRefusal,
        match="source coordinate",
    ):
        verify_evidence_arrays(
            arrays
        )
