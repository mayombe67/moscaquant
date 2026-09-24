from __future__ import annotations

import argparse
import gc
import hashlib
import json
import os
import subprocess
import time
import tomllib
from dataclasses import asdict, is_dataclass
from pathlib import Path

import numpy as np
from scipy import sparse

from brain.mq3_2_causal_intervention import zero_edges
from brain.mq5_ts_runtime import (
    CONNECTOME,
    GRADED,
    RELAY,
    RELEASE_GAIN,
    RETINA,
    TRANSMITTER,
)
from brain.physiology_constrained_visual_transduction import (
    PhysiologyConstrainedVisualTransductionRuntime,
)
from brain.sq05_betrayal_i import build_betrayal_i
from brain.sq05_betrayal_ii import build_betrayal_ii
from brain.sq05_stimulus import (
    EXPECTED_SCHEDULE_SHA256,
    TOTAL_FRAMES,
    assert_frozen_stimulus,
    stimulus_frame,
)
from brain.visual_transduction import VisualTransductionConfig


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = Path(
    os.environ.get("MOSCAQUANT_DATA_ROOT", str(Path.home() / "moscaquant-data"))
).expanduser().resolve()

CONFIG = ROOT / "config/controls/sq05-two-betrayals-runner-v1.toml"
CORE_PREREG = ROOT / "config/controls/sq05-two-betrayals-core-prereg-v1.toml"
RESULT_SCHEMA = ROOT / "config/controls/sq05-two-betrayals-result-schema-v1.json"
SHAM = ROOT / "config/controls/sq05-betrayal-i-sham-v1.json"

CONSENSUS = DATA_ROOT / "processed/mq3-dn-consensus-v1.npz"

AUTHORIZATION = (
    ROOT
    / "config/controls/sq05-two-betrayals-execution-authorization-v1.json"
)

RESULT_JSON = DATA_ROOT / "experiments/sq05-two-betrayals-v1.json"
RESULT_NPZ = DATA_ROOT / "experiments/sq05-two-betrayals-v1.npz"

EXPECTED_CORE_PREREG_SHA256 = "871f1216fe8a6160c937615b9d48a881209201aeb102a6993cf2e54bf37b5196"
EXPECTED_RESULT_SCHEMA_SHA256 = "bf1069e457eff0e828e890d74ae1b5831e2204e2bc070edd2fe5732311acd33f"
EXPECTED_SHAM_SHA256 = "d43488defc7b27705fe6765db50c8519c65cdaf6ac9a4443aa599c9dd1879f0d"

EXPECTED_DEPENDENCY_SHA256 = {
    "connectome": "e00e3f2a9828c921fe1f093cc567bf45a85adad0526176be0aa1b8be09336eeb",
    "retina": "c4655220e1aee4eab580a534df009f0a7493f075c42285b430ad1365ae37917f",
    "transmitter": "0a8b1abe338e17afde197f7ef2d9a6b86cc67a2b51d0f50d9610108f809af69f",
    "consensus": "2e1272b6db6219290af96a828f52764d0f60d937336508251d0a4d6c46fb31f5",
    "relay": "a3df2746ec69d10a2739a05f3ec55c4bd5f15b10b9a6167aee41c15a647e3478",
    "graded": "1c514bf58bf69b24bfba28489344d0fe3e0f7590d649e0ef446c33898d38e379",
    "mq5_ts_runtime": "b4792f626868742b0e6382d837c7676e103084171b5142aa52b211f5cc53e526",
    "mq3_2_operator": "007aa507ac22b07811bff5ae8102a0916c88549aa3011fa22fa57c70598c6a87",
    "betrayal_i": "c62767cac434f380104c8da5cd9b73dcee89fefbeea0a0efe17ca9bd812c8664",
    "betrayal_ii": "46c164d8e2c4c87f3ed6da70bf40bafe20352ebe098c5803eece489209158460",
    "stimulus": "90bf95fc7bf1baab5f8a77ba4dce9182a5ad5909ca6a3ca37a0cf10c946f623a",
}

