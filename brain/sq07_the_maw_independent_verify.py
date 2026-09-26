from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from brain.sq07_the_maw_evidence import verify_shard_evidence


RUN_ID = "sq07-maw-20260924-01"

ACQUISITION_HEAD = (
    "a4f5278d4f964c89b7b53bb9453a4355fd14b8a2"
)

ANALYSIS_HEAD = (
    "2455b7f3312d254147a67a85fb774767a52c5589"
)

EXPECTED_RESULT_SHA256 = (
    "2db405151cc8771ccd0c50080bcd6a83"
    "ca3824e5487c666d22e01db8bed6d80c"
)

AWS_AUTH_SHA256 = (
    "b6f99d8d61598f5e13867680266ad131"
    "edd82ef44db6f07ae0c2231742e65638"
)

TRANSPORT_SCHEMA = (
    "moscaquant.rasputin.sq07-shard-transport.v1"
)

S3_RUN_PREFIX = (
    "s3://moscaquant-rasputin-artifacts-249215389153/"
    "sq07/the-maw/runs/sq07-maw-20260924-01/"
)

L2_TOL = 1e-9
MAX_ABS_TOL = 1e-12

INTACT = "0000000000000"
FULL13 = "1111111111111"

LR_GROUP = "1111111111000"
RL_GROUP = "0000000000111"

LAYOUTS = ("LR", "RL")
CLASSES = ("EXACT_INTACT", "EXACT_FULL13", "INTERMEDIATE")


class VerificationError(RuntimeError):
    pass


def refuse(message: str) -> None:
    raise VerificationError(message)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()

    with path.open("rb") as handle:
        for block in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            h.update(block)

    return h.hexdigest()


def symmetric_normalized_l2(a, b) -> float:
    x = np.asarray(a, dtype=np.float64).reshape(-1)
    y = np.asarray(b, dtype=np.float64).reshape(-1)

    numerator = float(np.linalg.norm(x - y))

    denominator = max(
        float(np.linalg.norm(x) + np.linalg.norm(y)),
        1e-12,
    )

    return numerator / denominator


def max_abs_difference(a, b) -> float:
    x = np.asarray(a, dtype=np.float64)
    y = np.asarray(b, dtype=np.float64)

    return float(
        np.max(
            np.abs(x - y),
            initial=0.0,
        )
    )


def exact(candidate, reference) -> dict:
    l2 = symmetric_normalized_l2(
        candidate,
        reference,
    )

    max_abs = max_abs_difference(
        candidate,
        reference,
    )

    return {
        "symmetric_normalized_l2": l2,
        "max_abs": max_abs,
        "exact_reproduction": (
            l2 <= L2_TOL
            and max_abs <= MAX_ABS_TOL
        ),
    }


def classify(candidate, intact, full13) -> str:
    to_intact = exact(candidate, intact)
    to_full13 = exact(candidate, full13)

    is_intact = to_intact["exact_reproduction"]
    is_full13 = to_full13["exact_reproduction"]

    if is_intact and is_full13:
        refuse(
            "candidate is exact to both supposedly "
            "distinguishable anchors"
        )

    if is_intact:
        return "EXACT_INTACT"

    if is_full13:
        return "EXACT_FULL13"

    return "INTERMEDIATE"


def strict_submasks(mask: str):
    value = int(mask, 2)
    sub = (value - 1) & value

    while True:
        yield f"{sub:013b}"

        if sub == 0:
            break

        sub = (sub - 1) & value


def minimal_full13(
    exact_full13: set[str],
) -> list[str]:
    result = []

    for mask in sorted(exact_full13):
        if mask == INTACT:
            refuse("INTACT classified EXACT_FULL13")

        if not any(
            sub in exact_full13
            for sub in strict_submasks(mask)
        ):
            result.append(mask)

    return result


def inactive_masks(layout: str) -> list[str]:
    if layout == "LR":
        return [
            f"0000000000{x:03b}"
            for x in range(8)
        ]

    if layout == "RL":
        return [
            f"{x:010b}000"
            for x in range(1024)
        ]

    raise ValueError(layout)


