from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path

import numpy as np

from brain.sq08_three_body_episode import (
    RESULT_KEYS,
    duplicate_pair_exact,
    validate_condition,
    validate_result,
)
from brain.sq08_three_body_plan import (
    MASKS,
    REPLICATES,
    build_conditions,
)
from brain.sq08_three_body_readout import (
    BODY_RESPONDERS,
    FRONTIER_INDICES,
)


ROOT = Path(__file__).resolve().parents[1]

EVIDENCE_SCHEMA = (
    ROOT
    / "config/controls/"
    "sq08-three-body-evidence-schema-v1.json"
)

FRONTIER_MANIFEST = (
    ROOT
    / "config/controls/"
    "sq08-three-body-topology-frontier-v1.json"
)

EPISODE_COUNT = 16

SIDECAR_KEYS = (
    "condition_ordinal",
    "condition_id",
    "condition_mask",
    "condition_replicate",
    "body_responder_indices",
    "frontier_indices",
    "dn_indices",
    "primary_positive_voltage",
    "primary_spikes",
    "body_responder_voltage",
    "body_responder_spikes",
    "frontier_voltage",
    "frontier_spikes",
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
        for chunk in iter(
            lambda: handle.read(8 * 1024 * 1024),
            b"",
        ):
            h.update(chunk)

    return h.hexdigest()


def canonical_conditions() -> list[dict]:
    conditions = build_conditions()

    if len(conditions) != EPISODE_COUNT:
        refuse("SQ-08 canonical condition count drift")

    return conditions


def validate_episode_record(
    record: dict,
    *,
    expected_condition: dict,
) -> None:
    if set(record) != {
        "condition",
        "topology_provenance",
        "result",
        "timing",
    }:
        refuse(
            "unexpected SQ-08 episode record structure"
        )

    observed = validate_condition(
        record["condition"]
    )

    expected = validate_condition(
        expected_condition
    )

    if observed != expected:
        refuse(
            "SQ-08 condition membership/order drift"
        )

    if not isinstance(
        record["topology_provenance"],
        dict,
    ):
        refuse(
            "SQ-08 topology provenance must be dict"
        )

    validate_result(
        record["result"]
    )

    timing = record["timing"]

    if set(timing) != {
        "started_at_utc",
        "completed_at_utc",
        "elapsed_seconds",
    }:
        refuse(
            "SQ-08 episode timing structure drift"
        )

    if not isinstance(
        timing["started_at_utc"],
        str,
    ):
        refuse(
            "SQ-08 started_at_utc must be string"
        )

    if not isinstance(
        timing["completed_at_utc"],
        str,
    ):
        refuse(
            "SQ-08 completed_at_utc must be string"
        )

    elapsed = timing["elapsed_seconds"]

    if not isinstance(
        elapsed,
        (int, float),
    ):
        refuse(
            "SQ-08 elapsed_seconds must be numeric"
        )

    if (
        not np.isfinite(float(elapsed))
        or float(elapsed) < 0.0
    ):
        refuse(
            "SQ-08 elapsed_seconds invalid"
        )


def verify_duplicate_pairs(
    records: list[dict],
) -> tuple[bool, int]:
    by_mask: dict[str, dict[int, dict]] = {}

    for record in records:
        condition = validate_condition(
            record["condition"]
        )

        mask = condition["mask"]
        replicate = condition["replicate"]

        by_mask.setdefault(
            mask,
            {},
        )[replicate] = record

    if set(by_mask) != set(MASKS):
        refuse(
            "SQ-08 evidence missing Boolean masks"
        )

    pair_count = 0

    for mask in MASKS:
        pair = by_mask[mask]

        if set(pair) != {1, 2}:
            refuse(
                f"SQ-08 duplicate pair incomplete: {mask}"
            )

        if not duplicate_pair_exact(
            pair[1],
            pair[2],
        ):
            refuse(
                f"SQ-08 deterministic duplicate mismatch: {mask}"
            )

        pair_count += 1

    return True, pair_count


def assemble_arrays(
    *,
    records: list[dict],
    dn_indices: np.ndarray,
) -> tuple[
    dict[str, np.ndarray],
    bool,
    int,
]:
    canonical = canonical_conditions()

    if len(records) != EPISODE_COUNT:
        refuse(
            "SQ-08 evidence must contain exactly "
            "16 episode records"
        )

    for i, record in enumerate(records):
        validate_episode_record(
            record,
            expected_condition=canonical[i],
        )

    duplicate_exact, pair_count = (
        verify_duplicate_pairs(records)
    )

    conditions = [
        row["condition"]
        for row in records
    ]

    results = [
        row["result"]
        for row in records
    ]

    timings = [
        row["timing"]
        for row in records
    ]

    arrays = {
        "condition_ordinal": np.asarray(
            [
                row["ordinal"]
                for row in conditions
            ],
            dtype=np.int32,
        ),

        "condition_id": np.asarray(
            [
                row["condition_id"]
                for row in conditions
            ],
            dtype="<U32",
        ),

        "condition_mask": np.asarray(
            [
                row["mask"]
                for row in conditions
            ],
            dtype="<U3",
        ),

        "condition_replicate": np.asarray(
            [
                row["replicate"]
                for row in conditions
            ],
            dtype=np.int8,
        ),

        "body_responder_indices":
            np.array(
                BODY_RESPONDERS,
                dtype=np.int32,
                copy=True,
            ),

        "frontier_indices":
            np.array(
                FRONTIER_INDICES,
                dtype=np.int32,
                copy=True,
            ),

        "dn_indices":
            np.array(
                dn_indices,
                dtype=np.int32,
                copy=True,
            ),

        "primary_positive_voltage":
            np.stack(
                [
                    row["positive_voltage"]
                    for row in results
                ],
                axis=0,
            ),

        "primary_spikes":
            np.stack(
                [
                    row["spikes"]
                    for row in results
                ],
                axis=0,
            ),

        "body_responder_voltage":
            np.stack(
                [
                    row[
                        "body_responder_voltage"
                    ]
                    for row in results
                ],
                axis=0,
            ),

        "body_responder_spikes":
            np.stack(
                [
                    row[
                        "body_responder_spikes"
                    ]
                    for row in results
                ],
                axis=0,
            ),

        "frontier_voltage":
            np.stack(
                [
                    row["frontier_voltage"]
                    for row in results
                ],
                axis=0,
            ),

        "frontier_spikes":
            np.stack(
                [
                    row["frontier_spikes"]
                    for row in results
                ],
                axis=0,
            ),

        "channel_mean_positive_voltage":
            np.stack(
                [
                    row[
                        "channel_mean_positive_voltage"
                    ]
                    for row in results
                ],
                axis=0,
            ),

        "channel_positive_fraction":
            np.stack(
                [
                    row[
                        "channel_positive_fraction"
                    ]
                    for row in results
                ],
                axis=0,
            ),

        "channel_spike_count":
            np.stack(
                [
                    row["channel_spike_count"]
                    for row in results
                ],
                axis=0,
            ),

        "channel_spike_rate":
            np.stack(
                [
                    row["channel_spike_rate"]
                    for row in results
                ],
                axis=0,
            ),

        "episode_started_at_utc":
            np.asarray(
                [
                    row["started_at_utc"]
                    for row in timings
                ],
                dtype="<U40",
            ),

        "episode_completed_at_utc":
            np.asarray(
                [
                    row["completed_at_utc"]
                    for row in timings
                ],
                dtype="<U40",
            ),

        "episode_elapsed_seconds":
            np.asarray(
                [
                    row["elapsed_seconds"]
                    for row in timings
                ],
                dtype=np.float64,
            ),
    }

    validate_sidecar_arrays(
        arrays
    )

    return (
        arrays,
        duplicate_exact,
        pair_count,
    )


def validate_sidecar_arrays(
    arrays: dict[str, np.ndarray],
) -> None:
    if set(arrays) != set(SIDECAR_KEYS):
        refuse(
            "SQ-08 sidecar key-set drift"
        )

    numeric = {
        "condition_ordinal":
            ((16,), np.int32),

        "condition_replicate":
            ((16,), np.int8),

        "body_responder_indices":
            ((3,), np.int32),

        "frontier_indices":
            ((18,), np.int32),

        "dn_indices":
            ((1191,), np.int32),

        "primary_positive_voltage":
            ((16, 192, 1191), np.float32),

        "primary_spikes":
            ((16, 192, 1191), np.uint8),

        "body_responder_voltage":
            ((16, 192, 3), np.float32),

        "body_responder_spikes":
            ((16, 192, 3), np.uint8),

        "frontier_voltage":
            ((16, 192, 18), np.float32),

        "frontier_spikes":
            ((16, 192, 18), np.uint8),

        "channel_mean_positive_voltage":
            ((16, 3, 192), np.float64),

        "channel_positive_fraction":
            ((16, 3, 192), np.float64),

        "channel_spike_count":
            ((16, 3, 192), np.int32),

        "channel_spike_rate":
            ((16, 3, 192), np.float64),

        "episode_elapsed_seconds":
            ((16,), np.float64),
    }

    for key, (shape, dtype) in numeric.items():
        value = arrays[key]

        if value.shape != shape:
            refuse(
                f"SQ-08 sidecar shape drift "
                f"{key}: {value.shape}"
            )

        if value.dtype != np.dtype(dtype):
            refuse(
                f"SQ-08 sidecar dtype drift "
                f"{key}: {value.dtype}"
            )

    strings = {
        "condition_id": (16,),
        "condition_mask": (16,),
        "episode_started_at_utc": (16,),
        "episode_completed_at_utc": (16,),
    }

    for key, shape in strings.items():
        value = arrays[key]

        if value.shape != shape:
            refuse(
                f"SQ-08 unicode shape drift: {key}"
            )

        if value.dtype.kind != "U":
            refuse(
                f"SQ-08 unicode dtype drift: {key}"
            )

    if arrays[
        "body_responder_indices"
    ].tolist() != BODY_RESPONDERS.tolist():
        refuse(
            "SQ-08 BODY coordinate drift"
        )

    if arrays[
        "frontier_indices"
    ].tolist() != FRONTIER_INDICES.tolist():
        refuse(
            "SQ-08 frontier coordinate drift"
        )

    canonical = canonical_conditions()

    expected_ids = [
        row["condition_id"]
        for row in canonical
    ]

    expected_masks = [
        row["mask"]
        for row in canonical
    ]

    expected_replicates = [
        row["replicate"]
        for row in canonical
    ]

    expected_ordinals = [
        row["ordinal"]
        for row in canonical
    ]

    if (
        arrays["condition_id"].tolist()
        != expected_ids
    ):
        refuse(
            "SQ-08 condition ID/order drift"
        )

    if (
        arrays["condition_mask"].tolist()
        != expected_masks
    ):
        refuse(
            "SQ-08 mask/order drift"
        )

    if (
        arrays[
            "condition_replicate"
        ].tolist()
        != expected_replicates
    ):
        refuse(
            "SQ-08 replicate/order drift"
        )

    if (
        arrays[
            "condition_ordinal"
        ].tolist()
        != expected_ordinals
    ):
        refuse(
            "SQ-08 ordinal drift"
        )


def _atomic_write_npz(
    path: Path,
    arrays: dict[str, np.ndarray],
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fd, temp_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=path.parent,
    )

    try:
        with os.fdopen(
            fd,
            "wb",
        ) as handle:
            np.savez_compressed(
                handle,
                **arrays,
            )

            handle.flush()
            os.fsync(
                handle.fileno()
            )

        os.replace(
            temp_name,
            path,
        )

    except BaseException:
        try:
            os.unlink(
                temp_name
            )
        except FileNotFoundError:
            pass

        raise


def _atomic_write_json(
    path: Path,
    payload: dict,
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    encoded = (
        json.dumps(
            payload,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )

    fd, temp_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=path.parent,
    )

    try:
        with os.fdopen(
            fd,
            "w",
            encoding="utf-8",
        ) as handle:
            handle.write(encoded)

            handle.flush()
            os.fsync(
                handle.fileno()
            )

        os.replace(
            temp_name,
            path,
        )

    except BaseException:
        try:
            os.unlink(
                temp_name
            )
        except FileNotFoundError:
            pass

        raise


def write_evidence(
    *,
    records: list[dict],
    dn_indices: np.ndarray,
    output_dir: Path,
    run_metadata: dict,
) -> tuple[Path, Path]:
    if output_dir.exists():
        refuse(
            "SQ-08 evidence output directory "
            "already exists"
        )

    arrays, duplicate_exact, pair_count = (
        assemble_arrays(
            records=records,
            dn_indices=dn_indices,
        )
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=False,
    )

    sidecar = (
        output_dir
        / "sq08-three-body-evidence-v1.npz"
    )

    manifest = (
        output_dir
        / "sq08-three-body-evidence-v1.json"
    )

    _atomic_write_npz(
        sidecar,
        arrays,
    )

    sidecar_sha256 = sha256_file(
        sidecar
    )

    payload = {
        "schema_version": (
            "moscaquant."
            "sq08-three-body-evidence/v1"
        ),
        "experiment": "SQ-08",
        "codename": "THREE BODY PROBLEM",
        "status": "COMPLETE_EVIDENCE",
        "episode_count": EPISODE_COUNT,
        "duplicate_pairs_exact":
            bool(duplicate_exact),
        "duplicate_pair_count":
            int(pair_count),
        "sidecar": {
            "path": sidecar.name,
            "sha256":
                sidecar_sha256,
        },
        "coordinates": {
            "body_responders":
                BODY_RESPONDERS.tolist(),
            "frontier":
                FRONTIER_INDICES.tolist(),
        },
        "run_metadata": run_metadata,
        "claim_boundary": (
            "evidence preservation only; "
            "no mechanistic interpretation"
        ),
    }

    _atomic_write_json(
        manifest,
        payload,
    )

    return manifest, sidecar
