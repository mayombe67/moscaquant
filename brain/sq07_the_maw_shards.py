from __future__ import annotations

import hashlib
import json
import tomllib
from pathlib import Path

from brain.sq07_the_maw_plan import (
    condition_plan,
    condition_plan_sha256,
)


ROOT = Path(__file__).resolve().parents[1]

SHARDING = ROOT / "config/controls/sq07-the-maw-sharding-v1.toml"

EXPECTED_SHARDING_SHA256 = (
    "ede14b0add5d13e723c443be241504dea36d4bb0424e3f718b199b8c1c665d8a"
)

EXPECTED_PARENT_PLAN_SHA256 = (
    "850ae560ab1b25c65f9932615f8ea1851781881c4492672767bcda692667becb"
)

CONDITIONS_PER_SHARD = 64
MASKS_PER_SHARD = 16
EXPECTED_SHARD_COUNT = 512


class Refusal(RuntimeError):
    pass


def refuse(message: str) -> None:
    raise Refusal(message)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            h.update(chunk)

    return h.hexdigest()


def canonical_json_sha256(value) -> str:
    payload = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")

    return hashlib.sha256(payload).hexdigest()


def load_sharding_contract() -> dict:
    if not SHARDING.is_file():
        refuse(f"missing SQ-07 sharding contract: {SHARDING}")

    actual_sha = sha256_file(SHARDING)

    if actual_sha != EXPECTED_SHARDING_SHA256:
        refuse(
            "SQ-07 sharding contract SHA mismatch: "
            f"{actual_sha} != {EXPECTED_SHARDING_SHA256}"
        )

    with SHARDING.open("rb") as handle:
        cfg = tomllib.load(handle)

    artifact = cfg["artifact"]
    parent = cfg["parent_plan"]
    partition = cfg["partition"]
    identity = cfg["identity"]
    completeness = cfg["completeness"]
    boundaries = cfg["operational_boundaries"]

    if artifact["scientific_semantics"] is not False:
        refuse("SQ-07 shard contract may not claim scientific semantics")

    if parent["condition_plan_sha256"] != EXPECTED_PARENT_PLAN_SHA256:
        refuse("SQ-07 parent plan SHA drift")

    if parent["condition_count"] != 32768:
        refuse("SQ-07 parent condition-count drift")

    if parent["mask_count"] != 8192:
        refuse("SQ-07 parent mask-count drift")

    if parent["conditions_per_mask"] != 4:
        refuse("SQ-07 conditions-per-mask drift")

    if partition["conditions_per_shard"] != CONDITIONS_PER_SHARD:
        refuse("SQ-07 conditions-per-shard drift")

    if partition["masks_per_shard"] != MASKS_PER_SHARD:
        refuse("SQ-07 masks-per-shard drift")

    if partition["expected_shard_count"] != EXPECTED_SHARD_COUNT:
        refuse("SQ-07 shard-count drift")

    if partition["contiguous_canonical_ordinals"] is not True:
        refuse("SQ-07 shards must use contiguous canonical ordinals")

    if partition["whole_mask_quartets_required"] is not True:
        refuse("SQ-07 shards must preserve whole mask quartets")

    if partition["partial_mask_across_shards_forbidden"] is not True:
        refuse("SQ-07 partial-mask sharding must remain forbidden")

    if partition["empty_shards_forbidden"] is not True:
        refuse("SQ-07 empty shards must remain forbidden")

    if identity["shard_id_format"] != "sq07-shard-{index:03d}":
        refuse("SQ-07 shard ID format drift")

    if identity["first_shard_index"] != 0:
        refuse("SQ-07 first shard index drift")

    if identity["last_shard_index"] != 511:
        refuse("SQ-07 last shard index drift")

    if identity["condition_membership_must_be_explicit"] is not True:
        refuse("SQ-07 explicit condition membership drift")

    if identity["condition_membership_sha256_required"] is not True:
        refuse("SQ-07 condition-membership digest drift")

    if identity["parent_plan_sha256_required"] is not True:
        refuse("SQ-07 parent-plan binding drift")

    required_true = {
        "all_parent_conditions_required": completeness[
            "all_parent_conditions_required"
        ],
        "condition_duplication_across_shards_forbidden": completeness[
            "condition_duplication_across_shards_forbidden"
        ],
        "condition_omission_forbidden": completeness[
            "condition_omission_forbidden"
        ],
        "condition_substitution_forbidden": completeness[
            "condition_substitution_forbidden"
        ],
        "union_must_exactly_equal_parent_plan": completeness[
            "union_must_exactly_equal_parent_plan"
        ],
        "pairwise_shard_intersection_must_be_empty": completeness[
            "pairwise_shard_intersection_must_be_empty"
        ],
    }

    for name, value in required_true.items():
        if value is not True:
            refuse(f"SQ-07 completeness boundary drift: {name}")

    if boundaries["shard_membership_has_scientific_meaning"] is not False:
        refuse("SQ-07 shard membership may not gain scientific meaning")

    if boundaries["shard_index_has_scientific_meaning"] is not False:
        refuse("SQ-07 shard index may not gain scientific meaning")

    if boundaries["shard_size_has_scientific_meaning"] is not False:
        refuse("SQ-07 shard size may not gain scientific meaning")

    if boundaries["adaptive_condition_selection_forbidden"] is not True:
        refuse("SQ-07 adaptive condition selection drift")

    if boundaries["mask_pruning_forbidden"] is not True:
        refuse("SQ-07 mask-pruning boundary drift")

    if boundaries["early_stopping_based_on_results_forbidden"] is not True:
        refuse("SQ-07 result-driven early stopping boundary drift")

    if boundaries["sharding_does_not_authorize_neural_execution"] is not True:
        refuse("SQ-07 sharding may not authorize neural execution")

    if boundaries["sharding_does_not_authorize_result_execution"] is not True:
        refuse("SQ-07 sharding may not authorize result execution")

    return cfg


