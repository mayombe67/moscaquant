from __future__ import annotations

import hashlib
import json
from pathlib import Path

from scipy import sparse

from config.paths import data_path


CONNECTOME = data_path(
    "processed",
    "connectome-baseline-v1.npz",
)

OUTPUT = Path(
    "config/controls/"
    "sq08-three-body-topology-frontier-v1.json"
)

CALIBRATION_ARTIFACT = Path(
    "config/controls/"
    "sq08-three-body-topology-v1.json"
)

BODY_RESPONDERS = {
    "A": 137122,
    "B": 317,
    "C": 126002,
}

EXPECTED_COUNTS = {
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
}

EXPECTED_ABC = (
    7,
    72,
    129,
    411,
    470,
    1472,
    1574,
    1662,
    1919,
    2009,
    2327,
    3712,
    4068,
    14273,
    16349,
    18196,
    130134,
    131527,
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def direct_targets(
    graph: sparse.csc_matrix,
    source: int,
) -> dict[int, float]:
    start = graph.indptr[source]
    stop = graph.indptr[source + 1]

    return {
        int(post): float(weight)
        for post, weight in zip(
            graph.indices[start:stop],
            graph.data[start:stop],
        )
        if float(weight) != 0.0
    }


def main() -> None:
    if not CALIBRATION_ARTIFACT.exists():
        raise RuntimeError(
            "required topology calibration artifact missing"
        )

    graph = sparse.load_npz(CONNECTOME).tocsc()

    connectome_sha256 = sha256_file(CONNECTOME)
    calibration_sha256 = sha256_file(
        CALIBRATION_ARTIFACT
    )

    targets = {
        body: direct_targets(graph, source)
        for body, source in BODY_RESPONDERS.items()
    }

    sets = {
        body: set(rows)
        for body, rows in targets.items()
    }

    ab = sets["A"] & sets["B"]
    ac = sets["A"] & sets["C"]
    bc = sets["B"] & sets["C"]

    abc = (
        sets["A"]
        & sets["B"]
        & sets["C"]
    )

    ab_only = ab - abc
    ac_only = ac - abc
    bc_only = bc - abc

    counts = {
        "A": len(sets["A"]),
        "B": len(sets["B"]),
        "C": len(sets["C"]),
        "AB": len(ab),
        "AC": len(ac),
        "BC": len(bc),
        "AB_only": len(ab_only),
        "AC_only": len(ac_only),
        "BC_only": len(bc_only),
        "ABC": len(abc),
    }

    if counts != EXPECTED_COUNTS:
        raise RuntimeError(
            f"direct-frontier count drift: {counts}"
        )

    abc_sorted = tuple(sorted(abc))

    if abc_sorted != EXPECTED_ABC:
        raise RuntimeError(
            "three-way direct frontier identity drift"
        )

    for source in BODY_RESPONDERS.values():
        if source in abc:
            raise RuntimeError(
                "BODY responder appears in ABC frontier"
            )

    abc_records = []

    for node in abc_sorted:
        abc_records.append(
            {
                "node": node,
                "incoming_weights": {
                    "A": targets["A"][node],
                    "B": targets["B"][node],
                    "C": targets["C"][node],
                },
            }
        )

    payload = {
        "schema_version": (
            "moscaquant."
            "sq08-three-body-topology-frontier/v1"
        ),
        "experiment": "SQ-08",
        "codename": "THREE BODY PROBLEM",
        "status": "FROZEN_PRE_RESULT",
        "source_artifacts": {
            "connectome_path": str(CONNECTOME),
            "connectome_sha256": connectome_sha256,
            "calibration_artifact": str(
                CALIBRATION_ARTIFACT
            ),
            "calibration_artifact_sha256":
                calibration_sha256,
        },
        "selection_rule": {
            "type": "direct_structural_convergence",
            "directed_hops": 1,
            "uses_sq08_outcomes": False,
            "description": (
                "intersection of direct downstream "
                "targets of all three frozen BODY "
                "responders"
            ),
        },
        "bodies": {
            "A": {
                "edge_id": "E10",
                "responder": 137122,
            },
            "B": {
                "edge_id": "E11",
                "responder": 317,
            },
            "C": {
                "edge_id": "E12",
                "responder": 126002,
            },
        },
        "counts": counts,
        "pairwise_only": {
            "AB": sorted(ab_only),
            "AC": sorted(ac_only),
            "BC": sorted(bc_only),
        },
        "three_way_direct_frontier": abc_records,
        "claim_boundary": (
            "structural convergence candidates only; "
            "not functional mediation"
        ),
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
        )
        + "\n"
    )

    print(
        "SQ-08 THREE BODY direct frontier frozen"
    )
    print(
        "connectome sha256:",
        connectome_sha256,
    )
    print(
        "calibration sha256:",
        calibration_sha256,
    )
    print("ABC direct:", len(abc_sorted))
    print(
        "ABC nodes:",
        ",".join(map(str, abc_sorted)),
    )
    print("output:", OUTPUT)
    print(
        "output sha256:",
        sha256_file(OUTPUT),
    )


if __name__ == "__main__":
    main()
