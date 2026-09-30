"""THE CORNER three-arm runner. Execution fails closed without later authority."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import tempfile
import tomllib
from pathlib import Path

import numpy as np

from brain import mq5_er6r_the_corner as corner
from brain.mq5_er5r_way_down_in_the_hole_runner import load_c13
from brain.mq5_er_encoder import ARM_C, EncodingVariant
from brain.mq5_er_neural_runner import stimulus_list
from brain.mq5_er_real_artifact_verify import TERRITORIES, build_normalized_episode, sha256_array
from brain.mq5_ts_metrics import first_positive_onsets, positive_voltage_fingerprint
from brain.mq5_ts_runtime import CONNECTOME, RETINA, RELAY, GRADED, CAUSAL, RELEASE_GAIN
from brain.physiology_constrained_visual_transduction import (
    PhysiologyConstrainedVisualTransductionRuntime,
)
from brain.visual_transduction import VisualTransductionConfig
from config.paths import data_path


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "docs/experiments/mq5-er6r-the-corner-execution-protocol.md"
QUALIFICATION = ROOT / "artifacts/qualification/mq5-er6r-the-corner-runner-qualification-v1.json"
AUTHORIZATION = ROOT / "config/controls/mq5-er6r-the-corner-neural-execution-authorization-v1.json"
OUTPUT = data_path("experiments", "mq5-er6r-the-corner-v1.json")
INPUTS = {
    "connectome": CONNECTOME, "retina": RETINA, "relay": RELAY,
    "graded": GRADED, "territories": TERRITORIES, "causal": CAUSAL,
}
SOURCE_FILES = {
    "operator": Path(corner.__file__),
    "runner": Path(__file__),
    "runtime": ROOT / "brain/physiology_constrained_visual_transduction.py",
    "visual_runtime": ROOT / "brain/visual_transduction.py",
    "base_runtime": ROOT / "brain/runtime.py",
    "encoder": ROOT / "brain/mq5_er_encoder.py",
    "neural_stimuli": ROOT / "brain/mq5_er_neural_runner.py",
    "real_artifact": ROOT / "brain/mq5_er_real_artifact_verify.py",
    "ts_runtime": ROOT / "brain/mq5_ts_runtime.py",
    "metrics": ROOT / "brain/mq5_ts_metrics.py",
    "c13_loader": ROOT / "brain/mq5_er5r_way_down_in_the_hole_runner.py",
    "market_replay": ROOT / "brain/market_replay.py",
    "market_temporal": ROOT / "brain/market_temporal.py",
    "market_features": ROOT / "market/features.py",
    "market_normalization": ROOT / "market/normalization.py",
    "data_paths": ROOT / "config/paths.py",
}
REQUIRED_TRACKED = (
    "config/controls/mq5-er6r-the-corner-v1.toml",
    "docs/experiments/mq5-er6r-the-corner-execution-protocol.md",
    "brain/mq5_er6r_the_corner.py",
    "brain/mq5_er6r_the_corner_runner.py",
    "tests/test_mq5_er6r_the_corner_prereg.py",
    "tests/test_mq5_er6r_the_corner_contract.py",
    "tests/test_mq5_er6r_the_corner_runner.py",
    "artifacts/qualification/mq5-er6r-the-corner-runner-qualification-v1.json",
    "config/controls/mq5-er6r-the-corner-neural-execution-authorization-v1.json",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git(*args: str) -> str:
    completed = subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, text=True, check=False
    )
    if completed.returncode:
        raise corner.CornerRefusal("git provenance check failed")
    return completed.stdout.strip()


def execution_gate() -> dict:
    """Only a later sealed qualification and authorization can permit a run."""
    stage = corner.load_frozen_stage()
    if not QUALIFICATION.is_file() or not AUTHORIZATION.is_file():
        raise corner.CornerRefusal("neural qualification or authorization missing")
    qualification = json.loads(QUALIFICATION.read_text(encoding="utf-8"))
    authority = json.loads(AUTHORIZATION.read_text(encoding="utf-8"))
    expected = {
        "schema_version": "moscaquant.mq5-er6r-the-corner-neural-execution-authorization/v1",
        "stage_id": stage["stage_id"],
        "candidate_node": 1952,
        "matched_control_node": 3056,
        "neural_execution_authorized": True,
        "result_execution_authorized": True,
        "control_reselection_authorized": False,
        "candidate_replacement_authorized": False,
        "stage_config_sha256": _sha256(corner.CONFIG),
        "stage_protocol_sha256": _sha256(PROTOCOL),
        "control_artifact_sha256": _sha256(corner.CONTROL),
        "operator_sha256": _sha256(Path(corner.__file__)),
        "runner_sha256": _sha256(Path(__file__)),
        "qualification_sha256": _sha256(QUALIFICATION),
    }
    if any(type(authority.get(k)) is not type(v) or authority.get(k) != v
           for k, v in expected.items()):
        raise corner.CornerRefusal("neural authorization binding drift")
    if (qualification.get("status") != "CORNER_RUNNER_QUALIFIED_NO_NEURAL_EXECUTION"
            or qualification.get("runner_sha256") != expected["runner_sha256"]
            or qualification.get("operator_sha256") != expected["operator_sha256"]
            or qualification.get("neural_execution") is not False):
        raise corner.CornerRefusal("runner qualification drift")
    source_hashes = authority.get("source_sha256")
    if not isinstance(source_hashes, dict) or set(source_hashes) != set(SOURCE_FILES):
        raise corner.CornerRefusal("source hash manifest missing")
    if any(source_hashes[key] != _sha256(path) for key, path in SOURCE_FILES.items()):
        raise corner.CornerRefusal("runtime source hash drift")
    if _git("status", "--porcelain"):
        raise corner.CornerRefusal("working tree must be clean")
    _git("ls-files", "--error-unmatch", *REQUIRED_TRACKED)
    frozen_commit = authority.get("implementation_git_sha")
    if not isinstance(frozen_commit, str) or not re.fullmatch(r"[0-9a-f]{40}", frozen_commit):
        raise corner.CornerRefusal("implementation commit missing")
    if _git("merge-base", frozen_commit, "HEAD") != frozen_commit:
        raise corner.CornerRefusal("implementation commit not ancestral")
    input_hashes = authority.get("input_sha256")
    if not isinstance(input_hashes, dict) or set(input_hashes) != set(INPUTS):
        raise corner.CornerRefusal("input hash manifest missing")
    for key, path in INPUTS.items():
        if not path.is_file() or _sha256(path) != input_hashes[key]:
            raise corner.CornerRefusal(f"{key} input missing or hash drift")
    if OUTPUT.exists():
        raise corner.CornerRefusal("authoritative result already exists")
    if not OUTPUT.parent.is_dir():
        raise corner.CornerRefusal("durable result directory missing")
    try:
        with tempfile.NamedTemporaryFile(dir=OUTPUT.parent, prefix=".corner-write-check-", delete=True) as handle:
            handle.write(b"write-path-check")
            handle.flush()
            os.fsync(handle.fileno())
    except OSError as exc:
        raise corner.CornerRefusal("durable output write path unavailable") from exc
    return authority


def build_stimuli(stage: dict) -> list[np.ndarray]:
    stimuli = stimulus_list(build_normalized_episode(), EncodingVariant(ARM_C))
    if len(stimuli) != 192:
        raise corner.CornerRefusal("C13 frame count drift")
    digest = sha256_array(np.stack(stimuli, axis=0))
    if digest != stage["arm_c_stimulus_sha256"]:
        raise corner.CornerRefusal("C13 stimulus hash drift")
    return stimuli


def run_arm(arm: str, connectome, retina: np.ndarray, responders: tuple[int, ...],
            stimuli: list[np.ndarray]) -> dict:
    native_trace = []
    modifier = corner.arm_modifier(arm, population_size=connectome.shape[0])
    target = {"P1952": 1952, "PCONTROL": 3056}.get(arm)

    def observed_modifier(activity: np.ndarray, frame: int) -> np.ndarray:
        native_trace.append(float(activity[target]))
        return modifier(activity, frame)

    runtime = PhysiologyConstrainedVisualTransductionRuntime(
        connectome=connectome, retinal_indices=retina,
        relay_artifact=RELAY, graded_artifact=GRADED,
        config=VisualTransductionConfig(release_gain=RELEASE_GAIN),
        activity_modifier=None if modifier is None else observed_modifier,
    )
    indices = np.asarray(responders, dtype=np.int32)
    voltage = np.empty((len(stimuli), len(indices)), dtype=np.float64)
    spikes = np.empty_like(voltage)
    for frame, stimulus in enumerate(stimuli):
        runtime.step(stimulus, generation=frame)
        voltage[frame] = runtime.voltage[indices]
        spikes[frame] = runtime.spikes[indices]
    onsets = first_positive_onsets(voltage, indices)
    positive = np.maximum(voltage, 0.0)
    return {
        "onsets": onsets,
        "responder_voltage": voltage.tolist(),
        "responder_spikes": spikes.tolist(),
        "positive_fingerprint": positive_voltage_fingerprint(voltage).tolist(),
        "peak_positive_voltage": {int(t): float(positive[:, i].max()) for i, t in enumerate(indices)},
        "integrated_positive_voltage": {int(t): float(positive[:, i].sum()) for i, t in enumerate(indices)},
        "native_target_activity_before_silencing": native_trace,
    }


def _fingerprint_metrics(a: list[float], b: list[float]) -> dict:
    left, right = np.asarray(a, dtype=np.float64), np.asarray(b, dtype=np.float64)
    left_norm, right_norm = float(np.linalg.norm(left)), float(np.linalg.norm(right))
    if left_norm == 0 or right_norm == 0:
        return {"normalized_l2": None, "cosine": None}
    return {
        "normalized_l2": float(np.linalg.norm(left / left_norm - right / right_norm)),
        "cosine": float(np.dot(left, right) / (left_norm * right_norm)),
    }


def analyze(arms: dict[str, dict]) -> dict:
    p0 = arms["P0"]
    comparisons = {}
    for arm in ("P1952", "PCONTROL"):
        current = arms[arm]
        dependencies = corner.dependency_by_onset(p0["onsets"], current["onsets"])
        label, k = corner.classify_affected(dependencies)
        comparisons[arm] = {
            "classification": label,
            "affected_dependency_count": k,
            "dependency": {str(t): dependencies[t] for t in dependencies},
            "retained_dependency_count": sum(dependencies[t] for t in (51, 129, 317, 1273)),
            "secondary_fingerprint": _fingerprint_metrics(
                p0["positive_fingerprint"], current["positive_fingerprint"]
            ),
        }
    return comparisons


def execute() -> Path:
    authority = execution_gate()  # Refuse before reading or simulating neural inputs.
    stage = corner.load_frozen_stage()
    stimuli = build_stimuli(stage)
    _original, connectome, retina, responders = load_c13()
    if responders != tuple(stage["all_targets"]):
        raise corner.CornerRefusal("responder order drift")
    baseline = run_arm("P0", connectome, retina, responders, stimuli)
    frozen_onsets = {
        int(k): v for k, v in tomllib.loads(
            corner.WARRANT_CONFIG.read_text(encoding="utf-8")
        )["c13_onsets"].items()
    }
    if baseline["onsets"] != frozen_onsets:
        raise corner.CornerRefusal("P0 C13 onset vector drift")
    arms = {"P0": baseline}
    for arm in ("P1952", "PCONTROL"):
        arms[arm] = run_arm(arm, connectome, retina, responders, stimuli)
    payload = {
        "schema_version": "moscaquant.mq5-er6r-the-corner-result/v1",
        "experiment": stage["parent_experiment"], "stage": stage["stage_id"],
        "financial_semantics": "NOT ASSIGNED",
        "authorization_sha256": _sha256(AUTHORIZATION),
        "qualification_sha256": _sha256(QUALIFICATION),
        "implementation_git_sha": authority["implementation_git_sha"],
        "input_sha256": authority["input_sha256"],
        "arms": arms, "comparisons": analyze(arms),
        "claim_boundary": "COMPUTATIONAL NECESSITY IN FROZEN MODEL ONLY",
    }
    encoded = (json.dumps(payload, sort_keys=True, indent=2, allow_nan=False) + "\n").encode()
    if OUTPUT.exists():
        raise corner.CornerRefusal("authoritative result appeared during execution")
    fd, temp_name = tempfile.mkstemp(dir=OUTPUT.parent, prefix=".corner-result-")
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        if OUTPUT.exists():
            raise corner.CornerRefusal("authoritative result appeared during write")
        os.link(temp_name, OUTPUT)  # Atomic no-overwrite publication.
        directory_fd = os.open(OUTPUT.parent, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        Path(temp_name).unlink(missing_ok=True)
    return OUTPUT


def main() -> None:
    parser = argparse.ArgumentParser(description="THE CORNER gated neural execution")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if not args.execute:
        raise corner.CornerRefusal("explicit --execute required")
    print(execute())


if __name__ == "__main__":
    main()
