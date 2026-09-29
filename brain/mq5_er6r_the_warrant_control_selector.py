from __future__ import annotations

import tomllib

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy import sparse

from brain.mq5_ts_runtime import (
    CONNECTOME,
    RETINA,
    RELAY,
    GRADED,
    frozen_edges,
    load_frozen_causal_artifact,
)


OUTPUT = Path(
    "artifacts/"
    "mq5-er6r-the-warrant-matched-control-v1.json"
)

CONTROL_SELECTION_AUTHORIZATION = Path(
    "config/controls/"
    "mq5-er6r-the-warrant-control-selection-authorization-v1.json"
)

SELECTOR_QUALIFICATION = Path(
    "artifacts/qualification/"
    "mq5-er6r-the-warrant-selector-qualification-v2.json"
)


CANDIDATE = 1952

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

MAX_HOPS = 3

#
# Already-nominated WAY DOWN candidates are hypotheses, not controls.
#
WAY_DOWN_TOP5 = (
    1952,
    1963,
    2641,
    1944,
    23640,
)

#
# Do not recycle previously investigated ER.1-ER.4 entities as the matched
# neutral node control.
#
PRIOR_HYPOTHESIS_NODES = {
    116680,
    12024,
    78481,
    16087,
    11725,
    29921,
    11345,
    47350,
    10647,
    51642,
}

#
# Structural signature recorded in the sealed corrected WAY DOWN result.
# This is used as an integrity check, not as a post-WARRANT target-selection
# mechanism.
#
EXPECTED_1952_HOPS = {
    51: 2,
    55: 3,
    92: 2,
    129: 3,
    317: 3,
    656: 2,
    1273: 2,
    126002: 3,
    137122: 2,
}


class ControlSelectionError(
    RuntimeError
):
    pass


def sha256_bytes(
    payload: bytes,
) -> str:
    return hashlib.sha256(
        payload
    ).hexdigest()


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
        raise ControlSelectionError(
            f"required C13 edge absent: "
            f"{pre}->{post}"
        )

    if not np.isclose(
        current,
        float(expected_weight),
        rtol=1e-6,
        atol=1e-12,
    ):
        raise ControlSelectionError(
            f"C13 edge-weight drift "
            f"{pre}->{post}: "
            f"{current} != {expected_weight}"
        )

    modified[
        int(post),
        int(pre),
    ] = 0.0

    result = modified.tocsr()
    result.eliminate_zeros()
    result.sort_indices()

    return result


def load_c13() -> sparse.csr_matrix:
    payload = (
        load_frozen_causal_artifact()
    )

    graph = sparse.load_npz(
        CONNECTOME
    ).tocsr()

    graph.sum_duplicates()
    graph.sort_indices()

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

    return c13


def reverse_hop_array(
    graph: sparse.csr_matrix,
    target: int,
    max_hops: int,
) -> np.ndarray:
    """
    Return bounded structural distance from every presynaptic ancestor into
    target. -1 means target is not reached within max_hops.

    Matrix orientation is graph[post, pre].
    """

    distances = np.full(
        graph.shape[0],
        -1,
        dtype=np.int8,
    )

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

        pres = np.unique(
            block.indices.astype(
                np.int32,
                copy=False,
            )
        )

        if pres.size == 0:
            break

        new_pres = pres[
            ~seen[pres]
        ]

        distances[
            new_pres
        ] = int(hop)

        seen[new_pres] = True
        frontier = new_pres

    return distances


def population_mask(
    path: Path,
    n_nodes: int,
) -> np.ndarray:
    data = np.load(path)

    indices = np.asarray(
        data["neuron_index"],
        dtype=np.int64,
    )

    mask = np.zeros(
        n_nodes,
        dtype=bool,
    )

    mask[indices] = True

    return mask


def node_profiles(
    graph: sparse.csr_matrix,
):
    #
    # graph[post, pre]
    #
    indegree = np.diff(
        graph.indptr
    ).astype(np.int64)

    csc = graph.tocsc()

    outdegree = np.diff(
        csc.indptr
    ).astype(np.int64)

    abs_graph = abs(graph)

    incoming_abs = np.asarray(
        abs_graph.sum(axis=1)
    ).ravel().astype(np.float64)

    outgoing_abs = np.asarray(
        abs_graph.sum(axis=0)
    ).ravel().astype(np.float64)

    return (
        indegree,
        outdegree,
        incoming_abs,
        outgoing_abs,
    )


def safe_log_distance(
    a: float,
    b: float,
) -> float:
    return abs(
        np.log10(
            float(a) + 1.0
        )
        - np.log10(
            float(b) + 1.0
        )
    )


