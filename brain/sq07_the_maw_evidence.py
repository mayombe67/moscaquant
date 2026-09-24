from __future__ import annotations

import hashlib
import json
import os
import tempfile
from functools import lru_cache
from pathlib import Path

import numpy as np

from brain.sq07_the_maw_shards import (
    shard_plan,
    shard_plan_sha256,
)


ROOT = Path(__file__).resolve().parents[1]

SCHEMA = ROOT / "config/controls/sq07-the-maw-evidence-schema-v1.json"
SHARDS_SOURCE = ROOT / "brain/sq07_the_maw_shards.py"

EXPECTED_SCHEMA_SHA256 = (
    "c1065506a90b26856896e0a522c7023738de13b0ac5af7a17cea7973774d2f01"
)
EXPECTED_SHARDS_SOURCE_SHA256 = (
    "7cde07ad921543cdb9dba95f3299ccb4a1cfbb20f32a3a75fc678a2df61ef1af"
)
EXPECTED_CONDITION_PLAN_SHA256 = (
    "850ae560ab1b25c65f9932615f8ea1851781881c4492672767bcda692667becb"
)
EXPECTED_SHARD_PLAN_SHA256 = (
    "9039b8e708c2ffdb74436e5c6fdc8f7d2f38f3f3fb27fd7478dd2cc8101d2a55"
)
EXPECTED_SHARDING_CONTRACT_SHA256 = (
    "ede14b0add5d13e723c443be241504dea36d4bb0424e3f718b199b8c1c665d8a"
)

SCHEMA_ID = "moscaquant.sq07-the-maw-shard-evidence.v1"
SCHEMA_VERSION = "sq07-the-maw-evidence-schema-v1"

EPISODE_COUNT = 64
MASK_COUNT = 16
FRAME_COUNT = 192
DN_COUNT = 1191

RESULT_KEYS = (
    "positive_voltage",
    "spikes",
    "channel_mean_positive_voltage",
    "channel_positive_fraction",
    "channel_spike_count",
    "channel_spike_rate",
)