def contained_in_active_group(
    layout: str,
    mask: str,
) -> bool:
    if layout == "LR":
        return set(mask[10:]) <= {"0"}

    if layout == "RL":
        return set(mask[:10]) <= {"0"}

    raise ValueError(layout)


def mixed_group(mask: str) -> bool:
    return (
        "1" in mask[:10]
        and "1" in mask[10:]
    )


def local_from_s3(
    cloud_root: Path,
    uri: str,
) -> Path:
    if not isinstance(uri, str):
        refuse("transport URI is not string")

    if not uri.startswith(S3_RUN_PREFIX):
        refuse(
            f"object outside canonical run: {uri}"
        )

    candidate = (
        cloud_root / uri[len(S3_RUN_PREFIX):]
    ).resolve()

    try:
        candidate.relative_to(
            cloud_root.resolve()
        )
    except ValueError:
        refuse(f"unsafe transport path: {uri}")

    return candidate


def accepted_cloud_manifests(
    cloud_root: Path,
) -> dict[int, Path]:
    transport_paths = sorted(
        cloud_root.glob(
            "sq07-shard-*/transport-manifest.json"
        )
    )

    if len(transport_paths) != 511:
        refuse(
            "expected 511 canonical cloud transports; "
            f"found {len(transport_paths)}"
        )

    accepted = {}

    for transport_path in transport_paths:
        transport = json.loads(
            transport_path.read_text(
                encoding="utf-8"
            )
        )

        shard_index = transport.get(
            "shard_index"
        )

        if (
            not isinstance(shard_index, int)
            or not 1 <= shard_index <= 511
        ):
            refuse(
                f"invalid shard index: {shard_index}"
            )

        shard_id = (
            f"sq07-shard-{shard_index:03d}"
        )

        if transport.get("shard_id") != shard_id:
            refuse(
                f"{shard_id}: identity drift"
            )

        if transport.get("run_id") != RUN_ID:
            refuse(
                f"{shard_id}: run ID drift"
            )

        if (
            transport.get("schema_version")
            != TRANSPORT_SCHEMA
        ):
            refuse(
                f"{shard_id}: transport schema drift"
            )

        if (
            transport.get("science_git_sha")
            != ACQUISITION_HEAD
        ):
            refuse(
                f"{shard_id}: acquisition SHA drift"
            )

        if (
            transport.get("authorization_sha256")
            != AWS_AUTH_SHA256
        ):
            refuse(
                f"{shard_id}: authorization SHA drift"
            )

        if (
            transport.get(
                "remote_sha256_verified"
            )
            is not True
        ):
            refuse(
                f"{shard_id}: remote hash "
                "verification absent"
            )

        manifest = local_from_s3(
            cloud_root,
            transport[
                "science_manifest_object"
            ],
        )

        sidecar = local_from_s3(
            cloud_root,
            transport["sidecar_object"],
        )

        if not manifest.is_file():
            refuse(
                f"{shard_id}: manifest missing"
            )

        if not sidecar.is_file():
            refuse(
                f"{shard_id}: sidecar missing"
            )

        if (
            sha256_file(manifest)
            != transport[
                "science_manifest_sha256"
            ]
        ):
            refuse(
                f"{shard_id}: manifest SHA mismatch"
            )

        if (
            sha256_file(sidecar)
            != transport["sidecar_sha256"]
        ):
            refuse(
                f"{shard_id}: sidecar SHA mismatch"
            )

        verify_shard_evidence(manifest)

        if shard_index in accepted:
            refuse(
                f"duplicate shard {shard_index:03d}"
            )

        accepted[shard_index] = manifest

    if set(accepted) != set(range(1, 512)):
        refuse(
            "cloud shard universe is not "
            "exactly 001-511"
        )

    return accepted


def load_sidecar(
    manifest_path: Path,
) -> dict[str, np.ndarray]:
    verify_shard_evidence(manifest_path)

    manifest = json.loads(
        manifest_path.read_text(
            encoding="utf-8"
        )
    )

    sidecar = (
        manifest_path.parent
        / manifest["sidecar"]["path"]
    )

    with np.load(
        sidecar,
        allow_pickle=False,
    ) as z:
        return {
            key: np.array(
                z[key],
                copy=True,
            )
            for key in (
                "condition_mask13",
                "condition_layout",
                "condition_replicate",
                "primary_positive_voltage",
            )
        }