EXPECTED_SEEDS = tuple(range(20265100, 20265120))
LAYOUTS = ("LR", "RL")
CHANNELS = ("DN-C0", "DN-C1", "DN-C2")
ASSIGNED_DN_COUNT = 1191
FRAME_COUNT = 192
DETERMINISTIC_REPLICATES = 2
EXPECTED_EPISODE_COUNT = 52

PRIMARY_L2_TOL = 1e-9
PRIMARY_MAX_ABS_TOL = 1e-12
CUE_TRANSITION_TOL = 1e-12


class Refusal(RuntimeError):
    pass


def refuse(msg: str) -> None:
    raise Refusal(msg)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def _run_git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        cwd=str(ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )


def _jsonable(value):
    if is_dataclass(value):
        return _jsonable(asdict(value))
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return repr(value)


def load_runner_config() -> dict:
    if not CONFIG.is_file():
        refuse(f"missing SQ-05 runner config: {CONFIG}")
    with CONFIG.open("rb") as f:
        cfg = tomllib.load(f)

    if cfg["experiment"]["id"] != "sq05-two-betrayals-runner-v1":
        refuse("unexpected SQ-05 runner config id")
    if cfg["execution"]["mode"] != "local":
        refuse("reviewed SQ-05 runtime mode is not local")
    if cfg["execution"]["result_execution_authorized"] is not False:
        refuse("runner implementation config must not authorize execution")
    return cfg


def verify_frozen_dependencies() -> dict:
    cfg = load_runner_config()

    paths = {
        "connectome": Path(CONNECTOME),
        "retina": Path(RETINA),
        "transmitter": Path(TRANSMITTER),
        "consensus": CONSENSUS,
        "relay": Path(RELAY),
        "graded": Path(GRADED),
        "mq5_ts_runtime": ROOT / "brain/mq5_ts_runtime.py",
        "mq3_2_operator": ROOT / "brain/mq3_2_causal_intervention.py",
        "betrayal_i": ROOT / "brain/sq05_betrayal_i.py",
        "betrayal_ii": ROOT / "brain/sq05_betrayal_ii.py",
        "stimulus": ROOT / "brain/sq05_stimulus.py",
    }

    observed = {}
    for name, path in paths.items():
        if not path.is_file():
            refuse(f"missing frozen dependency {name}: {path}")
        actual = sha256_file(path)
        expected = EXPECTED_DEPENDENCY_SHA256[name]
        if actual != expected:
            refuse(
                f"SQ-05 dependency SHA mismatch for {name}: "
                f"{actual} != {expected}"
            )
        observed[name] = actual

    if not CORE_PREREG.is_file():
        refuse("missing core preregistration")
    if sha256_file(CORE_PREREG) != EXPECTED_CORE_PREREG_SHA256:
        refuse("core preregistration SHA mismatch")

    if not RESULT_SCHEMA.is_file():
        refuse("missing result schema")
    if sha256_file(RESULT_SCHEMA) != EXPECTED_RESULT_SCHEMA_SHA256:
        refuse("result schema SHA mismatch")

    if not SHAM.is_file():
        refuse("missing frozen sham artifact")
    if sha256_file(SHAM) != EXPECTED_SHAM_SHA256:
        refuse("frozen sham artifact SHA mismatch")

    if TOTAL_FRAMES != FRAME_COUNT:
        refuse("stimulus frame count drift")

    schedules = assert_frozen_stimulus()
    if schedules != EXPECTED_SCHEDULE_SHA256:
        refuse("stimulus schedule digest drift")

    with CORE_PREREG.open("rb") as f:
        prereg = tomllib.load(f)

    seeds = tuple(prereg["betrayal_ii_randomization"]["seeds"])
    if seeds != EXPECTED_SEEDS:
        refuse("core-preregistered BETRAYAL II seed block drift")

    if prereg["layouts"]["required"] != ["LR", "RL"]:
        refuse("core-preregistered layout set drift")

    return {
        "runner_config_sha256": sha256_file(CONFIG),
        "core_prereg_sha256": EXPECTED_CORE_PREREG_SHA256,
        "result_schema_sha256": EXPECTED_RESULT_SCHEMA_SHA256,
        "sham_sha256": EXPECTED_SHAM_SHA256,
        "dependencies": observed,
        "stimulus_schedule_sha256": dict(schedules),
        "seeds": list(EXPECTED_SEEDS),
    }


