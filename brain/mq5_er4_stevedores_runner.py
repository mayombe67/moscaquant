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


CONFIG = Path("config/controls/mq5-er4-the-stevedores-v1.toml")
CONTROL_ARTIFACT = Path("artifacts/mq5-er4-stevedores-matched-controls-v1.json")
OUTPUT = data_path("experiments", "mq5-er4-the-stevedores-v1.json")
RETOUR_RESULT = data_path("experiments", "mq5-er3-retour-v1.json")

EXPERIMENT_ID = "mq5-er4-the-stevedores-v1"
CODENAME = "THE STEVEDORES"
FINANCIAL_SEMANTICS = "NOT ASSIGNED"

EXPECTED_C_STIMULUS_SHA256 = (
    "e8af8077d7d4c13431f7ad3fa05d81e2009263d9a5cb0e7dd800e889ea61ec8a"
)
EXPECTED_RETOUR_RESULT_SHA256 = (
    "90d8198a1c218ad24ef29c2c70b4b7a88fd8b24804516d2fd8f20903b847ff3e"
)
EXPECTED_CONTROL_ARTIFACT_SHA256 = (
    "7afd63ef205a21e19306b9145b1bbfdd09e8b254f413a59950f77b8c0a9ce20c"
)

C13_ONSETS = {
    51: 150, 55: 145, 92: 141, 129: 149, 317: 156,
    656: 141, 1273: 149, 126002: 151, 137122: 151,
}
AFFECTED_TARGETS = (55, 92, 656, 126002, 137122)
RETAINED_TARGETS = (51, 129, 317, 1273)
ALL_TARGETS = (51, 55, 92, 129, 317, 656, 1273, 126002, 137122)

EXPECTED_CANDIDATES = {
    "S1": {
        "edge": (11725, 29921),
        "weight": -0.23459716141223907,
        "associated_targets": (55, 126002, 137122),
    },
    "S2": {
        "edge": (11345, 47350),
        "weight": -0.3401360511779785,
        "associated_targets": (92, 656, 126002),
    },
    "S3": {
        "edge": (10647, 51642),
        "weight": 0.35854342579841614,
        "associated_targets": (55, 92, 656),
    },
}

EXPECTED_CONTROLS = {
    "S1": {
        "edge": (19300, 26090),
        "weight": -0.22811059653759003,
    },
    "S2": {
        "edge": (16922, 34070),
        "weight": -0.33714285492897034,
    },
    "S3": {
        "edge": (12775, 57635),
        "weight": 0.3538961112499237,
    },
}

