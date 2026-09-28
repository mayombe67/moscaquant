from __future__ import annotations

import hashlib
import json
from pathlib import Path

from scipy import sparse

from config.paths import data_path


ROOT = Path(__file__).resolve().parents[1]

CONNECTOME = data_path(
    "processed",
    "connectome-baseline-v1.npz",
)

SQ08_FRONTIER = (
    ROOT
    / "config"
    / "controls"
    / "sq08-three-body-topology-frontier-v1.json"
)

OUTPUT = (
    ROOT
    / "config"
    / "controls"
    / "sq12-resonance-cascade-topology-v1.json"
)

EXPECTED_CONNECTOME_SHA256 = (
    "e00e3f2a9828c921fe1f093cc567bf45"
    "a85adad0526176be0aa1b8be09336eeb"
)

EXPECTED_SQ08_FRONTIER_SHA256 = (
    "ad87e904c13698552d3e52fb58e9558a"
    "efe4e0898a2ef6bb45b3c64652196361"
)

BODY_RESPONDERS = {
    "A": 137122,
    "B": 317,
    "C": 126002,
}

EXPECTED_RAW_COUNTS = {
    "A": 5355,
    "B": 1976,
    "C": 1964,
    "AB": 73,
    "AC": 152,
    "BC": 212,
    "AB_only": 55,
    "AC_only": 134,
    "BC_only": 194,
    "ABC": 18,
    "union": 8876,
    "single_only": 8475,
    "convergence_panel": 401,
}


class ResonanceTopologyError(RuntimeError):
    pass


def fail(message: str) -> None:
    raise ResonanceTopologyError(message)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(8 * 1024 * 1024),
            b"",
        ):
            h.update(chunk)

    return h.hexdigest()


def direct_targets(
    graph: sparse.csc_matrix,
    source: int,
) -> dict[int, float]:
    start = int(graph.indptr[source])
    stop = int(graph.indptr[source + 1])

    return {
        int(post): float(weight)
        for post, weight in zip(
            graph.indices[start:stop],
            graph.data[start:stop],
        )
        if float(weight) != 0.0
    }


def derive_topology(
    graph: sparse.csc_matrix,
    body_responders: dict[str, int],
) -> dict:
    targets = {
        body: direct_targets(
            graph,
            source,
        )
        for body, source
        in body_responders.items()
    }

    sets = {
        body: set(rows)
        for body, rows
        in targets.items()
    }

    a = sets["A"]
    b = sets["B"]
    c = sets["C"]

    ab = a & b
    ac = a & c
    bc = b & c

    abc = a & b & c

    ab_only = ab - abc
    ac_only = ac - abc
    bc_only = bc - abc

    a_only = a - b - c
    b_only = b - a - c
    c_only = c - a - b

    union = a | b | c

    convergence = (
        ab
        | ac
        | bc
    )

    body_nodes = set(
        body_responders.values()
    )

    excluded_body_nodes = (
        union
        & body_nodes
    )

    scan = union - body_nodes

    convergence_scan = (
        convergence
        - body_nodes
    )

    memberships = {}

    for node in sorted(union):
        parents = [
            body
            for body in ("A", "B", "C")
            if node in sets[body]
        ]

        memberships[node] = parents

    convergence_records = []

    for node in sorted(
        convergence_scan
    ):
        weights = {}

        for body in memberships[node]:
            weights[body] = (
                targets[body][node]
            )

        convergence_records.append({
            "node": node,
            "body_parents":
                memberships[node],
            "incoming_body_weights":
                weights,
        })

    return {
        "targets": targets,
        "sets": sets,
        "A_only": a_only,
        "B_only": b_only,
        "C_only": c_only,
        "AB": ab,
        "AC": ac,
        "BC": bc,
        "ABC": abc,
        "AB_only": ab_only,
        "AC_only": ac_only,
        "BC_only": bc_only,
        "union": union,
        "convergence": convergence,
        "excluded_body_nodes":
            excluded_body_nodes,
        "scan": scan,
        "convergence_scan":
            convergence_scan,
        "memberships": memberships,
        "convergence_records":
            convergence_records,
    }