def hop_signature(
    node: int,
    hop_arrays: dict[
        int,
        np.ndarray,
    ],
) -> tuple[int, ...]:
    #
    # Missing within MAX_HOPS is encoded as MAX_HOPS + 1 for deterministic
    # distance comparison.
    #
    return tuple(
        (
            int(
                hop_arrays[
                    int(target)
                ][int(node)]
            )
            if (
                int(
                    hop_arrays[
                        int(target)
                    ][int(node)]
                )
                >= 0
            )
            else MAX_HOPS + 1
        )
        for target
        in ALL_TARGETS
    )


def rank_key(
    *,
    node: int,
    candidate_signature:
        tuple[int, ...],
    control_signature:
        tuple[int, ...],
    indegree: np.ndarray,
    outdegree: np.ndarray,
    incoming_abs: np.ndarray,
    outgoing_abs: np.ndarray,
):
    hop_delta = tuple(
        abs(
            int(a)
            - int(b)
        )
        for a, b
        in zip(
            candidate_signature,
            control_signature,
        )
    )

    hop_mismatch_count = sum(
        int(delta != 0)
        for delta in hop_delta
    )

    hop_l1 = sum(
        hop_delta
    )

    d_in_degree = (
        safe_log_distance(
            indegree[node],
            indegree[CANDIDATE],
        )
    )

    d_out_degree = (
        safe_log_distance(
            outdegree[node],
            outdegree[CANDIDATE],
        )
    )

    d_in_weight = (
        safe_log_distance(
            incoming_abs[node],
            incoming_abs[CANDIDATE],
        )
    )

    d_out_weight = (
        safe_log_distance(
            outgoing_abs[node],
            outgoing_abs[CANDIDATE],
        )
    )

    structural = (
        d_in_degree,
        d_out_degree,
        d_in_weight,
        d_out_weight,
    )

    return (
        int(
            hop_mismatch_count
        ),
        int(hop_l1),
        float(max(structural)),
        float(sum(structural)),
        float(d_in_degree),
        float(d_out_degree),
        float(d_in_weight),
        float(d_out_weight),
        int(node),
    )


