"""Frozen THE CORNER operators and onset classification; no neural runner."""

from __future__ import annotations

import hashlib
import json
import tomllib
from pathlib import Path
from typing import Callable, Mapping

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config/controls/mq5-er6r-the-corner-v1.toml"
CONTROL = ROOT / "artifacts/mq5-er6r-the-warrant-matched-control-v1.json"
WARRANT_PROTOCOL = ROOT / "docs/experiments/mq5-er6r-the-warrant-protocol.md"
WARRANT_CONFIG = ROOT / "config/controls/mq5-er6r-the-warrant-v1.toml"


class CornerRefusal(RuntimeError):
    pass


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_frozen_stage() -> dict:
    """Read semantic bindings and refuse drift without authorizing execution."""
    stage = tomllib.loads(CONFIG.read_text(encoding="utf-8"))
    control = json.loads(CONTROL.read_text(encoding="utf-8"))
    expected = {
        "warrant_protocol_sha256": _sha256(WARRANT_PROTOCOL),
        "warrant_config_sha256": _sha256(WARRANT_CONFIG),
        "matched_control_artifact_sha256": _sha256(CONTROL),
    }
    for key, actual in expected.items():
        if stage.get(key) != actual:
            raise CornerRefusal(f"frozen {key} drift")
    if (stage.get("stage_id") != "mq5-er6r-the-corner-v1"
            or stage.get("parent_experiment") != "mq5-er6r-the-warrant-v1"
            or stage.get("candidate_node") != control["candidate"]["node"]
            or stage.get("matched_control_node") != control["selected_control"]["node"]
            or control.get("neural_outcomes_used") is not False
            or control.get("alternate_control_identities_exposed") is not False):
        raise CornerRefusal("frozen stage or control identity drift")
    if (stage.get("neural_execution_enabled") is not False
            or stage.get("result_execution_enabled") is not False):
        raise CornerRefusal("stage must remain execution disabled")
    if stage.get("arms") != {
        "baseline": "P0", "candidate": "P1952", "matched_control": "PCONTROL"
    }:
        raise CornerRefusal("arm identity drift")
    return stage


def output_silencer(
    node: int, *, population_size: int, start_frame: int = 0, end_frame: int = 191
) -> Callable[[np.ndarray, int], np.ndarray]:
    """Modifier for the shared runtime's post-native-activity hook."""
    if (not 0 <= node < population_size or start_frame != 0
            or end_frame != 191):
        raise CornerRefusal("unfrozen output-silencing parameters")

    def modifier(native_activity: np.ndarray, frame: int) -> np.ndarray:
        native = np.asarray(native_activity, dtype=np.float32)
        if native.shape != (population_size,) or not np.all(np.isfinite(native)):
            raise CornerRefusal("invalid native activity")
        if not 0 <= frame < 192:
            raise CornerRefusal("frame outside frozen window")
        modified = native.copy()
        modified[node] = np.float32(0.0)
        return modified

    return modifier


def arm_modifier(arm: str, *, population_size: int):
    """P0 gets the native runtime; both interventions use one operator."""
    stage = load_frozen_stage()
    if arm == stage["arms"]["baseline"]:
        return None
    nodes = {
        stage["arms"]["candidate"]: stage["candidate_node"],
        stage["arms"]["matched_control"]: stage["matched_control_node"],
    }
    if arm not in nodes:
        raise CornerRefusal("unknown arm")
    return output_silencer(nodes[arm], population_size=population_size)


def dependency_by_onset(
    baseline: Mapping[int, int | None], intervention: Mapping[int, int | None]
) -> dict[int, bool]:
    """A later or absent onset counts only when the P0 responder is present."""
    stage = load_frozen_stage()
    targets = stage["all_targets"]
    if set(baseline) != set(targets) or set(intervention) != set(targets):
        raise CornerRefusal("responder set drift")
    result = {}
    for target in targets:
        p0, treated = baseline[target], intervention[target]
        for onset in (p0, treated):
            if onset is not None and (type(onset) is not int or not 0 <= onset < 192):
                raise CornerRefusal("invalid first-positive onset")
        result[target] = p0 is not None and (treated is None or treated > p0)
    return result


def classify_affected(dependency: Mapping[int, bool]) -> tuple[str, int]:
    """Retained responders cannot alter the frozen affected-panel label."""
    stage = load_frozen_stage()
    if set(dependency) != set(stage["all_targets"]):
        raise CornerRefusal("responder set drift")
    if any(type(value) is not bool for value in dependency.values()):
        raise CornerRefusal("dependency must be boolean")
    k = sum(dependency[target] for target in stage["affected_targets"])
    label = (
        "WARRANT_NECESSITY_COMPLETE" if k == 5 else
        "WARRANT_NECESSITY_NOT_OBSERVED" if k == 0 else
        "WARRANT_NECESSITY_PARTIAL"
    )
    return label, k