REQUIRED_TRACKED_FILES = (
    "config/controls/mq5-er4-the-stevedores-v1.toml",
    "docs/experiments/mq5-er4-the-stevedores-protocol.md",
    "artifacts/mq5-er4-stevedores-matched-controls-v1.json",
    "brain/mq5_er4_stevedores_structural_audit.py",
    "brain/mq5_er4_stevedores_control_selector.py",
    "brain/mq5_er4_stevedores_runner.py",
    "tests/test_mq5_er4_stevedores_control_selector.py",
    "tests/test_mq5_er4_stevedores_runner_contract.py",
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


def edge_weight(matrix, pre: int, post: int) -> float:
    return float(matrix[int(post), int(pre)])


def lesion_exact_edge(matrix, pre: int, post: int, expected_weight: float):
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


def build_c_stimuli():
    episode = build_normalized_episode()
    stimuli = stimulus_list(episode, EncodingVariant(ARM_C))

    if len(stimuli) != EXPECTED_FRAMES:
        raise RuntimeError(
            f"expected {EXPECTED_FRAMES} Arm-C frames, got {len(stimuli)}"
        )

    actual = sha256_array(np.stack(stimuli, axis=0))
    if actual != EXPECTED_C_STIMULUS_SHA256:
        raise RuntimeError(f"Arm C stimulus hash mismatch: {actual}")

    return stimuli, actual


def normalized_fingerprint_l2(a: np.ndarray, b: np.ndarray) -> float:
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    an = float(np.linalg.norm(a))
    bn = float(np.linalg.norm(b))
    if an == 0.0 and bn == 0.0:
        return 0.0
    if an == 0.0 or bn == 0.0:
        return float("inf")
    return float(np.linalg.norm((a / an) - (b / bn)))


def normalized_fingerprint_cosine(a: np.ndarray, b: np.ndarray) -> float | None:
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    an = float(np.linalg.norm(a))
    bn = float(np.linalg.norm(b))
    if an == 0.0 or bn == 0.0:
        return None
    return float(np.dot(a, b) / (an * bn))


def run_condition(connectome, retinal_indices, responders, stimuli):
    runtime = PhysiologyConstrainedVisualTransductionRuntime(
        connectome=connectome,
        retinal_indices=retinal_indices,
        relay_artifact=RELAY,
        graded_artifact=GRADED,
        config=VisualTransductionConfig(release_gain=RELEASE_GAIN),
    )

    responder_indices = np.asarray(responders, dtype=np.int32)
    voltage = np.empty((len(stimuli), len(responders)), dtype=np.float64)

    for frame, stimulus in enumerate(stimuli):
        runtime.step(stimulus)
        voltage[frame] = np.asarray(
            runtime.voltage[responder_indices],
            dtype=np.float64,
        )

    onsets_raw = first_positive_onsets(voltage, responders)
    onsets = {
        int(k): None if v is None else int(v)
        for k, v in onsets_raw.items()
    }

    positive = np.clip(voltage, 0.0, None)
    fingerprint = np.asarray(
        positive_voltage_fingerprint(voltage),
        dtype=np.float64,
    )

    peak = {
        int(target): float(np.max(positive[:, i]))
        for i, target in enumerate(responders)
    }
    integrated = {
        int(target): float(np.sum(positive[:, i]))
        for i, target in enumerate(responders)
    }

    return {
        "onsets": onsets,
        "fingerprint": fingerprint,
        "peak_positive_voltage": peak,
        "integrated_positive_voltage": integrated,
    }


def dependency_rows(baseline_onsets: dict, intervention_onsets: dict) -> dict:
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


def specificity_label(rows: dict) -> str:
    affected_any = any(
        rows[str(target)]["dependency"]
        for target in AFFECTED_TARGETS
    )
    retained_any = any(
        rows[str(target)]["dependency"]
        for target in RETAINED_TARGETS
    )

    if affected_any and not retained_any:
        return "AFFECTED_SET_SPECIFIC_WITHIN_TESTED_TARGETS"
    if affected_any and retained_any:
        return "SHARED_WITH_RETAINED_DEPENDENCY_TARGETS"
    if (not affected_any) and retained_any:
        return "RETAINED_ONLY_OR_NONPRIMARY_PATTERN"
    return "SPECIFICITY_NOT_ESTABLISHED"


def classify_single(candidate_id: str, rows: dict) -> tuple[str, int]:
    targets = EXPECTED_CANDIDATES[candidate_id]["associated_targets"]
    count = sum(bool(rows[str(t)]["dependency"]) for t in targets)

    if count == len(targets):
        return "SINGLE_EDGE_CAUSAL_SUPPORT_COMPLETE", count
    if count > 0:
        return "SINGLE_EDGE_CAUSAL_SUPPORT_PARTIAL", count
    return "SINGLE_EDGE_CAUSAL_SUPPORT_NOT_OBSERVED", count


def classify_combined(rows: dict) -> tuple[str, int]:
    count = sum(bool(rows[str(t)]["dependency"]) for t in AFFECTED_TARGETS)
    if count == len(AFFECTED_TARGETS):
        return "COMBINED_SET_CAUSAL_SUPPORT_COMPLETE", count
    if count > 0:
        return "COMBINED_SET_CAUSAL_SUPPORT_PARTIAL", count
    return "COMBINED_SET_CAUSAL_SUPPORT_NOT_OBSERVED", count


def bubbles_report(reference: dict, intervention: dict, lesioned_edges: list) -> dict:
    target_rows = {}
    for target in ALL_TARGETS:
        b_on = reference["onsets"][int(target)]
        i_on = intervention["onsets"][int(target)]
        b_peak = reference["peak_positive_voltage"][int(target)]
        i_peak = intervention["peak_positive_voltage"][int(target)]
        b_int = reference["integrated_positive_voltage"][int(target)]
        i_int = intervention["integrated_positive_voltage"][int(target)]

        target_rows[str(target)] = {
            "baseline_onset": b_on,
            "intervention_onset": i_on,
            "onset_shift": (
                None if b_on is None or i_on is None else int(i_on) - int(b_on)
            ),
            "baseline_present": b_on is not None,
            "intervention_present": i_on is not None,
            "peak_positive_voltage_change": float(i_peak - b_peak),
            "integrated_positive_voltage_change": float(i_int - b_int),
        }

    unexpected = [
        int(t) for t in ALL_TARGETS
        if reference["onsets"][int(t)] is None
        and intervention["onsets"][int(t)] is not None
    ]

    return {
        "role": "DESCRIPTIVE ONLY",
        "lesioned_edges": [
            {"presynaptic": int(pre), "postsynaptic": int(post)}
            for pre, post in lesioned_edges
        ],
        "targets": target_rows,
        "normalized_fingerprint_l2": normalized_fingerprint_l2(
            reference["fingerprint"],
            intervention["fingerprint"],
        ),
        "normalized_fingerprint_cosine": normalized_fingerprint_cosine(
            reference["fingerprint"],
            intervention["fingerprint"],
        ),
        "unexpected_responder_appeared_within_frozen_nine_target_panel": bool(
            unexpected
        ),
        "unexpected_responders": unexpected,
        "causal_interpretation_authorized": False,
    }


def validate_protocol(protocol: dict) -> None:
    if protocol.get("experiment_id") != EXPERIMENT_ID:
        raise RuntimeError("experiment_id drift")
    if protocol.get("codename") != CODENAME:
        raise RuntimeError("codename drift")
    if protocol.get("financial_semantics") != FINANCIAL_SEMANTICS:
        raise RuntimeError("financial semantics drift")
    if int(protocol.get("frames")) != EXPECTED_FRAMES:
        raise RuntimeError("frame-count drift")
    if bool(protocol.get("result_execution_enabled")):
        # Validation does not authorize execution; this just permits the separate
        # execution gate to inspect a later one-line authorization commit.
        pass

    if tuple(protocol["affected_targets"]) != AFFECTED_TARGETS:
        raise RuntimeError("affected target drift")
    if tuple(protocol["retained_dependency_comparisons"]) != RETAINED_TARGETS:
        raise RuntimeError("retained target drift")
    if tuple(protocol["all_targets"]) != ALL_TARGETS:
        raise RuntimeError("all-target drift")

    configured_candidates = protocol.get("candidates", [])
    if len(configured_candidates) != 3:
        raise RuntimeError("candidate-count drift")

    for row in configured_candidates:
        cid = str(row["id"])
        expected = EXPECTED_CANDIDATES[cid]
        edge = (int(row["presynaptic"]), int(row["postsynaptic"]))
        if edge != expected["edge"]:
            raise RuntimeError(f"{cid} edge drift")
        if not np.isclose(
            float(row["weight"]),
            float(expected["weight"]),
            rtol=1e-6,
            atol=1e-12,
        ):
            raise RuntimeError(f"{cid} weight drift")
        if tuple(row["affected_targets"]) != expected["associated_targets"]:
            raise RuntimeError(f"{cid} associated-target drift")

    configured_controls = protocol.get("matched_control_edges", [])
    if len(configured_controls) != 3:
        raise RuntimeError("matched-control-count drift")

    for row in configured_controls:
        cid = str(row["candidate_id"])
        expected = EXPECTED_CONTROLS[cid]
        edge = (int(row["presynaptic"]), int(row["postsynaptic"]))
        if edge != expected["edge"]:
            raise RuntimeError(f"{cid} matched-control edge drift")
        if not np.isclose(
            float(row["weight"]),
            float(expected["weight"]),
            rtol=1e-6,
            atol=1e-12,
        ):
            raise RuntimeError(f"{cid} matched-control weight drift")


def verify_parent_artifacts() -> dict:
    if not RETOUR_RESULT.exists():
        raise RuntimeError(f"missing RETOUR parent result: {RETOUR_RESULT}")
    retour_sha = sha256_file(RETOUR_RESULT)
    if retour_sha != EXPECTED_RETOUR_RESULT_SHA256:
        raise RuntimeError(
            f"RETOUR parent result hash mismatch: {retour_sha}"
        )

    if not CONTROL_ARTIFACT.exists():
        raise RuntimeError(
            f"missing matched-control artifact: {CONTROL_ARTIFACT}"
        )
    control_sha = sha256_file(CONTROL_ARTIFACT)
    if control_sha != EXPECTED_CONTROL_ARTIFACT_SHA256:
        raise RuntimeError(
            f"matched-control artifact hash mismatch: {control_sha}"
        )

    return {
        "retour_parent_sha256": retour_sha,
        "matched_control_artifact_sha256": control_sha,
    }


def load_inputs(protocol: dict):
    payload = load_frozen_causal_artifact()
    original = sparse.load_npz(CONNECTOME).tocsr()
    original.sum_duplicates()
    original.sort_indices()

    retina_data = np.load(RETINA)
    retinal_indices = np.asarray(
        retina_data["neuron_index"],
        dtype=np.int32,
    )

    responders = tuple(int(x) for x in frozen_responders(payload))
    if tuple(responders) != ALL_TARGETS:
        raise RuntimeError(
            f"frozen responder order drift: {responders} != {ALL_TARGETS}"
        )

    c13 = original
    causal_edges = frozen_edges(payload)
    for pre, post, weight in causal_edges:
        c13 = lesion_exact_edge(
            c13,
            int(pre),
            int(post),
            float(weight),
        )

    candidates = {}
    for cid, expected in EXPECTED_CANDIDATES.items():
        pre, post = expected["edge"]
        actual_weight = edge_weight(original, pre, post)
        if not np.isclose(
            actual_weight,
            expected["weight"],
            rtol=1e-6,
            atol=1e-12,
        ):
            raise RuntimeError(f"{cid} connectome weight drift")
        candidates[cid] = {
            "edge": (pre, post),
            "weight": actual_weight,
        }

    controls = {}
    for cid, expected in EXPECTED_CONTROLS.items():
        pre, post = expected["edge"]
        actual_weight = edge_weight(original, pre, post)
        if not np.isclose(
            actual_weight,
            expected["weight"],
            rtol=1e-6,
            atol=1e-12,
        ):
            raise RuntimeError(f"{cid} matched-control connectome weight drift")
        controls[cid] = {
            "edge": (pre, post),
            "weight": actual_weight,
        }

    arms = {"C13": c13}

    for cid in ("S1", "S2", "S3"):
        pre, post = candidates[cid]["edge"]
        arms[f"C13-{cid}"] = lesion_exact_edge(
            c13, pre, post, candidates[cid]["weight"]
        )

    combined = c13
    for cid in ("S1", "S2", "S3"):
        pre, post = candidates[cid]["edge"]
        combined = lesion_exact_edge(
            combined, pre, post, candidates[cid]["weight"]
        )
    arms["C13-ALL"] = combined

    for cid in ("S1", "S2", "S3"):
        pre, post = controls[cid]["edge"]
        arms[f"C13-CTRL-{cid}"] = lesion_exact_edge(
            c13, pre, post, controls[cid]["weight"]
        )

    return {
        "retina": retinal_indices,
        "responders": responders,
        "arms": arms,
        "candidates": candidates,
        "controls": controls,
    }


def execution_gate(protocol: dict | None = None) -> str:
    protocol = load_protocol() if protocol is None else protocol
    validate_protocol(protocol)

    if not bool(protocol["result_execution_enabled"]):
        raise RuntimeError(
            "THE STEVEDORES RESULT EXECUTION REFUSED: "
            "result_execution_enabled is false"
        )

    if git_status_porcelain().strip():
        raise RuntimeError(
            "THE STEVEDORES RESULT EXECUTION REFUSED: working tree not clean"
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
            "THE STEVEDORES RESULT EXECUTION REFUSED: "
            "required frozen files are not all tracked"
        )

    if OUTPUT.exists():
        raise RuntimeError(
            f"THE STEVEDORES result artifact already exists: {OUTPUT}"
        )

    return git_head()


def run_stevedores(*, authorize_result: bool) -> dict:
    protocol = load_protocol()
    validate_protocol(protocol)
    parents = verify_parent_artifacts()

    head = execution_gate(protocol) if authorize_result else git_head()

    inputs = load_inputs(protocol)
    stimuli, stimulus_sha = build_c_stimuli()

    c13 = run_condition(
        inputs["arms"]["C13"],
        inputs["retina"],
        inputs["responders"],
        stimuli,
    )
    if c13["onsets"] != C13_ONSETS:
        raise RuntimeError(f"C13 replay onset mismatch: {c13['onsets']}")

    if not authorize_result:
        return {
            "experiment": EXPERIMENT_ID,
            "codename": CODENAME,
            "status": "KNOWN-REPLAY-VERIFIED",
            "git_head": head,
            **parents,
            "arm_c_stimulus_sha256": stimulus_sha,
            "c13_onsets": c13["onsets"],
            "candidates": {
                cid: {
                    "presynaptic": row["edge"][0],
                    "postsynaptic": row["edge"][1],
                    "weight": row["weight"],
                }
                for cid, row in inputs["candidates"].items()
            },
            "matched_controls": {
                cid: {
                    "presynaptic": row["edge"][0],
                    "postsynaptic": row["edge"][1],
                    "weight": row["weight"],
                }
                for cid, row in inputs["controls"].items()
            },
            "result_execution": False,
            "financial_semantics": FINANCIAL_SEMANTICS,
        }

    results = {"C13": c13}
    intervention_edges = {}

    for cid in ("S1", "S2", "S3"):
        arm = f"C13-{cid}"
        results[arm] = run_condition(
            inputs["arms"][arm],
            inputs["retina"],
            inputs["responders"],
            stimuli,
        )
        intervention_edges[arm] = [inputs["candidates"][cid]["edge"]]

    results["C13-ALL"] = run_condition(
        inputs["arms"]["C13-ALL"],
        inputs["retina"],
        inputs["responders"],
        stimuli,
    )
    intervention_edges["C13-ALL"] = [
        inputs["candidates"][cid]["edge"]
        for cid in ("S1", "S2", "S3")
    ]

    for cid in ("S1", "S2", "S3"):
        arm = f"C13-CTRL-{cid}"
        results[arm] = run_condition(
            inputs["arms"][arm],
            inputs["retina"],
            inputs["responders"],
            stimuli,
        )
        intervention_edges[arm] = [inputs["controls"][cid]["edge"]]

    single_tests = {}
    for cid in ("S1", "S2", "S3"):
        arm = f"C13-{cid}"
        rows = dependency_rows(c13["onsets"], results[arm]["onsets"])
        label, count = classify_single(cid, rows)
        single_tests[cid] = {
            "arm": arm,
            "comparison": f"{arm}_vs_C13",
            "classification": label,
            "associated_dependency_count": count,
            "associated_targets": list(
                EXPECTED_CANDIDATES[cid]["associated_targets"]
            ),
            "targets": rows,
            "specificity": specificity_label(rows),
        }

    combined_rows = dependency_rows(
        c13["onsets"],
        results["C13-ALL"]["onsets"],
    )
    combined_label, combined_count = classify_combined(combined_rows)

    controls = {}
    for cid in ("S1", "S2", "S3"):
        arm = f"C13-CTRL-{cid}"
        rows = dependency_rows(c13["onsets"], results[arm]["onsets"])
        controls[cid] = {
            "arm": arm,
            "comparison": f"{arm}_vs_C13",
            "targets": rows,
            "specificity": specificity_label(rows),
        }

    redundancy_compatible = {}
    for target in AFFECTED_TARGETS:
        singles_any = any(
            single_tests[cid]["targets"][str(target)]["dependency"]
            for cid in ("S1", "S2", "S3")
        )
        combined_dep = combined_rows[str(target)]["dependency"]
        redundancy_compatible[str(target)] = bool(
            (not singles_any) and combined_dep
        )

    bubbles = {
        arm: bubbles_report(
            c13,
            results[arm],
            intervention_edges[arm],
        )
        for arm in intervention_edges
    }

    payload = {
        "experiment": EXPERIMENT_ID,
        "codename": CODENAME,
        "kind": "confirmatory",
        "status": "RESULT",
        "git_head": head,
        **parents,
        "frames": EXPECTED_FRAMES,
        "arm_c_stimulus_sha256": stimulus_sha,
        "replay_gate": {"c13_onsets": c13["onsets"]},
        "single_edge_tests": single_tests,
        "combined_test": {
            "arm": "C13-ALL",
            "comparison": "C13-ALL_vs_C13",
            "classification": combined_label,
            "affected_dependency_count": combined_count,
            "targets": combined_rows,
            "specificity": specificity_label(combined_rows),
        },
        "matched_control_calibration": controls,
        "redundancy_compatible_pattern_by_target": redundancy_compatible,
        "bubbles_report": bubbles,
        "claim_limits": {
            "computational_necessity_only": True,
            "sufficiency_claimed": False,
            "uniqueness_claimed": False,
            "biological_causality_claimed": False,
            "cognition_claimed": False,
            "financial_semantics_assigned": False,
            "market_prediction_claimed": False,
            "trading_claimed": False,
        },
        "financial_semantics": FINANCIAL_SEMANTICS,
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(
            payload,
            indent=2,
            sort_keys=True,
            allow_nan=False,
        ) + "\n",
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

    payload = run_stevedores(
        authorize_result=bool(args.run_frozen)
    )
    print(
        json.dumps(
            payload,
            indent=2,
            sort_keys=True,
            allow_nan=False,
        )
    )


if __name__ == "__main__":
    main()
