from __future__ import annotations

import hashlib
import os
import subprocess
import tomllib
from functools import lru_cache
from pathlib import Path

from brain.sq07_the_maw_plan import condition_plan_sha256
from brain.sq07_the_maw_shards import (
    shard_plan,
    shard_plan_sha256,
)


ROOT = Path(__file__).resolve().parents[1]

DATA_ROOT = Path(
    os.environ.get(
        "MOSCAQUANT_DATA_ROOT",
        str(Path.home() / "moscaquant-data"),
    )
).expanduser().resolve()

CONFIG = ROOT / "config/controls/sq07-the-maw-readiness-v1.toml"

PREREG = ROOT / "config/controls/sq07-the-maw-v1.toml"
SHARDING = ROOT / "config/controls/sq07-the-maw-sharding-v1.toml"
EVIDENCE_SCHEMA = (
    ROOT / "config/controls/sq07-the-maw-evidence-schema-v1.json"
)
THROAT_CONFIG = (
    ROOT / "config/controls/sq07-the-maw-shard-runner-v1.toml"
)

PLAN_SOURCE = ROOT / "brain/sq07_the_maw_plan.py"
SHARDS_SOURCE = ROOT / "brain/sq07_the_maw_shards.py"
SUBSET_SOURCE = ROOT / "brain/sq07_the_maw_subset.py"
EPISODE_SOURCE = ROOT / "brain/sq07_the_maw_episode.py"
EVIDENCE_SOURCE = ROOT / "brain/sq07_the_maw_evidence.py"
THROAT_SOURCE = ROOT / "brain/sq07_the_maw_shard_runner.py"
THROAT_TEST = ROOT / "tests/brain/test_sq07_the_maw_shard_runner.py"

AUTHORIZATION_DIR = ROOT / "config/controls/sq07-authorizations"

RESULT_ROOT = (
    DATA_ROOT
    / "experiments"
    / "sq07-the-maw-v1"
)

EXPECTED_BRANCH = "science/sq07-the-maw"

EXPECTED_IMPLEMENTATION_COMMIT = (
    "e6c740cc5020b219f0ee98c285a309645e1260c0"
)

EXPECTED_CONDITION_PLAN_SHA256 = (
    "850ae560ab1b25c65f9932615f8ea1851781881c4492672767bcda692667becb"
)

EXPECTED_SHARD_PLAN_SHA256 = (
    "9039b8e708c2ffdb74436e5c6fdc8f7d2f38f3f3fb27fd7478dd2cc8101d2a55"
)

EXPECTED_HASHES = {
    "preregistration": (
        "0ff34f0f4c2c1315b766ecc1acf66e2e6c24650aba87ae033e5a71a2b707a84a"
    ),
    "sharding_contract": (
        "ede14b0add5d13e723c443be241504dea36d4bb0424e3f718b199b8c1c665d8a"
    ),
    "condition_planner": (
        "38b8e628492a475f63c40c332232b36c929512dfae8341f5b64afd1597f5411f"
    ),
    "shard_planner": (
        "7cde07ad921543cdb9dba95f3299ccb4a1cfbb20f32a3a75fc678a2df61ef1af"
    ),
    "subset_operator": (
        "693ae8c2455361351802d0ac0c9cee4ada3bb8a25a60043264de5da14da00a5e"
    ),
    "episode_executor": (
        "a4b85e45779ab98c9a1275a0e97ced9f1abb48bfadd974319bfcecf4305be9d8"
    ),
    "evidence_schema": (
        "c1065506a90b26856896e0a522c7023738de13b0ac5af7a17cea7973774d2f01"
    ),
    "evidence_writer": (
        "255427764b0f0b49273c27c44f000ecb50628fc7d129ec8dc9fcfddeb0af3e11"
    ),
    "shard_runner_config": (
        "a6e77226e50999b3dbc0ada7c64a8b5905ce638f92339406d724d9aa54e403ad"
    ),
    "shard_runner": (
        "bd736984acad6bbdceb812ca84ee6d413acaaa0f864f4a48899f9fbfacf87312"
    ),
    "shard_runner_test": (
        "f4028b709bbdc8679a2ceb70a9c3ec98b52e5ffe0f0826abc4bac6a8ab0c9c2d"
    ),
}