def build_payload() -> dict:
    graph = load_c13()

    n_nodes = int(
        graph.shape[0]
    )

    if CANDIDATE >= n_nodes:
        raise ControlSelectionError(
            "candidate outside graph"
        )

    (
        indegree,
        outdegree,
        incoming_abs,
        outgoing_abs,
    ) = node_profiles(graph)

    hop_arrays = {
        int(target):
            reverse_hop_array(
                graph,
                int(target),
                MAX_HOPS,
            )
        for target
        in ALL_TARGETS
    }

    candidate_signature = (
        hop_signature(
            CANDIDATE,
            hop_arrays,
        )
    )

    expected_signature = tuple(
        int(
            EXPECTED_1952_HOPS[
                int(target)
            ]
        )
        for target
        in ALL_TARGETS
    )

    if (
        candidate_signature
        != expected_signature
    ):
        raise ControlSelectionError(
            "1952 frozen structural "
            "hop-signature drift: "
            f"{candidate_signature} "
            f"!= {expected_signature}"
        )

    retina = population_mask(
        RETINA,
        n_nodes,
    )

    relay = population_mask(
        RELAY,
        n_nodes,
    )

    graded = population_mask(
        GRADED,
        n_nodes,
    )

    candidate_class = (
        bool(
            retina[CANDIDATE]
        ),
        bool(
            relay[CANDIDATE]
        ),
        bool(
            graded[CANDIDATE]
        ),
    )

    forbidden = (
        set(
            int(x)
            for x
            in ALL_TARGETS
        )
        | set(WAY_DOWN_TOP5)
        | set(
            PRIOR_HYPOTHESIS_NODES
        )
    )

    eligible = []

    for node in range(
        n_nodes
    ):
        if node in forbidden:
            continue

        #
        # Match special frozen runtime class exactly.
        #
        control_class = (
            bool(retina[node]),
            bool(relay[node]),
            bool(graded[node]),
        )

        if (
            control_class
            != candidate_class
        ):
            continue

        signature = hop_signature(
            node,
            hop_arrays,
        )

        #
        # Require the same frozen structural coverage:
        # all five affected and all four retained responders are reachable
        # within the same corrected <=3-hop universe used by WAY DOWN IN THE HOLE.
        #
        affected_reach = sum(
            int(
                hop_arrays[
                    int(target)
                ][node]
                >= 0
            )
            for target
            in AFFECTED_TARGETS
        )

        retained_reach = sum(
            int(
                hop_arrays[
                    int(target)
                ][node]
                >= 0
            )
            for target
            in RETAINED_TARGETS
        )

        if (
            affected_reach != 5
            or retained_reach != 4
        ):
            continue

        key = rank_key(
            node=node,
            candidate_signature=(
                candidate_signature
            ),
            control_signature=(
                signature
            ),
            indegree=indegree,
            outdegree=outdegree,
            incoming_abs=incoming_abs,
            outgoing_abs=outgoing_abs,
        )

        eligible.append(
            (
                key,
                int(node),
                signature,
            )
        )

    if not eligible:
        raise ControlSelectionError(
            "no structurally eligible "
            "matched-control node; "
            "do not relax selection "
            "post hoc"
        )

    eligible.sort(
        key=lambda item:
            item[0]
    )

    (
        selected_key,
        selected_node,
        selected_signature,
    ) = eligible[0]

    exact_hop_matches = sum(
        int(
            signature
            == candidate_signature
        )
        for _key, _node, signature
        in eligible
    )

    payload = {
        "schema_version":
            (
                "moscaquant."
                "mq5-er6r-the-warrant-"
                "matched-control/v1"
            ),
        "experiment":
            "mq5-er6r-the-warrant-v1",
        "codename":
            "THE WARRANT",
        "kind":
            (
                "PRE-OUTCOME "
                "STRUCTURAL NODE "
                "CONTROL SELECTION"
            ),
        "neural_outcomes_used":
            False,
        "selector_version":
            (
                "mq5-er6r-the-warrant-"
                "node-control-v1"
            ),
        "candidate": {
            "node":
                CANDIDATE,
            "hop_signature":
                {
                    str(target):
                        int(
                            candidate_signature[
                                index
                            ]
                        )
                    for index, target
                    in enumerate(
                        ALL_TARGETS
                    )
                },
            "indegree":
                int(
                    indegree[
                        CANDIDATE
                    ]
                ),
            "outdegree":
                int(
                    outdegree[
                        CANDIDATE
                    ]
                ),
            "incoming_abs_weight_sum":
                float(
                    incoming_abs[
                        CANDIDATE
                    ]
                ),
            "outgoing_abs_weight_sum":
                float(
                    outgoing_abs[
                        CANDIDATE
                    ]
                ),
            "runtime_class": {
                "retina":
                    candidate_class[0],
                "relay":
                    candidate_class[1],
                "graded":
                    candidate_class[2],
            },
        },
        "selection_rule": [
            (
                "exclude frozen responders, "
                "WAY DOWN top-five hypotheses, "
                "and prior ER hypothesis nodes"
            ),
            (
                "require exact candidate "
                "retina/relay/graded membership"
            ),
            (
                "require structural reachability "
                "within <=3 hops to all 5 affected "
                "and all 4 retained responders"
            ),
            (
                "minimize nine-target bounded "
                "hop-signature mismatch count"
            ),
            (
                "then minimize hop-distance L1"
            ),
            (
                "then minimize maximum structural "
                "log mismatch across indegree, "
                "outdegree, incoming absolute "
                "weight sum and outgoing absolute "
                "weight sum"
            ),
            (
                "then minimize summed structural "
                "log mismatch"
            ),
            (
                "then component mismatches in "
                "the frozen order"
            ),
            (
                "then lower node ID"
            ),
        ],
        "eligible_control_count":
            len(eligible),
        "exact_hop_signature_match_count":
            int(
                exact_hop_matches
            ),
        "selected_control": {
            "node":
                selected_node,
            "hop_signature": {
                str(target):
                    int(
                        selected_signature[
                            index
                        ]
                    )
                for index, target
                in enumerate(
                    ALL_TARGETS
                )
            },
            "indegree":
                int(
                    indegree[
                        selected_node
                    ]
                ),
            "outdegree":
                int(
                    outdegree[
                        selected_node
                    ]
                ),
            "incoming_abs_weight_sum":
                float(
                    incoming_abs[
                        selected_node
                    ]
                ),
            "outgoing_abs_weight_sum":
                float(
                    outgoing_abs[
                        selected_node
                    ]
                ),
            "rank_metrics": {
                "hop_mismatch_count":
                    int(
                        selected_key[
                            0
                        ]
                    ),
                "hop_l1":
                    int(
                        selected_key[
                            1
                        ]
                    ),
                "max_structural_log_mismatch":
                    float(
                        selected_key[
                            2
                        ]
                    ),
                "sum_structural_log_mismatch":
                    float(
                        selected_key[
                            3
                        ]
                    ),
                "indegree_log_mismatch":
                    float(
                        selected_key[
                            4
                        ]
                    ),
                "outdegree_log_mismatch":
                    float(
                        selected_key[
                            5
                        ]
                    ),
                "incoming_weight_log_mismatch":
                    float(
                        selected_key[
                            6
                        ]
                    ),
                "outgoing_weight_log_mismatch":
                    float(
                        selected_key[
                            7
                        ]
                    ),
            },
        },
        "alternate_control_identities_exposed":
            False,
    }

    return payload