def extract_anchor(
    manifest_path: Path,
    wanted_mask: str,
) -> dict[str, np.ndarray]:
    z = load_sidecar(manifest_path)

    found = {
        "LR": {},
        "RL": {},
    }

    for i in range(
        len(z["condition_mask13"])
    ):
        mask = str(
            z["condition_mask13"][i]
        )

        if mask != wanted_mask:
            continue

        layout = str(
            z["condition_layout"][i]
        )

        replicate = int(
            z["condition_replicate"][i]
        )

        found[layout][replicate] = (
            z["primary_positive_voltage"][i]
        )

    result = {}

    for layout in LAYOUTS:
        if set(found[layout]) != {1, 2}:
            refuse(
                f"{wanted_mask}/{layout}: "
                "anchor replicates incomplete"
            )

        if not np.array_equal(
            found[layout][1],
            found[layout][2],
        ):
            refuse(
                f"{wanted_mask}/{layout}: "
                "anchor duplicates differ"
            )

        result[layout] = (
            found[layout][1]
        )

    return result


def classify_shard(
    manifest_path: Path,
    anchors: dict,
    classes: dict,
) -> int:
    z = load_sidecar(manifest_path)

    masks = z["condition_mask13"]
    layouts = z["condition_layout"]
    reps = z["condition_replicate"]
    voltage = z["primary_positive_voltage"]

    if len(masks) != 64:
        refuse(
            "verified sidecar did not contain "
            "64 episodes"
        )

    mask_count = 0

    for offset in range(0, 64, 4):
        quartet_masks = {
            str(x)
            for x in masks[
                offset:offset + 4
            ]
        }

        if len(quartet_masks) != 1:
            refuse("mask quartet drift")

        mask = next(iter(quartet_masks))

        observed = tuple(
            (
                str(layouts[offset + i]),
                int(reps[offset + i]),
            )
            for i in range(4)
        )

        expected = (
            ("LR", 1),
            ("LR", 2),
            ("RL", 1),
            ("RL", 2),
        )

        if observed != expected:
            refuse(
                f"{mask}: episode ordering drift"
            )

        for layout, first, second in (
            ("LR", offset, offset + 1),
            ("RL", offset + 2, offset + 3),
        ):
            if not np.array_equal(
                voltage[first],
                voltage[second],
            ):
                refuse(
                    f"{mask}/{layout}: "
                    "duplicates differ"
                )

            if mask in classes[layout]:
                refuse(
                    f"{mask}/{layout}: "
                    "duplicate classification"
                )

            classes[layout][mask] = classify(
                voltage[first],
                anchors["INTACT"][layout],
                anchors["FULL13"][layout],
            )

        mask_count += 1

    return mask_count