EXPECTED_MASK_COUNT = 8192
EXPECTED_CONDITION_COUNT = 32768
EXPECTED_SHARD_COUNT = 512
CONDITIONS_PER_SHARD = 64
MASKS_PER_SHARD = 16


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


def _git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


@lru_cache(maxsize=1)
def load_config() -> dict:
    payload = tomllib.loads(
        CONFIG.read_text(encoding="utf-8")
    )

    readiness = payload["readiness"]
    universe = payload["universe"]
    authority = payload["authority"]
    hashes = payload["hashes"]
    boundaries = payload["boundaries"]

    if readiness["id"] != "sq07-the-maw-readiness-v1":
        refuse("SQ-07 readiness config ID drift")

    if readiness["expected_branch"] != EXPECTED_BRANCH:
        refuse("SQ-07 readiness branch drift")

    if readiness["may_execute"] is not False:
        refuse("SQ-07 readiness may never authorize execution")

    expected_universe = {
        "expected_mask_count": 8192,
        "expected_condition_count": 32768,
        "expected_shard_count": 512,
        "conditions_per_shard": 64,
        "masks_per_shard": 16,
        "conditions_per_mask": 4,
        "condition_plan_sha256": EXPECTED_CONDITION_PLAN_SHA256,
        "shard_plan_sha256": EXPECTED_SHARD_PLAN_SHA256,
    }

    for key, value in expected_universe.items():
        if universe.get(key) != value:
            refuse(f"SQ-07 readiness universe drift: {key}")

    if (
        authority["execution_implementation_commit"]
        != EXPECTED_IMPLEMENTATION_COMMIT
    ):
        refuse("SQ-07 readiness implementation commit drift")

    for key in (
        "implementation_commit_must_be_ancestor_of_readiness_head",
        "git_worktree_must_be_clean",
        "authorization_must_be_absent",
        "result_root_must_be_absent",
    ):
        if authority.get(key) is not True:
            refuse(f"SQ-07 readiness authority drift: {key}")

    if hashes != EXPECTED_HASHES:
        refuse("SQ-07 readiness frozen hash table drift")

    if any(boundaries.values()):
        refuse("SQ-07 readiness boundary drift")

    return payload


@lru_cache(maxsize=1)
def verify_frozen_dependencies() -> dict:
    load_config()

    paths = {
        "preregistration": PREREG,
        "sharding_contract": SHARDING,
        "condition_planner": PLAN_SOURCE,
        "shard_planner": SHARDS_SOURCE,
        "subset_operator": SUBSET_SOURCE,
        "episode_executor": EPISODE_SOURCE,
        "evidence_schema": EVIDENCE_SCHEMA,
        "evidence_writer": EVIDENCE_SOURCE,
        "shard_runner_config": THROAT_CONFIG,
        "shard_runner": THROAT_SOURCE,
        "shard_runner_test": THROAT_TEST,
    }

    observed = {}

    for name, path in paths.items():
        if not path.is_file():
            refuse(f"missing SQ-07 readiness dependency: {name}")

        actual = sha256_file(path)
        expected = EXPECTED_HASHES[name]

        if actual != expected:
            refuse(
                f"SQ-07 readiness dependency SHA drift for {name}: "
                f"{actual} != {expected}"
            )

        observed[name] = actual

    actual_condition_plan = condition_plan_sha256()

    if actual_condition_plan != EXPECTED_CONDITION_PLAN_SHA256:
        refuse("SQ-07 condition-plan SHA drift")

    shards = shard_plan()
    actual_shard_plan = shard_plan_sha256(shards)

    if actual_shard_plan != EXPECTED_SHARD_PLAN_SHA256:
        refuse("SQ-07 shard-plan SHA drift")

    return {
        "file_sha256": observed,
        "condition_plan_sha256": actual_condition_plan,
        "shard_plan_sha256": actual_shard_plan,
    }


