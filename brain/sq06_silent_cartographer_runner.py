from __future__ import annotations

import argparse
import gc
import hashlib
import json
import os
import subprocess
import tomllib
from pathlib import Path

import numpy as np
from scipy import sparse

from brain.mq5_ts_runtime import CONNECTOME, RETINA
from brain.sq05_betrayal_i import build_betrayal_i
from brain.sq05_stimulus import EXPECTED_SCHEDULE_SHA256, assert_frozen_stimulus
from brain.sq05_two_betrayals_runner import (
    build_sham,
    build_stimuli,
    duplicate_exact,
    load_primary_population,
    run_episode,
    symmetric_normalized_l2,
    verify_frozen_dependencies as verify_sq05_frozen_dependencies,
)
from brain.sq06_orientation_groups import build_orientation_group


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = Path(
    os.environ.get("MOSCAQUANT_DATA_ROOT", str(Path.home() / "moscaquant-data"))
).expanduser().resolve()

CONFIG = ROOT / "config/controls/sq06-silent-cartographer-runner-v1.toml"
PREREG = ROOT / "config/controls/sq06-silent-cartographer-v1.toml"
GROUPS = ROOT / "config/controls/sq06-orientation-edge-groups-v1.json"
RESULT_SCHEMA = ROOT / "config/controls/sq06-silent-cartographer-result-schema-v1.json"
AUTHORIZATION = ROOT / "config/controls/sq06-silent-cartographer-execution-authorization-v1.json"

CONSENSUS = DATA_ROOT / "processed/mq3-dn-consensus-v1.npz"
RESULT_JSON = DATA_ROOT / "experiments/sq06-silent-cartographer-v1.json"
RESULT_NPZ = DATA_ROOT / "experiments/sq06-silent-cartographer-v1.npz"

ARMS = (
    "INTACT",
    "FULL13_TARGETED",
    "FULL13_SHAM",
    "LR_GROUP_TARGETED",
    "LR_GROUP_SHAM",
    "RL_GROUP_TARGETED",
    "RL_GROUP_SHAM",
)
LAYOUTS = ("LR", "RL")
REPLICATES = (1, 2)
EXPECTED_EPISODE_COUNT = 28
ASSIGNED_DN_COUNT = 1191
FRAME_COUNT = 192
CHANNELS = ("DN-C0", "DN-C1", "DN-C2")
PRIMARY_L2_TOL = 1e-9
PRIMARY_MAX_ABS_TOL = 1e-12
ACCEPTED_NINE = (92, 656, 317, 137122, 126002, 55, 129, 51, 1273)

EXPECTED_SHA256 = {
    "prereg": "3182a91b08dacc278ba180999f0358eea812da94ec5e2eeff9ed834498820f92",
    "groups": "2fac74225e9874dfe13f919bfc47062065ba85b1ed1b61cce424f9a2c777c38d",
    "orientation_operator": "0ea1d6f3188f03e4a90da36898b9cb46a6546c830aebf9fb5f51508d66cce0ce",
    "sq05_runner": "06f640dd6c829d917bb537298f8e54048066455b92f6932dc09fe5abdef4867e",
    "sq05_betrayal_i": "c62767cac434f380104c8da5cd9b73dcee89fefbeea0a0efe17ca9bd812c8664",
    "sq05_sham": "d43488defc7b27705fe6765db50c8519c65cdaf6ac9a4443aa599c9dd1879f0d",
    "sq05_stimulus": "90bf95fc7bf1baab5f8a77ba4dce9182a5ad5909ca6a3ca37a0cf10c946f623a",
    "consensus": "2e1272b6db6219290af96a828f52764d0f60d937336508251d0a4d6c46fb31f5",
    "connectome": "e00e3f2a9828c921fe1f093cc567bf45a85adad0526176be0aa1b8be09336eeb",
    "retina": "c4655220e1aee4eab580a534df009f0a7493f075c42285b430ad1365ae37917f",
    "physiology_constrained_visual_transduction": "bf754a29155ade789349fbdfc3c579f1b2c8dbea3c63804f2cf3d858d0a2f605",
    "visual_transduction": "015cc699f49e16bb59f6e7e5f04f92cca7bfc1a3c7057e73fe54398c755831f6",
    "result_schema": "a0fe8b814a17e2c416576381c25aaf1d1b4ea0432af7c3112d617c5f1366eb37",
}


class Refusal(RuntimeError):
    pass


def refuse(message: str) -> None:
    raise Refusal(message)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )


