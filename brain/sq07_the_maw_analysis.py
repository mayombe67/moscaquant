from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

import numpy as np

from brain.sq06_silent_cartographer_runner import (
    PRIMARY_L2_TOL,
    PRIMARY_MAX_ABS_TOL,
    exact_primary_reproduction,
)
from brain.sq07_the_maw_evidence import verify_shard_evidence


EXPECTED_ACQUISITION_HEAD = (
    "a4f5278d4f964c89b7b53bb9453a4355fd14b8a2"
)

RUN_ID = "sq07-maw-20260924-01"

AWS_AUTH_SHA256 = (
    "b6f99d8d61598f5e13867680266ad131"
    "edd82ef44db6f07ae0c2231742e65638"
)

TRANSPORT_SCHEMA = "moscaquant.rasputin.sq07-shard-transport.v1"

S3_RUN_PREFIX = (
    "s3://moscaquant-rasputin-artifacts-249215389153/"
    "sq07/the-maw/runs/sq07-maw-20260924-01/"
)

INTACT_MASK = "0000000000000"
FULL13_MASK = "1111111111111"

# E00-E09 = LR_OBSERVED
# E10-E12 = RL_OBSERVED
LR_GROUP_MASK = "1111111111000"
RL_GROUP_MASK = "0000000000111"

LAYOUTS = ("LR", "RL")
CLASSES = ("EXACT_INTACT", "EXACT_FULL13", "INTERMEDIATE")


class AnalysisRefusal(RuntimeError):
    pass


def refuse(message: str) -> None:
    raise AnalysisRefusal(message)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git_head() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"],
        text=True,
    ).strip()


def require_clean_worktree() -> None:
    status = subprocess.check_output(
        ["git", "status", "--porcelain"],
        text=True,
    )
    if status.strip():
        refuse("SQ-07 analysis requires a clean Git working tree")


def exact_against(candidate: np.ndarray, reference: np.ndarray) -> dict:
    return exact_primary_reproduction(
        {"positive_voltage": candidate},
        {"positive_voltage": reference},
    )


def classify_fingerprint(
    candidate: np.ndarray,
    intact: np.ndarray,
    full13: np.ndarray,
) -> dict:
    to_intact = exact_against(candidate, intact)
    to_full13 = exact_against(candidate, full13)

    exact_intact = bool(to_intact["exact_reproduction"])
    exact_full13 = bool(to_full13["exact_reproduction"])

    if exact_intact and exact_full13:
        refuse(
            "SQ-07 candidate is exact to both distinguishable anchors"
        )

    if exact_intact:
        classification = "EXACT_INTACT"
    elif exact_full13:
        classification = "EXACT_FULL13"
    else:
        classification = "INTERMEDIATE"

    return {
        "classification": classification,
        "to_intact": to_intact,
        "to_full13": to_full13,
    }


def strict_submasks(mask: str):
    value = int(mask, 2)
    sub = (value - 1) & value

    while True:
        yield f"{sub:013b}"

        if sub == 0:
            break

        sub = (sub - 1) & value


def inclusion_minimal_full13(
    exact_full13_masks: set[str],
) -> list[str]:
    minimal = []

    for mask in sorted(exact_full13_masks):
        if mask == INTACT_MASK:
            # This should be impossible if anchors are distinguishable.
            refuse("INTACT unexpectedly classified EXACT_FULL13")

        if not any(
            submask in exact_full13_masks
            for submask in strict_submasks(mask)
        ):
            minimal.append(mask)

    return minimal


def mask_uses_only_lr_group(mask: str) -> bool:
    return set(mask[10:]) <= {"0"} and "1" in mask[:10]


def mask_uses_only_rl_group(mask: str) -> bool:
    return set(mask[:10]) <= {"0"} and "1" in mask[10:]


def mask_contained_in_lr_group(mask: str) -> bool:
    return set(mask[10:]) <= {"0"}