SIDECAR_KEYS = (
    "condition_ordinal",
    "condition_id",
    "condition_mask13",
    "condition_layout",
    "condition_replicate",
    "dn_indices",
    "primary_positive_voltage",
    "primary_spikes",
    "channel_mean_positive_voltage",
    "channel_positive_fraction",
    "channel_spike_count",
    "channel_spike_rate",
    "episode_started_at_utc",
    "episode_completed_at_utc",
    "episode_elapsed_seconds",
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


def sha256_array(value: np.ndarray) -> str:
    array = np.ascontiguousarray(value)
    h = hashlib.sha256()
    h.update(str(array.dtype).encode("ascii"))
    h.update(b"\0")
    h.update(
        ",".join(str(x) for x in array.shape).encode("ascii")
    )
    h.update(b"\0")
    h.update(array.tobytes(order="C"))
    return h.hexdigest()


@lru_cache(maxsize=1)
def verify_frozen_dependencies() -> dict:
    observed_schema = sha256_file(SCHEMA)
    if observed_schema != EXPECTED_SCHEMA_SHA256:
        refuse(
            "SQ-07 evidence schema SHA drift: "
            f"{observed_schema} != {EXPECTED_SCHEMA_SHA256}"
        )

    observed_shards_source = sha256_file(SHARDS_SOURCE)
    if observed_shards_source != EXPECTED_SHARDS_SOURCE_SHA256:
        refuse(
            "SQ-07 shard planner source SHA drift: "
            f"{observed_shards_source} != "
            f"{EXPECTED_SHARDS_SOURCE_SHA256}"
        )

    shards = shard_plan()
    observed_plan = shard_plan_sha256(shards)

    if observed_plan != EXPECTED_SHARD_PLAN_SHA256:
        refuse(
            "SQ-07 shard plan SHA drift: "
            f"{observed_plan} != {EXPECTED_SHARD_PLAN_SHA256}"
        )

    return {
        "evidence_schema_sha256": observed_schema,
        "shard_planner_source_sha256": observed_shards_source,
        "condition_plan_sha256": EXPECTED_CONDITION_PLAN_SHA256,
        "shard_plan_sha256": observed_plan,
        "sharding_contract_sha256": EXPECTED_SHARDING_CONTRACT_SHA256,
    }


def canonical_shard(shard_index: int) -> dict:
    verify_frozen_dependencies()

    if not isinstance(shard_index, int):
        raise TypeError("shard_index must be int")

    shards = shard_plan()

    if shard_index < 0 or shard_index >= len(shards):
        raise ValueError(f"invalid SQ-07 shard index: {shard_index}")

    return dict(shards[shard_index])


def parse_condition_id(condition_id: str) -> tuple[str, str, int]:
    parts = condition_id.split(":")

    if len(parts) != 4 or parts[0] != "sq07":
        raise ValueError(f"invalid SQ-07 condition ID: {condition_id}")

    mask13 = parts[1]
    layout = parts[2]
    replicate_text = parts[3]

    if len(mask13) != 13 or set(mask13) - {"0", "1"}:
        raise ValueError(f"invalid mask in condition ID: {condition_id}")

    if layout not in {"LR", "RL"}:
        raise ValueError(f"invalid layout in condition ID: {condition_id}")

    if replicate_text not in {"r1", "r2"}:
        raise ValueError(f"invalid replicate in condition ID: {condition_id}")

    return mask13, layout, int(replicate_text[1:])


def validate_result(result: dict) -> None:
    if set(result) != set(RESULT_KEYS):
        refuse("SQ-07 episode result key-set drift")

    expected = {
        "positive_voltage": ((192, 1191), np.dtype(np.float32)),
        "spikes": ((192, 1191), np.dtype(np.uint8)),
        "channel_mean_positive_voltage": (
            (3, 192),
            np.dtype(np.float64),
        ),
        "channel_positive_fraction": (
            (3, 192),
            np.dtype(np.float64),
        ),
        "channel_spike_count": (
            (3, 192),
            np.dtype(np.int32),
        ),
        "channel_spike_rate": (
            (3, 192),
            np.dtype(np.float64),
        ),
    }

    for key, (shape, dtype) in expected.items():
        value = result[key]

        if not isinstance(value, np.ndarray):
            refuse(f"episode evidence is not ndarray: {key}")

        if value.shape != shape:
            refuse(
                f"episode evidence shape drift for {key}: "
                f"{value.shape} != {shape}"
            )

        if value.dtype != dtype:
            refuse(
                f"episode evidence dtype drift for {key}: "
                f"{value.dtype} != {dtype}"
            )


def validate_episode_record(
    record: dict,
    expected_condition_id: str,
    expected_ordinal: int,
) -> None:
    if set(record) != {
        "condition",
        "topology_provenance",
        "result",
        "timing",
    }:
        refuse("unexpected SQ-07 episode evidence record structure")

    condition = record["condition"]

    required_condition = {
        "ordinal",
        "condition_id",
        "mask13",
        "layout",
        "replicate",
    }

    if set(condition) != required_condition:
        refuse("unexpected SQ-07 condition structure")

    if condition["condition_id"] != expected_condition_id:
        refuse(
            "condition membership/order mismatch: "
            f"{condition['condition_id']} != {expected_condition_id}"
        )

    if condition["ordinal"] != expected_ordinal:
        refuse(
            "condition ordinal mismatch: "
            f"{condition['ordinal']} != {expected_ordinal}"
        )

    mask13, layout, replicate = parse_condition_id(
        expected_condition_id
    )

    if condition["mask13"] != mask13:
        refuse("condition mask does not match condition ID")

    if condition["layout"] != layout:
        refuse("condition layout does not match condition ID")

    if condition["replicate"] != replicate:
        refuse("condition replicate does not match condition ID")

    if not isinstance(record["topology_provenance"], dict):
        refuse("topology provenance must be a dictionary")

    validate_result(record["result"])

    timing = record["timing"]

    if set(timing) != {
        "started_at_utc",
        "completed_at_utc",
        "elapsed_seconds",
    }:
        refuse("unexpected episode timing structure")

    if not isinstance(timing["started_at_utc"], str):
        refuse("episode started_at_utc must be string")

    if not isinstance(timing["completed_at_utc"], str):
        refuse("episode completed_at_utc must be string")

    elapsed = timing["elapsed_seconds"]

    if not isinstance(elapsed, (int, float)):
        refuse("episode elapsed_seconds must be numeric")

    if not np.isfinite(float(elapsed)) or float(elapsed) < 0.0:
        refuse("episode elapsed_seconds must be finite and nonnegative")


def validate_shard_timing(shard_timing: dict) -> dict:
    required = {
        "started_at_utc",
        "completed_at_utc",
        "elapsed_seconds",
    }

    if set(shard_timing) != required:
        raise ValueError("unexpected shard timing structure")

    if not isinstance(shard_timing["started_at_utc"], str):
        raise ValueError("shard started_at_utc must be string")

    if not isinstance(shard_timing["completed_at_utc"], str):
        raise ValueError("shard completed_at_utc must be string")

    elapsed = float(shard_timing["elapsed_seconds"])

    if not np.isfinite(elapsed) or elapsed < 0.0:
        raise ValueError(
            "shard elapsed_seconds must be finite and nonnegative"
        )

    return {
        "started_at_utc": shard_timing["started_at_utc"],
        "completed_at_utc": shard_timing["completed_at_utc"],
        "elapsed_seconds": elapsed,
    }


def duplicate_pair_exact(first: dict, second: dict) -> bool:
    return all(
        np.array_equal(
            first["result"][key],
            second["result"][key],
        )
        for key in RESULT_KEYS
    )


def verify_duplicate_pairs(records: list[dict]) -> tuple[bool, int]:
    if len(records) != EPISODE_COUNT:
        refuse("duplicate verification requires exactly 64 records")

    exact = True
    pair_count = 0

    for offset in range(0, EPISODE_COUNT, 4):
        lr1, lr2, rl1, rl2 = records[offset : offset + 4]

        exact = exact and duplicate_pair_exact(lr1, lr2)
        exact = exact and duplicate_pair_exact(rl1, rl2)
        pair_count += 2

    if pair_count != 32:
        refuse("expected exactly 32 duplicate pairs per shard")

    return exact, pair_count


def assemble_sidecar(
    shard: dict,
    records: list[dict],
    dn_indices: np.ndarray,
) -> tuple[dict[str, np.ndarray], bool, int]:
    if len(records) != EPISODE_COUNT:
        refuse(
            f"SQ-07 shard requires exactly {EPISODE_COUNT} "
            f"episode records"
        )

    dn_indices = np.asarray(dn_indices)

    if dn_indices.shape != (DN_COUNT,):
        refuse("SQ-07 DN identity must contain exactly 1191 indices")

    if dn_indices.dtype != np.dtype(np.int32):
        refuse("SQ-07 DN identity must be int32")

    if len(set(shard["condition_ids"])) != EPISODE_COUNT:
        refuse("canonical shard contains duplicate condition IDs")

    for i, record in enumerate(records):
        validate_episode_record(
            record,
            expected_condition_id=shard["condition_ids"][i],
            expected_ordinal=shard["start_ordinal"] + i,
        )

    duplicate_exact, pair_count = verify_duplicate_pairs(records)

    conditions = [record["condition"] for record in records]
    results = [record["result"] for record in records]
    timings = [record["timing"] for record in records]

    arrays = {
        "condition_ordinal": np.asarray(
            [row["ordinal"] for row in conditions],
            dtype=np.int32,
        ),
        "condition_id": np.asarray(
            [row["condition_id"] for row in conditions],
            dtype="<U64",
        ),
        "condition_mask13": np.asarray(
            [row["mask13"] for row in conditions],
            dtype="<U13",
        ),
        "condition_layout": np.asarray(
            [row["layout"] for row in conditions],
            dtype="<U2",
        ),
        "condition_replicate": np.asarray(
            [row["replicate"] for row in conditions],
            dtype=np.int8,
        ),
        "dn_indices": np.array(
            dn_indices,
            dtype=np.int32,
            copy=True,
        ),
        "primary_positive_voltage": np.stack(
            [row["positive_voltage"] for row in results],
            axis=0,
        ),
        "primary_spikes": np.stack(
            [row["spikes"] for row in results],
            axis=0,
        ),
        "channel_mean_positive_voltage": np.stack(
            [row["channel_mean_positive_voltage"] for row in results],
            axis=0,
        ),
        "channel_positive_fraction": np.stack(
            [row["channel_positive_fraction"] for row in results],
            axis=0,
        ),
        "channel_spike_count": np.stack(
            [row["channel_spike_count"] for row in results],
            axis=0,
        ),
        "channel_spike_rate": np.stack(
            [row["channel_spike_rate"] for row in results],
            axis=0,
        ),
        "episode_started_at_utc": np.asarray(
            [row["started_at_utc"] for row in timings],
            dtype="<U40",
        ),
        "episode_completed_at_utc": np.asarray(
            [row["completed_at_utc"] for row in timings],
            dtype="<U40",
        ),
        "episode_elapsed_seconds": np.asarray(
            [row["elapsed_seconds"] for row in timings],
            dtype=np.float64,
        ),
    }

    return arrays, duplicate_exact, pair_count


def validate_sidecar_arrays(
    arrays: dict[str, np.ndarray],
    shard: dict,
) -> None:
    if set(arrays) != set(SIDECAR_KEYS):
        refuse("SQ-07 sidecar key-set drift")

    numeric = {
        "condition_ordinal": ((64,), np.int32),
        "condition_replicate": ((64,), np.int8),
        "dn_indices": ((1191,), np.int32),
        "primary_positive_voltage": ((64, 192, 1191), np.float32),
        "primary_spikes": ((64, 192, 1191), np.uint8),
        "channel_mean_positive_voltage": ((64, 3, 192), np.float64),
        "channel_positive_fraction": ((64, 3, 192), np.float64),
        "channel_spike_count": ((64, 3, 192), np.int32),
        "channel_spike_rate": ((64, 3, 192), np.float64),
        "episode_elapsed_seconds": ((64,), np.float64),
    }

    for key, (shape, dtype) in numeric.items():
        value = arrays[key]

        if value.shape != shape:
            refuse(f"sidecar shape drift for {key}: {value.shape}")

        if value.dtype != np.dtype(dtype):
            refuse(f"sidecar dtype drift for {key}: {value.dtype}")

    for key, shape in {
        "condition_id": (64,),
        "condition_mask13": (64,),
        "condition_layout": (64,),
        "episode_started_at_utc": (64,),
        "episode_completed_at_utc": (64,),
    }.items():
        value = arrays[key]

        if value.shape != shape:
            refuse(f"sidecar shape drift for {key}: {value.shape}")

        if value.dtype.kind != "U":
            refuse(f"sidecar unicode dtype drift for {key}")

    expected_ids = shard["condition_ids"]

    if arrays["condition_id"].tolist() != expected_ids:
        refuse("sidecar condition membership/order drift")

    expected_ordinals = list(
        range(
            shard["start_ordinal"],
            shard["end_ordinal_exclusive"],
        )
    )

    if arrays["condition_ordinal"].tolist() != expected_ordinals:
        refuse("sidecar ordinal sequence drift")

    for index, condition_id in enumerate(expected_ids):
        mask13, layout, replicate = parse_condition_id(condition_id)

        if arrays["condition_mask13"][index] != mask13:
            refuse("sidecar mask coordinate drift")

        if arrays["condition_layout"][index] != layout:
            refuse("sidecar layout coordinate drift")

        if int(arrays["condition_replicate"][index]) != replicate:
            refuse("sidecar replicate coordinate drift")


def _atomic_write_npz(
    path: Path,
    arrays: dict[str, np.ndarray],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    fd, temp_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=path.parent,
    )

    try:
        with os.fdopen(fd, "wb") as handle:
            np.savez_compressed(handle, **arrays)
            handle.flush()
            os.fsync(handle.fileno())

        os.replace(temp_name, path)

    except BaseException:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


def _atomic_write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    fd, temp_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=path.parent,
    )

    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(
                payload,
                handle,
                indent=2,
                sort_keys=True,
            )
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())

        os.replace(temp_name, path)

    except BaseException:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