def condition_membership_sha256(rows: list[dict]) -> str:
    return canonical_json_sha256(
        [row["condition_id"] for row in rows]
    )


def shard_plan() -> list[dict]:
    cfg = load_sharding_contract()

    plan = condition_plan()

    parent_sha = condition_plan_sha256(plan)

    if parent_sha != EXPECTED_PARENT_PLAN_SHA256:
        refuse(
            f"SQ-07 parent condition plan SHA drift: "
            f"{parent_sha} != {EXPECTED_PARENT_PLAN_SHA256}"
        )

    expected_conditions = cfg["parent_plan"]["condition_count"]

    if len(plan) != expected_conditions:
        refuse(
            f"SQ-07 parent condition count drift: "
            f"{len(plan)} != {expected_conditions}"
        )

    shards = []

    for shard_index in range(EXPECTED_SHARD_COUNT):
        start = shard_index * CONDITIONS_PER_SHARD
        stop = start + CONDITIONS_PER_SHARD

        rows = plan[start:stop]

        if len(rows) != CONDITIONS_PER_SHARD:
            refuse(f"SQ-07 incomplete shard construction at {shard_index}")

        ordinals = [row["ordinal"] for row in rows]

        if ordinals != list(range(start, stop)):
            refuse(f"SQ-07 non-contiguous ordinals in shard {shard_index}")

        masks = []
        seen_masks = set()

        for row in rows:
            mask13 = row["mask13"]

            if mask13 not in seen_masks:
                seen_masks.add(mask13)
                masks.append(mask13)

        if len(masks) != MASKS_PER_SHARD:
            refuse(f"SQ-07 mask-count drift in shard {shard_index}")

        for mask13 in masks:
            mask_rows = [row for row in rows if row["mask13"] == mask13]

            if len(mask_rows) != 4:
                refuse(
                    f"SQ-07 partial mask quartet in shard {shard_index}: "
                    f"{mask13}"
                )

            coordinates = [
                (row["layout"], row["replicate"])
                for row in mask_rows
            ]

            if coordinates != [
                ("LR", 1),
                ("LR", 2),
                ("RL", 1),
                ("RL", 2),
            ]:
                refuse(
                    f"SQ-07 mask coordinate drift in shard {shard_index}: "
                    f"{mask13}"
                )

        descriptor = {
            "shard_id": f"sq07-shard-{shard_index:03d}",
            "shard_index": shard_index,
            "parent_plan_sha256": parent_sha,
            "sharding_contract_sha256": EXPECTED_SHARDING_SHA256,
            "start_ordinal": start,
            "end_ordinal_exclusive": stop,
            "condition_count": len(rows),
            "mask_count": len(masks),
            "first_condition_id": rows[0]["condition_id"],
            "last_condition_id": rows[-1]["condition_id"],
            "condition_ids": [row["condition_id"] for row in rows],
            "condition_membership_sha256": condition_membership_sha256(rows),
        }

        shards.append(descriptor)

    verify_shard_plan(shards, plan)

    return shards