def load_runner_config() -> dict:
    with CONFIG.open("rb") as f:
        cfg = tomllib.load(f)
    if tuple(cfg["episode_plan"]["arms"]) != ARMS:
        refuse("SQ-06 runner arm order drift")
    if tuple(cfg["episode_plan"]["layouts"]) != LAYOUTS:
        refuse("SQ-06 runner layout order drift")
    if tuple(cfg["episode_plan"]["replicates"]) != REPLICATES:
        refuse("SQ-06 runner replicate plan drift")
    if cfg["episode_plan"]["expected_total_episode_count"] != EXPECTED_EPISODE_COUNT:
        refuse("SQ-06 runner episode-count drift")
    if cfg["execution"]["result_execution_authorized"] is not False:
        refuse("implementation config may not authorize result execution")
    return cfg


def episode_plan() -> list[dict]:
    plan = []
    for arm in ARMS:
        for layout in LAYOUTS:
            for replicate in REPLICATES:
                plan.append({"arm": arm, "layout": layout, "replicate": replicate})
    if len(plan) != EXPECTED_EPISODE_COUNT:
        refuse("SQ-06 episode plan construction drift")
    return plan


def verify_frozen_dependencies() -> dict:
    load_runner_config()

    # SQ-06 reuses the SQ-05 neural execution substrate. Calling the frozen
    # SQ-05 verifier here binds the transitive runtime dependencies too:
    # transmitter signs, relay/graded artifacts, MQ5 runtime, MQ3.2 operator,
    # SQ-05 intervention adapters, stimulus, core preregistration, and schema.
    sq05_runtime = verify_sq05_frozen_dependencies()

    paths = {
        "prereg": PREREG,
        "groups": GROUPS,
        "orientation_operator": ROOT / "brain/sq06_orientation_groups.py",
        "sq05_runner": ROOT / "brain/sq05_two_betrayals_runner.py",
        "sq05_betrayal_i": ROOT / "brain/sq05_betrayal_i.py",
        "sq05_sham": ROOT / "config/controls/sq05-betrayal-i-sham-v1.json",
        "sq05_stimulus": ROOT / "brain/sq05_stimulus.py",
        "consensus": CONSENSUS,
        "connectome": Path(CONNECTOME),
        "retina": Path(RETINA),
        "physiology_constrained_visual_transduction":
            ROOT / "brain/physiology_constrained_visual_transduction.py",
        "visual_transduction": ROOT / "brain/visual_transduction.py",
        "result_schema": RESULT_SCHEMA,
    }
    observed = {}
    for name, path in paths.items():
        if not path.is_file():
            refuse(f"missing frozen dependency {name}: {path}")
        actual = sha256_file(path)
        expected = EXPECTED_SHA256[name]
        if actual != expected:
            refuse(f"SQ-06 dependency SHA mismatch for {name}: {actual} != {expected}")
        observed[name] = actual

    schedules = assert_frozen_stimulus()
    if schedules != EXPECTED_SCHEDULE_SHA256:
        refuse("SQ-06 inherited stimulus schedule digest drift")

    with PREREG.open("rb") as f:
        prereg = tomllib.load(f)
    if tuple(prereg["arms"]["names"]) != ARMS:
        refuse("SQ-06 preregistered arm set drift")
    if prereg["arms"]["expected_episode_count"] != EXPECTED_EPISODE_COUNT:
        refuse("SQ-06 preregistered episode count drift")
    if prereg["reporting"]["minimum_meaningful_effect_floor"] != "NOT_DEFINED":
        refuse("SQ-06 minimum-effect-floor provenance drift")

    return {
        "runner_config_sha256": sha256_file(CONFIG),
        "dependencies": observed,
        "stimulus_schedule_sha256": dict(schedules),
        "episode_count": EXPECTED_EPISODE_COUNT,
        "sq05_runtime_dependencies": sq05_runtime,
    }


def preflight() -> dict:
    deps = verify_frozen_dependencies()
    if RESULT_JSON.exists() or RESULT_NPZ.exists():
        refuse("SQ-06 result artifact already exists")
    return {
        "status": "PREFLIGHT_PASS",
        "execution_mode_candidate": "local",
        "authorization_present": AUTHORIZATION.is_file(),
        "result_exists": False,
        "topology_randomization_executed": False,
        "neural_execution_executed": False,
        "episode_plan": episode_plan(),
        "dependencies": deps,
    }


def max_abs_difference(a, b) -> float:
    x = np.asarray(a, dtype=np.float64)
    y = np.asarray(b, dtype=np.float64)
    return float(np.max(np.abs(x - y), initial=0.0))