def preflight() -> dict:
    deps = verify_frozen_dependencies()

    if RESULT_JSON.exists() or RESULT_NPZ.exists():
        refuse(
            "final SQ-05 result artifact already exists; refusing before "
            "topology construction or neural execution"
        )

    auth_present = AUTHORIZATION.is_file()

    return {
        "status": "PREFLIGHT_PASS",
        "execution_mode_candidate": "local",
        "authorization_present": auth_present,
        "result_exists": False,
        "topology_construction_executed": False,
        "neural_execution_executed": False,
        "preregistered_seed_executed": False,
        "dependencies": deps,
    }


def verify_execution_authorization() -> dict:
    verify_frozen_dependencies()

    if not AUTHORIZATION.is_file():
        refuse("SQ-05 execution authorization file is absent")

    tracked = _run_git("ls-files", "--error-unmatch", str(AUTHORIZATION.relative_to(ROOT)))
    if tracked.returncode != 0:
        refuse("SQ-05 execution authorization must be tracked by Git")

    status = _run_git("status", "--porcelain")
    if status.returncode != 0 or status.stdout.strip():
        refuse("SQ-05 result execution requires a clean Git working tree")

    auth = json.loads(AUTHORIZATION.read_text(encoding="utf-8"))

    required = {
        "artifact": "sq05-two-betrayals-execution-authorization-v1",
        "result_execution_enabled": True,
        "execution_mode": "local",
        "capacity_decision": "HABITAT_LOCAL_CAPACITY_SUPPORTED",
        "runner_sha256": sha256_file(Path(__file__).resolve()),
        "runner_config_sha256": sha256_file(CONFIG),
        "core_prereg_sha256": EXPECTED_CORE_PREREG_SHA256,
        "result_schema_sha256": EXPECTED_RESULT_SCHEMA_SHA256,
    }

    for key, expected in required.items():
        if auth.get(key) != expected:
            refuse(
                f"execution authorization mismatch for {key}: "
                f"{auth.get(key)!r} != {expected!r}"
            )

    implementation_commit = auth.get("implementation_commit")
    if not isinstance(implementation_commit, str) or not implementation_commit:
        refuse("execution authorization lacks implementation_commit")

    ancestor = _run_git(
        "merge-base", "--is-ancestor", implementation_commit, "HEAD"
    )
    if ancestor.returncode != 0:
        refuse("authorized implementation commit is not an ancestor of HEAD")

    if RESULT_JSON.exists() or RESULT_NPZ.exists():
        refuse(
            "SQ-05 result already exists; refusing before topology construction "
            "or neural execution"
        )

    return auth


def load_primary_population():
    consensus = np.load(CONSENSUS, allow_pickle=False)
    indices = np.asarray(consensus["neuron_index"], dtype=np.int32)
    clusters = np.asarray(consensus["consensus_cluster"], dtype=np.int32)

    keep = np.isin(clusters, [0, 1, 2])
    indices = indices[keep]
    clusters = clusters[keep]

    order = np.argsort(indices, kind="stable")
    indices = indices[order]
    clusters = clusters[order]

    if len(indices) != ASSIGNED_DN_COUNT:
        refuse(f"expected {ASSIGNED_DN_COUNT} assigned DNs, got {len(indices)}")

    observed = {
        "DN-C0": int(np.count_nonzero(clusters == 0)),
        "DN-C1": int(np.count_nonzero(clusters == 1)),
        "DN-C2": int(np.count_nonzero(clusters == 2)),
    }
    if observed != {"DN-C0": 6, "DN-C1": 646, "DN-C2": 539}:
        refuse(f"DN consensus population drift: {observed}")

    channel_positions = {
        "DN-C0": np.flatnonzero(clusters == 0).astype(np.int32),
        "DN-C1": np.flatnonzero(clusters == 1).astype(np.int32),
        "DN-C2": np.flatnonzero(clusters == 2).astype(np.int32),
    }

    return indices, clusters, channel_positions


