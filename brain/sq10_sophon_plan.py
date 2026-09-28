from __future__ import annotations

from brain.sq08_three_body_plan import (
    MASKS as SQ08_MASKS,
    REPLICATES as SQ08_REPLICATES,
)


EXPECTED_MASKS = (
    "000",
    "001",
    "010",
    "011",
    "100",
    "101",
    "110",
    "111",
)

EXPECTED_REPLICATES = (1, 2)

MASKS = tuple(SQ08_MASKS)
REPLICATES = tuple(SQ08_REPLICATES)


if MASKS != EXPECTED_MASKS:
    raise RuntimeError(
        "SQ-10 inherited SQ-08 mask universe drift"
    )

if REPLICATES != EXPECTED_REPLICATES:
    raise RuntimeError(
        "SQ-10 inherited SQ-08 replicate contract drift"
    )


def condition_id(
    mask: str,
    replicate: int,
) -> str:
    if mask not in MASKS:
        raise ValueError(
            f"invalid SQ-10 mask: {mask!r}"
        )

    if replicate not in REPLICATES:
        raise ValueError(
            f"invalid SQ-10 replicate: {replicate}"
        )

    return f"sq10:{mask}:r{replicate}"


def build_conditions() -> list[dict]:
    rows = []
    ordinal = 0

    for mask in MASKS:
        for replicate in REPLICATES:
            rows.append(
                {
                    "ordinal": ordinal,
                    "condition_id":
                        condition_id(
                            mask,
                            replicate,
                        ),
                    "mask": mask,
                    "replicate": replicate,
                    "edge_zeroed": {
                        "A": int(mask[0]),
                        "B": int(mask[1]),
                        "C": int(mask[2]),
                    },
                }
            )

            ordinal += 1

    if len(rows) != 16:
        raise RuntimeError(
            "SQ-10 condition universe must "
            "contain exactly 16 episodes"
        )

    ids = [
        row["condition_id"]
        for row in rows
    ]

    if len(ids) != len(set(ids)):
        raise RuntimeError(
            "duplicate SQ-10 condition IDs"
        )

    return rows