def mask_contained_in_rl_group(mask: str) -> bool:
    return set(mask[:10]) <= {"0"}


def mask_is_mixed_group(mask: str) -> bool:
    return ("1" in mask[:10]) and ("1" in mask[10:])


def inactive_masks(layout: str) -> list[str]:
    if layout == "LR":
        # RL group is inactive in LR: 2^3 masks.
        return [
            f"{x:010b}{y:03b}"
            for x in (0,)
            for y in range(8)
        ]

    if layout == "RL":
        # LR group is inactive in RL: 2^10 masks.
        return [
            f"{x:010b}000"
            for x in range(1024)
        ]

    raise ValueError(layout)


def canonical_transport_paths(cloud_root: Path) -> list[Path]:
    paths = sorted(
        cloud_root.glob("sq07-shard-*/transport-manifest.json")
    )

    if len(paths) != 511:
        refuse(
            "SQ-07 analysis requires exactly 511 canonical "
            f"cloud transport manifests; found {len(paths)}"
        )

    return paths


def local_from_s3(cloud_root: Path, uri: str) -> Path:
    if not uri.startswith(S3_RUN_PREFIX):
        refuse(f"transport object outside canonical run prefix: {uri}")

    relative = uri[len(S3_RUN_PREFIX):]
    candidate = (cloud_root / relative).resolve()

    try:
        candidate.relative_to(cloud_root.resolve())
    except ValueError:
        refuse(f"unsafe transport object path: {uri}")

    return candidate


def accepted_cloud_manifest(
    cloud_root: Path,
    transport_path: Path,
) -> tuple[int, Path]:
    transport = json.loads(
        transport_path.read_text(encoding="utf-8")
    )

    shard_index = transport.get("shard_index")

    if not isinstance(shard_index, int):
        refuse("transport shard index is not int")

    if not 1 <= shard_index <= 511:
        refuse(f"invalid cloud shard index: {shard_index}")

    shard_id = f"sq07-shard-{shard_index:03d}"

    if transport.get("shard_id") != shard_id:
        refuse(f"{shard_id}: transport identity drift")

    if transport.get("run_id") != RUN_ID:
        refuse(f"{shard_id}: run ID drift")

    if transport.get("schema_version") != TRANSPORT_SCHEMA:
        refuse(f"{shard_id}: transport schema drift")

    if transport.get("science_git_sha") != EXPECTED_ACQUISITION_HEAD:
        refuse(f"{shard_id}: acquisition science SHA drift")

    if transport.get("authorization_sha256") != AWS_AUTH_SHA256:
        refuse(f"{shard_id}: AWS authorization SHA drift")

    if transport.get("remote_sha256_verified") is not True:
        refuse(f"{shard_id}: transport remote SHA not verified")

    manifest = local_from_s3(
        cloud_root,
        transport["science_manifest_object"],
    )
    sidecar = local_from_s3(
        cloud_root,
        transport["sidecar_object"],
    )

    if not manifest.is_file():
        refuse(f"{shard_id}: accepted science manifest missing")

    if not sidecar.is_file():
        refuse(f"{shard_id}: accepted evidence sidecar missing")

    if sha256_file(manifest) != transport["science_manifest_sha256"]:
        refuse(f"{shard_id}: science manifest SHA mismatch")

    if sha256_file(sidecar) != transport["sidecar_sha256"]:
        refuse(f"{shard_id}: evidence sidecar SHA mismatch")

    verify_shard_evidence(manifest)

    return shard_index, manifest