def raw_counts(
    topology: dict,
) -> dict[str, int]:
    return {
        "A": len(topology["sets"]["A"]),
        "B": len(topology["sets"]["B"]),
        "C": len(topology["sets"]["C"]),
        "AB": len(topology["AB"]),
        "AC": len(topology["AC"]),
        "BC": len(topology["BC"]),
        "AB_only":
            len(topology["AB_only"]),
        "AC_only":
            len(topology["AC_only"]),
        "BC_only":
            len(topology["BC_only"]),
        "ABC": len(topology["ABC"]),
        "union": len(topology["union"]),
        "single_only": (
            len(topology["A_only"])
            + len(topology["B_only"])
            + len(topology["C_only"])
        ),
        "convergence_panel":
            len(topology["convergence"]),
    }


def verify_sq08_frontier(
    frontier: dict,
    topology: dict,
) -> None:
    if (
        frontier.get("schema_version")
        != (
            "moscaquant."
            "sq08-three-body-topology-frontier/v1"
        )
    ):
        fail(
            "SQ-08 frontier schema drift"
        )

    if (
        frontier.get("status")
        != "FROZEN_PRE_RESULT"
    ):
        fail(
            "SQ-08 frontier status drift"
        )

    selection = frontier.get(
        "selection_rule",
        {},
    )

    if (
        selection.get("directed_hops")
        != 1
    ):
        fail(
            "SQ-08 frontier hop-depth drift"
        )

    if (
        selection.get(
            "uses_sq08_outcomes"
        )
        is not False
    ):
        fail(
            "SQ-08 frontier outcome "
            "independence drift"
        )

    if (
        frontier.get("counts")
        != {
            key: EXPECTED_RAW_COUNTS[key]
            for key in (
                "A",
                "B",
                "C",
                "AB",
                "AC",
                "BC",
                "AB_only",
                "AC_only",
                "BC_only",
                "ABC",
            )
        }
    ):
        fail(
            "SQ-08 frozen frontier "
            "count drift"
        )

    abc = {
        int(row["node"])
        for row in frontier[
            "three_way_direct_frontier"
        ]
    }

    if abc != topology["ABC"]:
        fail(
            "SQ-08 ABC identity drift"
        )

    for name in (
        "AB",
        "AC",
        "BC",
    ):
        observed = {
            int(x)
            for x in frontier[
                "pairwise_only"
            ][name]
        }

        expected = topology[
            f"{name}_only"
        ]

        if observed != expected:
            fail(
                f"SQ-08 {name}-only "
                "identity drift"
            )


