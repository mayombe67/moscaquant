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

from brain.mq5_er_encoder import (
    ARM_C,
    EncodingVariant,
)
from brain.mq5_er_neural_runner import (
    stimulus_list,
)
from brain.mq5_er_real_artifact_verify import (
    build_normalized_episode,
    sha256_array,
)
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
from brain.visual_transduction import (
    VisualTransductionConfig,
)


CONFIG = Path(
    "config/controls/"
    "mq5-er5r-way-down-in-the-hole-v1.toml"
)

AUDIT_ARTIFACT = Path(
    "artifacts/audits/"
    "mq5-er5-greek-orientation-audit-v1.json"
)

OUTPUT = data_path(
    "experiments",
    "mq5-er5r-way-down-in-the-hole-v1.json",
)

EXPERIMENT_ID = (
    "mq5-er5r-way-down-in-the-hole-v1"
)

CODENAME = "WAY DOWN IN THE HOLE"

FINANCIAL_SEMANTICS = "NOT ASSIGNED"

EXPECTED_AUDIT_SHA256 = (
    "5e441e0027dd40363705ebcf914d5f3d53245efbde2bc91129cd8cbfac82b11f"
)

EXPECTED_C_STIMULUS_SHA256 = (
    "e8af8077d7d4c13431f7ad3fa05d81e2009263d9a5cb0e7dd800e889ea61ec8a"
)

AFFECTED_TARGETS = (
    55,
    92,
    656,
    126002,
    137122,
)

RETAINED_TARGETS = (
    51,
    129,
    317,
    1273,
)

ALL_TARGETS = (
    51,
    55,
    92,
    129,
    317,
    656,
    1273,
    126002,
    137122,
)

C13_ONSETS = {
    51: 150,
    55: 145,
    92: 141,
    129: 149,
    317: 156,
    656: 141,
    1273: 149,
    126002: 151,
    137122: 151,
}

MAX_BACKWARD_HOPS = 3
TOP_K = 5
FOCUSED_MIN_AFFECTED_COVERAGE = 4

#
# Same edge-hypothesis exclusion used by historical THE GREEK.
#
STEVEDORE_NODES = {
    11725,
    29921,
    11345,
    47350,
    10647,
    51642,
}

REQUIRED_TRACKED_FILES = (
    "config/controls/"
    "mq5-er5r-way-down-in-the-hole-v1.toml",
    "docs/experiments/"
    "mq5-er5r-way-down-in-the-hole-protocol.md",
    "brain/"
    "mq5_er5r_way_down_in_the_hole_runner.py",
    "tests/"
    "test_mq5_er5r_way_down_in_the_hole_runner.py",
)


class WayDownError(RuntimeError):
    pass


def sha256_file(
    path: Path,
) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for block in iter(
            lambda: handle.read(
                1024 * 1024
            ),
            b"",
        ):
            digest.update(block)

    return digest.hexdigest()