def exact_primary_reproduction(candidate: dict, reference: dict) -> dict:
    a = candidate["positive_voltage"]
    b = reference["positive_voltage"]
    l2 = symmetric_normalized_l2(a, b)
    max_abs = max_abs_difference(a, b)
    return {
        "symmetric_normalized_l2": l2,
        "max_abs": max_abs,
        "exact_reproduction": l2 <= PRIMARY_L2_TOL and max_abs <= PRIMARY_MAX_ABS_TOL,
    }


def classify_primary(first: dict[str, dict[str, dict]]) -> dict:
    conditions = {}

    full13 = {}
    for layout in LAYOUTS:
        intact = first["INTACT"][layout]
        target = first["FULL13_TARGETED"][layout]
        sham = first["FULL13_SHAM"][layout]
        target_distance = symmetric_normalized_l2(
            target["positive_voltage"], intact["positive_voltage"]
        )
        sham_distance = symmetric_normalized_l2(
            sham["positive_voltage"], intact["positive_voltage"]
        )
        full13[layout] = {
            "target_distance": target_distance,
            "sham_distance": sham_distance,
            "target_exceeds_sham": target_distance > sham_distance,
        }
    conditions["full13_positive_control"] = {
        "layouts": full13,
        "pass": all(full13[x]["target_exceeds_sham"] for x in LAYOUTS),
    }

    subset_shams = {}
    for arm in ("LR_GROUP_SHAM", "RL_GROUP_SHAM"):
        subset_shams[arm] = {
            layout: exact_primary_reproduction(first[arm][layout], first["INTACT"][layout])
            for layout in LAYOUTS
        }
    conditions["subset_sham_guard"] = {
        "comparisons": subset_shams,
        "pass": all(
            subset_shams[arm][layout]["exact_reproduction"]
            for arm in subset_shams
            for layout in LAYOUTS
        ),
    }

    conditions["lr_recapitulation"] = {
        **exact_primary_reproduction(
            first["LR_GROUP_TARGETED"]["LR"],
            first["FULL13_TARGETED"]["LR"],
        )
    }
    conditions["lr_recapitulation"]["pass"] = conditions["lr_recapitulation"][
        "exact_reproduction"
    ]

    conditions["lr_cross_group_null"] = {
        **exact_primary_reproduction(
            first["RL_GROUP_TARGETED"]["LR"],
            first["INTACT"]["LR"],
        )
    }
    conditions["lr_cross_group_null"]["pass"] = conditions["lr_cross_group_null"][
        "exact_reproduction"
    ]

    conditions["rl_recapitulation"] = {
        **exact_primary_reproduction(
            first["RL_GROUP_TARGETED"]["RL"],
            first["FULL13_TARGETED"]["RL"],
        )
    }
    conditions["rl_recapitulation"]["pass"] = conditions["rl_recapitulation"][
        "exact_reproduction"
    ]

    conditions["rl_cross_group_null"] = {
        **exact_primary_reproduction(
            first["LR_GROUP_TARGETED"]["RL"],
            first["INTACT"]["RL"],
        )
    }
    conditions["rl_cross_group_null"]["pass"] = conditions["rl_cross_group_null"][
        "exact_reproduction"
    ]

    return {
        "conditions": conditions,
        "all_primary_conditions_satisfied": all(
            item["pass"] for item in conditions.values()
        ),
        "single_overall_winner": None,
        "minimum_meaningful_effect_floor": "NOT_DEFINED",
    }


def build_arm_connectome(
    baseline: sparse.csr_matrix,
    arm: str,
) -> tuple[sparse.csr_matrix, dict]:
    if arm == "INTACT":
        return baseline, {"arm": arm, "edge_count": 0}
    if arm == "FULL13_TARGETED":
        candidate, provenance = build_betrayal_i(baseline)
        return candidate, {**provenance, "arm": arm}
    if arm == "FULL13_SHAM":
        candidate, provenance = build_sham(baseline)
        return candidate, {**provenance, "arm": arm}
    if arm == "LR_GROUP_TARGETED":
        return build_orientation_group(baseline, "LR_OBSERVED", "TARGETED")
    if arm == "LR_GROUP_SHAM":
        return build_orientation_group(baseline, "LR_OBSERVED", "SHAM")
    if arm == "RL_GROUP_TARGETED":
        return build_orientation_group(baseline, "RL_OBSERVED", "TARGETED")
    if arm == "RL_GROUP_SHAM":
        return build_orientation_group(baseline, "RL_OBSERVED", "SHAM")
    raise ValueError(f"unknown SQ-06 arm: {arm}")


