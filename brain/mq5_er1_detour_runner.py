from __future__ import annotations

import argparse
import hashlib
import heapq
import json
import os
import subprocess
import tempfile
import tomllib
from pathlib import Path

import numpy as np
from scipy import sparse

from brain.mq5_er_encoder import ARM_A, ARM_C, EncodingVariant
from brain.mq5_er_neural_runner import stimulus_list
from brain.mq5_er_real_artifact_verify import (
    build_normalized_episode,
    sha256_array,
)
from brain.mq5_ts_metrics import first_positive_onsets
from brain.mq5_ts_runtime import (
    CONNECTOME,
    RETINA,
    RELAY,
    GRADED,
    RELEASE_GAIN,
    frozen_edges,
    frozen_responders,
    lesion_frozen_edges,
)
from brain.physiology_constrained_visual_transduction import (
    PhysiologyConstrainedVisualTransductionRuntime,
)
from brain.visual_transduction import VisualTransductionConfig
from config.paths import data_path


CONFIG = Path("config/controls/mq5-er1-detour-v1.toml")
PARENT_RESULT = data_path(
    "experiments",
    "mq5-er-encoding-robustness-v1.json",
)
OUTPUT = data_path(
    "experiments",
    "mq5-er1-detour-v1.json",
)

EXPECTED_PARENT_SHA256 = (
    "737a316a98d91b95dc1a5fe3ac25e7bf229447ae422ecd23ecf39ea8d4f6bb39"
)
EXPECTED_A_STIMULUS_SHA256 = (
    "9c06a18293dd7dd27b1a1717785e2da25518d4b0081e5266794c3166a3f471e9"
)
EXPECTED_C_STIMULUS_SHA256 = (
    "e8af8077d7d4c13431f7ad3fa05d81e2009263d9a5cb0e7dd800e889ea61ec8a"
)

AFFECTED_TARGETS = (55, 92, 656, 126002, 137122)
RETAINED_TARGETS = (51, 129, 317, 1273)
ALL_TRACE_TARGETS = tuple(sorted(AFFECTED_TARGETS + RETAINED_TARGETS))

# Parent MQ-5.ER Arm-C first-positive onsets. These are already observed/frozen
# facts from the parent experiment and define DETOUR's temporal windows.
C_BASELINE_ONSETS = {
    51: 148,
    55: 145,
    92: 141,
    129: 148,
    317: 153,
    656: 141,
    1273: 144,
    126002: 151,
    137122: 151,
}

A_BASELINE_ONSETS = {
    51: 149,
    55: 146,
    92: 145,
    129: 148,
    317: 147,
    656: 145,
    1273: 147,
    126002: 147,
    137122: 146,
}

MAX_BACKWARD_HOPS = 3
TOP_K_PER_TARGET = 5
ACTIVITY_EPSILON = 1e-12
FOCUSED_MIN_TARGETS = 3


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load_config() -> dict:
    with CONFIG.open("rb") as handle:
        return tomllib.load(handle)


