from __future__ import annotations

import numpy as np

from brain.sq10_sophon_episode import (
    BODY_RESPONDERS,
    BODY_SOURCES,
    RESULT_KEYS,
    Refusal,
    duplicate_pair_exact,
    validate_condition,
    validate_result,
)
from brain.sq10_sophon_plan import (
    build_conditions,
)


MEASUREMENT_KEYS = (
    "source_voltage_pre_step",
    "source_spikes_pre_step",
    "source_effective_activity_pre_synaptic",
    "responder_voltage_pre_threshold",
    "responder_fired",
    "responder_voltage_post_reset",
    "responder_spikes_post_commit",
)

EVIDENCE_ARRAY_KEYS = (
    "condition_ordinal",
    "condition_id",
    "condition_mask",
    "condition_replicate",
    "source_indices",
    "responder_indices",
    "body_edge_weight",
    "condition_edge_zeroed",
    *MEASUREMENT_KEYS,
)


def refuse(message: str) -> None:
    raise Refusal(message)


def build_evidence_arrays(
    episodes: list[dict],
) -> dict[str, np.ndarray]:
    expected = build_conditions()

    if len(episodes) != len(expected):
        refuse(
            "SQ-10 evidence requires exactly "
            "16 episodes"
        )

    canonical_rows = []
    results = []

    for index, (
        episode,
        expected_condition,
    ) in enumerate(
        zip(episodes, expected)
    ):
        if set(episode) != {
            "condition",
            "topology_provenance",
            "result",
            "execution_authorized_here",
        }:
            refuse(
                f"SQ-10 episode envelope drift "
                f"at ordinal {index}"
            )

        if (
            episode[
                "execution_authorized_here"
            ]
            is not False
        ):
            refuse(
                "SQ-10 evidence packer received "
                "an execution-authorized episode"
            )

        condition = validate_condition(
            episode["condition"]
        )

        if condition != expected_condition:
            refuse(
                f"SQ-10 canonical condition "
                f"ordering drift at ordinal {index}"
            )

        result = episode["result"]
        validate_result(result)

        canonical_rows.append(condition)
        results.append(result)

    for offset in range(0, 16, 2):
        if not duplicate_pair_exact(
            episodes[offset],
            episodes[offset + 1],
        ):
            refuse(
                "SQ-10 deterministic duplicate "
                f"mismatch for "
                f"{canonical_rows[offset]['mask']}"
            )

    edge_weight = np.asarray(
        results[0]["body_edge_weight"],
        dtype=np.float32,
    ).copy()

    for result in results[1:]:
        if not np.array_equal(
            result["body_edge_weight"],
            edge_weight,
        ):
            refuse(
                "SQ-10 BODY edge weight drift "
                "across episodes"
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
            [
                int(row["mask"][0]),
                int(row["mask"][1]),
                int(row["mask"][2]),
            ]
            for row in canonical_rows
        ],
        dtype=np.uint8,
    )

    if not np.array_equal(
        condition_zeroed,
        expected_zeroed,
    ):
        refuse(
            "SQ-10 evidence lesion-coordinate "
            "drift"
        )

    arrays = {
        "condition_ordinal": np.asarray(
            [
                row["ordinal"]
                for row in canonical_rows
            ],
            dtype=np.int32,
        ),
        "condition_id": np.asarray(
            [
                row["condition_id"]
                for row in canonical_rows
            ],
            dtype="<U11",
        ),
        "condition_mask": np.asarray(
            [
                row["mask"]
                for row in canonical_rows
            ],
            dtype="<U3",
        ),
        "condition_replicate": np.asarray(
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
        "body_edge_weight":
            edge_weight,
        "condition_edge_zeroed":
            condition_zeroed,
    }

    for key in MEASUREMENT_KEYS:
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
            "SQ-10 evidence array key-set drift"
        )

    return arrays


def derive_edge_quantities(
    arrays: dict[str, np.ndarray],
) -> dict[str, np.ndarray]:
    activity = np.asarray(
        arrays[
            "source_effective_activity_pre_synaptic"
        ],
        dtype=np.float64,
    )

    weight = np.asarray(
        arrays["body_edge_weight"],
        dtype=np.float64,
    )

    zeroed = np.asarray(
        arrays["condition_edge_zeroed"],
        dtype=np.float64,
    )

    potential = (
        activity
        * weight[None, None, :]
    )

    zeroed_frame = zeroed[
        :,
        None,
        :,
    ]

    actual = (
        potential
        * (1.0 - zeroed_frame)
    )

    removed = (
        potential
        * zeroed_frame
    )

    return {
        "potential_direct_edge_drive":
            potential,
        "actual_direct_edge_contribution":
            actual,
        "removed_direct_edge_contribution":
            removed,
    }