def git_head() -> str:
    completed = subprocess.run(
        [
            "git",
            "rev-parse",
            "HEAD",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )

    if completed.returncode != 0:
        raise WayDownError(
            "unable to determine git HEAD"
        )

    return completed.stdout.strip()


def git_status_porcelain() -> str:
    completed = subprocess.run(
        [
            "git",
            "status",
            "--porcelain",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )

    if completed.returncode != 0:
        raise WayDownError(
            "unable to inspect git status"
        )

    return completed.stdout


def load_protocol() -> dict:
    with CONFIG.open("rb") as handle:
        return tomllib.load(handle)


def validate_protocol(
    protocol: dict,
) -> None:
    if (
        protocol["experiment_id"]
        != EXPERIMENT_ID
    ):
        raise WayDownError(
            "experiment_id drift"
        )

    if (
        protocol["codename"]
        != CODENAME
    ):
        raise WayDownError(
            "codename drift"
        )

    if (
        protocol[
            "financial_semantics"
        ]
        != FINANCIAL_SEMANTICS
    ):
        raise WayDownError(
            "financial semantics drift"
        )

    if (
        int(protocol["frames"])
        != EXPECTED_FRAMES
    ):
        raise WayDownError(
            "frame-count drift"
        )

    if (
        tuple(
            protocol[
                "affected_targets"
            ]
        )
        != AFFECTED_TARGETS
    ):
        raise WayDownError(
            "affected-target drift"
        )

    if (
        tuple(
            protocol[
                "retained_dependency_comparisons"
            ]
        )
        != RETAINED_TARGETS
    ):
        raise WayDownError(
            "retained-target drift"
        )

    if (
        tuple(
            protocol[
                "all_targets"
            ]
        )
        != ALL_TARGETS
    ):
        raise WayDownError(
            "all-target drift"
        )

    if (
        int(
            protocol[
                "max_backward_hops"
            ]
        )
        != MAX_BACKWARD_HOPS
    ):
        raise WayDownError(
            "hop-depth drift"
        )

    if (
        int(protocol["top_k"])
        != TOP_K
    ):
        raise WayDownError(
            "top-k drift"
        )

    if (
        int(
            protocol[
                "focused_min_affected_coverage"
            ]
        )
        != FOCUSED_MIN_AFFECTED_COVERAGE
    ):
        raise WayDownError(
            "focused-threshold drift"
        )

    orientation = (
        protocol["orientation"]
    )

    if (
        orientation[
            "matrix_semantics"
        ]
        != "graph[post, pre] = pre -> post"
    ):
        raise WayDownError(
            "matrix-orientation drift"
        )

    if (
        orientation[
            "reverse_ancestry_storage"
        ]
        != "csr_rows"
    ):
        raise WayDownError(
            "reverse-ancestry drift"
        )

    if (
        bool(
            orientation[
                "csc_column_reverse_ancestry_allowed"
            ]
        )
    ):
        raise WayDownError(
            "CSC-column reverse ancestry "
            "must remain forbidden"
        )

    dynamic = (
        protocol["dynamic_readout"]
    )

    if (
        dynamic[
            "candidate_signal"
        ]
        != "positive_membrane_voltage"
    ):
        raise WayDownError(
            "candidate dynamic-readout drift"
        )

    if (
        float(
            dynamic[
                "positive_threshold"
            ]
        )
        != 0.0
    ):
        raise WayDownError(
            "positive threshold drift"
        )


def verify_audit() -> str:
    if not AUDIT_ARTIFACT.exists():
        raise WayDownError(
            "orientation audit artifact missing"
        )

    actual = sha256_file(
        AUDIT_ARTIFACT
    )

    if (
        actual
        != EXPECTED_AUDIT_SHA256
    ):
        raise WayDownError(
            "orientation audit SHA mismatch: "
            f"{actual}"
        )

    payload = json.loads(
        AUDIT_ARTIFACT.read_text(
            encoding="utf-8"
        )
    )

    if (
        payload["classification"]
        !=
        "GREEK_ORIENTATION_DEFECT_CONFIRMED_ALL_TOP5"
    ):
        raise WayDownError(
            "orientation audit "
            "classification drift"
        )

    return actual


def lesion_exact_edge(
    matrix: sparse.csr_matrix,
    pre: int,
    post: int,
    expected_weight: float,
) -> sparse.csr_matrix:
    modified = matrix.tolil(
        copy=True
    )

    current = float(
        modified[
            int(post),
            int(pre),
        ]
    )

    if current == 0.0:
        raise WayDownError(
            f"required C13 edge absent: "
            f"{pre}->{post}"
        )

    if not np.isclose(
        current,
        float(expected_weight),
        rtol=1e-6,
        atol=1e-12,
    ):
        raise WayDownError(
            f"C13 edge-weight drift "
            f"{pre}->{post}: "
            f"{current} != "
            f"{expected_weight}"
        )

    modified[
        int(post),
        int(pre),
    ] = 0.0

    result = modified.tocsr()
    result.eliminate_zeros()
    result.sort_indices()

    return result


def load_c13():
    payload = (
        load_frozen_causal_artifact()
    )

    graph = sparse.load_npz(
        CONNECTOME
    ).tocsr()

    graph.sum_duplicates()
    graph.sort_indices()

    retina_data = np.load(
        RETINA
    )

    retinal_indices = np.asarray(
        retina_data["neuron_index"],
        dtype=np.int32,
    )

    responders = tuple(
        int(x)
        for x
        in frozen_responders(
            payload
        )
    )

    c13 = graph

    for (
        pre,
        post,
        weight,
    ) in frozen_edges(payload):
        c13 = lesion_exact_edge(
            c13,
            int(pre),
            int(post),
            float(weight),
        )

    return (
        graph,
        c13,
        retinal_indices,
        responders,
    )


def build_c_stimuli():
    episode = (
        build_normalized_episode()
    )

    stimuli = stimulus_list(
        episode,
        EncodingVariant(
            ARM_C
        ),
    )

    if (
        len(stimuli)
        != EXPECTED_FRAMES
    ):
        raise WayDownError(
            "unexpected Arm-C "
            f"frame count: {len(stimuli)}"
        )

    actual = sha256_array(
        np.stack(
            stimuli,
            axis=0,
        )
    )

    if (
        actual
        != EXPECTED_C_STIMULUS_SHA256
    ):
        raise WayDownError(
            "Arm-C stimulus hash mismatch: "
            f"{actual}"
        )

    return stimuli, actual


def reverse_hop_map(
    graph: sparse.csr_matrix,
    target: int,
    max_hops: int = MAX_BACKWARD_HOPS,
) -> dict[int, int]:
    """
    Correct reverse ancestry under:

        graph[post, pre] = pre -> post

    CSR row target contains direct presynaptic predecessors.
    """

    result: dict[int, int] = {}

    seen = np.zeros(
        graph.shape[0],
        dtype=bool,
    )

    frontier = np.asarray(
        [int(target)],
        dtype=np.int32,
    )

    seen[frontier] = True

    for hop in range(
        1,
        int(max_hops) + 1,
    ):
        if frontier.size == 0:
            break

        block = graph[
            frontier
        ]

        predecessors = np.unique(
            block.indices.astype(
                np.int32,
                copy=False,
            )
        )

        if predecessors.size == 0:
            break

        new_predecessors = (
            predecessors[
                ~seen[
                    predecessors
                ]
            ]
        )

        for node in (
            new_predecessors.tolist()
        ):
            result[
                int(node)
            ] = int(hop)

        seen[
            predecessors
        ] = True

        frontier = (
            new_predecessors
        )

    return result


def shortest_path_first_hops(
    graph_csc: sparse.csc_matrix,
    *,
    candidate: int,
    target: int,
    ancestry: dict[int, int],
) -> set[int]:
    """
    Return immediate candidate successors that lie on a shortest directed path
    from candidate to target.

    CSC column candidate is correct here because graph[post, pre] means column
    `candidate` contains postsynaptic destinations of candidate output.
    """

    distance = ancestry.get(
        int(candidate)
    )

    if distance is None:
        return set()

    start = graph_csc.indptr[
        int(candidate)
    ]

    end = graph_csc.indptr[
        int(candidate) + 1
    ]

    children = graph_csc.indices[
        start:end
    ]

    if int(distance) == 1:
        if np.any(
            children == int(target)
        ):
            return {
                int(target)
            }

        raise WayDownError(
            "direct-hop ancestry "
            "inconsistent with graph"
        )

    required_child_distance = (
        int(distance) - 1
    )

    return {
        int(child)
        for child
        in children.tolist()
        if ancestry.get(
            int(child)
        )
        == required_child_distance
    }


def orientation_contract() -> None:
    #
    # graph[post, pre]
    #
    # 0 -> 1 -> 2 -> 3
    #
    graph = sparse.csr_matrix(
        (
            np.asarray(
                [
                    1.0,
                    1.0,
                    1.0,
                ],
                dtype=np.float32,
            ),
            (
                np.asarray(
                    [1, 2, 3],
                    dtype=np.int32,
                ),
                np.asarray(
                    [0, 1, 2],
                    dtype=np.int32,
                ),
            ),
        ),
        shape=(4, 4),
    )

    observed = reverse_hop_map(
        graph,
        target=2,
        max_hops=3,
    )

    expected = {
        1: 1,
        0: 2,
    }

    if observed != expected:
        raise WayDownError(
            "orientation contract failed: "
            f"{observed} != {expected}"
        )

    if 3 in observed:
        raise WayDownError(
            "orientation contract "
            "included downstream node"
        )


def run_c13_trace(
    connectome: sparse.csr_matrix,
    retinal_indices: np.ndarray,
    responders: tuple[int, ...],
    stimuli,
    *,
    capture_candidate_signal: bool,
):
    runtime = (
        PhysiologyConstrainedVisualTransductionRuntime(
            connectome=connectome,
            retinal_indices=retinal_indices,
            relay_artifact=RELAY,
            graded_artifact=GRADED,
            config=VisualTransductionConfig(
                release_gain=RELEASE_GAIN
            ),
        )
    )

    responder_indices = np.asarray(
        responders,
        dtype=np.int32,
    )

    responder_voltage = np.empty(
        (
            len(stimuli),
            len(responders),
        ),
        dtype=np.float64,
    )

    candidate_signal = None

    if capture_candidate_signal:
        candidate_signal = np.empty(
            (
                len(stimuli),
                connectome.shape[0],
            ),
            dtype=np.float32,
        )

    for (
        frame,
        stimulus,
    ) in enumerate(stimuli):
        runtime.step(
            stimulus
        )

        voltage = np.asarray(
            runtime.voltage,
            dtype=np.float64,
        )

        responder_voltage[
            frame
        ] = voltage[
            responder_indices
        ]

        if (
            candidate_signal
            is not None
        ):
            candidate_signal[
                frame
            ] = np.clip(
                voltage,
                0.0,
                None,
            ).astype(
                np.float32
            )

    onsets = {}

    for (
        index,
        target,
    ) in enumerate(responders):
        positive = np.flatnonzero(
            responder_voltage[
                :,
                index,
            ]
            > 0.0
        )

        onsets[
            int(target)
        ] = (
            None
            if positive.size == 0
            else int(
                positive[0]
            )
        )

    return {
        "onsets":
            onsets,
        "candidate_signal":
            candidate_signal,
    }


def build_candidate_rows(
    graph: sparse.csr_matrix,
    candidate_signal: np.ndarray,
) -> list[dict]:
    ancestry = {
        int(target):
            reverse_hop_map(
                graph,
                int(target),
                MAX_BACKWARD_HOPS,
            )
        for target
        in ALL_TARGETS
    }

    graph_csc = graph.tocsc()

    candidate_ids: set[int] = set()

    for target in ALL_TARGETS:
        candidate_ids.update(
            ancestry[
                int(target)
            ].keys()
        )

    excluded = (
        set(
            int(x)
            for x
            in ALL_TARGETS
        )
        | set(
            STEVEDORE_NODES
        )
    )

    candidate_ids.difference_update(
        excluded
    )

    rows: list[dict] = []

    for node in sorted(
        candidate_ids
    ):
        trace = candidate_signal[
            :,
            int(node),
        ]

        positive = np.flatnonzero(
            trace > 0.0
        )

        if positive.size == 0:
            continue

        node_onset = int(
            positive[0]
        )

        affected = []
        retained = []
        hops = {}
        temporal_leads = []
        branch_nodes: set[int] = set()

        latest_affected_onset = None

        for target in AFFECTED_TARGETS:
            hop = ancestry[
                int(target)
            ].get(
                int(node)
            )

            if hop is None:
                continue

            target_onset = (
                C13_ONSETS[
                    int(target)
                ]
            )

            if (
                node_onset
                >= target_onset
            ):
                continue

            affected.append(
                int(target)
            )

            hops[
                str(target)
            ] = int(hop)

            temporal_leads.append(
                int(
                    target_onset
                    - node_onset
                )
            )

            latest_affected_onset = (
                target_onset
                if (
                    latest_affected_onset
                    is None
                )
                else max(
                    latest_affected_onset,
                    target_onset,
                )
            )

            branch_nodes.update(
                shortest_path_first_hops(
                    graph_csc,
                    candidate=int(node),
                    target=int(target),
                    ancestry=ancestry[
                        int(target)
                    ],
                )
            )

        if not affected:
            continue

        for target in RETAINED_TARGETS:
            hop = ancestry[
                int(target)
            ].get(
                int(node)
            )

            if hop is None:
                continue

            target_onset = (
                C13_ONSETS[
                    int(target)
                ]
            )

            if (
                node_onset
                >= target_onset
            ):
                continue

            retained.append(
                int(target)
            )

            hops[
                str(target)
            ] = int(hop)

        integrated_positive = float(
            np.sum(
                trace[
                    :
                    int(
                        latest_affected_onset
                    )
                    + 1
                ],
                dtype=np.float64,
            )
        )

        rows.append(
            {
                "node":
                    int(node),
                "affected_targets":
                    affected,
                "affected_coverage":
                    len(
                        affected
                    ),
                "retained_targets":
                    retained,
                "retained_coverage":
                    len(
                        retained
                    ),
                "hop_signature":
                    hops,
                "first_positive_frame":
                    int(
                        node_onset
                    ),
                "minimum_temporal_lead":
                    int(
                        min(
                            temporal_leads
                        )
                    ),
                "integrated_positive_activity":
                    integrated_positive,
                "distinct_downstream_branches":
                    len(
                        branch_nodes
                    ),
            }
        )

    rows.sort(
        key=lambda row: (
            -int(
                row[
                    "affected_coverage"
                ]
            ),
            -int(
                row[
                    "distinct_downstream_branches"
                ]
            ),
            -int(
                row[
                    "minimum_temporal_lead"
                ]
            ),
            int(
                row[
                    "retained_coverage"
                ]
            ),
            max(
                int(
                    row[
                        "hop_signature"
                    ][str(target)]
                )
                for target
                in row[
                    "affected_targets"
                ]
            ),
            int(
                row["node"]
            ),
        )
    )

    return rows


def classify(
    rows: list[dict],
) -> str:
    if any(
        int(
            row[
                "affected_coverage"
            ]
        )
        >=
        FOCUSED_MIN_AFFECTED_COVERAGE
        for row in rows
    ):
        return (
            "GREEK_FOCUSED_"
            "COORDINATOR_CANDIDATE"
        )

    top = rows[
        :TOP_K
    ]

    covered: set[int] = set()

    for row in top:
        covered.update(
            int(x)
            for x
            in row[
                "affected_targets"
            ]
        )

    if (
        len(top) >= 2
        and set(
            AFFECTED_TARGETS
        ).issubset(
            covered
        )
    ):
        return (
            "GREEK_DISTRIBUTED_"
            "COORDINATOR_PATTERN"
        )

    return (
        "NO_CLEAR_GREEK_COORDINATOR"
    )


def verify_required_files_tracked():
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
        raise WayDownError(
            "required frozen files "
            "are not all tracked"
        )


def execution_gate(
    protocol: dict,
) -> str:
    validate_protocol(
        protocol
    )

    if not bool(
        protocol[
            "result_execution_enabled"
        ]
    ):
        raise WayDownError(
            "WAY DOWN IN THE HOLE "
            "RESULT EXECUTION REFUSED: "
            "result_execution_enabled "
            "is false"
        )

    if (
        git_status_porcelain().strip()
    ):
        raise WayDownError(
            "WAY DOWN IN THE HOLE "
            "RESULT EXECUTION REFUSED: "
            "working tree not clean"
        )

    verify_required_files_tracked()

    if OUTPUT.exists():
        raise WayDownError(
            "result artifact already "
            f"exists: {OUTPUT}"
        )

    verify_audit()
    orientation_contract()

    return git_head()


def verify_known_replay() -> dict:
    protocol = load_protocol()
    validate_protocol(
        protocol
    )

    audit_sha = verify_audit()

    orientation_contract()

    (
        _original,
        c13,
        retina,
        responders,
    ) = load_c13()

    if (
        tuple(responders)
        != ALL_TARGETS
    ):
        raise WayDownError(
            "frozen responder identity/order drift: "
            f"{responders}"
        )

    stimuli, stimulus_sha = (
        build_c_stimuli()
    )

    trace = run_c13_trace(
        c13,
        retina,
        responders,
        stimuli,
        capture_candidate_signal=False,
    )

    if (
        trace["onsets"]
        != C13_ONSETS
    ):
        raise WayDownError(
            "C13 onset mismatch: "
            f"{trace['onsets']}"
        )

    return {
        "experiment":
            EXPERIMENT_ID,
        "codename":
            CODENAME,
        "status":
            "KNOWN-REPLAY-VERIFIED",
        "result_execution":
            False,
        "candidate_discovery":
            False,
        "candidate_identities_exposed":
            False,
        "orientation_contract":
            "PASS",
        "orientation_audit_sha256":
            audit_sha,
        "arm_c_stimulus_sha256":
            stimulus_sha,
        "c13_onsets":
            trace["onsets"],
        "financial_semantics":
            FINANCIAL_SEMANTICS,
    }


def run_frozen() -> dict:
    protocol = load_protocol()

    head = execution_gate(
        protocol
    )

    audit_sha = verify_audit()

    (
        _original,
        c13,
        retina,
        responders,
    ) = load_c13()

    if (
        tuple(responders)
        != ALL_TARGETS
    ):
        raise WayDownError(
            "frozen responder identity/order drift"
        )

    stimuli, stimulus_sha = (
        build_c_stimuli()
    )

    trace = run_c13_trace(
        c13,
        retina,
        responders,
        stimuli,
        capture_candidate_signal=True,
    )

    if (
        trace["onsets"]
        != C13_ONSETS
    ):
        raise WayDownError(
            "C13 onset mismatch: "
            f"{trace['onsets']}"
        )

    candidate_signal = (
        trace[
            "candidate_signal"
        ]
    )

    if candidate_signal is None:
        raise WayDownError(
            "candidate signal "
            "was not captured"
        )

    rows = build_candidate_rows(
        c13,
        candidate_signal,
    )

    classification = classify(
        rows
    )

    top = rows[
        :TOP_K
    ]

    payload = {
        "experiment":
            EXPERIMENT_ID,
        "codename":
            CODENAME,
        "kind":
            "corrected_discovery",
        "status":
            "DISCOVERY ONLY",
        "git_head":
            head,
        "orientation_contract":
            "PASS",
        "orientation_audit_sha256":
            audit_sha,
        "arm_c_stimulus_sha256":
            stimulus_sha,
        "max_backward_hops":
            MAX_BACKWARD_HOPS,
        "top_k":
            TOP_K,
        "focused_min_affected_coverage":
            FOCUSED_MIN_AFFECTED_COVERAGE,
        "candidate_dynamic_readout":
            "positive_membrane_voltage",
        "classification":
            classification,
        "top_candidates":
            top,
        "eligible_candidate_count":
            len(
                rows
            ),
        "causal_claims_authorized":
            False,
        "financial_semantics":
            FINANCIAL_SEMANTICS,
        "historical_candidate_priority":
            False,
        "claim_limits": {
            "biological_identity_claimed":
                False,
            "causal_necessity_claimed":
                False,
            "causal_sufficiency_claimed":
                False,
            "cognition_claimed":
                False,
            "market_understanding_claimed":
                False,
            "trading_claimed":
                False,
            "predictive_value_claimed":
                False,
        },
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

    return payload


def main() -> None:
    parser = argparse.ArgumentParser()

    group = (
        parser.add_mutually_exclusive_group(
            required=True
        )
    )

    group.add_argument(
        "--verify-known-replay",
        action="store_true",
    )

    group.add_argument(
        "--run-frozen",
        action="store_true",
    )

    args = parser.parse_args()

    if args.verify_known_replay:
        payload = verify_known_replay()
    else:
        payload = run_frozen()

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
