from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tomllib
from pathlib import Path

import numpy as np
from scipy import sparse

import brain.mq5_er6r_the_warrant_control_selector as selector


ROOT = Path(__file__).resolve().parents[1]

CONFIG = (
    ROOT
    / "config/controls/"
    "mq5-er6r-the-warrant-v1.toml"
)

PROTOCOL = (
    ROOT
    / "docs/experiments/"
    "mq5-er6r-the-warrant-protocol.md"
)

SELECTOR = (
    ROOT
    / "brain/"
    "mq5_er6r_the_warrant_control_selector.py"
)

OUTPUT = (
    ROOT
    / "artifacts/qualification/"
    "mq5-er6r-the-warrant-selector-qualification-v2.json"
)

EXPECTED_CONFIG_SHA256 = (
    "d19905969cb4fb06c776c59ba0c7621b"
    "d174dff351bf52b31c23bf136288a135"
)

EXPECTED_PROTOCOL_SHA256 = (
    "20eefc0a830a81a4123a675666db303f"
    "e57bce00e0d7691f874f9378d87b6c1b"
)

EXPECTED_SELECTOR_SHA256 = (
    "c0c1df6d31ec32e641d2fa95d9fb76"
    "e418beaf0342d7ee2dfbb8ccf663496c22"
)

SELECTOR_FREEZE_GIT_SHA = (
    "83bd7e77912a4b7c63bd949369444df0d471e60d"
)


class QualificationError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def git_output(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args],
        cwd=ROOT,
        text=True,
    ).strip()


def verify_repository_boundary() -> str:
    if (
        git_output("branch", "--show-current")
        != "science/mq5-er6r-the-warrant"
    ):
        raise QualificationError(
            "wrong science branch"
        )

    status = git_output(
        "status",
        "--porcelain",
    )

    if status:
        raise QualificationError(
            "science worktree is not clean"
        )

    return git_output(
        "rev-parse",
        "HEAD",
    )


def verify_frozen_files() -> None:
    expected = {
        CONFIG: EXPECTED_CONFIG_SHA256,
        PROTOCOL: EXPECTED_PROTOCOL_SHA256,
        SELECTOR: EXPECTED_SELECTOR_SHA256,
    }

    for path, wanted in expected.items():
        if not path.is_file():
            raise QualificationError(
                f"missing frozen file: {path}"
            )

        actual = sha256_file(path)

        if actual != wanted:
            raise QualificationError(
                f"SHA drift for {path}: "
                f"{actual} != {wanted}"
            )