def load_anchor_from_manifest(
    manifest_path: Path,
    mask: str,
) -> dict[str, np.ndarray]:
    manifest = json.loads(
        manifest_path.read_text(encoding="utf-8")
    )
    sidecar_path = manifest_path.parent / manifest["sidecar"]["path"]

    found: dict[str, dict[int, np.ndarray]] = {
        "LR": {},
        "RL": {},
    }

    with np.load(sidecar_path, allow_pickle=False) as z:
        masks = np.asarray(z["condition_mask13"])
        layouts = np.asarray(z["condition_layout"])
        replicates = np.asarray(z["condition_replicate"])
        voltages = np.asarray(z["primary_positive_voltage"])

        for i in range(len(masks)):
            if str(masks[i]) != mask:
                continue

            layout = str(layouts[i])
            replicate = int(replicates[i])

            found[layout][replicate] = np.array(
                voltages[i],
                copy=True,
            )

    result = {}

    for layout in LAYOUTS:
        if set(found[layout]) != {1, 2}:
            refuse(
                f"anchor {mask}/{layout} does not contain both replicates"
            )

        if not np.array_equal(
            found[layout][1],
            found[layout][2],
        ):
            refuse(
                f"anchor {mask}/{layout} duplicates are not exact"
            )

        result[layout] = found[layout][1]

    return result


def classify_manifest(
    manifest_path: Path,
    anchors: dict[str, dict[str, np.ndarray]],
    classes: dict[str, dict[str, str]],
) -> int:
    verify_shard_evidence(manifest_path)

    manifest = json.loads(
        manifest_path.read_text(encoding="utf-8")
    )
    sidecar_path = manifest_path.parent / manifest["sidecar"]["path"]

    masks_seen = 0

    with np.load(sidecar_path, allow_pickle=False) as z:
        masks = np.asarray(z["condition_mask13"])
        layouts = np.asarray(z["condition_layout"])
        replicates = np.asarray(z["condition_replicate"])
        voltages = np.asarray(z["primary_positive_voltage"])

        if len(masks) != 64:
            refuse("verified shard did not contain 64 episodes")

        for offset in range(0, 64, 4):
            group_masks = {str(x) for x in masks[offset:offset + 4]}

            if len(group_masks) != 1:
                refuse("four-episode mask quartet drift")

            mask = next(iter(group_masks))

            expected = (
                ("LR", 1),
                ("LR", 2),
                ("RL", 1),
                ("RL", 2),
            )

            observed = tuple(
                (
                    str(layouts[offset + i]),
                    int(replicates[offset + i]),
                )
                for i in range(4)
            )

            if observed != expected:
                refuse(
                    f"{mask}: quartet layout/replicate ordering drift"
                )

            for layout, first, second in (
                ("LR", offset, offset + 1),
                ("RL", offset + 2, offset + 3),
            ):
                if not np.array_equal(
                    voltages[first],
                    voltages[second],
                ):
                    refuse(
                        f"{mask}/{layout}: primary duplicates differ"
                    )

                if mask in classes[layout]:
                    refuse(
                        f"duplicate mask/layout classification: "
                        f"{mask}/{layout}"
                    )

                report = classify_fingerprint(
                    voltages[first],
                    anchors["INTACT"][layout],
                    anchors["FULL13"][layout],
                )

                classes[layout][mask] = report["classification"]

            masks_seen += 1

    return masks_seen


