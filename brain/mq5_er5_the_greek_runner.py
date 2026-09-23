from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tomllib
from collections import deque
from pathlib import Path

import numpy as np
from scipy import sparse

from config.paths import data_path
from brain.mq5_er_encoder import ARM_C, EncodingVariant
from brain.mq5_er_neural_runner import stimulus_list
from brain.mq5_er_real_artifact_verify import build_normalized_episode, sha256_array
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


CONFIG = Path("config/controls/mq5-er5-the-greek-v1.toml")
OUTPUT = data_path("experiments", "mq5-er5-the-greek-v1.json")
PARENT_RESULT = data_path("experiments", "mq5-er4-the-stevedores-v1.json")

EXPERIMENT_ID = "mq5-er5-the-greek-v1"
CODENAME = "THE GREEK"
FINANCIAL_SEMANTICS = "NOT ASSIGNED"

EXPECTED_PARENT_SHA256 = (
    "4de3cd6f52782908fc7afad853a5db0e0a1595923de1965c0b47606b5329f5dc"
)
EXPECTED_C_STIMULUS_SHA256 = (
    "e8af8077d7d4c13431f7ad3fa05d81e2009263d9a5cb0e7dd800e889ea61ec8a"
)

AFFECTED_TARGETS = (55, 92, 656, 126002, 137122)
RETAINED_TARGETS = (51, 129, 317, 1273)
ALL_TARGETS = (51, 55, 92, 129, 317, 656, 1273, 126002, 137122)

C13_ONSETS = {
    51: 150, 55: 145, 92: 141, 129: 149, 317: 156,
    656: 141, 1273: 149, 126002: 151, 137122: 151,
}

MAX_BACKWARD_HOPS = 3
TOP_K = 5
FOCUSED_MIN_AFFECTED_COVERAGE = 4

