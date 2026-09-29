from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

import numpy as np
from scipy import sparse

from brain import mq5_er5_the_greek_runner as greek


AUDIT_ID = "mq5-er5-the-greek-orientation-audit-v1"

OUTPUT = Path(
    "artifacts/audits/"
    "mq5-er5-greek-orientation-audit-v1.json"
)

GREEK_RESULT_SHA256 = (
    "1ed37ae6d4e19cd39409a2bb714ed7394236d2a273316005c6ae596e5d837790"
)

GREEK_RESULT_SEAL_SHA256 = (
    "63fb631e661ff054e28869f0c784eddea088ab8c3307a0c82bc5d55a40b94ee9"
)

CANDIDATES = (
    1952,
    2641,
    1963,
    1944,
    23640,
)

TARGETS = (
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
# Exact signatures reported by the sealed GREEK implementation.
#
SEALED_SIGNATURES = {
    1952: (
        2, 3, 2, 2, 3, 2, 2, 2, 2,
    ),
    2641: (
        2, 2, 2, 2, 3, 2, 2, 2, 2,
    ),
    1963: (
        2, 2, 2, 2, 2, 1, 2, 2, 2,
    ),
    1944: (
        2, 2, 3, 2, 2, 1, 2, 2, 2,
    ),
    23640: (
        2, 3, 3, 3, 2, 2, 1, 2, 2,
    ),
}


class OrientationAuditError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
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
        raise OrientationAuditError(
            "unable to determine git HEAD"
        )

    return completed.stdout.strip()


def legacy_greek_reverse_hops(
    graph: sparse.csr_matrix,
    target: int,
    max_hops: int = MAX_HOPS,
) -> dict[int, int]:
    """
    Exact traversal semantics used by the sealed GREEK implementation.

    This intentionally preserves the historical CSC-column behavior for audit
    reproduction. It is not presented as the correct connectome traversal.
    """

    csc = graph.tocsc()

    distances = {
        int(target): 0,
    }

    frontier = [
        int(target),
    ]

    for depth in range(
        1,
        int(max_hops) + 1,
    ):
        next_frontier = []

        for post in frontier:
            start = csc.indptr[
                post
            ]
            end = csc.indptr[
                post + 1
            ]

            pres = csc.indices[
                start:end
            ]

            for pre in pres:
                pre = int(pre)

                if pre not in distances:
                    distances[
                        pre
                    ] = int(depth)

                    next_frontier.append(
                        pre
                    )

        frontier = next_frontier

        if not frontier:
            break

    distances.pop(
        int(target),
        None,
    )

    return distances


def correct_reverse_hops(
    graph: sparse.csr_matrix,
    target: int,
    max_hops: int = MAX_HOPS,
) -> dict[int, int]:
    """
    Reverse ancestry under MoscaQuant's frozen convention:

        graph[post, pre] = pre -> post

    A postsynaptic CSR row therefore contains its direct presynaptic
    predecessors.
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
                ~seen[predecessors]
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


def signature(
    maps: dict[
        int,
        dict[int, int],
    ],
    node: int,
) -> tuple[
    int | None,
    ...,
]:
    return tuple(
        maps[
            int(target)
        ].get(
            int(node)
        )
        for target in TARGETS
    )


def build_payload() -> dict:
    (
        _original,
        c13,
        _retina,
        _responders,
    ) = greek.load_c13()

    legacy_maps = {
        int(target):
            legacy_greek_reverse_hops(
                c13,
                int(target),
                MAX_HOPS,
            )
        for target
        in TARGETS
    }

    correct_maps = {
        int(target):
            correct_reverse_hops(
                c13,
                int(target),
                MAX_HOPS,
            )
        for target
        in TARGETS
    }

    rows = []

    for node in CANDIDATES:
        legacy = signature(
            legacy_maps,
            node,
        )

        expected = (
            SEALED_SIGNATURES[
                node
            ]
        )

        if legacy != expected:
            raise OrientationAuditError(
                "legacy traversal failed "
                "to reproduce sealed "
                f"GREEK signature for "
                f"node {node}: "
                f"{legacy} != {expected}"
            )

        corrected = signature(
            correct_maps,
            node,
        )

        differences = []

        for (
            target,
            old_hop,
            new_hop,
        ) in zip(
            TARGETS,
            legacy,
            corrected,
        ):
            if old_hop != new_hop:
                differences.append(
                    {
                        "target":
                            int(target),
                        "sealed_greek_hops":
                            old_hop,
                        "correct_reverse_hops":
                            new_hop,
                    }
                )

        rows.append(
            {
                "node":
                    int(node),
                "sealed_signature":
                    list(legacy),
                "correct_reverse_signature":
                    list(corrected),
                "identical":
                    legacy == corrected,
                "difference_count":
                    len(
                        differences
                    ),
                "differences":
                    differences,
            }
        )

    mismatch_count = sum(
        not bool(
            row["identical"]
        )
        for row in rows
    )

    if mismatch_count == len(
        CANDIDATES
    ):
        classification = (
            "GREEK_ORIENTATION_DEFECT_"
            "CONFIRMED_ALL_TOP5"
        )
    elif mismatch_count > 0:
        classification = (
            "GREEK_ORIENTATION_DEFECT_"
            "CONFIRMED_PARTIAL"
        )
    else:
        classification = (
            "NO_GREEK_ORIENTATION_"
            "DISCREPANCY"
        )

    runner = Path(
        "brain/"
        "mq5_er5_the_greek_runner.py"
    )

    return {
        "audit":
            AUDIT_ID,
        "kind":
            (
                "STRUCTURAL "
                "SEMANTICS AUDIT"
            ),
        "neural_execution":
            False,
        "new_candidate_search":
            False,
        "candidate_reranking":
            False,
        "connectome_convention":
            (
                "graph[post, pre] "
                "= pre -> post"
            ),
        "max_hops":
            MAX_HOPS,
        "targets":
            list(TARGETS),
        "candidate_nodes":
            list(CANDIDATES),
        "greek_result_sha256":
            GREEK_RESULT_SHA256,
        "greek_result_seal_sha256":
            (
                GREEK_RESULT_SEAL_SHA256
            ),
        "greek_runner_sha256":
            sha256_file(
                runner
            ),
        "audit_git_head":
            git_head(),
        "classification":
            classification,
        "mismatching_top5_count":
            int(
                mismatch_count
            ),
        "all_sealed_signatures_reproduced":
            True,
        "rows":
            rows,
        "claim_boundary": {
            "corrected_winner_determined":
                False,
            "pinch_authorized":
                False,
            "pine_barrens_authorized":
                False,
            "sealed_greek_bytes_modified":
                False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--audit",
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
            raise OrientationAuditError(
                "refusing to overwrite "
                f"existing artifact: "
                f"{OUTPUT}"
            )

        OUTPUT.write_bytes(
            encoded
        )

        print(
            "classification:",
            payload[
                "classification"
            ],
        )

        print(
            "mismatching top-five:",
            payload[
                "mismatching_top5_count"
            ],
        )

        print(
            "artifact:",
            OUTPUT,
        )

        print(
            "sha256:",
            hashlib.sha256(
                encoded
            ).hexdigest(),
        )

        return

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