def build_result(
    classes: dict[str, dict[str, str]],
    anchor_distinguishability: dict,
    analysis_head: str,
) -> dict:
    for layout in LAYOUTS:
        if len(classes[layout]) != 8192:
            refuse(
                f"{layout}: expected 8192 mask classifications; "
                f"found {len(classes[layout])}"
            )

        expected_masks = {
            f"{x:013b}"
            for x in range(8192)
        }

        if set(classes[layout]) != expected_masks:
            refuse(f"{layout}: mask universe is not exact")

    class_counts = {}
    class_masks = {}
    minimal = {}
    inactive_failures = {}
    partition = {}

    for layout in LAYOUTS:
        class_counts[layout] = {
            cls: sum(
                value == cls
                for value in classes[layout].values()
            )
            for cls in CLASSES
        }

        class_masks[layout] = {
            cls: [
                mask
                for mask in sorted(classes[layout])
                if classes[layout][mask] == cls
            ]
            for cls in CLASSES
        }

        exact_full = set(
            class_masks[layout]["EXACT_FULL13"]
        )

        minimal[layout] = inclusion_minimal_full13(exact_full)

        inactive_failures[layout] = [
            mask
            for mask in inactive_masks(layout)
            if classes[layout][mask] != "EXACT_INTACT"
        ]

    partition["LR"] = {
        "active_group_mask": LR_GROUP_MASK,
        "active_group_class": classes["LR"][LR_GROUP_MASK],
        "inactive_group_mask": RL_GROUP_MASK,
        "inactive_group_class": classes["LR"][RL_GROUP_MASK],
        "pass": (
            classes["LR"][LR_GROUP_MASK] == "EXACT_FULL13"
            and classes["LR"][RL_GROUP_MASK] == "EXACT_INTACT"
        ),
    }

    partition["RL"] = {
        "active_group_mask": RL_GROUP_MASK,
        "active_group_class": classes["RL"][RL_GROUP_MASK],
        "inactive_group_mask": LR_GROUP_MASK,
        "inactive_group_class": classes["RL"][LR_GROUP_MASK],
        "pass": (
            classes["RL"][RL_GROUP_MASK] == "EXACT_FULL13"
            and classes["RL"][LR_GROUP_MASK] == "EXACT_INTACT"
        ),
    }

    closure = {
        layout: len(inactive_failures[layout]) == 0
        for layout in LAYOUTS
    }

    minimal_details = {}

    for layout in LAYOUTS:
        if layout == "LR":
            active_only = mask_contained_in_lr_group
        else:
            active_only = mask_contained_in_rl_group

        minimal_details[layout] = [
            {
                "mask13": mask,
                "hamming_weight": mask.count("1"),
                "active_group_only": active_only(mask),
                "mixed_group": mask_is_mixed_group(mask),
            }
            for mask in minimal[layout]
        ]

    all_minimal_active_only = all(
        row["active_group_only"]
        for layout in LAYOUTS
        for row in minimal_details[layout]
    )

    mixed_present = any(
        row["mixed_group"]
        for layout in LAYOUTS
        for row in minimal_details[layout]
    )

    sq06_partition_replicated = all(
        partition[layout]["pass"]
        for layout in LAYOUTS
    )

    inactive_closure_supported = all(closure.values())
    inactive_effect_present = not inactive_closure_supported

    strict_subset_separability = (
        sq06_partition_replicated
        and inactive_closure_supported
        and all_minimal_active_only
        and not mixed_present
    )

    flags = {
        "SQ06_PARTITION_REPLICATED":
            sq06_partition_replicated,
        "INACTIVE_SUBSET_CLOSURE_SUPPORTED":
            inactive_closure_supported,
        "INACTIVE_SUBSET_EFFECT_PRESENT":
            inactive_effect_present,
        "ALL_MINIMAL_FULL13_RECAPITULATORS_ACTIVE_ONLY":
            all_minimal_active_only,
        "MIXED_GROUP_MINIMAL_RECAPITULATOR_PRESENT":
            mixed_present,
        "STRICT_SUBSET_SEPARABILITY_SUPPORTED":
            strict_subset_separability,
    }

    return {
        "artifact": "sq07-the-maw-analysis-result-v1",
        "status": "PREREGISTERED_ANALYSIS_COMPLETE",
        "run_id": RUN_ID,
        "acquisition_science_git_sha": EXPECTED_ACQUISITION_HEAD,
        "analysis_git_sha": analysis_head,
        "endpoint": {
            "fingerprint": "primary_positive_voltage",
            "shape": [192, 1191],
            "symmetric_normalized_l2_exact_max": PRIMARY_L2_TOL,
            "max_abs_exact_max": PRIMARY_MAX_ABS_TOL,
            "classes": list(CLASSES),
        },
        "universe": {
            "mask_count": 8192,
            "layouts": list(LAYOUTS),
            "replicates_per_mask_layout": 2,
            "episode_count": 32768,
        },
        "anchor_distinguishability": anchor_distinguishability,
        "class_counts": class_counts,
        "class_masks": class_masks,
        "sq06_partition": partition,
        "inactive_subset": {
            "closure_by_layout": closure,
            "failures_by_layout": inactive_failures,
        },
        "minimal_full13_recapitulators": minimal_details,
        "result_flags": flags,
        "single_overall_winner": None,
        "minimum_meaningful_effect_floor": "NOT_DEFINED",
        "claim_boundaries": {
            "biological_behavior_claim": False,
            "population_level_biology_claim": False,
            "financial_value_claim": False,
            "intermediate_has_biological_meaning": False,
            "sq05_reinterpreted": False,
            "sq06_reinterpreted": False,
        },
    }