def expected_condition_id(ordinal: int) -> str:
    if not isinstance(ordinal, int):
        raise TypeError("ordinal must be int")

    if ordinal < 0 or ordinal >= EXPECTED_CONDITION_COUNT:
        raise ValueError("ordinal outside SQ-07 universe")

    mask_value, slot = divmod(ordinal, 4)
    mask13 = f"{mask_value:013b}"

    layout, replicate = (
        ("LR", 1),
        ("LR", 2),
        ("RL", 1),
        ("RL", 2),
    )[slot]

    return f"sq07:{mask13}:{layout}:r{replicate}"


def verify_complete_universe() -> dict:
    shards = shard_plan()

    if len(shards) != EXPECTED_SHARD_COUNT:
        refuse(
            f"expected {EXPECTED_SHARD_COUNT} shards, "
            f"got {len(shards)}"
        )

    observed_ids = []

    for index, shard in enumerate(shards):
        expected_start = index * CONDITIONS_PER_SHARD
        expected_end = expected_start + CONDITIONS_PER_SHARD

        checks = {
            "shard_index": index,
            "shard_id": f"sq07-shard-{index:03d}",
            "parent_plan_sha256": EXPECTED_CONDITION_PLAN_SHA256,
            "sharding_contract_sha256": EXPECTED_HASHES[
                "sharding_contract"
            ],
            "start_ordinal": expected_start,
            "end_ordinal_exclusive": expected_end,
            "condition_count": CONDITIONS_PER_SHARD,
            "mask_count": MASKS_PER_SHARD,
        }

        for key, value in checks.items():
            if shard.get(key) != value:
                refuse(
                    f"SQ-07 canonical shard {index} drift: {key}"
                )

        condition_ids = shard.get("condition_ids")

        if (
            not isinstance(condition_ids, list)
            or len(condition_ids) != CONDITIONS_PER_SHARD
        ):
            refuse(
                f"SQ-07 shard {index} condition-list drift"
            )

        if len(set(condition_ids)) != CONDITIONS_PER_SHARD:
            refuse(
                f"SQ-07 shard {index} contains duplicate conditions"
            )

        if shard.get("first_condition_id") != condition_ids[0]:
            refuse(
                f"SQ-07 shard {index} first-condition drift"
            )

        if shard.get("last_condition_id") != condition_ids[-1]:
            refuse(
                f"SQ-07 shard {index} last-condition drift"
            )

        membership_sha = shard.get(
            "condition_membership_sha256"
        )

        if (
            not isinstance(membership_sha, str)
            or len(membership_sha) != 64
        ):
            refuse(
                f"SQ-07 shard {index} membership SHA drift"
            )

        observed_ids.extend(condition_ids)

    if len(observed_ids) != EXPECTED_CONDITION_COUNT:
        refuse("SQ-07 condition-universe size drift")

    if len(set(observed_ids)) != EXPECTED_CONDITION_COUNT:
        refuse("SQ-07 condition-universe overlap detected")

    for ordinal, condition_id in enumerate(observed_ids):
        expected = expected_condition_id(ordinal)

        if condition_id != expected:
            refuse(
                "SQ-07 condition-universe order/identity drift "
                f"at ordinal {ordinal}"
            )

    masks = {
        condition_id.split(":")[1]
        for condition_id in observed_ids
    }

    if len(masks) != EXPECTED_MASK_COUNT:
        refuse("SQ-07 mask-universe size drift")

    if masks != {
        f"{value:013b}"
        for value in range(EXPECTED_MASK_COUNT)
    }:
        refuse("SQ-07 mask-universe identity drift")

    return {
        "mask_count": len(masks),
        "condition_count": len(observed_ids),
        "unique_condition_count": len(set(observed_ids)),
        "shard_count": len(shards),
        "conditions_per_shard": CONDITIONS_PER_SHARD,
        "masks_per_shard": MASKS_PER_SHARD,
        "overlap_count": 0,
        "omission_count": 0,
        "canonical_order_exact": True,
    }


