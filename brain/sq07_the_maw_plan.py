from __future__ import annotations

import hashlib
import json
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

PREREG = ROOT / "config/controls/sq07-the-maw-v1.toml"
REGISTRY = ROOT / "config/controls/sq07-the-maw-edge-registry-v1.json"

EXPECTED_SHA256 = {
    "prereg": "0ff34f0f4c2c1315b766ecc1acf66e2e6c24650aba87ae033e5a71a2b707a84a",
    "registry": "0e9502f3147d2f833d00ce2c05af258b973f7391a43c9d89f695556d8823dedd",
}

MASK_WIDTH = 13
MASK_COUNT = 2**MASK_WIDTH

LAYOUTS = ("LR", "RL")
REPLICATES = (1, 2)

EXPECTED_CONDITION_COUNT = MASK_COUNT * len(LAYOUTS) * len(REPLICATES)

INTACT_MASK = "0000000000000"
FULL13_MASK = "1111111111111"
LR_GROUP_MASK = "1111111111000"
RL_GROUP_MASK = "0000000000111"


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


def verify_frozen_authority() -> dict:
    paths = {
        "prereg": PREREG,
        "registry": REGISTRY,
    }

    observed = {}

    for name, path in paths.items():
        if not path.is_file():
            refuse(f"missing frozen SQ-07 authority: {name}: {path}")

        actual = sha256_file(path)
        expected = EXPECTED_SHA256[name]

        if actual != expected:
            refuse(
                f"SQ-07 frozen authority SHA mismatch for {name}: "
                f"{actual} != {expected}"
            )

        observed[name] = actual

    with PREREG.open("rb") as handle:
        prereg = tomllib.load(handle)

    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))

    edge = prereg["edge_universe"]
    mask = prereg["mask_contract"]
    execution = prereg["execution_universe"]
    authority = prereg["human_command_authority"]

    if edge["edge_count"] != MASK_WIDTH:
        refuse("SQ-07 edge-count drift")

    if edge["lr_observed_indices"] != list(range(10)):
        refuse("SQ-07 LR edge-coordinate drift")

    if edge["rl_observed_indices"] != [10, 11, 12]:
        refuse("SQ-07 RL edge-coordinate drift")

    if mask["representation"] != "13-character binary string":
        refuse("SQ-07 mask representation drift")

    if mask["enumeration"] != "lexicographic ascending":
        refuse("SQ-07 mask enumeration drift")

    if mask["intact_mask"] != INTACT_MASK:
        refuse("SQ-07 INTACT mask drift")

    if mask["full13_mask"] != FULL13_MASK:
        refuse("SQ-07 FULL13 mask drift")

    if mask["lr_group_mask"] != LR_GROUP_MASK:
        refuse("SQ-07 LR-group mask drift")

    if mask["rl_group_mask"] != RL_GROUP_MASK:
        refuse("SQ-07 RL-group mask drift")

    if mask["mask_count_per_layout"] != MASK_COUNT:
        refuse("SQ-07 mask-count drift")

    if tuple(prereg["stimulus"]["layouts"]) != LAYOUTS:
        refuse("SQ-07 layout-order drift")

    if tuple(execution["replicates"]) != REPLICATES:
        refuse("SQ-07 replicate-order drift")

    if execution["expected_unique_masks_per_layout"] != MASK_COUNT:
        refuse("SQ-07 unique-mask-count drift")

    if execution["expected_total_episode_count"] != EXPECTED_CONDITION_COUNT:
        refuse("SQ-07 total-condition-count drift")

    if authority["human_execution_authorization_required"] is not True:
        refuse("SQ-07 human-command authority drift")

    if authority["authorization_must_be_explicit_and_run_specific"] is not True:
        refuse("SQ-07 run-specific human authorization drift")

    edges = registry["edges"]

    if len(edges) != MASK_WIDTH:
        refuse("SQ-07 registry edge-count drift")

    for i, row in enumerate(edges):
        if row["edge_index"] != i:
            refuse(f"SQ-07 registry edge-index drift at {i}")

        if row["edge_id"] != f"E{i:02d}":
            refuse(f"SQ-07 registry edge-id drift at {i}")

        expected_group = "LR_OBSERVED" if i < 10 else "RL_OBSERVED"

        if row["sq06_group"] != expected_group:
            refuse(f"SQ-07 registry group drift at E{i:02d}")

    registry_mask = registry["mask_contract"]

    if registry_mask["length"] != MASK_WIDTH:
        refuse("SQ-07 registry mask-width drift")

    if registry_mask["subset_count"] != MASK_COUNT:
        refuse("SQ-07 registry subset-count drift")

    if registry_mask["enumeration"] != "lexicographic ascending":
        refuse("SQ-07 registry enumeration drift")

    if registry_mask["character_index_semantics"] != "mask13[i] corresponds to edges[i]":
        refuse("SQ-07 registry coordinate semantics drift")

    return {
        "prereg_sha256": observed["prereg"],
        "registry_sha256": observed["registry"],
        "edge_count": MASK_WIDTH,
        "mask_count": MASK_COUNT,
        "condition_count": EXPECTED_CONDITION_COUNT,
    }


def masks() -> tuple[str, ...]:
    result = tuple(f"{value:0{MASK_WIDTH}b}" for value in range(MASK_COUNT))

    if len(result) != MASK_COUNT:
        refuse("SQ-07 mask construction count drift")

    if result[0] != INTACT_MASK or result[-1] != FULL13_MASK:
        refuse("SQ-07 mask endpoint drift")

    if list(result) != sorted(result):
        refuse("SQ-07 mask lexicographic-order drift")

    return result


def condition_id(mask13: str, layout: str, replicate: int) -> str:
    if len(mask13) != MASK_WIDTH or set(mask13) - {"0", "1"}:
        raise ValueError(f"invalid mask13: {mask13!r}")

    if layout not in LAYOUTS:
        raise ValueError(f"invalid layout: {layout!r}")

    if replicate not in REPLICATES:
        raise ValueError(f"invalid replicate: {replicate!r}")

    return f"sq07:{mask13}:{layout}:r{replicate}"


def condition_plan() -> list[dict]:
    verify_frozen_authority()

    plan = []
    ordinal = 0

    for mask13 in masks():
        for layout in LAYOUTS:
            for replicate in REPLICATES:
                plan.append(
                    {
                        "ordinal": ordinal,
                        "condition_id": condition_id(mask13, layout, replicate),
                        "mask13": mask13,
                        "layout": layout,
                        "replicate": replicate,
                    }
                )
                ordinal += 1

    if len(plan) != EXPECTED_CONDITION_COUNT:
        refuse(
            f"SQ-07 condition-plan count drift: "
            f"{len(plan)} != {EXPECTED_CONDITION_COUNT}"
        )

    if len({row["condition_id"] for row in plan}) != EXPECTED_CONDITION_COUNT:
        refuse("SQ-07 condition IDs are not globally unique")

    return plan


def condition_plan_sha256(plan: list[dict] | None = None) -> str:
    rows = condition_plan() if plan is None else plan

    if len(rows) != EXPECTED_CONDITION_COUNT:
        refuse("SQ-07 plan digest refuses incomplete condition universe")

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