def build_stimuli(layout: str) -> tuple[np.ndarray, ...]:
    if layout not in LAYOUTS:
        raise ValueError(f"unknown SQ-05 layout: {layout}")
    frames = []
    for frame in range(FRAME_COUNT):
        stimulus = np.asarray(stimulus_frame(layout, frame), dtype=np.float32)
        stimulus.setflags(write=False)
        frames.append(stimulus)
    return tuple(frames)


def run_episode(
    connectome: sparse.csr_matrix,
    retinal_indices: np.ndarray,
    dn_indices: np.ndarray,
    channel_positions: dict[str, np.ndarray],
    stimuli: tuple[np.ndarray, ...],
) -> dict[str, np.ndarray]:
    if len(stimuli) != FRAME_COUNT:
        raise ValueError("SQ-05 episode must contain exactly 192 frames")

    runtime = PhysiologyConstrainedVisualTransductionRuntime(
        connectome=connectome.tocsr(copy=False),
        retinal_indices=np.asarray(retinal_indices, dtype=np.int32),
        relay_artifact=RELAY,
        graded_artifact=GRADED,
        config=VisualTransductionConfig(release_gain=RELEASE_GAIN),
    )

    positive = np.empty(
        (FRAME_COUNT, ASSIGNED_DN_COUNT),
        dtype=np.float32,
    )
    spikes = np.empty(
        (FRAME_COUNT, ASSIGNED_DN_COUNT),
        dtype=np.uint8,
    )
    channel_mean = np.empty((3, FRAME_COUNT), dtype=np.float64)
    channel_fraction = np.empty((3, FRAME_COUNT), dtype=np.float64)
    channel_spike_count = np.empty((3, FRAME_COUNT), dtype=np.int32)
    channel_spike_rate = np.empty((3, FRAME_COUNT), dtype=np.float64)

    for frame, stimulus in enumerate(stimuli):
        runtime.step(stimulus)

        voltage = np.asarray(runtime.voltage[dn_indices], dtype=np.float32)
        local_positive = np.maximum(voltage, 0.0)
        local_spikes = np.asarray(
            runtime.spikes[dn_indices] > 0,
            dtype=np.uint8,
        )

        positive[frame] = local_positive
        spikes[frame] = local_spikes

        for channel_index, channel in enumerate(CHANNELS):
            pos = channel_positions[channel]
            pv = local_positive[pos]
            sp = local_spikes[pos]
            channel_mean[channel_index, frame] = float(pv.mean())
            channel_fraction[channel_index, frame] = float(
                np.mean(pv > 0.0)
            )
            channel_spike_count[channel_index, frame] = int(sp.sum())
            channel_spike_rate[channel_index, frame] = float(sp.mean())

    return {
        "positive_voltage": positive,
        "spikes": spikes,
        "channel_mean_positive_voltage": channel_mean,
        "channel_positive_fraction": channel_fraction,
        "channel_spike_count": channel_spike_count,
        "channel_spike_rate": channel_spike_rate,
    }


def _load_sham_edges() -> list[tuple[int, int, float]]:
    payload = json.loads(SHAM.read_text(encoding="utf-8"))
    if payload.get("artifact") != "sq05-betrayal-i-sham-v1":
        refuse("unexpected sham artifact id")
    if payload.get("edge_count") != 13:
        refuse("unexpected sham edge count")
    if payload.get("selection", {}).get("derive_at_execution") is not False:
        refuse("sham derivation at execution is forbidden")

    return [
        (
            int(row["presynaptic"]),
            int(row["postsynaptic"]),
            float(row["weight"]),
        )
        for row in payload["edges"]
    ]


