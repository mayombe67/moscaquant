from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tomllib
from dataclasses import asdict, is_dataclass
from pathlib import Path

import numpy as np
from scipy import sparse

from config.paths import data_path
from brain.mq5_er_encoder import (
    ARM_A,
    ARM_B,
    ARM_C,
    ARM_D,
    ARM_E,
    EncodingVariant,
    balanced_asset_territory_mappings,
)
from brain.mq5_er_real_artifact_verify import (
    build_normalized_episode,
    encode_episode_variant,
    sha256_array,
)
from brain.mq5_ts_metrics import compare_fingerprints
from brain.mq5_ts_runtime import (
    CONNECTOME,
    RETINA,
    evaluate_topology,
    frozen_edges,
    frozen_responders,
    lesion_frozen_edges,
    load_frozen_causal_artifact,
)


CONFIG = Path("config/controls/mq5-er-encoding-robustness-v1.toml")
ENCODING_GATE = Path(
    "artifacts/mq5-er-encoding-real-artifact-verification-v1.json"
)
OUTPUT = data_path(
    "experiments",
    "mq5-er-encoding-robustness-v1.json",
)

EXPECTED_ENCODING_GATE_SHA256 = (
    "15340cae365c291424f88ac3206e7ddc3f16885a52e89aece96d347bba741acb"
)
EXPECTED_MQ5_TS_A_PAYLOAD_SHA256 = (
    "03f0149a7c2bbd05869eda3cf799d2368eeab4dd493c4f0c44d8147d6ae51b9c"
)
EXPECTED_MQ5_TS_D_PAYLOAD_SHA256 = (
    "d321ed9288404db49d41c45110c0b97b891869fec08212c3ed97c89f14548ed3"
)