def authorization_files() -> list[str]:
    if not AUTHORIZATION_DIR.exists():
        return []

    if not AUTHORIZATION_DIR.is_dir():
        refuse("SQ-07 authorization path exists but is not a directory")

    return sorted(
        str(path.relative_to(ROOT))
        for path in AUTHORIZATION_DIR.rglob("*")
        if path.is_file()
    )


def git_state() -> dict:
    head = _git("rev-parse", "HEAD")
    branch = _git("rev-parse", "--abbrev-ref", "HEAD")
    status = _git("status", "--porcelain")

    if (
        head.returncode != 0
        or branch.returncode != 0
        or status.returncode != 0
    ):
        refuse("unable to resolve SQ-07 Git readiness state")

    ancestry = _git(
        "merge-base",
        "--is-ancestor",
        EXPECTED_IMPLEMENTATION_COMMIT,
        "HEAD",
    )

    return {
        "head": head.stdout.strip(),
        "branch": branch.stdout.strip(),
        "clean": status.stdout.strip() == "",
        "implementation_commit_is_ancestor": (
            ancestry.returncode == 0
        ),
    }


def evaluate_readiness() -> dict:
    dependencies = verify_frozen_dependencies()
    universe = verify_complete_universe()
    git = git_state()

    auth_files = authorization_files()
    authorization_absent = len(auth_files) == 0

    result_root_absent = not RESULT_ROOT.exists()

    checks = {
        "frozen_dependencies_exact": True,
        "condition_universe_exact": (
            universe["condition_count"]
            == EXPECTED_CONDITION_COUNT
        ),
        "mask_universe_exact": (
            universe["mask_count"]
            == EXPECTED_MASK_COUNT
        ),
        "shard_universe_exact": (
            universe["shard_count"]
            == EXPECTED_SHARD_COUNT
        ),
        "condition_overlap_absent": (
            universe["overlap_count"] == 0
        ),
        "condition_omission_absent": (
            universe["omission_count"] == 0
        ),
        "canonical_condition_order_exact": (
            universe["canonical_order_exact"]
        ),
        "expected_branch": (
            git["branch"] == EXPECTED_BRANCH
        ),
        "git_worktree_clean": git["clean"],
        "execution_implementation_is_ancestor": (
            git["implementation_commit_is_ancestor"]
        ),
        "authorization_absent": authorization_absent,
        "result_root_absent": result_root_absent,
    }

    ready = all(checks.values())

    return {
        "artifact": "sq07-the-maw-readiness-report-v1",
        "scientific_readiness": (
            "READY" if ready else "NOT_READY"
        ),
        "human_execution_authorization": (
            "ABSENT"
            if authorization_absent
            else "PRESENT"
        ),
        "result_execution": (
            "NOT_STARTED"
            if result_root_absent
            else "RESULT_ROOT_PRESENT"
        ),
        "real_episode_count": 0 if result_root_absent else None,
        "may_execute": False,
        "ready_but_not_authorized": (
            ready and authorization_absent
        ),
        "checks": checks,
        "git": git,
        "authorization_files": auth_files,
        "result_root": str(RESULT_ROOT),
        "universe": universe,
        "dependencies": dependencies,
        "boundaries": {
            "execution_authorized_by_this_report": False,
            "neural_execution_performed": False,
            "authorization_created": False,
            "results_created": False,
            "results_classified": False,
        },
    }
