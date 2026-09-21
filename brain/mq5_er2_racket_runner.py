from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tomllib
from pathlib import Path

import numpy as np
from scipy import sparse

from config.paths import data_path
from brain.mq5_er_encoder import ARM_C, EncodingVariant
from brain.mq5_er_neural_runner import stimulus_list
from brain.mq5_er_real_artifact_verify import build_normalized_episode, sha256_array
from brain.mq5_ts_metrics import first_positive_onsets, positive_voltage_fingerprint
from brain.mq5_ts_runtime import (
    CONNECTOME,
    RETINA,
    RELAY,
    GRADED,
    RELEASE_GAIN,
    EXPECTED_FRAMES,
    frozen_edges,
    frozen_responders,
    load_frozen_causal_artifact,
)
from brain.physiology_constrained_visual_transduction import (
    PhysiologyConstrainedVisualTransductionRuntime,
)
from brain.visual_transduction import VisualTransductionConfig


CONFIG = Path("config/controls/mq5-er2-the-racket-v1.toml")
OUTPUT = data_path("experiments", "mq5-er2-the-racket-v1.json")

EXPERIMENT_ID = "mq5-er2-the-racket-v1"
CODENAME = "THE RACKET"
FINANCIAL_SEMANTICS = "NOT ASSIGNED"

EXPECTED_C_STIMULUS_SHA256 = (
    "e8af8077d7d4c13431f7ad3fa05d81e2009263d9a5cb0e7dd800e889ea61ec8a"
)

FOCUSED_EDGE = (116680, 12024)
MATCHED_CONTROL_EDGE = (78481, 16087)

C_BASELINE_ONSETS = {
    51: 148, 55: 145, 92: 141, 129: 148, 317: 153,
    656: 141, 1273: 144, 126002: 151, 137122: 151,
}

C_LESION13_ONSETS = {
    51: 150, 55: 145, 92: 141, 129: 149, 317: 156,
    656: 141, 1273: 149, 126002: 151, 137122: 151,
}

PRIMARY_TARGETS = (92, 656, 137122)
AFFECTED_NEGATIVE_COMPARISONS = (55, 126002)
RETAINED_DEPENDENCY_COMPARISONS = (51, 129, 317, 1273)
ALL_TARGETS = (51, 55, 92, 129, 317, 656, 1273, 126002, 137122)