REQUIRED_TRACKED_FILES = (
    "config/controls/mq5-er-encoding-robustness-v1.toml",
    "artifacts/mq5-er-encoding-real-artifact-verification-v1.json",
    "brain/mq5_er_encoder.py",
    "brain/mq5_er_real_artifact_verify.py",
    "brain/mq5_er_neural_runner.py",
    "tests/brain/test_mq5_er_encoder.py",
    "tests/brain/test_mq5_er_real_artifact_verify.py",
    "tests/brain/test_mq5_er_neural_runner.py",
    "docs/experiments/mq5-er-encoding-robustness-protocol.md",
    "docs/experiments/mq5-er-encoding-robustness-amendment-v1.md",
    "docs/experiments/mq5-er-response-classification-contract-v1.md",
    "docs/experiments/mq5-er-response-contract-amendment-v1.md",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_payload_bytes(result) -> bytes:
    payload = asdict(result) if is_dataclass(result) else result
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def canonical_payload_sha256(result) -> str:
    return hashlib.sha256(
        canonical_payload_bytes(result)
    ).hexdigest()


def git_status_porcelain() -> str:
    completed = subprocess.run(
        ["git", "status", "--porcelain"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            "unable to inspect git status: "
            + completed.stdout
        )
    return completed.stdout


def git_head() -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            "unable to determine git HEAD: "
            + completed.stdout
        )
    return completed.stdout.strip()


def load_protocol() -> dict:
    with CONFIG.open("rb") as handle:
        return tomllib.load(handle)


def execution_gate(protocol: dict | None = None) -> str:
    protocol = load_protocol() if protocol is None else protocol

    if not protocol["execution"]["result_execution_enabled"]:
        raise RuntimeError(
            "MQ-5.ER RESULT EXECUTION REFUSED: "
            "result_execution_enabled is false"
        )

    if not protocol["classification"][
        "preservation_tolerances_frozen"
    ]:
        raise RuntimeError(
            "MQ-5.ER RESULT EXECUTION REFUSED: "
            "classification contract is not frozen"
        )

    if sha256_file(ENCODING_GATE) != EXPECTED_ENCODING_GATE_SHA256:
        raise RuntimeError(
            "MQ-5.ER encoding verification artifact hash mismatch"
        )

    if git_status_porcelain().strip():
        raise RuntimeError(
            "MQ-5.ER RESULT EXECUTION REFUSED: "
            "working tree is not clean"
        )

    completed = subprocess.run(
        [
            "git",
            "ls-files",
            "--error-unmatch",
            *REQUIRED_TRACKED_FILES,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            "MQ-5.ER RESULT EXECUTION REFUSED: "
            "required frozen files are not all tracked"
        )

    if OUTPUT.exists():
        raise RuntimeError(
            f"MQ-5.ER result artifact already exists: {OUTPUT}"
        )

    return git_head()


def stimulus_list(
    episode: list[np.ndarray],
    variant: EncodingVariant,
) -> list[np.ndarray]:
    sequence = encode_episode_variant(
        episode,
        variant,
    )
    return [
        np.asarray(frame, dtype=np.float32)
        for frame in sequence
    ]


def verify_stimulus_hash(
    sequence: list[np.ndarray],
    expected_sha256: str,
    label: str,
) -> str:
    array = np.stack(sequence, axis=0)
    actual = sha256_array(array)
    if actual != expected_sha256:
        raise RuntimeError(
            f"{label} stimulus hash mismatch: "
            f"{actual} != {expected_sha256}"
        )
    return actual


def present_targets(result) -> tuple[int, ...]:
    return tuple(
        sorted(
            int(index)
            for index, onset
            in result.first_positive_onsets.items()
            if onset is not None
        )
    )


def causal_expression_report(
    baseline_result,
    lesion_result,
    targets: tuple[int, ...],
) -> dict:
    rows = {}
    all_expressed = True

    for target in targets:
        base = baseline_result.first_positive_onsets[
            int(target)
        ]
        lesion = lesion_result.first_positive_onsets[
            int(target)
        ]

        expressed = (
            base is not None
            and (
                lesion is None
                or int(lesion) > int(base)
            )
        )

        rows[str(target)] = {
            "baseline_onset": base,
            "lesion_onset": lesion,
            "expressed": bool(expressed),
        }

        all_expressed = (
            all_expressed
            and bool(expressed)
        )

    return {
        "all_targets_expressed": bool(all_expressed),
        "targets": rows,
    }


def classify_encoding(
    arm_a_result,
    baseline_result,
    lesion_result,
    *,
    targets: tuple[int, ...],
    fingerprint_tolerance: float,
) -> dict:
    target_set = tuple(sorted(int(x) for x in targets))
    present = present_targets(baseline_result)
    all_present = present == target_set

    causal = causal_expression_report(
        baseline_result,
        lesion_result,
        target_set,
    )

    onset_exact = (
        baseline_result.first_positive_onsets
        == arm_a_result.first_positive_onsets
    )

    fingerprint = compare_fingerprints(
        np.asarray(
            arm_a_result.positive_voltage_fingerprint,
            dtype=np.float64,
        ),
        np.asarray(
            baseline_result.positive_voltage_fingerprint,
            dtype=np.float64,
        ),
    )

    fingerprint_match = (
        fingerprint["normalized_l2_distance"]
        <= float(fingerprint_tolerance)
    )

    if (
        all_present
        and onset_exact
        and fingerprint_match
        and causal["all_targets_expressed"]
    ):
        label = "RESPONSE PATTERN PRESERVED"
    elif (
        all_present
        and causal["all_targets_expressed"]
    ):
        label = "RESPONSE RETAINED WITH ALTERED EXPRESSION"
    else:
        label = "RESPONSE PATTERN NOT RETAINED"

    return {
        "classification": label,
        "all_9_targets_present": bool(all_present),
        "present_targets": list(present),
        "onset_vector_exact_vs_A": bool(onset_exact),
        "fingerprint_match_vs_A": bool(fingerprint_match),
        "fingerprint_comparison_vs_A": fingerprint,
        "causal_expression": causal,
    }


def classify_arm_d_family(classifications: list[str]) -> str:
    if len(classifications) != 11:
        raise ValueError(
            "Arm D family requires exactly 11 non-identity mappings"
        )

    preserved = sum(
        label == "RESPONSE PATTERN PRESERVED"
        for label in classifications
    )
    retained = sum(
        label in {
            "RESPONSE PATTERN PRESERVED",
            "RESPONSE RETAINED WITH ALTERED EXPRESSION",
        }
        for label in classifications
    )

    if preserved == 11:
        return "ASSET-TERRITORY ROBUST ACROSS TESTED REMAPS"

    if retained == 11:
        return (
            "ASSET-TERRITORY RETAINED BUT ALTERED "
            "ACROSS TESTED REMAPS"
        )

    if retained == 0:
        return "ASSET-TERRITORY ASSIGNMENT DEPENDENCE SUPPORTED"

    return "MIXED ASSET-TERRITORY DEPENDENCE"


def load_real_inputs():
    original = sparse.load_npz(
        CONNECTOME
    ).tocsr()

    retina_data = np.load(RETINA)
    retinal_indices = np.asarray(
        retina_data["neuron_index"],
        dtype=np.int32,
    )

    causal = load_frozen_causal_artifact()
    responders = frozen_responders(causal)
    edges = frozen_edges(causal)
    lesioned = lesion_frozen_edges(
        original,
        edges,
    )

    return (
        original,
        lesioned,
        retinal_indices,
        responders,
        edges,
    )


def evaluate_pair(
    original,
    lesioned,
    retinal_indices,
    responders,
    edges,
    stimuli,
):
    kwargs = {
        "retinal_indices": retinal_indices,
        "responder_indices": responders,
        "causal_edges": [
            (int(pre), int(post))
            for pre, post, _weight in edges
        ],
        "stimuli": stimuli,
    }

    baseline = evaluate_topology(
        original,
        **kwargs,
    )
    lesion = evaluate_topology(
        lesioned,
        **kwargs,
    )

    return baseline, lesion


def run_frozen_ensemble() -> dict:
    protocol = load_protocol()
    freeze_commit = execution_gate(protocol)

    classification_cfg = protocol["classification"]
    tolerance = float(
        classification_cfg[
            "fingerprint_normalized_l2_max"
        ]
    )
    targets = tuple(
        int(x)
        for x in classification_cfg["target_indices"]
    )

    expected_onsets = {
        int(target): int(onset)
        for target, onset in zip(
            classification_cfg["target_indices"],
            classification_cfg["arm_a_onsets"],
            strict=True,
        )
    }

    encoding_gate = json.loads(
        ENCODING_GATE.read_text(encoding="utf-8")
    )
    episode = build_normalized_episode()

    (
        original,
        lesioned,
        retinal_indices,
        responders,
        edges,
    ) = load_real_inputs()

    arm_a_stimuli = stimulus_list(
        episode,
        EncodingVariant(ARM_A),
    )
    verify_stimulus_hash(
        arm_a_stimuli,
        protocol["verification"]["arm_a_stimulus_sha256"],
        "Arm A",
    )

    print("running Arm A baseline duplicate 1/2...")
    arm_a_1 = evaluate_topology(
        original,
        retinal_indices=retinal_indices,
        responder_indices=responders,
        causal_edges=[
            (int(pre), int(post))
            for pre, post, _weight in edges
        ],
        stimuli=arm_a_stimuli,
    )

    print("running Arm A baseline duplicate 2/2...")
    arm_a_2 = evaluate_topology(
        original,
        retinal_indices=retinal_indices,
        responder_indices=responders,
        causal_edges=[
            (int(pre), int(post))
            for pre, post, _weight in edges
        ],
        stimuli=arm_a_stimuli,
    )

    if canonical_payload_bytes(arm_a_1) != canonical_payload_bytes(arm_a_2):
        raise RuntimeError(
            "Arm A duplicate replay is not exact"
        )

    if canonical_payload_sha256(arm_a_1) != EXPECTED_MQ5_TS_A_PAYLOAD_SHA256:
        raise RuntimeError(
            "Arm A no longer reproduces frozen MQ-5.TS accepted payload"
        )

    if arm_a_1.first_positive_onsets != expected_onsets:
        raise RuntimeError(
            "Arm A onset vector differs from frozen response contract"
        )

    print("running Arm A frozen 13-edge lesion...")
    arm_a_lesion = evaluate_topology(
        lesioned,
        retinal_indices=retinal_indices,
        responder_indices=responders,
        causal_edges=[
            (int(pre), int(post))
            for pre, post, _weight in edges
        ],
        stimuli=arm_a_stimuli,
    )

    if canonical_payload_sha256(
        arm_a_lesion
    ) != EXPECTED_MQ5_TS_D_PAYLOAD_SHA256:
        raise RuntimeError(
            "Arm A lesion no longer reproduces frozen MQ-5.TS D payload"
        )

    arm_a_class = classify_encoding(
        arm_a_1,
        arm_a_1,
        arm_a_lesion,
        targets=targets,
        fingerprint_tolerance=tolerance,
    )

    if arm_a_class["classification"] != "RESPONSE PATTERN PRESERVED":
        raise RuntimeError(
            "Arm A fails its own frozen classification contract"
        )

    results = {
        "A": {
            "stimulus_sha256":
                protocol["verification"]["arm_a_stimulus_sha256"],
            "baseline_payload_sha256":
                canonical_payload_sha256(arm_a_1),
            "lesion_payload_sha256":
                canonical_payload_sha256(arm_a_lesion),
            "classification":
                arm_a_class,
            "baseline":
                asdict(arm_a_1),
            "lesion":
                asdict(arm_a_lesion),
        }
    }

    primary_specs = (
        (
            "B",
            EncodingVariant(ARM_B),
            protocol["verification"]["arm_b_stimulus_sha256"],
        ),
        (
            "C",
            EncodingVariant(ARM_C),
            protocol["verification"]["arm_c_stimulus_sha256"],
        ),
        (
            "E",
            EncodingVariant(ARM_E),
            protocol["verification"]["arm_e_stimulus_sha256"],
        ),
    )

    for label, variant, expected_stimulus_sha in primary_specs:
        print(f"running Arm {label} baseline...")
        stimuli = stimulus_list(
            episode,
            variant,
        )
        verify_stimulus_hash(
            stimuli,
            expected_stimulus_sha,
            f"Arm {label}",
        )

        baseline, lesion = evaluate_pair(
            original,
            lesioned,
            retinal_indices,
            responders,
            edges,
            stimuli,
        )

        classification = classify_encoding(
            arm_a_1,
            baseline,
            lesion,
            targets=targets,
            fingerprint_tolerance=tolerance,
        )

        results[label] = {
            "stimulus_sha256": expected_stimulus_sha,
            "baseline_payload_sha256":
                canonical_payload_sha256(baseline),
            "lesion_payload_sha256":
                canonical_payload_sha256(lesion),
            "classification": classification,
            "baseline": asdict(baseline),
            "lesion": asdict(lesion),
        }

    d_results = []
    expected_d = {
        row["mapping_name"]: row["sha256"]
        for row in encoding_gate["arm_d_mappings"]
    }

    for mapping_name, mapping in balanced_asset_territory_mappings():
        if mapping == (0, 1, 2, 3, 4, 5):
            continue

        print(f"running Arm D {mapping_name} baseline...")
        stimuli = stimulus_list(
            episode,
            EncodingVariant(
                ARM_D,
                asset_mapping=mapping,
            ),
        )

        expected_sha = expected_d[mapping_name]
        verify_stimulus_hash(
            stimuli,
            expected_sha,
            f"Arm D {mapping_name}",
        )

        baseline, lesion = evaluate_pair(
            original,
            lesioned,
            retinal_indices,
            responders,
            edges,
            stimuli,
        )

        classification = classify_encoding(
            arm_a_1,
            baseline,
            lesion,
            targets=targets,
            fingerprint_tolerance=tolerance,
        )

        d_results.append(
            {
                "mapping_name": mapping_name,
                "mapping": list(mapping),
                "stimulus_sha256": expected_sha,
                "baseline_payload_sha256":
                    canonical_payload_sha256(baseline),
                "lesion_payload_sha256":
                    canonical_payload_sha256(lesion),
                "classification": classification,
                "baseline": asdict(baseline),
                "lesion": asdict(lesion),
            }
        )

    if len(d_results) != 11:
        raise RuntimeError(
            f"expected 11 non-identity Arm D runs, got {len(d_results)}"
        )

    d_family = classify_arm_d_family(
        [
            item["classification"]["classification"]
            for item in d_results
        ]
    )

    return {
        "experiment": "mq5-er-encoding-robustness-v1",
        "freeze_commit": freeze_commit,
        "encoding_verification_sha256":
            EXPECTED_ENCODING_GATE_SHA256,
        "mq5_ts_reference_payloads": {
            "A": EXPECTED_MQ5_TS_A_PAYLOAD_SHA256,
            "D_13_edge_lesion": EXPECTED_MQ5_TS_D_PAYLOAD_SHA256,
        },
        "financial_semantics": False,
        "result_execution_was_authorized": True,
        "classification_contract": {
            "target_indices": list(targets),
            "fingerprint_normalized_l2_max": tolerance,
            "strict_onset_match": "exact",
            "causal_expression":
                protocol["causal_expression"],
        },
        "arms": results,
        "arm_d_nonidentity": d_results,
        "arm_d_family_classification": d_family,
    }


def write_result(payload: dict) -> Path:
    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    if OUTPUT.exists():
        raise RuntimeError(
            f"refusing to overwrite existing result: {OUTPUT}"
        )

    OUTPUT.write_text(
        json.dumps(
            payload,
            indent=2,
            sort_keys=True,
            allow_nan=False,
        )
        + "\n",
        encoding="utf-8",
    )

    return OUTPUT


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--run-frozen-ensemble",
        action="store_true",
    )
    args = parser.parse_args()

    if not args.run_frozen_ensemble:
        parser.error(
            "only --run-frozen-ensemble is supported"
        )

    payload = run_frozen_ensemble()
    path = write_result(payload)

    print()
    print("=" * 88)
    print("MQ-5.ER FROZEN ENSEMBLE COMPLETE")
    print("=" * 88)
    print(
        "Arm B:",
        payload["arms"]["B"]["classification"]["classification"],
    )
    print(
        "Arm C:",
        payload["arms"]["C"]["classification"]["classification"],
    )
    print(
        "Arm E:",
        payload["arms"]["E"]["classification"]["classification"],
    )
    print(
        "Arm D family:",
        payload["arm_d_family_classification"],
    )
    print("artifact:", path)
    print("artifact sha256:", sha256_file(path))
    print("FINANCIAL SEMANTICS: NOT ASSIGNED")


if __name__ == "__main__":
    main()
