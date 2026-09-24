from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import time
import tomllib
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path

import numpy as np
from scipy import sparse

from brain.sq05_two_betrayals_runner import (
    CONNECTOME,
    RETINA,
    load_primary_population,
)
from brain.sq07_the_maw_episode import execute_condition
from brain.sq07_the_maw_evidence import (
    canonical_shard,
    parse_condition_id,
    write_shard_evidence,
)


ROOT = Path(__file__).resolve().parents[1]

DATA_ROOT = Path(
    os.environ.get(
        "MOSCAQUANT_DATA_ROOT",
        str(Path.home() / "moscaquant-data"),
    )
).expanduser().resolve()

RUNNER_CONFIG = (
    ROOT / "config/controls/sq07-the-maw-shard-runner-v1.toml"
)
PREREG = ROOT / "config/controls/sq07-the-maw-v1.toml"
SHARDING = ROOT / "config/controls/sq07-the-maw-sharding-v1.toml"
EVIDENCE_SCHEMA = (
    ROOT / "config/controls/sq07-the-maw-evidence-schema-v1.json"
)

SHARDS_SOURCE = ROOT / "brain/sq07_the_maw_shards.py"
SUBSET_SOURCE = ROOT / "brain/sq07_the_maw_subset.py"
EPISODE_SOURCE = ROOT / "brain/sq07_the_maw_episode.py"
EVIDENCE_SOURCE = ROOT / "brain/sq07_the_maw_evidence.py"

AUTHORIZATION_DIR = ROOT / "config/controls/sq07-authorizations"