def build_sham(baseline: sparse.csr_matrix) -> tuple[sparse.csr_matrix, dict]:
    edges = _load_sham_edges()
    candidate = zero_edges(baseline, edges)

    expected_pairs = {(pre, post) for pre, post, _ in edges}
    diff = (baseline != candidate).tocoo()
    observed_pairs = {
        (int(col), int(row))
        for row, col in zip(diff.row, diff.col)
    }

    if observed_pairs != expected_pairs:
        refuse("BETRAYAL I sham modified unexpected edge identities")

    if candidate.nnz != baseline.nnz - len(edges):
        refuse("BETRAYAL I sham changed unexpected edge count")

    for pre, post, expected_weight in edges:
        before = float(baseline[post, pre])
        after = float(candidate[post, pre])
        if not np.isclose(
            before,
            expected_weight,
            rtol=1e-6,
            atol=1e-12,
        ):
            refuse(f"sham baseline weight mismatch {pre}->{post}")
        if after != 0.0:
            refuse(f"sham failed to zero {pre}->{post}")

    return candidate, {
        "arm": "BETRAYAL_I_SHAM",
        "edge_count": len(edges),
        "sham_artifact_sha256": EXPECTED_SHAM_SHA256,
    }


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
    return float(np.max(np.abs(x - y), initial=0.0))


def trace_comparison(a, b) -> dict:
    return {
        "symmetric_normalized_l2": symmetric_normalized_l2(a, b),
        "max_abs": max_abs_difference(a, b),
    }


def exact_reproduction_against_intact(candidate, intact) -> dict:
    primary = trace_comparison(
        candidate["positive_voltage"],
        intact["positive_voltage"],
    )
    channel = trace_comparison(
        candidate["channel_mean_positive_voltage"],
        intact["channel_mean_positive_voltage"],
    )

    primary_pass = (
        primary["symmetric_normalized_l2"] <= PRIMARY_L2_TOL
        and primary["max_abs"] <= PRIMARY_MAX_ABS_TOL
    )
    channel_pass = (
        channel["symmetric_normalized_l2"] <= PRIMARY_L2_TOL
        and channel["max_abs"] <= PRIMARY_MAX_ABS_TOL
    )

    return {
        "primary": primary,
        "channel_summary": channel,
        "primary_pass": primary_pass,
        "channel_summary_pass": channel_pass,
        "exact_reproduction": primary_pass and channel_pass,
    }


def cue_transition_for_layout(intact_episode: dict) -> dict:
    trace = np.asarray(
        intact_episode["channel_mean_positive_voltage"],
        dtype=np.float64,
    )
    reference = trace[:, 80:96].mean(axis=1)

    blocks = (
        (96, 112),
        (112, 128),
        (128, 144),
        (144, 160),
        (160, 176),
        (176, 192),
    )

    block_deltas = []
    responds = False
    for start, stop in blocks:
        block_mean = trace[:, start:stop].mean(axis=1)
        delta = block_mean - reference
        block_deltas.append(delta.tolist())
        if np.any(np.abs(delta) > CUE_TRANSITION_TOL):
            responds = True

    return {
        "responds": bool(responds),
        "reference_mean": reference.tolist(),
        "block_deltas": block_deltas,
    }


def classify_cue_transition(by_layout: dict[str, dict]) -> str:
    count = sum(bool(by_layout[layout]["responds"]) for layout in LAYOUTS)
    if count == 2:
        return "BOTH_LAYOUTS_RESPOND_TO_CUE_B"
    if count == 1:
        return "LAYOUT_DEPENDENT_CUE_B_RESPONSE"
    return "NO_DN_CUE_B_RESPONSE"