REQUIRED_TRACKED_FILES = (
    "config/controls/mq5-er5-the-greek-v1.toml",
    "docs/experiments/mq5-er5-the-greek-protocol.md",
    "brain/mq5_er5_the_greek_runner.py",
    "tests/test_mq5_er5_the_greek_runner_contract.py",
)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def git_status_porcelain() -> str:
    p = subprocess.run(
        ["git", "status", "--porcelain"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    if p.returncode != 0:
        raise RuntimeError("unable to inspect git status: " + p.stdout)
    return p.stdout


def git_head() -> str:
    p = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    if p.returncode != 0:
        raise RuntimeError("unable to determine git HEAD: " + p.stdout)
    return p.stdout.strip()


def load_protocol() -> dict:
    with CONFIG.open("rb") as f:
        return tomllib.load(f)


def validate_protocol(protocol: dict) -> None:
    if protocol["experiment_id"] != EXPERIMENT_ID:
        raise RuntimeError("experiment_id drift")
    if protocol["codename"] != CODENAME:
        raise RuntimeError("codename drift")
    if protocol["financial_semantics"] != FINANCIAL_SEMANTICS:
        raise RuntimeError("financial semantics drift")
    if int(protocol["frames"]) != EXPECTED_FRAMES:
        raise RuntimeError("frame-count drift")
    if tuple(protocol["affected_targets"]) != AFFECTED_TARGETS:
        raise RuntimeError("affected-target drift")
    if tuple(protocol["retained_dependency_comparisons"]) != RETAINED_TARGETS:
        raise RuntimeError("retained-target drift")
    if tuple(protocol["all_targets"]) != ALL_TARGETS:
        raise RuntimeError("all-target drift")
    if int(protocol["max_backward_hops"]) != MAX_BACKWARD_HOPS:
        raise RuntimeError("hop-depth drift")
    if int(protocol["top_k"]) != TOP_K:
        raise RuntimeError("top-k drift")
    if int(protocol["focused_min_affected_coverage"]) != FOCUSED_MIN_AFFECTED_COVERAGE:
        raise RuntimeError("focused-threshold drift")


def verify_parent_result() -> str:
    if not PARENT_RESULT.exists():
        raise RuntimeError(f"missing parent result: {PARENT_RESULT}")
    actual = sha256_file(PARENT_RESULT)
    if actual != EXPECTED_PARENT_SHA256:
        raise RuntimeError(f"parent result SHA mismatch: {actual}")
    return actual


def _lesion_exact_edge(matrix, pre: int, post: int, expected_weight: float):
    modified = matrix.tolil(copy=True)
    current = float(modified[int(post), int(pre)])
    if current == 0.0:
        raise RuntimeError(f"required edge absent: {pre}->{post}")
    if not np.isclose(current, expected_weight, rtol=1e-6, atol=1e-12):
        raise RuntimeError(
            f"edge-weight drift {pre}->{post}: {current} != {expected_weight}"
        )
    modified[int(post), int(pre)] = 0.0
    out = modified.tocsr()
    out.eliminate_zeros()
    out.sort_indices()
    return out


def load_c13():
    payload = load_frozen_causal_artifact()
    graph = sparse.load_npz(CONNECTOME).tocsr()
    graph.sum_duplicates()
    graph.sort_indices()

    retina_data = np.load(RETINA)
    retinal_indices = np.asarray(retina_data["neuron_index"], dtype=np.int32)
    responders = tuple(int(x) for x in frozen_responders(payload))

    c13 = graph
    for pre, post, weight in frozen_edges(payload):
        c13 = _lesion_exact_edge(c13, int(pre), int(post), float(weight))

    return graph, c13, retinal_indices, responders


def build_c_stimuli():
    episode = build_normalized_episode()
    stimuli = stimulus_list(episode, EncodingVariant(ARM_C))
    if len(stimuli) != EXPECTED_FRAMES:
        raise RuntimeError(f"expected {EXPECTED_FRAMES} frames, got {len(stimuli)}")
    sha = sha256_array(np.stack(stimuli, axis=0))
    if sha != EXPECTED_C_STIMULUS_SHA256:
        raise RuntimeError(f"Arm-C stimulus hash mismatch: {sha}")
    return stimuli, sha


def run_c13_trace(connectome, retinal_indices, responders, stimuli):
    runtime = PhysiologyConstrainedVisualTransductionRuntime(
        connectome=connectome,
        retinal_indices=retinal_indices,
        relay_artifact=RELAY,
        graded_artifact=GRADED,
        config=VisualTransductionConfig(release_gain=RELEASE_GAIN),
    )

    responder_indices = np.asarray(responders, dtype=np.int32)
    n_nodes = connectome.shape[0]

    respondent_voltage = np.empty(
        (len(stimuli), len(responders)),
        dtype=np.float64,
    )
    positive_activity = np.zeros(
        (len(stimuli), n_nodes),
        dtype=np.float32,
    )

    for frame, stimulus in enumerate(stimuli):
        runtime.step(stimulus)
        full = np.asarray(runtime.voltage, dtype=np.float64)
        respondent_voltage[frame] = full[responder_indices]
        positive_activity[frame] = np.clip(full, 0.0, None).astype(np.float32)

    onsets = {}
    for i, target in enumerate(responders):
        positive = np.flatnonzero(respondent_voltage[:, i] > 0.0)
        onsets[int(target)] = None if len(positive) == 0 else int(positive[0])

    return {
        "onsets": onsets,
        "positive_activity": positive_activity,
    }


def reverse_shortest_distances(graph: sparse.csr_matrix, target: int, max_hops: int):
    csc = graph.tocsc()
    distances = {int(target): 0}
    frontier = [int(target)]

    for depth in range(1, max_hops + 1):
        next_frontier = []
        for post in frontier:
            start, end = csc.indptr[post], csc.indptr[post + 1]
            pres = csc.indices[start:end]
            for pre in pres:
                pre = int(pre)
                if pre not in distances:
                    distances[pre] = depth
                    next_frontier.append(pre)
        frontier = next_frontier
        if not frontier:
            break

    distances.pop(int(target), None)
    return distances


def shortest_path_first_hops(
    graph: sparse.csr_matrix,
    candidate: int,
    target: int,
    max_hops: int,
) -> set[int]:
    # Frozen reference implementation retained for equivalence testing.
    if candidate == target:
        return set()

    csr = graph.tocsr()
    q = deque([(candidate, 0)])
    best_depth = None
    first_hops = set()
    seen_depth = {candidate: 0}

    while q:
        node, depth = q.popleft()
        if best_depth is not None and depth >= best_depth:
            continue
        if depth >= max_hops:
            continue

        row = csr[:, node].tocoo()
        posts = [int(x) for x in row.row]
        for post in posts:
            nd = depth + 1
            if post == target:
                best_depth = nd if best_depth is None else min(best_depth, nd)
                if depth == 0:
                    first_hops.add(post)
                else:
                    # recover first hop by searching direct children that can reach target
                    for child in posts if depth == 0 else []:
                        first_hops.add(int(child))
                continue

            prev = seen_depth.get(post)
            if prev is None or nd <= prev:
                seen_depth[post] = nd
                q.append((post, nd))

    if best_depth is None:
        return set()

    # Deterministic direct-child test for first-hop branches.
    start_nodes = []
    col = csr[:, candidate].tocoo()
    for child in sorted(int(x) for x in col.row):
        d = reverse_shortest_distances(csr, target, max_hops - 1).get(child)
        if d is not None and d + 1 == best_depth:
            start_nodes.append(child)
    return set(start_nodes)


def shortest_distances_to_target(
    graph: sparse.csr_matrix,
    target: int,
    max_hops: int,
) -> dict[int, int]:
    # Exact bounded shortest-path distances into target for the frozen orientation.
    csr = graph.tocsr()
    distances = {int(target): 0}
    frontier = [int(target)]

    for depth in range(1, max_hops + 1):
        next_frontier = []
        for post in frontier:
            start, end = csr.indptr[post], csr.indptr[post + 1]
            pres = csr.indices[start:end]
            for pre in pres:
                pre = int(pre)
                if pre not in distances:
                    distances[pre] = depth
                    next_frontier.append(pre)
        frontier = next_frontier
        if not frontier:
            break

    distances.pop(int(target), None)
    return distances


def build_first_hop_cache(
    graph: sparse.csr_matrix,
    targets: tuple[int, ...],
    max_hops: int,
):
    # Precompute data the frozen reference recomputes per candidate/target pair.
    csc = graph.tocsc()

    to_target = {
        int(target): shortest_distances_to_target(
            graph, int(target), max_hops
        )
        for target in targets
    }

    branch_masks: dict[int, dict[int, np.ndarray]] = {}
    n_nodes = graph.shape[0]

    for target in targets:
        reverse = reverse_shortest_distances(
            graph, int(target), max_hops - 1
        )
        masks: dict[int, np.ndarray] = {}
        for best_depth in range(1, max_hops + 1):
            wanted = best_depth - 1
            mask = np.zeros(n_nodes, dtype=np.bool_)
            matching = [
                int(node)
                for node, distance in reverse.items()
                if int(distance) == wanted
            ]
            if matching:
                mask[np.asarray(matching, dtype=np.int32)] = True
            masks[best_depth] = mask
        branch_masks[int(target)] = masks

    return csc, to_target, branch_masks


def shortest_path_first_hops_cached(
    csc: sparse.csc_matrix,
    candidate: int,
    target: int,
    *,
    to_target: dict[int, dict[int, int]],
    branch_masks: dict[int, dict[int, np.ndarray]],
) -> set[int]:
    if candidate == target:
        return set()

    best_depth = to_target[int(target)].get(int(candidate))
    if best_depth is None:
        return set()

    start, end = csc.indptr[int(candidate)], csc.indptr[int(candidate) + 1]
    children = csc.indices[start:end]
    if len(children) == 0:
        return set()

    mask = branch_masks[int(target)][int(best_depth)]
    selected = children[mask[children]]
    return {int(x) for x in selected}


def build_candidate_rows(graph, positive_activity):
    all_targets = AFFECTED_TARGETS + RETAINED_TARGETS
    distances = {
        int(target): reverse_shortest_distances(
            graph, int(target), MAX_BACKWARD_HOPS
        )
        for target in all_targets
    }

    first_hop_csc, first_hop_to_target, first_hop_branch_masks = (
        build_first_hop_cache(
            graph,
            AFFECTED_TARGETS,
            MAX_BACKWARD_HOPS,
        )
    )

    stevedore_nodes = {
        11725, 29921, 11345, 47350, 10647, 51642
    }
    excluded_nodes = set(ALL_TARGETS) | stevedore_nodes

    candidate_ids = set()
    for target in all_targets:
        candidate_ids.update(distances[target].keys())
    candidate_ids.difference_update(excluded_nodes)

    rows = []

    for node in sorted(candidate_ids):
        affected = []
        retained = []
        hop_signature = {}
        temporal_leads = []
        branch_nodes = set()

        node_trace = positive_activity[:, int(node)]
        pos = np.flatnonzero(node_trace > 0.0)
        node_onset = None if len(pos) == 0 else int(pos[0])
        if node_onset is None:
            continue

        latest_affected_onset = None

        for target in AFFECTED_TARGETS:
            hop = distances[int(target)].get(int(node))
            if hop is None:
                continue
            target_onset = C13_ONSETS[int(target)]
            if node_onset < target_onset:
                affected.append(int(target))
                hop_signature[str(target)] = int(hop)
                temporal_leads.append(int(target_onset - node_onset))
                latest_affected_onset = (
                    target_onset if latest_affected_onset is None
                    else max(latest_affected_onset, target_onset)
                )
                branch_nodes.update(
                    shortest_path_first_hops_cached(
                        first_hop_csc,
                        int(node),
                        int(target),
                        to_target=first_hop_to_target,
                        branch_masks=first_hop_branch_masks,
                    )
                )

        if not affected:
            continue

        for target in RETAINED_TARGETS:
            hop = distances[int(target)].get(int(node))
            if hop is None:
                continue
            target_onset = C13_ONSETS[int(target)]
            if node_onset < target_onset:
                retained.append(int(target))
                hop_signature[str(target)] = int(hop)

        integrated_positive = float(
            np.sum(
                node_trace[
                    : int(latest_affected_onset) + 1
                ],
                dtype=np.float64,
            )
        )

        rows.append(
            {
                "node": int(node),
                "affected_targets": affected,
                "affected_coverage": len(affected),
                "retained_targets": retained,
                "retained_coverage": len(retained),
                "hop_signature": hop_signature,
                "first_positive_frame": int(node_onset),
                "minimum_temporal_lead": int(min(temporal_leads)),
                "integrated_positive_activity": integrated_positive,
                "distinct_downstream_branches": len(branch_nodes),
            }
        )

    rows.sort(
        key=lambda r: (
            -int(r["affected_coverage"]),
            -int(r["distinct_downstream_branches"]),
            -int(r["minimum_temporal_lead"]),
            int(r["retained_coverage"]),
            max(
                int(r["hop_signature"][str(t)])
                for t in r["affected_targets"]
            ),
            int(r["node"]),
        )
    )
    return rows


def classify(rows: list[dict]) -> str:
    if any(
        int(row["affected_coverage"]) >= FOCUSED_MIN_AFFECTED_COVERAGE
        for row in rows
    ):
        return "GREEK_FOCUSED_COORDINATOR_CANDIDATE"

    top = rows[:TOP_K]
    covered = set()
    for row in top:
        covered.update(int(x) for x in row["affected_targets"])

    if len(top) >= 2 and set(AFFECTED_TARGETS).issubset(covered):
        return "GREEK_DISTRIBUTED_COORDINATOR_PATTERN"

    return "NO_CLEAR_GREEK_COORDINATOR"


def execution_gate(protocol: dict | None = None) -> str:
    protocol = load_protocol() if protocol is None else protocol
    validate_protocol(protocol)

    if not bool(protocol["result_execution_enabled"]):
        raise RuntimeError(
            "THE GREEK RESULT EXECUTION REFUSED: result_execution_enabled is false"
        )

    if git_status_porcelain().strip():
        raise RuntimeError(
            "THE GREEK RESULT EXECUTION REFUSED: working tree not clean"
        )

    p = subprocess.run(
        ["git", "ls-files", "--error-unmatch", *REQUIRED_TRACKED_FILES],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    if p.returncode != 0:
        raise RuntimeError(
            "THE GREEK RESULT EXECUTION REFUSED: required frozen files are not all tracked"
        )

    if OUTPUT.exists():
        raise RuntimeError(f"THE GREEK result artifact already exists: {OUTPUT}")

    return git_head()


def run_the_greek(*, authorize_result: bool) -> dict:
    protocol = load_protocol()
    validate_protocol(protocol)
    parent_sha = verify_parent_result()
    head = execution_gate(protocol) if authorize_result else git_head()

    original, c13, retina, responders = load_c13()
    stimuli, stim_sha = build_c_stimuli()
    trace = run_c13_trace(c13, retina, responders, stimuli)

    if trace["onsets"] != C13_ONSETS:
        raise RuntimeError(f"C13 replay onset mismatch: {trace['onsets']}")

    if not authorize_result:
        return {
            "experiment": EXPERIMENT_ID,
            "codename": CODENAME,
            "status": "KNOWN-REPLAY-VERIFIED",
            "git_head": head,
            "parent_result_sha256": parent_sha,
            "arm_c_stimulus_sha256": stim_sha,
            "c13_onsets": trace["onsets"],
            "result_execution": False,
            "financial_semantics": FINANCIAL_SEMANTICS,
        }

    rows = build_candidate_rows(
        c13,
        trace["positive_activity"],
    )
    top = rows[:TOP_K]
    classification = classify(rows)

    payload = {
        "experiment": EXPERIMENT_ID,
        "codename": CODENAME,
        "kind": "discovery",
        "status": "DISCOVERY ONLY",
        "git_head": head,
        "parent_result_sha256": parent_sha,
        "arm_c_stimulus_sha256": stim_sha,
        "max_backward_hops": MAX_BACKWARD_HOPS,
        "top_k": TOP_K,
        "focused_min_affected_coverage": FOCUSED_MIN_AFFECTED_COVERAGE,
        "classification": classification,
        "top_candidates": top,
        "eligible_candidate_count": len(rows),
        "causal_claims_authorized": False,
        "financial_semantics": FINANCIAL_SEMANTICS,
        "claim_limits": {
            "biological_identity_claimed": False,
            "causal_necessity_claimed": False,
            "causal_sufficiency_claimed": False,
            "cognition_claimed": False,
            "market_understanding_claimed": False,
            "trading_claimed": False,
            "predictive_value_claimed": False,
        },
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

    payload = run_the_greek(
        authorize_result=bool(args.run_frozen)
    )
    print(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