def verify_shard_plan(
    shards: list[dict],
    parent_plan: list[dict] | None = None,
) -> dict:
    plan = condition_plan() if parent_plan is None else parent_plan

    if len(shards) != EXPECTED_SHARD_COUNT:
        refuse(
            f"SQ-07 shard count drift: "
            f"{len(shards)} != {EXPECTED_SHARD_COUNT}"
        )

    expected_ids = [row["condition_id"] for row in plan]
    observed_ids = []

    observed_shard_ids = set()

    for expected_index, shard in enumerate(shards):
        if shard["shard_index"] != expected_index:
            refuse("SQ-07 shard-index ordering drift")

        expected_shard_id = f"sq07-shard-{expected_index:03d}"

        if shard["shard_id"] != expected_shard_id:
            refuse(f"SQ-07 shard-id drift at {expected_index}")

        if shard["shard_id"] in observed_shard_ids:
            refuse(f"SQ-07 duplicate shard ID: {shard['shard_id']}")

        observed_shard_ids.add(shard["shard_id"])

        if shard["parent_plan_sha256"] != EXPECTED_PARENT_PLAN_SHA256:
            refuse(f"SQ-07 shard parent-plan binding drift: {shard['shard_id']}")

        if shard["sharding_contract_sha256"] != EXPECTED_SHARDING_SHA256:
            refuse(
                f"SQ-07 shard contract binding drift: {shard['shard_id']}"
            )

        ids = shard["condition_ids"]

        if len(ids) != CONDITIONS_PER_SHARD:
            refuse(f"SQ-07 shard condition-count drift: {shard['shard_id']}")

        if len(set(ids)) != CONDITIONS_PER_SHARD:
            refuse(f"SQ-07 duplicate condition within shard: {shard['shard_id']}")

        expected_membership_sha = hashlib.sha256(
            json.dumps(
                ids,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=True,
            ).encode("utf-8")
        ).hexdigest()

        if shard["condition_membership_sha256"] != expected_membership_sha:
            refuse(
                f"SQ-07 shard membership digest mismatch: {shard['shard_id']}"
            )

        observed_ids.extend(ids)

    if len(observed_ids) != len(expected_ids):
        refuse("SQ-07 shard union cardinality drift")

    if len(set(observed_ids)) != len(expected_ids):
        refuse("SQ-07 shard condition duplication detected")

    if observed_ids != expected_ids:
        refuse("SQ-07 shard union/order does not exactly equal parent plan")

    return {
        "shard_count": len(shards),
        "condition_count": len(observed_ids),
        "unique_condition_count": len(set(observed_ids)),
        "parent_plan_sha256": EXPECTED_PARENT_PLAN_SHA256,
        "sharding_contract_sha256": EXPECTED_SHARDING_SHA256,
    }


def shard_plan_sha256(shards: list[dict] | None = None) -> str:
    rows = shard_plan() if shards is None else shards

    if len(rows) != EXPECTED_SHARD_COUNT:
        refuse("SQ-07 shard-plan digest refuses incomplete shard universe")

    h = hashlib.sha256()

    for row in rows:
        payload = json.dumps(
            row,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("utf-8")

        h.update(payload)
        h.update(b"\n")

    return h.hexdigest()