def classify_betrayal_i(
    intact_by_layout: dict[str, dict],
    lesion_by_layout: dict[str, dict],
    sham_by_layout: dict[str, dict],
) -> dict:
    layout_reports = {}
    exceeds = 0

    for layout in LAYOUTS:
        lesion_distance = symmetric_normalized_l2(
            lesion_by_layout[layout]["positive_voltage"],
            intact_by_layout[layout]["positive_voltage"],
        )
        sham_distance = symmetric_normalized_l2(
            sham_by_layout[layout]["positive_voltage"],
            intact_by_layout[layout]["positive_voltage"],
        )
        layout_exceeds = lesion_distance > sham_distance
        exceeds += int(layout_exceeds)
        layout_reports[layout] = {
            "lesion_distance": lesion_distance,
            "sham_distance": sham_distance,
            "lesion_exceeds_sham": layout_exceeds,
        }

    if exceeds == 2:
        status = "LESION_EFFECT_EXCEEDS_SHAM_BOTH_LAYOUTS"
    elif exceeds == 1:
        status = "LAYOUT_DEPENDENT_LESION_EFFECT"
    else:
        status = "LESION_NOT_SEPARATED_FROM_SHAM"

    return {"status": status, "layouts": layout_reports}


def classify_betrayal_ii(exact_count: int, completed_seed_count: int) -> str:
    if completed_seed_count != 20:
        return "INCOMPLETE_OR_INVALID"
    if 0 <= exact_count <= 1:
        return "STRICT_NULL_RARELY_REPRODUCES_INTACT_RESPONSE"
    if 2 <= exact_count <= 9:
        return "MIXED_STRICT_NULL_REPRODUCTION"
    if 10 <= exact_count <= 20:
        return "STRICT_NULL_FREQUENTLY_REPRODUCES_INTACT_RESPONSE"
    return "INCOMPLETE_OR_INVALID"


def duplicate_exact(a: dict, b: dict) -> bool:
    keys = (
        "positive_voltage",
        "spikes",
        "channel_mean_positive_voltage",
        "channel_positive_fraction",
        "channel_spike_count",
        "channel_spike_rate",
    )
    return all(np.array_equal(a[key], b[key]) for key in keys)


def secondary_responder_summary(
    episode: dict,
    dn_indices: np.ndarray,
    responder_indices: list[int],
) -> dict:
    position_by_index = {
        int(index): pos
        for pos, index in enumerate(dn_indices.tolist())
    }

    trace = np.asarray(episode["positive_voltage"], dtype=np.float32)
    result = {}

    for index in responder_indices:
        if index not in position_by_index:
            refuse(f"secondary responder {index} missing from primary population")

        local = trace[:, position_by_index[index]]
        positive_frames = np.flatnonzero(local > 0.0)
        result[str(index)] = {
            "responded": bool(len(positive_frames)),
            "first_positive_onset": (
                int(positive_frames[0]) if len(positive_frames) else None
            ),
            "positive_voltage": local.tolist(),
        }

    return result


def _episode_arrays(episodes: list[dict]) -> dict[str, np.ndarray]:
    if len(episodes) != EXPECTED_EPISODE_COUNT:
        refuse(
            f"expected {EXPECTED_EPISODE_COUNT} completed episodes, "
            f"got {len(episodes)}"
        )

    return {
        "dn_indices": episodes[0]["dn_indices"].astype(np.int32),
        "episode_arm": np.asarray(
            [ep["arm"] for ep in episodes],
            dtype="U32",
        ),
        "episode_layout": np.asarray(
            [ep["layout"] for ep in episodes],
            dtype="U2",
        ),
        "episode_seed": np.asarray(
            [ep["seed"] for ep in episodes],
            dtype=np.int64,
        ),
        "episode_replicate": np.asarray(
            [ep["replicate"] for ep in episodes],
            dtype=np.int8,
        ),
        "primary_positive_voltage": np.stack(
            [ep["result"]["positive_voltage"] for ep in episodes],
            axis=0,
        ).astype(np.float32, copy=False),
        "primary_spikes": np.stack(
            [ep["result"]["spikes"] for ep in episodes],
            axis=0,
        ).astype(np.uint8, copy=False),
        "channel_mean_positive_voltage": np.stack(
            [
                ep["result"]["channel_mean_positive_voltage"]
                for ep in episodes
            ],
            axis=0,
        ).astype(np.float64, copy=False),
        "channel_positive_fraction": np.stack(
            [ep["result"]["channel_positive_fraction"] for ep in episodes],
            axis=0,
        ).astype(np.float64, copy=False),
        "channel_spike_count": np.stack(
            [ep["result"]["channel_spike_count"] for ep in episodes],
            axis=0,
        ).astype(np.int32, copy=False),
        "channel_spike_rate": np.stack(
            [ep["result"]["channel_spike_rate"] for ep in episodes],
            axis=0,
        ).astype(np.float64, copy=False),
    }


