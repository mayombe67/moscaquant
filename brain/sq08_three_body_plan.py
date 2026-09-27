from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path


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

CONNECTOME_SHA256 = (
    "e00e3f2a9828c921fe1f093cc567bf45"
    "a85adad0526176be0aa1b8be09336eeb"
)

CALIBRATION_SHA256 = (
    "1f5e5bb25c9bd0a403f0f47d5b4c587"
    "0a53cfbbe0f5ebcfb945ad73d4859c075"
)

FRONTIER_SHA256 = (
    "ad87e904c13698552d3e52fb58e9558a"
    "efe4e0898a2ef6bb45b3c64652196361"
)

EVIDENCE_SCHEMA_SHA256 = (
    "9f9e4465eb26b1bf5c85befcc624a0d1"
    "b9f84ffe8359281b212ff0883d47cdc2"
)

OUTPUT = Path(
    "config/controls/"
    "sq08-three-body-execution-manifest-v1.json"
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def science_git_sha() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"],
        text=True,
    ).strip()


def condition_id(mask: str, replicate: int) -> str:
    if mask not in MASKS:
        raise ValueError(f"invalid SQ-08 mask: {mask}")

    if replicate not in REPLICATES:
        raise ValueError(
            f"invalid SQ-08 replicate: {replicate}"
        )

    return f"sq08:{mask}:r{replicate}"


def build_conditions() -> list[dict]:
    rows = []

    ordinal = 0

    for mask in MASKS:
        for replicate in REPLICATES:
            rows.append(
                {
                    "ordinal": ordinal,
                    "condition_id": condition_id(
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

    return rows


def main() -> None:
    conditions = build_conditions()

    if len(conditions) != 16:
        raise RuntimeError(
            "SQ-08 execution universe must contain "
            "exactly 16 work units"
        )

    ids = [
        row["condition_id"]
        for row in conditions
    ]

    if len(ids) != len(set(ids)):
        raise RuntimeError(
            "duplicate SQ-08 condition IDs"
        )

    covered_masks = {
        row["mask"]
        for row in conditions
    }

    if covered_masks != set(MASKS):
        raise RuntimeError(
            "incomplete SQ-08 Boolean cube"
        )

    for mask in MASKS:
        reps = {
            row["replicate"]
            for row in conditions
            if row["mask"] == mask
        }

        if reps != {1, 2}:
            raise RuntimeError(
                f"incomplete replicates for {mask}"
            )

    payload = {
        "schema_version": (
            "moscaquant."
            "sq08-three-body-execution-manifest/v1"
        ),
        "experiment": "SQ-08",
        "codename": "THREE BODY PROBLEM",
        "status": "FROZEN_PRE_EXECUTION",
        "science_git_sha": science_git_sha(),
        "execution_contract": {
            "condition_masks": list(MASKS),
            "replicates": list(REPLICATES),
            "work_unit_count": 16,
            "body_order": ["A", "B", "C"],
        },
        "frozen_inputs": {
            "connectome_sha256":
                CONNECTOME_SHA256,
            "topology_calibration_sha256":
                CALIBRATION_SHA256,
            "topology_frontier_sha256":
                FRONTIER_SHA256,
            "evidence_schema_sha256":
                EVIDENCE_SCHEMA_SHA256,
        },
        "conditions": conditions,
        "integrity": {
            "all_16_work_units_required": True,
            "both_replicates_required_per_mask": True,
            "duplicate_condition_ids_forbidden": True,
            "extra_conditions_forbidden": True,
            "missing_conditions_forbidden": True,
            "condition_id_must_match_mask_and_replicate": True,
        },
    }

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT.write_text(
        json.dumps(
            payload,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )

    print("SQ-08 execution manifest frozen")
    print("science git sha:", payload["science_git_sha"])
    print("work units:", len(conditions))

    for row in conditions:
        print(
            f'{row["ordinal"]:02d}',
            row["condition_id"],
            row["body_state"],
        )

    print("output:", OUTPUT)
    print(
        "output sha256:",
        sha256_file(OUTPUT),
    )


if __name__ == "__main__":
    main()