def build_payload() -> dict:
    if not CONNECTOME.is_file():
        fail(
            f"connectome missing: {CONNECTOME}"
        )

    if not SQ08_FRONTIER.is_file():
        fail(
            "SQ-08 frozen frontier missing"
        )

    connectome_sha = sha256_file(
        CONNECTOME
    )

    if (
        connectome_sha
        != EXPECTED_CONNECTOME_SHA256
    ):
        fail(
            "connectome SHA drift: "
            f"{connectome_sha}"
        )

    frontier_sha = sha256_file(
        SQ08_FRONTIER
    )

    if (
        frontier_sha
        != EXPECTED_SQ08_FRONTIER_SHA256
    ):
        fail(
            "SQ-08 frontier SHA drift: "
            f"{frontier_sha}"
        )

    graph = sparse.load_npz(
        CONNECTOME
    ).tocsc()

    topology = derive_topology(
        graph,
        BODY_RESPONDERS,
    )

    counts = raw_counts(
        topology
    )

    if counts != EXPECTED_RAW_COUNTS:
        fail(
            "SQ-12 raw topology count drift: "
            f"{counts}"
        )

    frontier = json.loads(
        SQ08_FRONTIER.read_text(
            encoding="utf-8"
        )
    )

    verify_sq08_frontier(
        frontier,
        topology,
    )

    scan_nodes = sorted(
        topology["scan"]
    )

    convergence_nodes = sorted(
        topology["convergence_scan"]
    )

    membership_counts = {}

    for label in (
        "A",
        "B",
        "C",
        "AB",
        "AC",
        "BC",
        "ABC",
    ):
        membership_counts[label] = 0

    for node in scan_nodes:
        parents = topology[
            "memberships"
        ][node]

        membership_counts[
            "".join(parents)
        ] += 1

    return {
        "schema_version":
            (
                "moscaquant."
                "sq12-resonance-cascade-"
                "topology/v1"
            ),
        "experiment": "SQ-12",
        "codename":
            "RESONANCE CASCADE",
        "status":
            "FROZEN_STRUCTURAL_CALIBRATION",
        "neural_execution_performed":
            False,
        "uses_sq12_outcomes":
            False,
        "selection_rule": {
            "type":
                "one_hop_structural_union",
            "directed_hops": 1,
            "source_nodes":
                BODY_RESPONDERS,
            "exclude_immediate_body_responders":
                True,
            "description": (
                "union of direct downstream "
                "targets of frozen BODY "
                "responders A/B/C, with the "
                "three immediate BODY responders "
                "removed from the SQ-12 "
                "downstream scan population"
            ),
        },
        "source_artifacts": {
            "connectome_path":
                str(CONNECTOME),
            "connectome_sha256":
                connectome_sha,
            "sq08_frontier_path":
                str(
                    SQ08_FRONTIER.relative_to(
                        ROOT
                    )
                ),
            "sq08_frontier_sha256":
                frontier_sha,
        },
        "raw_counts":
            counts,
        "body_responder_exclusion": {
            "body_responders":
                BODY_RESPONDERS,
            "present_in_raw_union":
                sorted(
                    topology[
                        "excluded_body_nodes"
                    ]
                ),
            "excluded_count":
                len(
                    topology[
                        "excluded_body_nodes"
                    ]
                ),
        },
        "scan_population": {
            "node_count":
                len(scan_nodes),
            "nodes":
                scan_nodes,
            "membership_counts":
                membership_counts,
        },
        "convergence_panel": {
            "definition": (
                "nodes receiving direct "
                "structural input from at least "
                "two BODY responders"
            ),
            "node_count":
                len(convergence_nodes),
            "nodes":
                convergence_nodes,
            "records":
                topology[
                    "convergence_records"
                ],
        },
        "claim_boundary": (
            "topology-only pre-result "
            "calibration; structural reachability "
            "does not establish functional "
            "propagation, mediation, biological "
            "mechanism, behavior, cognition, "
            "or financial value"
        ),
    }


def main() -> None:
    payload = build_payload()

    if OUTPUT.exists():
        fail(
            "SQ-12 topology artifact "
            "already exists"
        )

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT.write_text(
        json.dumps(
            payload,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    print(
        "SQ-12 RESONANCE CASCADE "
        "TOPOLOGY FROZEN"
    )

    print(
        "raw one-hop union:",
        payload["raw_counts"]["union"],
    )

    print(
        "excluded BODY responders:",
        payload[
            "body_responder_exclusion"
        ]["present_in_raw_union"],
    )

    print(
        "scan population:",
        payload[
            "scan_population"
        ]["node_count"],
    )

    print(
        "convergence panel:",
        payload[
            "convergence_panel"
        ]["node_count"],
    )

    print(
        "neural execution performed:",
        payload[
            "neural_execution_performed"
        ],
    )

    print(
        "output:",
        OUTPUT,
    )

    print(
        "output sha256:",
        sha256_file(OUTPUT),
    )


if __name__ == "__main__":
    main()
