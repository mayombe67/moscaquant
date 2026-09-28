from __future__ import annotations

from brain.sq10_sophon_plan import (
    MASKS as SQ10_MASKS,
    REPLICATES as SQ10_REPLICATES,
)


MASKS = (
    "000",
    "001",
    "010",
    "011",
    "100",
    "101",
    "110",
    "111",
)

REPLICATES = (1, 2)


if tuple(SQ10_MASKS) != MASKS:
    raise RuntimeError(
        "SQ-10 mask universe drift"
    )

if tuple(SQ10_REPLICATES) != REPLICATES:
    raise RuntimeError(
        "SQ-10 replicate universe drift"
    )


def expected_ordinal(
    mask: str,
    replicate: int,
) -> int:
    if mask not in MASKS:
        raise ValueError(
            f"invalid SQ-11 mask: {mask!r}"
        )

    if replicate not in REPLICATES:
        raise ValueError(
            f"invalid SQ-11 replicate: {replicate!r}"
        )

    return (
        MASKS.index(mask) * 2
        + (replicate - 1)
    )


def expected_condition_id(
    mask: str,
    replicate: int,
) -> str:
    expected_ordinal(
        mask,
        replicate,
    )

    return f"sq11:{mask}:r{replicate}"


def edge_zeroed(
    mask: str,
) -> list[int]:
    if mask not in MASKS:
        raise ValueError(
            f"invalid SQ-11 mask: {mask!r}"
        )

    return [
        int(bit)
        for bit in mask
    ]


def validate_condition(
    condition: dict,
) -> dict:
    required = {
        "ordinal",
        "condition_id",
        "mask",
        "replicate",
        "edge_zeroed",
    }

    if set(condition) != required:
        raise ValueError(
            "SQ-11 condition key-set drift"
        )

    mask = condition["mask"]
    replicate = condition["replicate"]

    if (
        condition["ordinal"]
        != expected_ordinal(
            mask,
            replicate,
        )
    ):
        raise ValueError(
            "SQ-11 ordinal drift"
        )

    if (
        condition["condition_id"]
        != expected_condition_id(
            mask,
            replicate,
        )
    ):
        raise ValueError(
            "SQ-11 condition-ID drift"
        )

    if (
        condition["edge_zeroed"]
        != edge_zeroed(mask)
    ):
        raise ValueError(
            "SQ-11 lesion-coordinate drift"
        )

    return dict(condition)


def build_conditions() -> list[dict]:
    rows = []

    for mask in MASKS:
        for replicate in REPLICATES:
            rows.append(
                validate_condition(
                    {
                        "ordinal":
                            expected_ordinal(
                                mask,
                                replicate,
                            ),

                        "condition_id":
                            expected_condition_id(
                                mask,
                                replicate,
                            ),

                        "mask":
                            mask,

                        "replicate":
                            replicate,

                        "edge_zeroed":
                            edge_zeroed(mask),
                    }
                )
            )

    if len(rows) != 16:
        raise RuntimeError(
            "SQ-11 plan must contain "
            "exactly 16 units"
        )

    return rows