def analyze(
    *,
    cloud_root: Path,
    shard000_dir: Path,
) -> dict:
    require_clean_worktree()
    analysis_head = git_head()

    manifest000 = (
        shard000_dir / "sq07-shard-000.manifest.json"
    )

    if not manifest000.is_file():
        refuse("local shard 000 manifest missing")

    verify_shard_evidence(manifest000)

    transports = canonical_transport_paths(cloud_root)

    cloud_manifests = {}

    for transport_path in transports:
        shard_index, manifest_path = accepted_cloud_manifest(
            cloud_root,
            transport_path,
        )

        if shard_index in cloud_manifests:
            refuse(f"duplicate cloud shard {shard_index:03d}")

        cloud_manifests[shard_index] = manifest_path

    if set(cloud_manifests) != set(range(1, 512)):
        refuse("cloud shard universe is not exactly 001-511")

    anchors = {
        "INTACT": load_anchor_from_manifest(
            manifest000,
            INTACT_MASK,
        ),
        "FULL13": load_anchor_from_manifest(
            cloud_manifests[511],
            FULL13_MASK,
        ),
    }

    anchor_distinguishability = {}

    for layout in LAYOUTS:
        comparison = exact_against(
            anchors["INTACT"][layout],
            anchors["FULL13"][layout],
        )

        if comparison["exact_reproduction"]:
            refuse(
                f"{layout}: INTACT and FULL13 anchors collapsed"
            )

        anchor_distinguishability[layout] = {
            **comparison,
            "distinguishable": True,
        }

    classes = {
        "LR": {},
        "RL": {},
    }

    total_masks = classify_manifest(
        manifest000,
        anchors,
        classes,
    )

    for shard_index in range(1, 512):
        total_masks += classify_manifest(
            cloud_manifests[shard_index],
            anchors,
            classes,
        )

    if total_masks != 8192:
        refuse(
            f"expected 8192 mask quartets; found {total_masks}"
        )

    return build_result(
        classes,
        anchor_distinguishability,
        analysis_head,
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
        "--output",
        required=True,
        type=Path,
    )

    args = parser.parse_args()

    if args.output.exists():
        refuse(
            f"refusing to overwrite existing analysis result: "
            f"{args.output}"
        )

    result = analyze(
        cloud_root=args.cloud_root.resolve(),
        shard000_dir=args.shard000_dir.resolve(),
    )

    args.output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    args.output.write_text(
        json.dumps(
            result,
            indent=2,
            sort_keys=True,
        ) + "\n",
        encoding="utf-8",
    )

    print("SQ-07 THE MAW ANALYSIS COMPLETE")
    print(f"result: {args.output}")
    print()
    print("RESULT FLAGS")

    for key, value in result["result_flags"].items():
        print(f"{key}: {value}")

    print()
    for layout in LAYOUTS:
        print(
            f"{layout} minimal FULL13 recapitulators: "
            f"{len(result['minimal_full13_recapitulators'][layout])}"
        )


if __name__ == "__main__":
    main()