def write_result_sidecar_atomic(arrays: dict[str, np.ndarray]) -> str:
    RESULT_NPZ.parent.mkdir(parents=True, exist_ok=True)
    tmp = RESULT_NPZ.with_suffix(".npz.tmp")

    if tmp.exists():
        tmp.unlink()

    with tmp.open("wb") as f:
        np.savez_compressed(f, **arrays)

    sidecar_sha = sha256_file(tmp)
    os.replace(tmp, RESULT_NPZ)
    return sidecar_sha


def write_manifest_atomic(manifest: dict) -> None:
    RESULT_JSON.parent.mkdir(parents=True, exist_ok=True)
    tmp = RESULT_JSON.with_suffix(".json.tmp")

    if tmp.exists():
        tmp.unlink()

    tmp.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(tmp, RESULT_JSON)


def run_frozen() -> dict:
    auth = verify_execution_authorization()
    deps = verify_frozen_dependencies()

    baseline = sparse.load_npz(CONNECTOME).tocsr()
    transmitter = np.asarray(np.load(TRANSMITTER), dtype=np.int8)
    retina = np.load(RETINA, allow_pickle=False)
    retinal_indices = np.asarray(retina["neuron_index"], dtype=np.int32)

    dn_indices, _clusters, channel_positions = load_primary_population()

    with CORE_PREREG.open("rb") as f:
        prereg = tomllib.load(f)

    responders = [
        int(x)
        for x in prereg["lesion_specific_secondary"][
            "accepted_responder_indices"
        ]
    ]

    stimuli = {layout: build_stimuli(layout) for layout in LAYOUTS}

    episodes = []
    deterministic_first = {
        "INTACT": {},
        "BETRAYAL_I_LESIONED": {},
        "BETRAYAL_I_SHAM": {},
    }
    deterministic_provenance = {}

    b1_topology, b1_provenance = build_betrayal_i(baseline)
    sham_topology, sham_provenance = build_sham(baseline)

    topologies = {
        "INTACT": baseline,
        "BETRAYAL_I_LESIONED": b1_topology,
        "BETRAYAL_I_SHAM": sham_topology,
    }
    deterministic_provenance["BETRAYAL_I_LESIONED"] = _jsonable(
        b1_provenance
    )
    deterministic_provenance["BETRAYAL_I_SHAM"] = _jsonable(
        sham_provenance
    )

    for arm in (
        "INTACT",
        "BETRAYAL_I_LESIONED",
        "BETRAYAL_I_SHAM",
    ):
        for layout in LAYOUTS:
            pair = []
            for replicate in (1, 2):
                result = run_episode(
                    topologies[arm],
                    retinal_indices,
                    dn_indices,
                    channel_positions,
                    stimuli[layout],
                )
                episodes.append(
                    {
                        "arm": arm,
                        "layout": layout,
                        "seed": -1,
                        "replicate": replicate,
                        "dn_indices": dn_indices,
                        "result": result,
                    }
                )
                pair.append(result)

            if not duplicate_exact(pair[0], pair[1]):
                refuse(
                    f"deterministic duplicate replay mismatch: "
                    f"{arm} / {layout}"
                )

            deterministic_first[arm][layout] = pair[0]

    cue_layout_reports = {
        layout: cue_transition_for_layout(
            deterministic_first["INTACT"][layout]
        )
        for layout in LAYOUTS
    }

    cue_status = classify_cue_transition(cue_layout_reports)

    b1_classification = classify_betrayal_i(
        deterministic_first["INTACT"],
        deterministic_first["BETRAYAL_I_LESIONED"],
        deterministic_first["BETRAYAL_I_SHAM"],
    )

    secondary = {
        arm: {
            layout: secondary_responder_summary(
                deterministic_first[arm][layout],
                dn_indices,
                responders,
            )
            for layout in LAYOUTS
        }
        for arm in (
            "INTACT",
            "BETRAYAL_I_LESIONED",
            "BETRAYAL_I_SHAM",
        )
    }

    randomized_reports = []
    failed_seeds = []
    exact_count = 0

    for seed in EXPECTED_SEEDS:
        try:
            (
                candidate,
                diagnostics,
                invariants,
                provenance,
            ) = build_betrayal_ii(
                baseline,
                transmitter,
                retinal_indices,
                seed=seed,
            )
        except Exception as exc:
            failed_seeds.append(
                {
                    "seed": int(seed),
                    "stage": "topology_build",
                    "error": repr(exc),
                }
            )
            continue

        seed_report = {
            "seed": int(seed),
            "diagnostics": _jsonable(diagnostics),
            "invariants": _jsonable(invariants),
            "provenance": _jsonable(provenance),
            "layouts": {},
        }

        seed_exact = True

        for layout in LAYOUTS:
            result = run_episode(
                candidate,
                retinal_indices,
                dn_indices,
                channel_positions,
                stimuli[layout],
            )
            episodes.append(
                {
                    "arm": "BETRAYAL_II_SHUFFLED",
                    "layout": layout,
                    "seed": int(seed),
                    "replicate": 1,
                    "dn_indices": dn_indices,
                    "result": result,
                }
            )

            comparison = exact_reproduction_against_intact(
                result,
                deterministic_first["INTACT"][layout],
            )
            seed_report["layouts"][layout] = comparison
            seed_exact = seed_exact and bool(
                comparison["exact_reproduction"]
            )

        seed_report["exact_reproduction_both_layouts"] = seed_exact
        exact_count += int(seed_exact)
        randomized_reports.append(seed_report)

        del candidate
        gc.collect()

    completed_seed_count = len(randomized_reports)
    b2_status = classify_betrayal_ii(
        exact_count,
        completed_seed_count,
    )

    complete = (
        completed_seed_count == 20
        and len(failed_seeds) == 0
        and len(episodes) == EXPECTED_EPISODE_COUNT
    )

    if complete:
        arrays = _episode_arrays(episodes)
        sidecar_sha = write_result_sidecar_atomic(arrays)
    else:
        sidecar_sha = None

    manifest = {
        "artifact": "sq05-two-betrayals-v1",
        "schema_version": "moscaquant.sq05-two-betrayals-result.v1",
        "status": (
            "COMPLETE_PREREGISTERED_RESULT"
            if complete
            else "INCOMPLETE_OR_INVALID"
        ),
        "canonical_parent": "SQ-05 — TWO BETRAYALS",
        "narrative": "TWO BETRAYALS",
        "execution_mode": "local",
        "authorization": _jsonable(auth),
        "provenance": deps,
        "financial_semantics_used": False,
        "single_overall_winner": None,
        "single_overall_winner_forbidden": True,
        "cue_transition": {
            "status": cue_status,
            "layouts": cue_layout_reports,
        },
        "betrayal_i": {
            **b1_classification,
            "provenance": deterministic_provenance,
            "secondary_accepted_nine": secondary,
        },
        "betrayal_ii": {
            "status": b2_status,
            "expected_seed_count": 20,
            "completed_seed_count": completed_seed_count,
            "failed_seeds": failed_seeds,
            "exact_reproduction_count": exact_count,
            "seed_reports": randomized_reports,
        },
        "sidecar": {
            "path": str(RESULT_NPZ),
            "sha256": sidecar_sha,
            "schema_sha256": EXPECTED_RESULT_SCHEMA_SHA256,
            "written": bool(complete),
        },
        "claim_boundaries": {
            "fruit_recognition": False,
            "hunger": False,
            "threat_perception": False,
            "fear": False,
            "behavior": False,
            "biological_causality": False,
            "financial_semantics": False,
        },
        "episode_count_expected": EXPECTED_EPISODE_COUNT,
        "episode_count_completed": len(episodes),
    }

    write_manifest_atomic(manifest)
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

    result = run_frozen()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