def recompute(
    local_manifest: Path,
    cloud_manifests: dict[int, Path],
) -> dict:
    anchors = {
        "INTACT": extract_anchor(
            local_manifest,
            INTACT,
        ),
        "FULL13": extract_anchor(
            cloud_manifests[511],
            FULL13,
        ),
    }

    anchor_distinguishability = {}

    for layout in LAYOUTS:
        comparison = exact(
            anchors["INTACT"][layout],
            anchors["FULL13"][layout],
        )

        if comparison["exact_reproduction"]:
            refuse(
                f"{layout}: anchors collapsed"
            )

        anchor_distinguishability[
            layout
        ] = {
            **comparison,
            "distinguishable": True,
        }

    classes = {
        "LR": {},
        "RL": {},
    }

    masks_seen = classify_shard(
        local_manifest,
        anchors,
        classes,
    )

    for shard_index in range(1, 512):
        masks_seen += classify_shard(
            cloud_manifests[shard_index],
            anchors,
            classes,
        )

    if masks_seen != 8192:
        refuse(
            f"expected 8192 masks; "
            f"found {masks_seen}"
        )

    expected_masks = {
        f"{x:013b}"
        for x in range(8192)
    }

    for layout in LAYOUTS:
        if set(classes[layout]) != expected_masks:
            refuse(
                f"{layout}: mask universe drift"
            )

    class_counts = {}
    class_masks = {}
    minimal_details = {}
    inactive_failures = {}

    for layout in LAYOUTS:
        class_counts[layout] = {
            cls: sum(
                value == cls
                for value
                in classes[layout].values()
            )
            for cls in CLASSES
        }

        class_masks[layout] = {
            cls: [
                mask
                for mask in sorted(
                    classes[layout]
                )
                if (
                    classes[layout][mask]
                    == cls
                )
            ]
            for cls in CLASSES
        }

        exact_full = set(
            class_masks[layout][
                "EXACT_FULL13"
            ]
        )

        mins = minimal_full13(
            exact_full
        )

        minimal_details[layout] = [
            {
                "mask13": mask,
                "hamming_weight":
                    mask.count("1"),
                "active_group_only":
                    contained_in_active_group(
                        layout,
                        mask,
                    ),
                "mixed_group":
                    mixed_group(mask),
            }
            for mask in mins
        ]

        inactive_failures[layout] = [
            mask
            for mask in inactive_masks(
                layout
            )
            if (
                classes[layout][mask]
                != "EXACT_INTACT"
            )
        ]

    partition = {
        "LR": {
            "active_group_mask":
                LR_GROUP,
            "active_group_class":
                classes["LR"][LR_GROUP],
            "inactive_group_mask":
                RL_GROUP,
            "inactive_group_class":
                classes["LR"][RL_GROUP],
            "pass": (
                classes["LR"][LR_GROUP]
                == "EXACT_FULL13"
                and
                classes["LR"][RL_GROUP]
                == "EXACT_INTACT"
            ),
        },
        "RL": {
            "active_group_mask":
                RL_GROUP,
            "active_group_class":
                classes["RL"][RL_GROUP],
            "inactive_group_mask":
                LR_GROUP,
            "inactive_group_class":
                classes["RL"][LR_GROUP],
            "pass": (
                classes["RL"][RL_GROUP]
                == "EXACT_FULL13"
                and
                classes["RL"][LR_GROUP]
                == "EXACT_INTACT"
            ),
        },
    }

    closure = {
        layout: (
            len(
                inactive_failures[
                    layout
                ]
            )
            == 0
        )
        for layout in LAYOUTS
    }

    partition_ok = all(
        partition[x]["pass"]
        for x in LAYOUTS
    )

    closure_ok = all(
        closure.values()
    )

    all_active_only = all(
        row["active_group_only"]
        for layout in LAYOUTS
        for row in minimal_details[
            layout
        ]
    )

    mixed_present = any(
        row["mixed_group"]
        for layout in LAYOUTS
        for row in minimal_details[
            layout
        ]
    )

    flags = {
        "SQ06_PARTITION_REPLICATED":
            partition_ok,
        "INACTIVE_SUBSET_CLOSURE_SUPPORTED":
            closure_ok,
        "INACTIVE_SUBSET_EFFECT_PRESENT":
            not closure_ok,
        "ALL_MINIMAL_FULL13_RECAPITULATORS_ACTIVE_ONLY":
            all_active_only,
        "MIXED_GROUP_MINIMAL_RECAPITULATOR_PRESENT":
            mixed_present,
        "STRICT_SUBSET_SEPARABILITY_SUPPORTED":
            (
                partition_ok
                and closure_ok
                and all_active_only
                and not mixed_present
            ),
    }

    return {
        "anchor_distinguishability":
            anchor_distinguishability,
        "class_counts":
            class_counts,
        "class_masks":
            class_masks,
        "sq06_partition":
            partition,
        "inactive_subset": {
            "closure_by_layout":
                closure,
            "failures_by_layout":
                inactive_failures,
        },
        "minimal_full13_recapitulators":
            minimal_details,
        "result_flags":
            flags,
    }