def load_config() -> dict:
    with CONFIG.open("rb") as handle:
        config = tomllib.load(handle)

    if (
        config.get(
            "matched_control_selection_enabled"
        )
        is not False
    ):
        raise QualificationError(
            "matched-control selection is not disabled"
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
        raise QualificationError(
            "matched-control section is not disabled"
        )

    if (
        config.get("result_execution_enabled")
        is not False
    ):
        raise QualificationError(
            "result execution is not disabled"
        )

    return config


def orientation_contract() -> None:
    #
    # graph[post, pre]
    #
    # 0 -> 1 -> 2 -> 3
    #
    graph = sparse.csr_matrix(
        (
            np.asarray(
                [1.0, 1.0, 1.0],
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

    observed = selector.reverse_hop_array(
        graph,
        target=2,
        max_hops=3,
    )

    if int(observed[1]) != 1:
        raise QualificationError(
            "orientation contract: node 1 != hop 1"
        )

    if int(observed[0]) != 2:
        raise QualificationError(
            "orientation contract: node 0 != hop 2"
        )

    if int(observed[3]) != -1:
        raise QualificationError(
            "orientation contract: downstream node "
            "appeared in reverse ancestry"
        )


def qualify() -> dict:
    head = verify_repository_boundary()

    verify_frozen_files()
    config = load_config()
    orientation_contract()

    graph = selector.load_c13()

    n_nodes = int(graph.shape[0])

    if graph.shape[0] != graph.shape[1]:
        raise QualificationError(
            "C13 graph is not square"
        )

    if selector.CANDIDATE >= n_nodes:
        raise QualificationError(
            "candidate outside graph"
        )

    hop_arrays = {
        int(target):
            selector.reverse_hop_array(
                graph,
                int(target),
                selector.MAX_HOPS,
            )
        for target
        in selector.ALL_TARGETS
    }

    candidate_signature = (
        selector.hop_signature(
            selector.CANDIDATE,
            hop_arrays,
        )
    )

    expected_signature = tuple(
        int(
            selector.EXPECTED_1952_HOPS[
                int(target)
            ]
        )
        for target
        in selector.ALL_TARGETS
    )

    if candidate_signature != expected_signature:
        raise QualificationError(
            "corrected 1952 signature mismatch: "
            f"{candidate_signature} "
            f"!= {expected_signature}"
        )

    affected_reach = sum(
        int(
            hop_arrays[
                int(target)
            ][selector.CANDIDATE]
            >= 0
        )
        for target
        in selector.AFFECTED_TARGETS
    )

    retained_reach = sum(
        int(
            hop_arrays[
                int(target)
            ][selector.CANDIDATE]
            >= 0
        )
        for target
        in selector.RETAINED_TARGETS
    )

    if affected_reach != 5:
        raise QualificationError(
            "1952 affected structural coverage drift"
        )

    if retained_reach != 4:
        raise QualificationError(
            "1952 retained structural coverage drift"
        )

    retina = selector.population_mask(
        selector.RETINA,
        n_nodes,
    )

    relay = selector.population_mask(
        selector.RELAY,
        n_nodes,
    )

    graded = selector.population_mask(
        selector.GRADED,
        n_nodes,
    )

    candidate_class = (
        bool(
            retina[
                selector.CANDIDATE
            ]
        ),
        bool(
            relay[
                selector.CANDIDATE
            ]
        ),
        bool(
            graded[
                selector.CANDIDATE
            ]
        ),
    )

    forbidden = (
        set(
            int(x)
            for x
            in selector.ALL_TARGETS
        )
        | set(
            int(x)
            for x
            in selector.WAY_DOWN_TOP5
        )
        | set(
            int(x)
            for x
            in selector.PRIOR_HYPOTHESIS_NODES
        )
    )

    eligible_control_count = 0
    exact_hop_signature_match_count = 0

    #
    # QUALIFICATION ONLY:
    #
    # Enumerate the frozen structural eligibility universe,
    # but DO NOT call rank_key(), sort eligible nodes,
    # select a winner, or retain any eligible node identity.
    #
    for node in range(n_nodes):
        if node in forbidden:
            continue

        control_class = (
            bool(retina[node]),
            bool(relay[node]),
            bool(graded[node]),
        )

        if control_class != candidate_class:
            continue

        affected = sum(
            int(
                hop_arrays[
                    int(target)
                ][node]
                >= 0
            )
            for target
            in selector.AFFECTED_TARGETS
        )

        retained = sum(
            int(
                hop_arrays[
                    int(target)
                ][node]
                >= 0
            )
            for target
            in selector.RETAINED_TARGETS
        )

        if affected != 5 or retained != 4:
            continue

        eligible_control_count += 1

        signature = selector.hop_signature(
            node,
            hop_arrays,
        )

        if signature == candidate_signature:
            exact_hop_signature_match_count += 1

    if eligible_control_count <= 0:
        raise QualificationError(
            "no structurally eligible control universe"
        )

    if eligible_control_count != 149893:
        raise QualificationError(
            "eligible-control universe drift: "
            f"{eligible_control_count} != 149893"
        )

    if exact_hop_signature_match_count != 1885:
        raise QualificationError(
            "exact-hop-match universe drift: "
            f"{exact_hop_signature_match_count} != 1885"
        )

    return {
        "schema_version":
            "moscaquant."
            "mq5-er6r-the-warrant-"
            "selector-qualification/v2",

        "experiment":
            "mq5-er6r-the-warrant-v1",

        "codename":
            "THE WARRANT",

        "status":
            "SELECTOR_QUALIFIED_NO_IDENTITY_EXPOSURE",

        "qualification_git_sha":
            head,

        "selector_freeze_git_sha":
            SELECTOR_FREEZE_GIT_SHA,

        "selector_sha256":
            EXPECTED_SELECTOR_SHA256,

        "config_sha256":
            EXPECTED_CONFIG_SHA256,

        "protocol_sha256":
            EXPECTED_PROTOCOL_SHA256,

        "candidate_node":
            1952,

        "target_order":
            list(selector.ALL_TARGETS),

        "corrected_candidate_signature":
            list(candidate_signature),

        "affected_structural_coverage":
            affected_reach,

        "retained_structural_coverage":
            retained_reach,

        "candidate_runtime_class": {
            "retina":
                candidate_class[0],
            "relay":
                candidate_class[1],
            "graded":
                candidate_class[2],
        },

        "graph_node_count":
            n_nodes,

        "eligible_control_count":
            eligible_control_count,

        "exact_hop_signature_match_count":
            exact_hop_signature_match_count,

        "ranking_performed":
            False,

        "control_selected":
            False,

        "control_identity_exposed":
            False,

        "alternate_control_identities_exposed":
            False,

        "neural_execution":
            False,

        "result_execution":
            False,

        "matched_control_selection_enabled":
            False,

        "financial_semantics":
            config["financial_semantics"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--write",
        action="store_true",
    )

    args = parser.parse_args()

    if not args.write:
        raise QualificationError(
            "qualification requires --write"
        )

    if OUTPUT.exists():
        raise QualificationError(
            f"refusing to overwrite {OUTPUT}"
        )

    payload = qualify()

    encoded = (
        json.dumps(
            payload,
            indent=2,
            sort_keys=True,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT.write_bytes(encoded)

    print(
        "THE WARRANT selector qualification: PASS"
    )

    print(
        "corrected_1952_signature:",
        tuple(
            payload[
                "corrected_candidate_signature"
            ]
        ),
    )

    print(
        "eligible_control_count:",
        payload[
            "eligible_control_count"
        ],
    )

    print(
        "exact_hop_signature_match_count:",
        payload[
            "exact_hop_signature_match_count"
        ],
    )

    print("ranking_performed: False")
    print("control_selected: False")
    print("control_identity_exposed: False")
    print("neural_execution: False")
    print("artifact:", OUTPUT)

    print(
        "sha256:",
        hashlib.sha256(
            encoded
        ).hexdigest(),
    )


if __name__ == "__main__":
    main()