def descriptive_effect(
    candidate: dict,
    intact: dict,
    dn_indices: np.ndarray,
    channel_positions: dict[str, np.ndarray],
) -> dict:
    delta = (
        np.asarray(candidate["positive_voltage"], dtype=np.float64)
        - np.asarray(intact["positive_voltage"], dtype=np.float64)
    )
    per_dn_l2 = np.linalg.norm(delta, axis=0)
    total_energy = float(np.sum(delta * delta))

    accepted_positions = {
        int(idx): pos for pos, idx in enumerate(np.asarray(dn_indices).tolist())
        if int(idx) in ACCEPTED_NINE
    }
    accepted_energy = float(
        sum(np.sum(delta[:, pos] ** 2) for pos in accepted_positions.values())
    )

    phases = {
        "baseline_0_31": float(np.sum(delta[0:32] ** 2)),
        "cue_a_only_32_95": float(np.sum(delta[32:96] ** 2)),
        "cue_a_plus_b_96_191": float(np.sum(delta[96:192] ** 2)),
    }
    channels = {
        channel: float(np.sum(delta[:, positions] ** 2))
        for channel, positions in channel_positions.items()
    }

    return {
        "per_dn_l2_aligned_to_dn_indices": per_dn_l2.tolist(),
        "effect_energy_total": total_energy,
        "accepted_nine_effect_energy_fraction": (
            accepted_energy / total_energy if total_energy > 0.0 else 0.0
        ),
        "phase_effect_energy": phases,
        "dn_channel_effect_energy": channels,
    }


def _episode_arrays(episodes: list[dict]) -> dict[str, np.ndarray]:
    if len(episodes) != EXPECTED_EPISODE_COUNT:
        refuse(f"expected {EXPECTED_EPISODE_COUNT} episodes, got {len(episodes)}")
    return {
        "dn_indices": np.asarray(episodes[0]["dn_indices"], dtype=np.int32),
        "episode_arm": np.asarray([x["arm"] for x in episodes], dtype="U32"),
        "episode_layout": np.asarray([x["layout"] for x in episodes], dtype="U2"),
        "episode_replicate": np.asarray([x["replicate"] for x in episodes], dtype=np.int8),
        "primary_positive_voltage": np.stack(
            [x["result"]["positive_voltage"] for x in episodes]
        ).astype(np.float32),
        "primary_spikes": np.stack(
            [x["result"]["spikes"] for x in episodes]
        ).astype(np.uint8),
        "channel_mean_positive_voltage": np.stack(
            [x["result"]["channel_mean_positive_voltage"] for x in episodes]
        ).astype(np.float64),
        "channel_positive_fraction": np.stack(
            [x["result"]["channel_positive_fraction"] for x in episodes]
        ).astype(np.float64),
        "channel_spike_count": np.stack(
            [x["result"]["channel_spike_count"] for x in episodes]
        ).astype(np.int32),
        "channel_spike_rate": np.stack(
            [x["result"]["channel_spike_rate"] for x in episodes]
        ).astype(np.float64),
    }


def _write_sidecar_atomic(arrays: dict[str, np.ndarray]) -> str:
    RESULT_NPZ.parent.mkdir(parents=True, exist_ok=True)
    tmp = RESULT_NPZ.with_suffix(".npz.tmp")
    with tmp.open("wb") as f:
        np.savez_compressed(f, **arrays)
    os.replace(tmp, RESULT_NPZ)
    return sha256_file(RESULT_NPZ)


def _write_manifest_atomic(manifest: dict) -> None:
    RESULT_JSON.parent.mkdir(parents=True, exist_ok=True)
    tmp = RESULT_JSON.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, RESULT_JSON)


