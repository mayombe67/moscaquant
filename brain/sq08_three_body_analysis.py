from __future__ import annotations

import json
from pathlib import Path

import numpy as np


MASKS = (
    "000",
    "001",
    "010",
    "011",
    "100",
    "101",
    "110",
    "111",
)

PRIMARY_L2_TOL = 1e-9
PRIMARY_MAX_ABS_TOL = 1e-12

FRONTIER_INDICES = (
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


class AnalysisFailure(RuntimeError):
    pass


def fail(message: str) -> None:
    raise AnalysisFailure(message)


def symmetric_normalized_l2(
    a: np.ndarray,
    b: np.ndarray,
) -> float:
    x = np.asarray(
        a,
        dtype=np.float64,
    ).reshape(-1)

    y = np.asarray(
        b,
        dtype=np.float64,
    ).reshape(-1)

    numerator = float(
        np.linalg.norm(x - y)
    )

    denominator = max(
        float(
            np.linalg.norm(x)
            + np.linalg.norm(y)
        ),
        1e-12,
    )

    return numerator / denominator


def max_abs_difference(
    a: np.ndarray,
    b: np.ndarray,
) -> float:
    x = np.asarray(
        a,
        dtype=np.float64,
    )

    y = np.asarray(
        b,
        dtype=np.float64,
    )

    return float(
        np.max(
            np.abs(x - y),
            initial=0.0,
        )
    )


def factorial_terms(
    by_mask: dict[str, np.ndarray],
) -> dict[str, np.ndarray]:
    if set(by_mask) != set(MASKS):
        fail(
            "SQ-08 factorial cube incomplete"
        )

    y000 = by_mask["000"]
    y001 = by_mask["001"]
    y010 = by_mask["010"]
    y011 = by_mask["011"]
    y100 = by_mask["100"]
    y101 = by_mask["101"]
    y110 = by_mask["110"]
    y111 = by_mask["111"]

    shape = y000.shape

    for mask in MASKS:
        if by_mask[mask].shape != shape:
            fail(
                f"SQ-08 factorial shape drift: {mask}"
            )

    m_a = (
        y100
        - y000
    )

    m_b = (
        y010
        - y000
    )

    m_c = (
        y001
        - y000
    )

    i_ab = (
        y110
        - y100
        - y010
        + y000
    )

    i_ac = (
        y101
        - y100
        - y001
        + y000
    )

    i_bc = (
        y011
        - y010
        - y001
        + y000
    )

    i_abc = (
        y111
        - y110
        - y101
        - y011
        + y100
        + y010
        + y001
        - y000
    )

    y111_pairwise = (
        y000
        + m_a
        + m_b
        + m_c
        + i_ab
        + i_ac
        + i_bc
    )

    return {
        "M_A": m_a,
        "M_B": m_b,
        "M_C": m_c,
        "I_AB": i_ab,
        "I_AC": i_ac,
        "I_BC": i_bc,
        "I_ABC": i_abc,
        "Y111_pairwise": y111_pairwise,
    }


def classify_three_way(
    by_mask: dict[str, np.ndarray],
) -> dict:
    terms = factorial_terms(
        by_mask
    )

    observed = by_mask["111"]
    reconstructed = terms[
        "Y111_pairwise"
    ]

    l2 = symmetric_normalized_l2(
        observed,
        reconstructed,
    )

    max_abs = max_abs_difference(
        observed,
        reconstructed,
    )

    exact_zero = (
        l2 <= PRIMARY_L2_TOL
        and max_abs <= PRIMARY_MAX_ABS_TOL
    )

    return {
        "classification": (
            "THREE_WAY_EXACT_ZERO"
            if exact_zero
            else "THREE_WAY_NONZERO"
        ),
        "symmetric_normalized_l2":
            l2,
        "max_abs_difference":
            max_abs,
        "thresholds": {
            "symmetric_normalized_l2_max":
                PRIMARY_L2_TOL,
            "max_abs_difference_max":
                PRIMARY_MAX_ABS_TOL,
        },
        "I_ABC":
            terms["I_ABC"],
        "Y111_pairwise":
            reconstructed,
    }


def first_nonzero_frame(
    trajectory: np.ndarray,
) -> int | None:
    values = np.asarray(
        trajectory
    )

    if values.ndim != 1:
        raise ValueError(
            "trajectory must be one-dimensional"
        )

    hits = np.flatnonzero(
        values != 0
    )

    if len(hits) == 0:
        return None

    return int(
        hits[0]
    )


def frontier_report(
    by_mask: dict[str, np.ndarray],
) -> dict:
    for mask in MASKS:
        value = by_mask[mask]

        if value.shape != (
            192,
            18,
        ):
            fail(
                f"frontier shape drift: {mask}"
            )

    report = classify_three_way(
        by_mask
    )

    i_abc = report["I_ABC"]

    nodes = []

    for position, node in enumerate(
        FRONTIER_INDICES
    ):
        trajectory = np.asarray(
            i_abc[:, position],
            dtype=np.float64,
        )

        node_nonzero = bool(
            np.any(
                trajectory != 0
            )
        )

        nodes.append({
            "position": position,
            "node": node,
            "three_way_nonzero":
                node_nonzero,
            "first_nonzero_frame": (
                first_nonzero_frame(
                    trajectory
                )
                if node_nonzero
                else None
            ),
            "max_abs_i_abc": float(
                np.max(
                    np.abs(
                        trajectory
                    ),
                    initial=0.0,
                )
            ),
        })

    return {
        "classification":
            report["classification"],
        "symmetric_normalized_l2":
            report[
                "symmetric_normalized_l2"
            ],
        "max_abs_difference":
            report[
                "max_abs_difference"
            ],
        "node_count": len(nodes),
        "nodes": nodes,
    }


def extract_canonical_cube(
    z,
    key: str,
) -> dict[str, np.ndarray]:
    ids = z["condition_id"]
    masks = z["condition_mask"]
    reps = z["condition_replicate"]
    values = z[key]

    if len(ids) != 16:
        fail(
            "SQ-08 evidence episode count drift"
        )

    by_mask: dict[
        str,
        dict[int, np.ndarray],
    ] = {}

    for i in range(16):
        mask = str(
            masks[i]
        )

        replicate = int(
            reps[i]
        )

        condition_id = str(
            ids[i]
        )

        expected_id = (
            f"sq08:{mask}:r{replicate}"
        )

        if condition_id != expected_id:
            fail(
                "SQ-08 condition coordinate drift"
            )

        by_mask.setdefault(
            mask,
            {},
        )[replicate] = np.array(
            values[i],
            copy=True,
        )

    if set(by_mask) != set(MASKS):
        fail(
            "SQ-08 Boolean cube incomplete"
        )

    canonical = {}

    for mask in MASKS:
        pair = by_mask[mask]

        if set(pair) != {1, 2}:
            fail(
                f"replicate pair incomplete: {mask}"
            )

        if not np.array_equal(
            pair[1],
            pair[2],
        ):
            fail(
                f"replicate mismatch before analysis: {mask}"
            )

        canonical[mask] = pair[1]

    return canonical


def analyze_evidence(
    sidecar_path: Path,
) -> dict:
    with np.load(
        sidecar_path,
        allow_pickle=False,
    ) as z:

        primary = (
            extract_canonical_cube(
                z,
                "primary_positive_voltage",
            )
        )

        body = (
            extract_canonical_cube(
                z,
                "body_responder_voltage",
            )
        )

        frontier = (
            extract_canonical_cube(
                z,
                "frontier_voltage",
            )
        )

        primary_report = (
            classify_three_way(
                primary
            )
        )

        body_report = (
            classify_three_way(
                body
            )
        )

        frontier_summary = (
            frontier_report(
                frontier
            )
        )

        spike_summary = {
            "primary_total_spikes_by_mask": {},
            "body_total_spikes_by_mask": {},
            "frontier_total_spikes_by_mask": {},
        }

        for source_key, report_key in (
            (
                "primary_spikes",
                "primary_total_spikes_by_mask",
            ),
            (
                "body_responder_spikes",
                "body_total_spikes_by_mask",
            ),
            (
                "frontier_spikes",
                "frontier_total_spikes_by_mask",
            ),
        ):
            cube = extract_canonical_cube(
                z,
                source_key,
            )

            for mask in MASKS:
                spike_summary[
                    report_key
                ][mask] = int(
                    np.sum(
                        cube[mask]
                    )
                )

    return {
        "schema_version":
            "moscaquant.sq08-three-body-analysis/v1",

        "experiment": "SQ-08",

        "codename":
            "THREE BODY PROBLEM",

        "mask_semantics":
            "0=retained,1=zeroed",

        "primary_three_way": {
            "classification":
                primary_report[
                    "classification"
                ],
            "symmetric_normalized_l2":
                primary_report[
                    "symmetric_normalized_l2"
                ],
            "max_abs_difference":
                primary_report[
                    "max_abs_difference"
                ],
        },

        "body_responder_three_way": {
            "classification":
                body_report[
                    "classification"
                ],
            "symmetric_normalized_l2":
                body_report[
                    "symmetric_normalized_l2"
                ],
            "max_abs_difference":
                body_report[
                    "max_abs_difference"
                ],
        },

        "frontier_three_way":
            frontier_summary,

        "spikes":
            spike_summary,

        "claim_boundary": (
            "computational factorial analysis only; "
            "no biological or behavioral inference"
        ),
    }


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "sidecar",
        type=Path,
    )

    args = parser.parse_args()

    report = analyze_evidence(
        args.sidecar.resolve()
    )

    print(
        json.dumps(
            report,
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