def write_shard_evidence(
    *,
    shard_index: int,
    records: list[dict],
    dn_indices: np.ndarray,
    shard_timing: dict,
    output_dir: Path,
) -> tuple[Path, Path]:
    authority = verify_frozen_dependencies()
    shard = canonical_shard(shard_index)
    timing = validate_shard_timing(shard_timing)

    arrays, all_duplicates_exact, pair_count = assemble_sidecar(
        shard,
        records,
        dn_indices,
    )

    validate_sidecar_arrays(arrays, shard)

    output_dir = Path(output_dir)
    sidecar_path = output_dir / f"{shard['shard_id']}.evidence.npz"
    manifest_path = output_dir / f"{shard['shard_id']}.manifest.json"

    if sidecar_path.exists() or manifest_path.exists():
        refuse("SQ-07 evidence writer refuses to overwrite artifacts")

    _atomic_write_npz(sidecar_path, arrays)

    sidecar_sha = sha256_file(sidecar_path)

    manifest = {
        "status": "COMPLETE_EVIDENCE",
        "schema_version": SCHEMA_VERSION,
        "shard_identity": {
            **shard,
            "shard_plan_sha256": EXPECTED_SHARD_PLAN_SHA256,
        },
        "provenance": {
            **authority,
            "sidecar_schema_id": SCHEMA_ID,
            "dn_indices_sha256": sha256_array(arrays["dn_indices"]),
        },
        "completeness": {
            "expected_condition_count": EPISODE_COUNT,
            "observed_condition_count": len(records),
            "expected_mask_count": MASK_COUNT,
            "observed_mask_count": shard["mask_count"],
            "condition_membership_exact": True,
            "condition_order_exact": True,
            "duplicate_pairs_checked": pair_count,
            "duplicate_replay_all_exact": all_duplicates_exact,
        },
        "timing": timing,
        "sidecar": {
            "path": sidecar_path.name,
            "sha256": sidecar_sha,
            "schema_id": SCHEMA_ID,
            "written": True,
        },
        "claim_boundaries": {
            "contains_result_classification": False,
            "contains_condition_selection": False,
            "contains_execution_authorization": False,
            "timing_has_scientific_semantics": False,
        },
    }

    _atomic_write_json(manifest_path, manifest)

    verify_shard_evidence(manifest_path)

    return manifest_path, sidecar_path