def verify_execution_authorization() -> dict:
    deps = verify_frozen_dependencies()

    if not AUTHORIZATION.is_file():
        refuse("SQ-06 execution authorization file is absent")

    rel = str(AUTHORIZATION.relative_to(ROOT))
    tracked = _git("ls-files", "--error-unmatch", rel)
    if tracked.returncode != 0:
        refuse("SQ-06 execution authorization must be tracked by Git")

    status = _git("status", "--porcelain")
    if status.returncode != 0 or status.stdout.strip():
        refuse("SQ-06 result execution requires a clean Git working tree")

    auth = json.loads(AUTHORIZATION.read_text(encoding="utf-8"))
    required = {
        "artifact": "sq06-silent-cartographer-execution-authorization-v1",
        "result_execution_enabled": True,
        "execution_mode": "local",
        "expected_episode_count": EXPECTED_EPISODE_COUNT,
    }
    for key, value in required.items():
        if auth.get(key) != value:
            refuse(f"SQ-06 authorization field drift: {key}")

    runner_sha = sha256_file(Path(__file__))
    config_sha = sha256_file(CONFIG)
    bindings = {
        "runner_sha256": runner_sha,
        "runner_config_sha256": config_sha,
        "preregistration_sha256": EXPECTED_SHA256["prereg"],
        "result_schema_sha256": EXPECTED_SHA256["result_schema"],
        "orientation_operator_sha256": EXPECTED_SHA256["orientation_operator"],
    }
    for key, value in bindings.items():
        if auth.get(key) != value:
            refuse(f"SQ-06 authorization binding mismatch: {key}")

    implementation_commit = auth.get("implementation_commit")
    if not isinstance(implementation_commit, str) or len(implementation_commit) != 40:
        refuse("SQ-06 authorization missing implementation commit")

    ancestry = _git("merge-base", "--is-ancestor", implementation_commit, "HEAD")
    if ancestry.returncode != 0:
        refuse("SQ-06 implementation commit is not an ancestor of execution HEAD")

    if RESULT_JSON.exists() or RESULT_NPZ.exists():
        refuse("SQ-06 result already exists")

    return {"authorization": auth, "dependencies": deps}


def run_frozen() -> dict:
    verified = verify_execution_authorization()

    baseline = sparse.load_npz(CONNECTOME).tocsr()
    retina = np.load(RETINA, allow_pickle=False)
    retinal_indices = np.asarray(retina["neuron_index"], dtype=np.int32)
    dn_indices, _clusters, channel_positions = load_primary_population()
    stimuli = {layout: build_stimuli(layout) for layout in LAYOUTS}

    episodes = []
    first = {arm: {} for arm in ARMS}
    arm_provenance = {}

    for arm in ARMS:
        candidate, provenance = build_arm_connectome(baseline, arm)
        arm_provenance[arm] = provenance

        for layout in LAYOUTS:
            pair = []
            for replicate in REPLICATES:
                result = run_episode(
                    candidate,
                    retinal_indices,
                    dn_indices,
                    channel_positions,
                    stimuli[layout],
                )
                pair.append(result)
                episodes.append({
                    "arm": arm,
                    "layout": layout,
                    "replicate": replicate,
                    "dn_indices": dn_indices,
                    "result": result,
                })

            if not duplicate_exact(pair[0], pair[1]):
                refuse(f"SQ-06 duplicate replay mismatch: {arm} / {layout}")
            first[arm][layout] = pair[0]

        if arm != "INTACT":
            del candidate
            gc.collect()

    if len(episodes) != EXPECTED_EPISODE_COUNT:
        refuse("SQ-06 incomplete episode execution")

    primary = classify_primary(first)

    secondary = {}
    for arm in ("FULL13_TARGETED", "LR_GROUP_TARGETED", "RL_GROUP_TARGETED"):
        secondary[arm] = {
            layout: descriptive_effect(
                first[arm][layout],
                first["INTACT"][layout],
                dn_indices,
                channel_positions,
            )
            for layout in LAYOUTS
        }

    arrays = _episode_arrays(episodes)
    sidecar_sha = _write_sidecar_atomic(arrays)

    manifest = {
        "artifact": "sq06-silent-cartographer-v1",
        "schema_version": "moscaquant.sq06-silent-cartographer-result.v1",
        "status": "COMPLETE_PREREGISTERED_RESULT",
        "canonical_parent": "SQ-06 — SILENT CARTOGRAPHER",
        "execution_mode": "local",
        "authorization": verified["authorization"],
        "provenance": {
            **verified["dependencies"],
            "arm_provenance": arm_provenance,
        },
        "primary_conditions": primary,
        "secondary_descriptive": secondary,
        "sidecar": {
            "path": str(RESULT_NPZ),
            "sha256": sidecar_sha,
            "schema_sha256": EXPECTED_SHA256["result_schema"],
            "written": True,
        },
        "claim_boundaries": {
            "sq05_result_rewritten": False,
            "independent_discovery": False,
            "biological_orientation_circuit": False,
            "behavior": False,
            "fear": False,
            "hunger": False,
            "threat_perception": False,
            "financial_value": False,
        },
        "episode_count_expected": EXPECTED_EPISODE_COUNT,
        "episode_count_completed": len(episodes),
        "single_overall_winner": None,
    }

    _write_manifest_atomic(manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--preflight-only", action="store_true")
    group.add_argument("--run-frozen", action="store_true")
    args = parser.parse_args()

    if args.preflight_only:
        print(json.dumps(preflight(), indent=2, sort_keys=True))
        return

    print(json.dumps(run_frozen(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