def git_status_porcelain() -> str:
    completed = subprocess.run(
        ["git", "status", "--porcelain"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stdout)
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
        raise RuntimeError(completed.stdout)
    return completed.stdout.strip()


def load_parent_result() -> dict:
    actual = sha256_file(PARENT_RESULT)
    if actual != EXPECTED_PARENT_SHA256:
        raise RuntimeError(
            f"parent MQ-5.ER result SHA mismatch: {actual}"
        )
    return json.loads(PARENT_RESULT.read_text(encoding="utf-8"))


def load_inputs():
    original = sparse.load_npz(CONNECTOME).tocsr()
    original.sum_duplicates()
    original.sort_indices()

    retina_data = np.load(RETINA)
    retinal_indices = np.asarray(
        retina_data["neuron_index"],
        dtype=np.int32,
    )
    responders = frozen_responders()
    edges = frozen_edges()
    lesioned = lesion_frozen_edges(original, edges)

    return original, lesioned, retinal_indices, responders, edges


def build_stimuli():
    episode = build_normalized_episode()

    a = stimulus_list(
        episode,
        EncodingVariant(ARM_A),
    )
    c = stimulus_list(
        episode,
        EncodingVariant(ARM_C),
    )

    a_sha = sha256_array(np.stack(a, axis=0))
    c_sha = sha256_array(np.stack(c, axis=0))

    if a_sha != EXPECTED_A_STIMULUS_SHA256:
        raise RuntimeError(f"Arm A stimulus hash mismatch: {a_sha}")
    if c_sha != EXPECTED_C_STIMULUS_SHA256:
        raise RuntimeError(f"Arm C stimulus hash mismatch: {c_sha}")

    return a, c, a_sha, c_sha


class ActivityCapture:
    def __init__(
        self,
        *,
        mode: str,
        population_size: int,
        memmap=None,
        reference_memmap=None,
        snapshot_frames=(),
    ):
        self.mode = str(mode)
        self.population_size = int(population_size)
        self.memmap = memmap
        self.reference_memmap = reference_memmap
        self.snapshot_frames = {int(x) for x in snapshot_frames}
        self.frame = 0
        self.accumulator = np.zeros(
            self.population_size,
            dtype=np.float64,
        )
        self.snapshots: dict[int, np.ndarray] = {}

    def __call__(self, activity, synaptic):
        activity = np.asarray(activity, dtype=np.float32)

        if self.mode == "write":
            self.memmap[self.frame] = activity

        elif self.mode == "difference":
            reference = np.asarray(
                self.reference_memmap[self.frame],
                dtype=np.float32,
            )
            self.accumulator += np.abs(
                activity.astype(np.float64)
                - reference.astype(np.float64)
            )

        elif self.mode == "absolute":
            self.accumulator += np.abs(
                activity.astype(np.float64)
            )

        else:
            raise RuntimeError(f"unsupported capture mode: {self.mode}")

        if (
            self.mode in {"difference", "absolute"}
            and self.frame in self.snapshot_frames
        ):
            self.snapshots[self.frame] = self.accumulator.copy()

        self.frame += 1
        return synaptic


def run_condition(
    *,
    connectome,
    retinal_indices,
    responders,
    stimuli,
    capture: ActivityCapture,
):
    runtime = PhysiologyConstrainedVisualTransductionRuntime(
        connectome=connectome,
        retinal_indices=retinal_indices,
        relay_artifact=RELAY,
        graded_artifact=GRADED,
        config=VisualTransductionConfig(
            release_gain=RELEASE_GAIN,
        ),
        synaptic_modifier=capture,
    )

    voltage = np.empty(
        (len(stimuli), len(responders)),
        dtype=np.float64,
    )

    for frame, stimulus in enumerate(stimuli):
        runtime.step(stimulus)
        voltage[frame] = np.asarray(
            runtime.voltage[responders],
            dtype=np.float64,
        )

    onsets = first_positive_onsets(
        voltage,
        responders,
    )

    return {
        "onsets": {
            int(k): (
                None if v is None else int(v)
            )
            for k, v in onsets.items()
        },
        "voltage": voltage,
    }


def verify_known_replay(
    *,
    original,
    lesioned,
    retinal_indices,
    responders,
    a_stimuli,
    c_stimuli,
    scratch_dir: Path,
):
    unique_onsets = tuple(
        sorted(set(C_BASELINE_ONSETS.values()))
    )

    mmap_path = scratch_dir / "detour-a-activity.f32"
    population_size = int(original.shape[0])

    a_activity = np.memmap(
        mmap_path,
        dtype=np.float32,
        mode="w+",
        shape=(len(a_stimuli), population_size),
    )

    a_capture = ActivityCapture(
        mode="write",
        population_size=population_size,
        memmap=a_activity,
    )
    a_result = run_condition(
        connectome=original,
        retinal_indices=retinal_indices,
        responders=responders,
        stimuli=a_stimuli,
        capture=a_capture,
    )
    a_activity.flush()

    if a_result["onsets"] != A_BASELINE_ONSETS:
        raise RuntimeError(
            f"Arm A replay onset mismatch: {a_result['onsets']}"
        )

    c_capture = ActivityCapture(
        mode="difference",
        population_size=population_size,
        reference_memmap=a_activity,
        snapshot_frames=unique_onsets,
    )
    c_result = run_condition(
        connectome=original,
        retinal_indices=retinal_indices,
        responders=responders,
        stimuli=c_stimuli,
        capture=c_capture,
    )

    if c_result["onsets"] != C_BASELINE_ONSETS:
        raise RuntimeError(
            f"Arm C replay onset mismatch: {c_result['onsets']}"
        )

    lesion_capture = ActivityCapture(
        mode="absolute",
        population_size=population_size,
        snapshot_frames=unique_onsets,
    )
    lesion_result = run_condition(
        connectome=lesioned,
        retinal_indices=retinal_indices,
        responders=responders,
        stimuli=c_stimuli,
        capture=lesion_capture,
    )

    return {
        "a_result": a_result,
        "c_result": c_result,
        "lesion_result": lesion_result,
        "divergence_snapshots": c_capture.snapshots,
        "lesion_snapshots": lesion_capture.snapshots,
    }


def _push_top_candidate(heap, row):
    # Min-heap keeping only the best TOP_K_PER_TARGET rows.
    key = (
        float(row["score"]),
        -int(row["hop_from_target"]),
        -int(row["postsynaptic"]),
        -int(row["presynaptic"]),
    )
    item = (key, row)

    if len(heap) < TOP_K_PER_TARGET:
        heapq.heappush(heap, item)
        return

    if item[0] > heap[0][0]:
        heapq.heapreplace(heap, item)


def score_target_streaming(
    *,
    original: sparse.csr_matrix,
    lesioned_edges: set[tuple[int, int]],
    target: int,
    onset: int,
    divergence_snapshot: np.ndarray,
    lesion_snapshot: np.ndarray,
    max_backward_hops: int = MAX_BACKWARD_HOPS,
):
    frontier = np.asarray([int(target)], dtype=np.int32)
    visited_posts: set[int] = set()
    heap = []
    edge_visits = 0

    for hop in range(1, int(max_backward_hops) + 1):
        next_nodes = []

        for post_raw in frontier:
            post = int(post_raw)
            if post in visited_posts:
                continue
            visited_posts.add(post)

            start = int(original.indptr[post])
            stop = int(original.indptr[post + 1])
            if stop <= start:
                continue

            pres = original.indices[start:stop].astype(
                np.int32,
                copy=False,
            )
            weights = original.data[start:stop].astype(
                np.float64,
                copy=False,
            )
            edge_visits += int(stop - start)

            enc = (
                np.abs(weights)
                * divergence_snapshot[pres]
            )
            lesion_part = (
                np.abs(weights)
                * lesion_snapshot[pres]
            )

            if lesioned_edges:
                mask_lesioned = np.fromiter(
                    (
                        (int(pre), post) in lesioned_edges
                        for pre in pres
                    ),
                    dtype=bool,
                    count=len(pres),
                )
                lesion_part[mask_lesioned] = 0.0

            eligible = np.flatnonzero(
                (enc > ACTIVITY_EPSILON)
                & (lesion_part > ACTIVITY_EPSILON)
            )

            if eligible.size:
                scores = enc[eligible] * lesion_part[eligible]

                if eligible.size > TOP_K_PER_TARGET:
                    take = np.argpartition(
                        scores,
                        -TOP_K_PER_TARGET,
                    )[-TOP_K_PER_TARGET:]
                    eligible = eligible[take]
                    scores = scores[take]

                for local_idx, score in zip(
                    eligible.tolist(),
                    scores.tolist(),
                ):
                    pre = int(pres[int(local_idx)])
                    row = {
                        "target": int(target),
                        "presynaptic": pre,
                        "postsynaptic": post,
                        "hop_from_target": int(hop),
                        "onset_frame": int(onset),
                        "encoding_divergence_l1": float(
                            enc[int(local_idx)]
                        ),
                        "lesion_persistence_l1": float(
                            lesion_part[int(local_idx)]
                        ),
                        "score": float(score),
                    }
                    _push_top_candidate(heap, row)

            next_nodes.extend(int(x) for x in pres)

        if not next_nodes:
            break

        frontier = np.unique(
            np.asarray(next_nodes, dtype=np.int32)
        )

    rows = [item[1] for item in heap]
    rows.sort(
        key=lambda row: (
            -float(row["score"]),
            int(row["hop_from_target"]),
            int(row["postsynaptic"]),
            int(row["presynaptic"]),
        )
    )

    return {
        "target": int(target),
        "onset": int(onset),
        "edge_visits": int(edge_visits),
        "top_candidates": rows,
    }


def classify_family(by_target: dict[int, dict]) -> str:
    all_rows = [
        row
        for target in AFFECTED_TARGETS
        for row in by_target[int(target)]["top_candidates"]
    ]

    if not all_rows:
        return "NO_CLEAR_DETOUR_CANDIDATES"

    recurrence: dict[tuple[int, int], set[int]] = {}

    for row in all_rows:
        edge = (
            int(row["presynaptic"]),
            int(row["postsynaptic"]),
        )
        recurrence.setdefault(edge, set()).add(
            int(row["target"])
        )

    if any(
        len(targets) >= FOCUSED_MIN_TARGETS
        for targets in recurrence.values()
    ):
        return "FOCUSED_DETOUR_CANDIDATES"

    return "DIFFUSE_DETOUR_CANDIDATES"


def execution_gate(protocol: dict) -> str:
    if not protocol["execution"]["result_execution_enabled"]:
        raise RuntimeError(
            "MQ-5.ER.1 DETOUR RESULT EXECUTION REFUSED: "
            "result_execution_enabled is false"
        )

    if not protocol["candidate_scope"]["ranking_rule_frozen"]:
        raise RuntimeError("DETOUR ranking rule not frozen")
    if not protocol["candidate_scope"]["candidate_cap_frozen"]:
        raise RuntimeError("DETOUR candidate cap not frozen")
    if not protocol["candidate_scope"]["tie_rule_frozen"]:
        raise RuntimeError("DETOUR tie rule not frozen")
    if not protocol["classification"]["thresholds_frozen"]:
        raise RuntimeError("DETOUR classification thresholds not frozen")

    if git_status_porcelain().strip():
        raise RuntimeError(
            "DETOUR RESULT EXECUTION REFUSED: working tree not clean"
        )

    if OUTPUT.exists():
        raise RuntimeError(
            f"DETOUR result artifact already exists: {OUTPUT}"
        )

    return git_head()


def run_detour(*, authorize_result: bool) -> dict:
    parent = load_parent_result()
    del parent  # hash verification is the required parent gate here.

    protocol = load_config()

    if authorize_result:
        head = execution_gate(protocol)
    else:
        head = git_head()

    original, lesioned, retina, responders, causal_edges = load_inputs()
    a_stimuli, c_stimuli, a_sha, c_sha = build_stimuli()

    with tempfile.TemporaryDirectory(
        prefix="mq5-er1-detour-"
    ) as temp:
        replay = verify_known_replay(
            original=original,
            lesioned=lesioned,
            retinal_indices=retina,
            responders=responders,
            a_stimuli=a_stimuli,
            c_stimuli=c_stimuli,
            scratch_dir=Path(temp),
        )

        if not authorize_result:
            return {
                "status": "KNOWN-REPLAY-VERIFIED",
                "git_head": head,
                "arm_a_stimulus_sha256": a_sha,
                "arm_c_stimulus_sha256": c_sha,
                "arm_a_onsets": replay["a_result"]["onsets"],
                "arm_c_onsets": replay["c_result"]["onsets"],
                "result_execution": False,
            }

        lesioned_edge_set = {
            (int(pre), int(post))
            for pre, post, _weight in causal_edges
        }

        by_target = {}

        for target in ALL_TRACE_TARGETS:
            onset = C_BASELINE_ONSETS[int(target)]
            by_target[int(target)] = score_target_streaming(
                original=original,
                lesioned_edges=lesioned_edge_set,
                target=int(target),
                onset=int(onset),
                divergence_snapshot=replay[
                    "divergence_snapshots"
                ][int(onset)],
                lesion_snapshot=replay[
                    "lesion_snapshots"
                ][int(onset)],
            )

        classification = classify_family(by_target)

        payload = {
            "experiment": "mq5-er1-detour-v1",
            "codename": "DETOUR",
            "status": "DISCOVERY ONLY",
            "git_head": head,
            "parent_result_sha256": EXPECTED_PARENT_SHA256,
            "arm_a_stimulus_sha256": a_sha,
            "arm_c_stimulus_sha256": c_sha,
            "max_backward_hops": MAX_BACKWARD_HOPS,
            "top_k_per_target": TOP_K_PER_TARGET,
            "affected_targets": list(AFFECTED_TARGETS),
            "retained_dependency_targets": list(RETAINED_TARGETS),
            "classification": classification,
            "targets": {
                str(k): v
                for k, v in sorted(by_target.items())
            },
            "causal_claims_authorized": False,
            "required_followup": "mq5-er2-roadblock",
            "financial_semantics": "NOT ASSIGNED",
        }

        OUTPUT.parent.mkdir(
            parents=True,
            exist_ok=True,
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

        payload["result_artifact"] = str(OUTPUT)
        payload["result_sha256"] = sha256_file(OUTPUT)
        return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--verify-known-replay",
        action="store_true",
    )
    group.add_argument(
        "--run-frozen",
        action="store_true",
    )
    args = parser.parse_args()

    payload = run_detour(
        authorize_result=bool(args.run_frozen),
    )

    print(json.dumps(
        payload,
        indent=2,
        sort_keys=True,
        allow_nan=False,
    ))


if __name__ == "__main__":
    main()