def verify_reported_result(
    recomputed: dict,
    result: dict,
) -> None:
    if (
        result.get("run_id")
        != RUN_ID
    ):
        refuse("reported run ID drift")

    if (
        result.get(
            "acquisition_science_git_sha"
        )
        != ACQUISITION_HEAD
    ):
        refuse(
            "reported acquisition SHA drift"
        )

    if (
        result.get("analysis_git_sha")
        != ANALYSIS_HEAD
    ):
        refuse(
            "reported analysis SHA drift"
        )

    for key in (
        "anchor_distinguishability",
        "class_counts",
        "class_masks",
        "sq06_partition",
        "inactive_subset",
        "minimal_full13_recapitulators",
        "result_flags",
    ):
        if result.get(key) != recomputed[key]:
            refuse(
                f"reported result disagrees "
                f"with independent "
                f"recomputation: {key}"
            )

    if (
        result.get(
            "single_overall_winner"
        )
        is not None
    ):
        refuse(
            "single overall winner "
            "must remain null"
        )

    if (
        result.get(
            "minimum_meaningful_effect_floor"
        )
        != "NOT_DEFINED"
    ):
        refuse(
            "meaningful-effect floor drift"
        )


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--cloud-root",
        required=True,
        type=Path,
    )

    parser.add_argument(
        "--shard000-dir",
        required=True,
        type=Path,
    )

    parser.add_argument(
        "--result",
        required=True,
        type=Path,
    )

    parser.add_argument(
        "--verification-output",
        required=True,
        type=Path,
    )

    args = parser.parse_args()

    result_path = args.result.resolve()

    if not result_path.is_file():
        refuse("analysis result missing")

    actual_result_sha = sha256_file(
        result_path
    )

    if (
        actual_result_sha
        != EXPECTED_RESULT_SHA256
    ):
        refuse(
            "analysis result SHA mismatch"
        )

    local_manifest = (
        args.shard000_dir.resolve()
        / "sq07-shard-000.manifest.json"
    )

    if not local_manifest.is_file():
        refuse(
            "local shard 000 manifest missing"
        )

    verify_shard_evidence(
        local_manifest
    )

    cloud_manifests = (
        accepted_cloud_manifests(
            args.cloud_root.resolve()
        )
    )

    recomputed = recompute(
        local_manifest,
        cloud_manifests,
    )

    result = json.loads(
        result_path.read_text(
            encoding="utf-8"
        )
    )

    verify_reported_result(
        recomputed,
        result,
    )

    verification = {
        "artifact":
            "sq07-the-maw-independent-verification-v1",
        "status": "PASS",
        "run_id": RUN_ID,
        "analysis_result_sha256":
            actual_result_sha,
        "analysis_git_sha":
            ANALYSIS_HEAD,
        "acquisition_git_sha":
            ACQUISITION_HEAD,
        "shards_verified": 512,
        "cloud_shards_verified": 511,
        "local_shards_verified": 1,
        "episodes_verified": 32768,
        "mask_layout_conditions_verified":
            16384,
        "classification_recomputed":
            True,
        "minimality_recomputed":
            True,
        "result_flags_recomputed":
            True,
        "analysis_module_imported":
            False,
        "sq06_classifier_imported":
            False,
        "result_mutation":
            False,
        "result_flags":
            recomputed[
                "result_flags"
            ],
        "minimal_full13_recapitulators":
            recomputed[
                "minimal_full13_recapitulators"
            ],
    }

    output = (
        args.verification_output.resolve()
    )

    if output.exists():
        refuse(
            "refusing to overwrite existing "
            "verification output"
        )

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output.write_text(
        json.dumps(
            verification,
            indent=2,
            sort_keys=True,
        ) + "\n",
        encoding="utf-8",
    )

    print(
        "SQ-07 THE MAW INDEPENDENT "
        "VERIFICATION: PASS"
    )

    print(
        f"result SHA-256: "
        f"{actual_result_sha}"
    )

    print(
        "shards verified: 512/512"
    )

    print(
        "episodes verified: 32768/32768"
    )

    print()

    for key, value in (
        recomputed[
            "result_flags"
        ].items()
    ):
        print(
            f"{key}: {value}"
        )


if __name__ == "__main__":
    main()