def require_control_selection_authorization() -> dict:
    """
    Authorize matched-control selection without mutating the
    frozen THE WARRANT preregistration.

    The preregistration must remain disabled. Authority comes
    only from a separately frozen authorization artifact that
    binds the requalified selector.
    """

    root = Path(__file__).resolve().parents[1]

    config_path = (
        root
        / "config/controls/"
        "mq5-er6r-the-warrant-v1.toml"
    )

    auth_path = (
        root
        / CONTROL_SELECTION_AUTHORIZATION
    )

    qualification_path = (
        root
        / SELECTOR_QUALIFICATION
    )

    with config_path.open("rb") as handle:
        config = tomllib.load(handle)

    #
    # The preregistration itself remains immutable and disabled.
    #
    if (
        config.get(
            "matched_control_selection_enabled"
        )
        is not False
    ):
        raise ControlSelectionError(
            "THE WARRANT preregistration "
            "selection flag drift"
        )

    if (
        config.get(
            "matched_control",
            {},
        ).get(
            "selection_enabled"
        )
        is not False
    ):
        raise ControlSelectionError(
            "THE WARRANT preregistration "
            "matched-control flag drift"
        )

    if (
        config.get(
            "result_execution_enabled"
        )
        is not False
    ):
        raise ControlSelectionError(
            "THE WARRANT result execution "
            "must remain disabled during "
            "control selection"
        )

    if not auth_path.is_file():
        raise ControlSelectionError(
            "THE WARRANT control-selection "
            "authorization missing"
        )

    if not qualification_path.is_file():
        raise ControlSelectionError(
            "THE WARRANT selector "
            "qualification v2 missing"
        )

    selector_sha = hashlib.sha256(
        Path(__file__).read_bytes()
    ).hexdigest()

    qualification_sha = hashlib.sha256(
        qualification_path.read_bytes()
    ).hexdigest()

    qualification = json.loads(
        qualification_path.read_text(
            encoding="utf-8"
        )
    )

    if (
        qualification.get("status")
        != "SELECTOR_QUALIFIED_NO_IDENTITY_EXPOSURE"
    ):
        raise ControlSelectionError(
            "selector qualification status drift"
        )

    if (
        qualification.get("selector_sha256")
        != selector_sha
    ):
        raise ControlSelectionError(
            "selector qualification SHA drift"
        )

    for key in (
        "ranking_performed",
        "control_selected",
        "control_identity_exposed",
        "alternate_control_identities_exposed",
        "neural_execution",
        "result_execution",
    ):
        if qualification.get(key) is not False:
            raise ControlSelectionError(
                "selector qualification "
                f"unexpectedly sets {key}"
            )

    authorization = json.loads(
        auth_path.read_text(
            encoding="utf-8"
        )
    )

    required = {
        "schema_version":
            "moscaquant."
            "mq5-er6r-the-warrant-"
            "control-selection-authorization/v1",

        "experiment":
            "mq5-er6r-the-warrant-v1",

        "codename":
            "THE WARRANT",

        "status":
            "AUTHORIZED_FOR_MATCHED_CONTROL_SELECTION",

        "selector_sha256":
            selector_sha,

        "qualification_sha256":
            qualification_sha,

        "candidate_node":
            1952,

        "control_selection_authorized":
            True,

        "neural_execution_authorized":
            False,

        "result_execution_authorized":
            False,

        "alternate_control_fishing_authorized":
            False,

        "selector_relaxation_authorized":
            False,
    }

    for key, expected in required.items():
        if authorization.get(key) != expected:
            raise ControlSelectionError(
                "control-selection authorization "
                f"drift for {key}: "
                f"{authorization.get(key)!r} "
                f"!= {expected!r}"
            )

    return authorization



def main() -> None:
    require_control_selection_authorization()
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--select",
        action="store_true",
        required=True,
    )

    parser.add_argument(
        "--write",
        action="store_true",
    )

    args = parser.parse_args()

    payload = build_payload()

    encoded = (
        json.dumps(
            payload,
            indent=2,
            sort_keys=True,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")

    if args.write:
        OUTPUT.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        if OUTPUT.exists():
            raise ControlSelectionError(
                "refusing to overwrite "
                f"existing artifact: "
                f"{OUTPUT}"
            )

        OUTPUT.write_bytes(
            encoded
        )

        print(
            "THE WARRANT matched control "
            "frozen."
        )

        print(
            "artifact:",
            OUTPUT,
        )

        print(
            "sha256:",
            sha256_bytes(
                encoded
            ),
        )

        print(
            "selected node:",
            payload[
                "selected_control"
            ]["node"],
        )

        print(
            "eligible controls:",
            payload[
                "eligible_control_count"
            ],
        )

        print(
            "exact hop matches:",
            payload[
                "exact_hop_signature_match_count"
            ],
        )

        return

    #
    # Dry-run output deliberately does not expose alternate identities.
    #
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