EXPECTED_SHA256 = {
    "prereg": (
        "0ff34f0f4c2c1315b766ecc1acf66e2e6c24650aba87ae033e5a71a2b707a84a"
    ),
    "sharding_contract": (
        "ede14b0add5d13e723c443be241504dea36d4bb0424e3f718b199b8c1c665d8a"
    ),
    "evidence_schema": (
        "c1065506a90b26856896e0a522c7023738de13b0ac5af7a17cea7973774d2f01"
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
    "evidence_writer": (
        "255427764b0f0b49273c27c44f000ecb50628fc7d129ec8dc9fcfddeb0af3e11"
    ),
}

EXPECTED_CONDITION_PLAN_SHA256 = (
    "850ae560ab1b25c65f9932615f8ea1851781881c4492672767bcda692667becb"
)
EXPECTED_SHARD_PLAN_SHA256 = (
    "9039b8e708c2ffdb74436e5c6fdc8f7d2f38f3f3fb27fd7478dd2cc8101d2a55"
)

EXPECTED_SHARD_COUNT = 512
EXPECTED_EPISODE_COUNT = 32768
CONDITIONS_PER_SHARD = 64

AUTHORIZATION_STATEMENT = (
    "I explicitly authorize execution of this frozen SQ-07 THE MAW run."
)


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


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def validate_run_id(run_id: str) -> str:
    if not isinstance(run_id, str):
        raise TypeError("run_id must be string")

    if not re.fullmatch(r"[A-Za-z0-9._-]{1,64}", run_id):
        raise ValueError(
            "run_id must contain only A-Z, a-z, 0-9, dot, underscore, or hyphen"
        )

    return run_id


@lru_cache(maxsize=1)
def load_runner_config() -> dict:
    payload = tomllib.loads(
        RUNNER_CONFIG.read_text(encoding="utf-8")
    )

    experiment = payload["experiment"]
    execution = payload["execution"]
    authority = payload["human_command_authority"]
    boundaries = payload["boundaries"]

    if experiment["id"] != "sq07-the-maw-shard-runner-v1":
        refuse("SQ-07 shard runner config ID drift")

    if experiment["neural_execution_authorized"] is not False:
        refuse("runner config may not pre-authorize neural execution")

    if experiment["result_execution_authorized"] is not False:
        refuse("runner config may not pre-authorize result execution")

    expected_execution = {
        "expected_shard_count": 512,
        "expected_total_episode_count": 32768,
        "conditions_per_shard": 64,
        "masks_per_shard": 16,
        "max_shards_per_invocation": 1,
        "fresh_runtime_each_episode": True,
        "no_adaptive_selection": True,
        "no_result_driven_pruning": True,
        "no_early_stopping": True,
        "partial_shard_result_write_forbidden": True,
        "existing_shard_output_refuses_execution": True,
    }

    for key, value in expected_execution.items():
        if execution.get(key) != value:
            refuse(f"SQ-07 runner execution config drift: {key}")

    required_authority = {
        "authorization_scope": "complete_sq07_run",
        "human_execution_authorization_required": True,
        "automated_authorization_forbidden": True,
        "ai_generated_authorization_forbidden": True,
        "ci_success_is_not_execution_authorization": True,
        "test_success_is_not_execution_authorization": True,
        "runner_presence_is_not_execution_authorization": True,
        "authorization_must_be_explicit_and_run_specific": True,
        "authorization_may_not_be_inferred_from_prior_runs": True,
        "authorization_file_must_be_git_tracked": True,
        "authorization_commit_must_equal_execution_head": True,
        "implementation_commit_must_be_ancestor_of_execution_head": True,
        "implementation_commit_must_precede_authorization_commit": True,
        "clean_git_worktree_required": True,
    }

    for key, value in required_authority.items():
        if authority.get(key) != value:
            refuse(f"SQ-07 runner authority config drift: {key}")

    if any(boundaries.values()):
        refuse("SQ-07 runner claim boundary drift")

    return payload


@lru_cache(maxsize=1)
def verify_frozen_dependencies() -> dict:
    load_runner_config()

    paths = {
        "prereg": PREREG,
        "sharding_contract": SHARDING,
        "evidence_schema": EVIDENCE_SCHEMA,
        "shard_planner": SHARDS_SOURCE,
        "subset_operator": SUBSET_SOURCE,
        "episode_executor": EPISODE_SOURCE,
        "evidence_writer": EVIDENCE_SOURCE,
    }

    observed = {}

    for name, path in paths.items():
        if not path.is_file():
            refuse(f"missing frozen SQ-07 runner dependency: {name}")

        actual = sha256_file(path)
        expected = EXPECTED_SHA256[name]

        if actual != expected:
            refuse(
                f"SQ-07 runner dependency SHA drift for {name}: "
                f"{actual} != {expected}"
            )

        observed[name] = actual

    return {
        **observed,
        "condition_plan_sha256": EXPECTED_CONDITION_PLAN_SHA256,
        "shard_plan_sha256": EXPECTED_SHARD_PLAN_SHA256,
        "runner_config_sha256": sha256_file(RUNNER_CONFIG),
    }


def _resolve_authorization_path(path: Path) -> Path:
    candidate = Path(path)

    if not candidate.is_absolute():
        candidate = ROOT / candidate

    candidate = candidate.resolve()
    auth_root = AUTHORIZATION_DIR.resolve()

    try:
        candidate.relative_to(auth_root)
    except ValueError:
        refuse(
            "SQ-07 authorization must reside under "
            "config/controls/sq07-authorizations"
        )

    return candidate


def verify_execution_authorization(
    *,
    authorization_path: Path,
    run_id: str,
) -> dict:
    run_id = validate_run_id(run_id)
    deps = verify_frozen_dependencies()

    auth_path = _resolve_authorization_path(authorization_path)

    if not auth_path.is_file():
        refuse("SQ-07 execution authorization file is absent")

    rel = str(auth_path.relative_to(ROOT))

    tracked = _git("ls-files", "--error-unmatch", rel)
    if tracked.returncode != 0:
        refuse("SQ-07 execution authorization must be tracked by Git")

    status = _git("status", "--porcelain")
    if status.returncode != 0 or status.stdout.strip():
        refuse("SQ-07 result execution requires a clean Git working tree")

    head = _git("rev-parse", "HEAD")
    if head.returncode != 0:
        refuse("unable to resolve SQ-07 execution HEAD")

    head_sha = head.stdout.strip()

    auth_commit = _git(
        "log",
        "-1",
        "--format=%H",
        "--",
        rel,
    )

    if auth_commit.returncode != 0 or not auth_commit.stdout.strip():
        refuse("unable to resolve SQ-07 authorization commit")

    authorization_commit = auth_commit.stdout.strip()

    if authorization_commit != head_sha:
        refuse(
            "SQ-07 authorization commit must equal execution HEAD"
        )

    auth = json.loads(
        auth_path.read_text(encoding="utf-8")
    )

    required = {
        "artifact": "sq07-the-maw-run-execution-authorization-v1",
        "authorization_scope": "complete_sq07_run",
        "run_id": run_id,
        "human_execution_authorized": True,
        "neural_execution_enabled": True,
        "result_execution_enabled": True,
        "execution_mode": "local",
        "expected_shard_count": EXPECTED_SHARD_COUNT,
        "expected_episode_count": EXPECTED_EPISODE_COUNT,
        "condition_plan_sha256": EXPECTED_CONDITION_PLAN_SHA256,
        "shard_plan_sha256": EXPECTED_SHARD_PLAN_SHA256,
        "preregistration_sha256": EXPECTED_SHA256["prereg"],
        "evidence_schema_sha256": EXPECTED_SHA256["evidence_schema"],
        "episode_executor_sha256": EXPECTED_SHA256["episode_executor"],
        "evidence_writer_sha256": EXPECTED_SHA256["evidence_writer"],
        "authorization_statement": AUTHORIZATION_STATEMENT,
        "human_authorization_source": "manual-human-command",
        "automated_authorization": False,
        "ai_generated_authorization": False,
    }

    for key, value in required.items():
        if auth.get(key) != value:
            refuse(f"SQ-07 authorization field drift: {key}")

    runner_sha = sha256_file(Path(__file__))
    config_sha = sha256_file(RUNNER_CONFIG)

    if auth.get("runner_sha256") != runner_sha:
        refuse("SQ-07 authorization runner SHA mismatch")

    if auth.get("runner_config_sha256") != config_sha:
        refuse("SQ-07 authorization runner config SHA mismatch")

    implementation_commit = auth.get("implementation_commit")

    if (
        not isinstance(implementation_commit, str)
        or not re.fullmatch(r"[0-9a-f]{40}", implementation_commit)
    ):
        refuse("SQ-07 authorization missing implementation commit")

    if implementation_commit == head_sha:
        refuse(
            "SQ-07 implementation freeze must precede authorization commit"
        )

    ancestry = _git(
        "merge-base",
        "--is-ancestor",
        implementation_commit,
        "HEAD",
    )

    if ancestry.returncode != 0:
        refuse(
            "SQ-07 implementation commit is not an ancestor "
            "of execution HEAD"
        )

    return {
        "authorization": auth,
        "authorization_path": rel,
        "authorization_sha256": sha256_file(auth_path),
        "authorization_commit": authorization_commit,
        "execution_head": head_sha,
        "dependencies": deps,
    }


def _shard_output_dir(run_id: str, shard: dict) -> Path:
    run_id = validate_run_id(run_id)

    return (
        DATA_ROOT
        / "experiments"
        / "sq07-the-maw-v1"
        / "runs"
        / run_id
        / shard["shard_id"]
    )


def _load_runtime_inputs():
    baseline = sparse.load_npz(CONNECTOME).tocsr()

    retina = np.load(RETINA, allow_pickle=False)
    retinal_indices = np.asarray(
        retina["neuron_index"],
        dtype=np.int32,
    )

    dn_indices, _clusters, channel_positions = (
        load_primary_population()
    )

    return (
        baseline,
        retinal_indices,
        dn_indices,
        channel_positions,
    )


def run_authorized_shard(
    *,
    shard_index: int,
    run_id: str,
    authorization_path: Path,
) -> dict:
    # The authorization gate is deliberately first.
    verified = verify_execution_authorization(
        authorization_path=authorization_path,
        run_id=run_id,
    )

    shard = canonical_shard(shard_index)
    output_dir = _shard_output_dir(run_id, shard)

    if output_dir.exists():
        refuse(
            "SQ-07 shard output directory already exists; "
            "execution refuses overwrite or implicit resume"
        )

    (
        baseline,
        retinal_indices,
        dn_indices,
        channel_positions,
    ) = _load_runtime_inputs()

    started_at = _utc_now()
    started_clock = time.perf_counter()

    records = []

    for offset, condition_id in enumerate(
        shard["condition_ids"]
    ):
        mask13, layout, replicate = parse_condition_id(
            condition_id
        )

        condition = {
            "ordinal": shard["start_ordinal"] + offset,
            "condition_id": condition_id,
            "mask13": mask13,
            "layout": layout,
            "replicate": replicate,
        }

        records.append(
            execute_condition(
                baseline=baseline,
                retinal_indices=retinal_indices,
                dn_indices=dn_indices,
                channel_positions=channel_positions,
                condition=condition,
            )
        )

    if len(records) != CONDITIONS_PER_SHARD:
        refuse(
            "SQ-07 shard execution did not complete all 64 episodes"
        )

    elapsed = time.perf_counter() - started_clock
    completed_at = _utc_now()

    manifest_path, sidecar_path = write_shard_evidence(
        shard_index=shard_index,
        records=records,
        dn_indices=dn_indices,
        shard_timing={
            "started_at_utc": started_at,
            "completed_at_utc": completed_at,
            "elapsed_seconds": float(elapsed),
        },
        output_dir=output_dir,
    )

    return {
        "status": "COMPLETE_SHARD_EVIDENCE",
        "run_id": run_id,
        "shard_id": shard["shard_id"],
        "shard_index": shard_index,
        "condition_count": len(records),
        "authorization": {
            "path": verified["authorization_path"],
            "sha256": verified["authorization_sha256"],
            "commit": verified["authorization_commit"],
        },
        "manifest_path": str(manifest_path),
        "sidecar_path": str(sidecar_path),
    }