REQUIRED_TRACKED_FILES = (
    "config/controls/mq5-er2-the-racket-v1.toml",
    "docs/experiments/mq5-er2-the-racket-protocol.md",
    "docs/experiments/mq5-er2-the-racket-control-rule.md",
    "brain/mq5_er2_racket_control.py",
    "brain/mq5_er2_racket_runner.py",
    "tests/test_mq5_er2_racket_control.py",
    "tests/test_mq5_er2_racket_runner_contract.py",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git_status_porcelain() -> str:
    completed = subprocess.run(
        ["git", "status", "--porcelain"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError("unable to inspect git status: " + completed.stdout)
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
        raise RuntimeError("unable to determine git HEAD: " + completed.stdout)
    return completed.stdout.strip()


def load_protocol() -> dict:
    with CONFIG.open("rb") as handle:
        return tomllib.load(handle)


def _edge_weight(matrix, pre: int, post: int) -> float:
    return float(matrix[int(post), int(pre)])


def _lesion_exact_edge(matrix, pre: int, post: int, expected_weight: float):
    modified = matrix.tolil(copy=True)
    current = float(modified[int(post), int(pre)])

    if current == 0.0:
        raise RuntimeError(f"required intervention edge absent: {pre}->{post}")

    if not np.isclose(current, float(expected_weight), rtol=1e-6, atol=1e-12):
        raise RuntimeError(
            f"intervention edge weight mismatch {pre}->{post}: "
            f"{current} != {expected_weight}"
        )

    modified[int(post), int(pre)] = 0.0
    result = modified.tocsr()
    result.eliminate_zeros()
    result.sort_indices()
    return result


def _load_inputs(protocol: dict):
    payload = load_frozen_causal_artifact()
    original = sparse.load_npz(CONNECTOME).tocsr()
    original.sum_duplicates()
    original.sort_indices()

    retina_data = np.load(RETINA)
    retinal_indices = np.asarray(retina_data["neuron_index"], dtype=np.int32)

    responders = frozen_responders(payload)
    causal_edges = frozen_edges(payload)

    focused = (int(protocol["focused_edge_pre"]), int(protocol["focused_edge_post"]))
    if focused != FOCUSED_EDGE:
        raise RuntimeError(f"focused edge config drift: {focused} != {FOCUSED_EDGE}")

    control = protocol["matched_control"]
    control_edge = (int(control["presynaptic"]), int(control["postsynaptic"]))
    if control_edge != MATCHED_CONTROL_EDGE:
        raise RuntimeError(
            f"matched-control edge config drift: {control_edge} != {MATCHED_CONTROL_EDGE}"
        )

    focused_weight = _edge_weight(original, *FOCUSED_EDGE)
    control_weight = _edge_weight(original, *MATCHED_CONTROL_EDGE)

    expected_control_weight = float(control["weight"])
    if not np.isclose(control_weight, expected_control_weight, rtol=1e-6, atol=1e-12):
        raise RuntimeError(
            "matched-control connectome weight drift: "
            f"{control_weight} != {expected_control_weight}"
        )

    c0 = original
    c13 = c0
    for edge in causal_edges:
        c13 = _lesion_exact_edge(c13, *edge)

    cr = _lesion_exact_edge(c0, FOCUSED_EDGE[0], FOCUSED_EDGE[1], focused_weight)
    c13r = _lesion_exact_edge(c13, FOCUSED_EDGE[0], FOCUSED_EDGE[1], focused_weight)
    cc = _lesion_exact_edge(
        c0, MATCHED_CONTROL_EDGE[0], MATCHED_CONTROL_EDGE[1], control_weight
    )
    c13c = _lesion_exact_edge(
        c13, MATCHED_CONTROL_EDGE[0], MATCHED_CONTROL_EDGE[1], control_weight
    )

    return {
        "retina": retinal_indices,
        "responders": responders,
        "causal_edges": causal_edges,
        "focused_weight": focused_weight,
        "control_weight": control_weight,
        "arms": {
            "C0": c0,
            "C13": c13,
            "CR": cr,
            "C13R": c13r,
            "CC": cc,
            "C13C": c13c,
        },
    }


def _build_c_stimuli():
    episode = build_normalized_episode()
    stimuli = stimulus_list(episode, EncodingVariant(ARM_C))

    if len(stimuli) != EXPECTED_FRAMES:
        raise RuntimeError(f"expected {EXPECTED_FRAMES} Arm-C frames, got {len(stimuli)}")

    actual = sha256_array(np.stack(stimuli, axis=0))
    if actual != EXPECTED_C_STIMULUS_SHA256:
        raise RuntimeError(f"Arm C stimulus hash mismatch: {actual}")

    return stimuli, actual


def _run_condition(connectome, retinal_indices, responders, stimuli):
    runtime = PhysiologyConstrainedVisualTransductionRuntime(
        connectome=connectome,
        retinal_indices=retinal_indices,
        relay_artifact=RELAY,
        graded_artifact=GRADED,
        config=VisualTransductionConfig(release_gain=RELEASE_GAIN),
    )

    voltage = np.empty((len(stimuli), len(responders)), dtype=np.float64)

    for frame, stimulus in enumerate(stimuli):
        runtime.step(stimulus)
        voltage[frame] = np.asarray(runtime.voltage[responders], dtype=np.float64)

    onsets_raw = first_positive_onsets(voltage, responders)
    onsets = {
        int(k): None if v is None else int(v)
        for k, v in onsets_raw.items()
    }

    fingerprint = np.asarray(positive_voltage_fingerprint(voltage), dtype=np.float64)

    return {"onsets": onsets, "fingerprint": fingerprint}


def _normalized_fingerprint_l2(a: np.ndarray, b: np.ndarray) -> float:
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    a_norm = float(np.linalg.norm(a))
    b_norm = float(np.linalg.norm(b))
    if a_norm == 0.0 and b_norm == 0.0:
        return 0.0
    if a_norm == 0.0 or b_norm == 0.0:
        return float("inf")
    return float(np.linalg.norm((a / a_norm) - (b / b_norm)))


def _dependency_rows(baseline_onsets: dict, intervention_onsets: dict):
    rows = {}
    for target in ALL_TARGETS:
        baseline = baseline_onsets[int(target)]
        intervention = intervention_onsets[int(target)]
        dependency = (
            baseline is not None
            and (intervention is None or int(intervention) > int(baseline))
        )
        rows[str(target)] = {
            "baseline_onset": baseline,
            "intervention_onset": intervention,
            "dependency": bool(dependency),
            "onset_shift": (
                None
                if baseline is None or intervention is None
                else int(intervention) - int(baseline)
            ),
        }
    return rows


def _primary_classification(rows: dict) -> tuple[str, int]:
    count = sum(bool(rows[str(target)]["dependency"]) for target in PRIMARY_TARGETS)
    if count == 3:
        return "RACKET_CAUSAL_SUPPORT_COMPLETE", count
    if count in (1, 2):
        return "RACKET_CAUSAL_SUPPORT_PARTIAL", count
    if count == 0:
        return "RACKET_CAUSAL_SUPPORT_NOT_OBSERVED", count
    raise RuntimeError(f"unexpected primary dependency count: {count}")


def _target_specificity(rows: dict) -> str:
    primary_any = any(rows[str(target)]["dependency"] for target in PRIMARY_TARGETS)
    retained_any = any(
        rows[str(target)]["dependency"]
        for target in RETAINED_DEPENDENCY_COMPARISONS
    )
    if primary_any and not retained_any:
        return "AFFECTED_SET_SPECIFIC_WITHIN_TESTED_TARGETS"
    if primary_any and retained_any:
        return "SHARED_WITH_RETAINED_DEPENDENCY_TARGETS"
    if (not primary_any) and retained_any:
        return "RETAINED_ONLY_OR_NONPRIMARY_PATTERN"
    return "SPECIFICITY_NOT_ESTABLISHED"


def _matched_control_calibration(focused_rows: dict, control_rows: dict) -> dict:
    focused_primary = [
        int(t) for t in PRIMARY_TARGETS if focused_rows[str(t)]["dependency"]
    ]
    control_primary = [
        int(t) for t in PRIMARY_TARGETS if control_rows[str(t)]["dependency"]
    ]

    if focused_primary and not control_primary:
        interpretation = "FOCUSED_WITHOUT_MATCHED_CONTROL_PRIMARY_DEPENDENCY"
    elif focused_primary and control_primary:
        interpretation = "FOCUSED_AND_MATCHED_CONTROL_PRIMARY_DEPENDENCY"
    elif (not focused_primary) and control_primary:
        interpretation = "MATCHED_CONTROL_ONLY_PRIMARY_DEPENDENCY"
    else:
        interpretation = "NO_PRIMARY_DEPENDENCY_IN_EITHER_INTERVENTION"

    return {
        "focused_primary_dependency_targets": focused_primary,
        "matched_control_primary_dependency_targets": control_primary,
        "interpretation": interpretation,
    }


def _validate_protocol(protocol: dict) -> None:
    if protocol.get("experiment_id") != EXPERIMENT_ID:
        raise RuntimeError("experiment_id drift")
    if protocol.get("codename") != CODENAME:
        raise RuntimeError("codename drift")
    if protocol.get("financial_semantics") != FINANCIAL_SEMANTICS:
        raise RuntimeError("financial semantics drift")
    if int(protocol.get("frames")) != EXPECTED_FRAMES:
        raise RuntimeError("frame-count drift")

    if tuple(protocol["primary_targets"]) != PRIMARY_TARGETS:
        raise RuntimeError("primary target drift")
    if tuple(protocol["affected_negative_comparisons"]) != AFFECTED_NEGATIVE_COMPARISONS:
        raise RuntimeError("affected-negative comparison drift")
    if tuple(protocol["retained_dependency_comparisons"]) != RETAINED_DEPENDENCY_COMPARISONS:
        raise RuntimeError("retained-dependency comparison drift")
    if tuple(protocol["all_targets"]) != ALL_TARGETS:
        raise RuntimeError("all-target set drift")

    mci = protocol["matched_control_intervention"]
    if not bool(mci["enabled"]):
        raise RuntimeError("matched-control intervention is not enabled")
    if mci["control_only_arm"] != "CC":
        raise RuntimeError("CC arm contract drift")
    if mci["control_plus_13_arm"] != "C13C":
        raise RuntimeError("C13C arm contract drift")
    if mci["primary_control_comparison"] != "C13C_vs_C13":
        raise RuntimeError("matched-control comparison drift")


def execution_gate(protocol: dict | None = None) -> str:
    protocol = load_protocol() if protocol is None else protocol
    _validate_protocol(protocol)

    if not bool(protocol["result_execution_enabled"]):
        raise RuntimeError(
            "THE RACKET RESULT EXECUTION REFUSED: result_execution_enabled is false"
        )

    if git_status_porcelain().strip():
        raise RuntimeError(
            "THE RACKET RESULT EXECUTION REFUSED: working tree not clean"
        )

    completed = subprocess.run(
        ["git", "ls-files", "--error-unmatch", *REQUIRED_TRACKED_FILES],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            "THE RACKET RESULT EXECUTION REFUSED: required frozen files are not all tracked"
        )

    if OUTPUT.exists():
        raise RuntimeError(f"THE RACKET result artifact already exists: {OUTPUT}")

    return git_head()


def run_racket(*, authorize_result: bool) -> dict:
    protocol = load_protocol()
    _validate_protocol(protocol)

    head = execution_gate(protocol) if authorize_result else git_head()

    inputs = _load_inputs(protocol)
    stimuli, stimulus_sha = _build_c_stimuli()

    c0 = _run_condition(
        inputs["arms"]["C0"], inputs["retina"], inputs["responders"], stimuli
    )
    if c0["onsets"] != C_BASELINE_ONSETS:
        raise RuntimeError(f"Arm C0 replay onset mismatch: {c0['onsets']}")

    c13 = _run_condition(
        inputs["arms"]["C13"], inputs["retina"], inputs["responders"], stimuli
    )
    if c13["onsets"] != C_LESION13_ONSETS:
        raise RuntimeError(f"Arm C13 replay onset mismatch: {c13['onsets']}")

    if not authorize_result:
        return {
            "experiment": EXPERIMENT_ID,
            "codename": CODENAME,
            "status": "KNOWN-REPLAY-VERIFIED",
            "git_head": head,
            "arm_c_stimulus_sha256": stimulus_sha,
            "c0_onsets": c0["onsets"],
            "c13_onsets": c13["onsets"],
            "focused_edge": {
                "presynaptic": FOCUSED_EDGE[0],
                "postsynaptic": FOCUSED_EDGE[1],
                "weight": float(inputs["focused_weight"]),
            },
            "matched_control_edge": {
                "presynaptic": MATCHED_CONTROL_EDGE[0],
                "postsynaptic": MATCHED_CONTROL_EDGE[1],
                "weight": float(inputs["control_weight"]),
            },
            "result_execution": False,
            "financial_semantics": FINANCIAL_SEMANTICS,
        }

    results = {"C0": c0, "C13": c13}

    for arm in ("CR", "C13R", "CC", "C13C"):
        results[arm] = _run_condition(
            inputs["arms"][arm], inputs["retina"], inputs["responders"], stimuli
        )

    focused_rows = _dependency_rows(
        results["C13"]["onsets"], results["C13R"]["onsets"]
    )
    control_rows = _dependency_rows(
        results["C13"]["onsets"], results["C13C"]["onsets"]
    )

    primary_classification, primary_count = _primary_classification(focused_rows)
    target_specificity = _target_specificity(focused_rows)
    control_calibration = _matched_control_calibration(focused_rows, control_rows)

    descriptive = {}
    for arm in ("CR", "C13R", "CC", "C13C"):
        reference = "C0" if arm in ("CR", "CC") else "C13"
        descriptive[arm] = {
            "onsets": results[arm]["onsets"],
            "normalized_fingerprint_l2_vs_reference": _normalized_fingerprint_l2(
                results[reference]["fingerprint"], results[arm]["fingerprint"]
            ),
        }

    payload = {
        "experiment": EXPERIMENT_ID,
        "codename": CODENAME,
        "kind": "confirmatory",
        "status": "RESULT",
        "git_head": head,
        "frames": EXPECTED_FRAMES,
        "arm_c_stimulus_sha256": stimulus_sha,
        "focused_edge": {
            "presynaptic": FOCUSED_EDGE[0],
            "postsynaptic": FOCUSED_EDGE[1],
            "weight": float(inputs["focused_weight"]),
        },
        "matched_control_edge": {
            "presynaptic": MATCHED_CONTROL_EDGE[0],
            "postsynaptic": MATCHED_CONTROL_EDGE[1],
            "weight": float(inputs["control_weight"]),
            "selector": protocol["matched_control"]["selector"],
        },
        "replay_gates": {
            "c0_onsets": results["C0"]["onsets"],
            "c13_onsets": results["C13"]["onsets"],
        },
        "primary_test": {
            "comparison": "C13R_vs_C13",
            "classification": primary_classification,
            "primary_dependency_count": primary_count,
            "targets": focused_rows,
        },
        "target_set_specificity": target_specificity,
        "matched_control_calibration": {
            "comparison": "C13C_vs_C13",
            "targets": control_rows,
            **control_calibration,
        },
        "affected_negative_comparisons": list(AFFECTED_NEGATIVE_COMPARISONS),
        "retained_dependency_comparisons": list(RETAINED_DEPENDENCY_COMPARISONS),
        "secondary_descriptive": descriptive,
        "claim_limits": {
            "necessity_only_in_tested_computational_condition": True,
            "sufficiency_claimed": False,
            "uniqueness_claimed": False,
            "biological_causality_claimed": False,
            "cognition_claimed": False,
            "market_prediction_claimed": False,
            "trading_claimed": False,
        },
        "financial_semantics": FINANCIAL_SEMANTICS,
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )

    payload["result_artifact"] = str(OUTPUT)
    payload["result_sha256"] = sha256_file(OUTPUT)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--verify-known-replay", action="store_true")
    group.add_argument("--run-frozen", action="store_true")
    args = parser.parse_args()

    payload = run_racket(authorize_result=bool(args.run_frozen))
    print(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