def verify_shard_evidence(manifest_path: Path) -> dict:
    authority = verify_frozen_dependencies()

    manifest_path = Path(manifest_path)

    if not manifest_path.is_file():
        refuse(f"missing SQ-07 shard manifest: {manifest_path}")

    manifest = json.loads(
        manifest_path.read_text(encoding="utf-8")
    )

    required_sections = {
        "status",
        "schema_version",
        "shard_identity",
        "provenance",
        "completeness",
        "timing",
        "sidecar",
        "claim_boundaries",
    }

    if set(manifest) != required_sections:
        refuse("SQ-07 shard manifest section drift")

    if manifest["status"] != "COMPLETE_EVIDENCE":
        refuse("SQ-07 shard evidence status is not complete")

    if manifest["schema_version"] != SCHEMA_VERSION:
        refuse("SQ-07 evidence schema-version drift")

    identity = manifest["shard_identity"]
    shard_index = identity.get("shard_index")

    canonical = canonical_shard(shard_index)

    expected_identity = {
        **canonical,
        "shard_plan_sha256": EXPECTED_SHARD_PLAN_SHA256,
    }

    if identity != expected_identity:
        refuse("SQ-07 shard identity does not match canonical plan")

    provenance = manifest["provenance"]

    for key, value in authority.items():
        if provenance.get(key) != value:
            refuse(f"SQ-07 provenance drift for {key}")

    if provenance.get("sidecar_schema_id") != SCHEMA_ID:
        refuse("SQ-07 sidecar schema ID drift")

    sidecar = manifest["sidecar"]

    if sidecar.get("schema_id") != SCHEMA_ID:
        refuse("SQ-07 manifest sidecar schema ID drift")

    if sidecar.get("written") is not True:
        refuse("SQ-07 manifest does not mark sidecar written")

    sidecar_path = manifest_path.parent / sidecar["path"]

    if not sidecar_path.is_file():
        refuse("SQ-07 sidecar is missing")

    actual_sha = sha256_file(sidecar_path)

    if actual_sha != sidecar["sha256"]:
        refuse("SQ-07 sidecar SHA-256 mismatch")

    with np.load(sidecar_path, allow_pickle=False) as loaded:
        arrays = {
            key: np.asarray(loaded[key])
            for key in loaded.files
        }

    validate_sidecar_arrays(arrays, canonical)

    if provenance.get("dn_indices_sha256") != sha256_array(
        arrays["dn_indices"]
    ):
        refuse("SQ-07 DN identity SHA mismatch")

    completeness = manifest["completeness"]

    if completeness.get("expected_condition_count") != 64:
        refuse("SQ-07 manifest expected condition count drift")

    if completeness.get("observed_condition_count") != 64:
        refuse("SQ-07 manifest observed condition count drift")

    if completeness.get("expected_mask_count") != 16:
        refuse("SQ-07 manifest expected mask count drift")

    if completeness.get("observed_mask_count") != 16:
        refuse("SQ-07 manifest observed mask count drift")

    if completeness.get("condition_membership_exact") is not True:
        refuse("SQ-07 manifest membership is not exact")

    if completeness.get("condition_order_exact") is not True:
        refuse("SQ-07 manifest ordering is not exact")

    if completeness.get("duplicate_pairs_checked") != 32:
        refuse("SQ-07 manifest duplicate pair count drift")

    recomputed_all_exact = True

    for offset in range(0, 64, 4):
        for first, second in (
            (offset, offset + 1),
            (offset + 2, offset + 3),
        ):
            for key in (
                "primary_positive_voltage",
                "primary_spikes",
                "channel_mean_positive_voltage",
                "channel_positive_fraction",
                "channel_spike_count",
                "channel_spike_rate",
            ):
                if not np.array_equal(
                    arrays[key][first],
                    arrays[key][second],
                ):
                    recomputed_all_exact = False

    if completeness.get("duplicate_replay_all_exact") is not (
        recomputed_all_exact
    ):
        refuse("SQ-07 duplicate replay summary disagrees with evidence")

    boundaries = manifest["claim_boundaries"]

    if boundaries != {
        "contains_result_classification": False,
        "contains_condition_selection": False,
        "contains_execution_authorization": False,
        "timing_has_scientific_semantics": False,
    }:
        refuse("SQ-07 evidence claim-boundary drift")

    validate_shard_timing(manifest["timing"])

    return {
        "valid": True,
        "shard_id": canonical["shard_id"],
        "condition_count": 64,
        "mask_count": 16,
        "duplicate_pairs_checked": 32,
        "duplicate_replay_all_exact": recomputed_all_exact,
        "sidecar_sha256": actual_sha,
    }
