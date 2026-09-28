from __future__ import annotations

import numpy as np

from brain.sq11_dark_forest_episode import (
    BODY_RESPONDERS,
    BODY_SOURCES,
    DYNAMIC_KEYS,
    RESULT_KEYS,
    STATIC_KEYS,
    Refusal,
    duplicate_pair_exact,
    validate_result,
)

from brain.sq11_dark_forest_plan import (
    build_conditions,
    validate_condition,
)


EVIDENCE_ARRAY_KEYS = (
    "condition_ordinal",
    "condition_id",
    "condition_mask",
    "condition_replicate",
    "source_indices",
    "responder_indices",
    "condition_edge_zeroed",
    "body_edge_weight",
    "row_offsets",
    "row_indices",
    "row_weights",
    "body_positions",
    "body_flat_positions",
    "presynaptic_union_indices",
    "row_union_positions",
    *DYNAMIC_KEYS,
)


def refuse(
    message: str,
) -> None:
    raise Refusal(message)


def validate_episode_envelope(
    episode: dict,
    expected_condition: dict,
) -> dict:
    if set(episode) != {
        "condition",
        "topology_provenance",
        "result",
        "execution_authorized_here",
    }:
        refuse(
            "SQ-11 episode envelope drift"
        )

    if (
        episode[
            "execution_authorized_here"
        ]
        is not False
    ):
        refuse(
            "SQ-11 evidence packer received "
            "an execution-authorized episode"
        )

    condition = validate_condition(
        episode["condition"]
    )

    if condition != expected_condition:
        refuse(
            "SQ-11 canonical condition-order drift"
        )

    validate_result(
        episode["result"],
        mask=condition["mask"],
    )

    return condition


def verify_duplicate_pairs(
    episodes: list[dict],
) -> None:
    if len(episodes) != 16:
        refuse(
            "SQ-11 duplicate verification "
            "requires exactly 16 episodes"
        )

    for offset in range(
        0,
        16,
        2,
    ):
        first = episodes[offset]
        second = episodes[
            offset + 1
        ]

        if not duplicate_pair_exact(
            first,
            second,
        ):
            mask = first[
                "condition"
            ][
                "mask"
            ]

            refuse(
                "SQ-11 deterministic duplicate "
                f"mismatch for {mask}"
            )


def build_evidence_arrays(
    episodes: list[dict],
) -> dict[str, np.ndarray]:
    expected = build_conditions()

    if len(episodes) != len(expected):
        refuse(
            "SQ-11 evidence requires "
            "exactly 16 episodes"
        )

    canonical_rows = []
    results = []

    for episode, expected_condition in zip(
        episodes,
        expected,
    ):
        condition = (
            validate_episode_envelope(
                episode,
                expected_condition,
            )
        )

        canonical_rows.append(
            condition
        )

        results.append(
            episode["result"]
        )

    verify_duplicate_pairs(
        episodes
    )

    #
    # Static replay geometry must be identical
    # across every condition.
    #
    first = results[0]

    for result in results[1:]:
        for key in STATIC_KEYS:
            if not np.array_equal(
                result[key],
                first[key],
            ):
                refuse(
                    "SQ-11 static replay geometry "
                    f"drift across episodes: {key}"
                )

    condition_zeroed = np.stack(
        [
            result[
                "condition_edge_zeroed"
            ]
            for result in results
        ]
    ).astype(
        np.uint8,
        copy=False,
    )

    expected_zeroed = np.asarray(
        [
            row["edge_zeroed"]
            for row in canonical_rows
        ],
        dtype=np.uint8,
    )

    if not np.array_equal(
        condition_zeroed,
        expected_zeroed,
    ):
        refuse(
            "SQ-11 packed lesion-coordinate drift"
        )

    arrays = {
        "condition_ordinal":
            np.asarray(
                [
                    row["ordinal"]
                    for row in canonical_rows
                ],
                dtype=np.int32,
            ),

        "condition_id":
            np.asarray(
                [
                    row["condition_id"]
                    for row in canonical_rows
                ],
                dtype="<U11",
            ),

        "condition_mask":
            np.asarray(
                [
                    row["mask"]
                    for row in canonical_rows
                ],
                dtype="<U3",
            ),

        "condition_replicate":
            np.asarray(
                [
                    row["replicate"]
                    for row in canonical_rows
                ],
                dtype=np.int8,
            ),

        "source_indices":
            BODY_SOURCES.astype(
                np.int64,
                copy=True,
            ),

        "responder_indices":
            BODY_RESPONDERS.astype(
                np.int64,
                copy=True,
            ),

        "condition_edge_zeroed":
            condition_zeroed,

        "body_edge_weight":
            first[
                "body_edge_weight"
            ].copy(),

        "row_offsets":
            first[
                "row_offsets"
            ].copy(),

        "row_indices":
            first[
                "row_indices"
            ].copy(),

        "row_weights":
            first[
                "row_weights"
            ].copy(),

        "body_positions":
            first[
                "body_positions"
            ].copy(),

        "body_flat_positions":
            first[
                "body_flat_positions"
            ].copy(),

        "presynaptic_union_indices":
            first[
                "presynaptic_union_indices"
            ].copy(),

        "row_union_positions":
            first[
                "row_union_positions"
            ].copy(),
    }

    for key in DYNAMIC_KEYS:
        arrays[key] = np.stack(
            [
                result[key]
                for result in results
            ]
        )

    if set(arrays) != set(
        EVIDENCE_ARRAY_KEYS
    ):
        refuse(
            "SQ-11 evidence array key-set drift"
        )

    return arrays
