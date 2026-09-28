from __future__ import annotations

import copy

import numpy as np
import pytest

import brain.sq11_dark_forest_episode as episode_module
import brain.sq11_dark_forest_evidence as evidence_module

from brain.sq11_dark_forest_episode import (
    DYNAMIC_KEYS,
    RESULT_KEYS,
    STATIC_KEYS,
    Refusal,
)

from brain.sq11_dark_forest_evidence import (
    EVIDENCE_ARRAY_KEYS,
    build_evidence_arrays,
)

from brain.sq11_dark_forest_plan import (
    MASKS,
    build_conditions,
)


def synthetic_result(
    mask: str,
) -> dict[str, np.ndarray]:
    mask_index = MASKS.index(mask)

    static = {
        "row_offsets":
            np.asarray(
                [0, 1, 2, 3],
                dtype=np.int64,
            ),

        "row_indices":
            np.asarray(
                [10, 20, 30],
                dtype=np.int64,
            ),

        "row_weights":
            np.asarray(
                [0.25, 0.5, 0.75],
                dtype=np.float32,
            ),

        "body_positions":
            np.asarray(
                [0, 0, 0],
                dtype=np.int64,
            ),

        "body_flat_positions":
            np.asarray(
                [0, 1, 2],
                dtype=np.int64,
            ),

        "presynaptic_union_indices":
            np.asarray(
                [10, 20, 30],
                dtype=np.int64,
            ),

        "row_union_positions":
            np.asarray(
                [0, 1, 2],
                dtype=np.int64,
            ),

        "body_edge_weight":
            np.asarray(
                [0.25, 0.5, 0.75],
                dtype=np.float32,
            ),
    }

    result = {
        key:
            np.asarray(
                [[float(mask_index)]],
                dtype=np.float32,
            )
        for key in DYNAMIC_KEYS
    }

    result.update(static)

    result[
        "condition_edge_zeroed"
    ] = np.asarray(
        [int(bit) for bit in mask],
        dtype=np.uint8,
    )

    assert set(result) == set(
        RESULT_KEYS
    )

    return result


def synthetic_episodes():
    episodes = []

    for condition in build_conditions():
        episodes.append(
            {
                "condition":
                    copy.deepcopy(
                        condition
                    ),

                "topology_provenance":
                    {
                        "synthetic":
                            True
                    },

                "result":
                    synthetic_result(
                        condition["mask"]
                    ),

                "execution_authorized_here":
                    False,
            }
        )

    return episodes


@pytest.fixture(autouse=True)
def isolate_packer_from_episode_shape_validation(
    monkeypatch,
):
    #
    # Episode shape/replay validation has its
    # own contract tests. These tests isolate
    # packer ordering, duplicate and static
    # geometry behavior using tiny arrays.
    #
    def accept_result(
        result,
        *,
        mask,
    ):
        assert set(result) == set(
            RESULT_KEYS
        )

    monkeypatch.setattr(
        episode_module,
        "validate_result",
        accept_result,
    )

    monkeypatch.setattr(
        evidence_module,
        "validate_result",
        accept_result,
    )


def test_canonical_16_units_pack():
    episodes = synthetic_episodes()

    arrays = build_evidence_arrays(
        episodes
    )

    assert set(arrays) == set(
        EVIDENCE_ARRAY_KEYS
    )

    assert arrays[
        "condition_ordinal"
    ].tolist() == list(
        range(16)
    )

    assert arrays[
        "condition_id"
    ].tolist() == [
        condition["condition_id"]
        for condition in build_conditions()
    ]

    assert arrays[
        "condition_mask"
    ].tolist() == [
        condition["mask"]
        for condition in build_conditions()
    ]

    assert arrays[
        "condition_replicate"
    ].tolist() == [
        condition["replicate"]
        for condition in build_conditions()
    ]

    assert arrays[
        "condition_edge_zeroed"
    ].shape == (16, 3)


def test_reordered_condition_is_refused():
    episodes = synthetic_episodes()

    episodes[0], episodes[2] = (
        episodes[2],
        episodes[0],
    )

    with pytest.raises(
        Refusal,
        match="canonical condition-order drift",
    ):
        build_evidence_arrays(
            episodes
        )


def test_r2_dynamic_mutation_is_refused():
    episodes = synthetic_episodes()

    key = DYNAMIC_KEYS[0]

    episodes[1]["result"][
        key
    ] = episodes[1]["result"][
        key
    ].copy()

    episodes[1]["result"][
        key
    ][0, 0] = np.float32(
        999.0
    )

    with pytest.raises(
        Refusal,
        match="deterministic duplicate mismatch",
    ):
        build_evidence_arrays(
            episodes
        )


def test_static_geometry_drift_is_refused():
    episodes = synthetic_episodes()

    #
    # Mutate BOTH replicates for mask 001.
    # Their duplicate pair remains exact, but
    # geometry now differs from mask 000.
    #
    for index in (2, 3):
        episodes[index]["result"][
            "row_weights"
        ] = episodes[index][
            "result"
        ][
            "row_weights"
        ].copy()

        episodes[index]["result"][
            "row_weights"
        ][0] = np.float32(
            123.0
        )

    with pytest.raises(
        Refusal,
        match="static replay geometry drift",
    ):
        build_evidence_arrays(
            episodes
        )


def test_authorized_episode_is_refused():
    episodes = synthetic_episodes()

    episodes[0][
        "execution_authorized_here"
    ] = True

    with pytest.raises(
        Refusal,
        match="execution-authorized episode",
    ):
        build_evidence_arrays(
            episodes
        )


def test_episode_count_is_exact():
    episodes = synthetic_episodes()

    with pytest.raises(
        Refusal,
        match="exactly 16 episodes",
    ):
        build_evidence_arrays(
            episodes[:-1]
        )


def test_static_key_universe_matches_packer():
    expected_static = {
        "row_offsets",
        "row_indices",
        "row_weights",
        "body_positions",
        "body_flat_positions",
        "presynaptic_union_indices",
        "row_union_positions",
        "body_edge_weight",
    }

    assert set(STATIC_KEYS) == (
        expected_static
    )
