from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np


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

BODY_RESPONDERS = np.asarray(
    [137122, 317, 126002],
    dtype=np.int32,
)

FRONTIER_INDICES = np.asarray(
    [
        7,
        72,
        129,
        411,
        470,
        1472,
        1574,
        1662,
        1919,
        2009,
        2327,
        3712,
        4068,
        14273,
        16349,
        18196,
        130134,
        131527,
    ],
    dtype=np.int32,
)

EXPECTED_KEYS = {
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
}


class VerificationFailure(RuntimeError):
    pass


def fail(message: str) -> None:
    raise VerificationFailure(message)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(8 * 1024 * 1024),
            b"",
        ):
            h.update(chunk)

    return h.hexdigest()


def expected_condition_rows() -> list[tuple[int, str, str, int]]:
    rows = []
    ordinal = 0

    for mask in MASKS:
        for replicate in REPLICATES:
            rows.append(
                (
                    ordinal,
                    f"sq08:{mask}:r{replicate}",
                    mask,
                    replicate,
                )
            )
            ordinal += 1

    return rows


def verify_npz(path: Path) -> dict:
    with np.load(
        path,
        allow_pickle=False,
    ) as z:
        keys = set(z.files)

        if keys != EXPECTED_KEYS:
            fail(
                "SQ-08 independent verifier "
                f"key-set drift: {sorted(keys)}"
            )

        expected_numeric = {
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

        for key, (shape, dtype) in expected_numeric.items():
            arr = z[key]

            if arr.shape != shape:
                fail(
                    f"{key} shape drift: "
                    f"{arr.shape} != {shape}"
                )

            if arr.dtype != np.dtype(dtype):
                fail(
                    f"{key} dtype drift: "
                    f"{arr.dtype} != {np.dtype(dtype)}"
                )

        for key in (
            "condition_id",
            "condition_mask",
            "episode_started_at_utc",
            "episode_completed_at_utc",
        ):
            if z[key].shape != (16,):
                fail(
                    f"{key} shape drift"
                )

            if z[key].dtype.kind != "U":
                fail(
                    f"{key} must be unicode"
                )

        if not np.array_equal(
            z["body_responder_indices"],
            BODY_RESPONDERS,
        ):
            fail(
                "BODY responder coordinate mismatch"
            )

        if not np.array_equal(
            z["frontier_indices"],
            FRONTIER_INDICES,
        ):
            fail(
                "frontier coordinate mismatch"
            )

        expected = expected_condition_rows()

        for i, (
            ordinal,
            condition_id,
            mask,
            replicate,
        ) in enumerate(expected):

            if int(
                z["condition_ordinal"][i]
            ) != ordinal:
                fail(
                    f"ordinal mismatch at {i}"
                )

            if str(
                z["condition_id"][i]
            ) != condition_id:
                fail(
                    f"condition ID mismatch at {i}"
                )

            if str(
                z["condition_mask"][i]
            ) != mask:
                fail(
                    f"mask mismatch at {i}"
                )

            if int(
                z["condition_replicate"][i]
            ) != replicate:
                fail(
                    f"replicate mismatch at {i}"
                )

        # Deterministic duplicate verification.
        duplicate_pairs = 0

        evidence_arrays = (
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
        )

        for mask_index, mask in enumerate(MASKS):
            first = mask_index * 2
            second = first + 1

            if str(
                z["condition_mask"][first]
            ) != mask:
                fail(
                    f"duplicate mask mismatch: {mask}"
                )

            if str(
                z["condition_mask"][second]
            ) != mask:
                fail(
                    f"duplicate mask mismatch: {mask}"
                )

            for key in evidence_arrays:
                if not np.array_equal(
                    z[key][first],
                    z[key][second],
                ):
                    fail(
                        "deterministic replicate "
                        f"mismatch {mask} / {key}"
                    )

            duplicate_pairs += 1

        if duplicate_pairs != 8:
            fail(
                "expected exactly 8 duplicate pairs"
            )

        # Binary spike contract.
        for key in (
            "primary_spikes",
            "body_responder_spikes",
            "frontier_spikes",
        ):
            values = np.unique(z[key])

            if not set(
                values.tolist()
            ).issubset({0, 1}):
                fail(
                    f"non-binary spike evidence: {key}"
                )

        # Finite numeric evidence.
        for key in (
            "primary_positive_voltage",
            "body_responder_voltage",
            "frontier_voltage",
            "channel_mean_positive_voltage",
            "channel_positive_fraction",
            "channel_spike_count",
            "channel_spike_rate",
            "episode_elapsed_seconds",
        ):
            if not np.all(
                np.isfinite(z[key])
            ):
                fail(
                    f"non-finite evidence: {key}"
                )

        return {
            "status": "VERIFIED",
            "episode_count": 16,
            "mask_count": 8,
            "duplicate_pair_count": 8,
            "body_responder_count": 3,
            "frontier_count": 18,
        }


def verify_manifest(
    manifest_path: Path,
) -> dict:
    payload = json.loads(
        manifest_path.read_text(
            encoding="utf-8",
        )
    )

    if (
        payload.get("schema_version")
        != "moscaquant.sq08-three-body-evidence/v1"
    ):
        fail(
            "unexpected SQ-08 evidence schema version"
        )

    if payload.get("episode_count") != 16:
        fail(
            "manifest episode count drift"
        )

    if (
        payload.get("duplicate_pairs_exact")
        is not True
    ):
        fail(
            "manifest does not assert exact duplicates"
        )

    if (
        payload.get("duplicate_pair_count")
        != 8
    ):
        fail(
            "manifest duplicate count drift"
        )

    sidecar = manifest_path.parent / (
        payload["sidecar"]["path"]
    )

    if not sidecar.is_file():
        fail(
            "manifest sidecar missing"
        )

    actual_sha = sha256_file(
        sidecar
    )

    expected_sha = payload[
        "sidecar"
    ][
        "sha256"
    ]

    if actual_sha != expected_sha:
        fail(
            "SQ-08 evidence sidecar SHA mismatch"
        )

    npz_report = verify_npz(
        sidecar
    )

    return {
        "status":
            "INDEPENDENT_VERIFICATION_PASS",
        "manifest_path":
            str(manifest_path),
        "manifest_sha256":
            sha256_file(manifest_path),
        "sidecar_path":
            str(sidecar),
        "sidecar_sha256":
            actual_sha,
        "npz":
            npz_report,
    }


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "manifest",
        type=Path,
    )

    args = parser.parse_args()

    report = verify_manifest(
        args.manifest.resolve()
    )

    print(
        json.dumps(
            report,
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
