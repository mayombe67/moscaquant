from __future__ import annotations

import json
import math
import os
from pathlib import Path

import numpy as np
from scipy import sparse

from brain.market_replay import (
    ASSETS,
    FRAME_COUNT,
    OBSERVATIONS,
    SENSORY_GAIN,
    market_window_at,
    synthetic_series,
)
from brain.market_temporal import MarketVisionTemporalEncoder
from brain.physiology_constrained_visual_transduction import (
    PhysiologyConstrainedVisualTransductionRuntime,
)
from brain.visual_transduction import VisualTransductionConfig
from market.features import compute_features
from market.normalization import CausalNormalizer


DATA_ROOT = Path(
    os.environ.get(
        "MOSCAQUANT_DATA_ROOT",
        str(Path.home() / "moscaquant-data"),
    )
)

PROCESSED = DATA_ROOT / "processed"
EXPERIMENTS = DATA_ROOT / "experiments"

CONNECTOME = PROCESSED / "connectome-baseline-v1.npz"
RETINA = PROCESSED / "visual-r1-r6-map-v1.npz"
RELAY = PROCESSED / "visual-relay-map-v1.npz"
TERRITORIES = PROCESSED / "market-retinal-territories-v1.npz"
GRADED = PROCESSED / "mq3-2-graded-visual-types-v1.npz"

CAUSAL = (
    PROCESSED
    / "mq3-2-first-onset-causal-edges-v1.json"
)

OUTPUT = (
    EXPERIMENTS
    / "mq5-control-feasibility-scan-v1.json"
)

RELEASE_GAIN = 0.9981738484618123

MIN_ACTIVITY_RATIO = 0.25
MAX_ACTIVITY_RATIO = 4.0


def load_index_set(
    path: Path,
) -> set[int]:
    data = np.load(path)

    return set(
        np.asarray(
            data["neuron_index"],
            dtype=np.int64,
        ).tolist()
    )


def graded_type_map() -> dict[int, str]:
    data = np.load(GRADED)

    indices = np.asarray(
        data["neuron_index"],
        dtype=np.int64,
    )

    types = np.asarray(
        data["type"]
    ).astype(str)

    return {
        int(index): str(cell_type)
        for index, cell_type
        in zip(indices, types)
    }


def role(
    index: int,
    retina: set[int],
    relay: set[int],
    graded: dict[int, str],
) -> tuple[str, str | None]:
    if index in retina:
        return ("retina", None)

    if index in relay:
        return ("relay", None)

    if index in graded:
        return (
            "graded",
            graded[index],
        )

    return ("other", None)


def frozen_causal_nodes(
    data: dict,
) -> set[int]:
    nodes = set()

    for edge in data["edges"]:
        nodes.add(
            int(edge["presynaptic"])
        )
        nodes.add(
            int(edge["postsynaptic"])
        )

    return nodes


def capture_effective_activity_by_frame(
    connectome,
    retinal_indices,
    wanted_frames: set[int],
) -> dict[int, np.ndarray]:
    runtime = (
        PhysiologyConstrainedVisualTransductionRuntime(
            connectome=connectome,
            retinal_indices=retinal_indices,
            relay_artifact=RELAY,
            graded_artifact=GRADED,
            config=VisualTransductionConfig(
                release_gain=RELEASE_GAIN,
            ),
        )
    )

    encoder = MarketVisionTemporalEncoder(
        TERRITORIES
    )

    normalizers = [
        CausalNormalizer(
            window_size=64,
            min_history=8,
        )
        for _ in ASSETS
    ]

    series = [
        synthetic_series(
            "A",
            i,
        )
        for i in range(len(ASSETS))
    ]

    captured = {}
    global_frame = 0

    for observation in range(
        OBSERVATIONS
    ):
        normalized = np.empty(
            (
                len(ASSETS),
                7,
            ),
            dtype=np.float32,
        )

        for asset_index in range(
            len(ASSETS)
        ):
            window = market_window_at(
                series[asset_index],
                observation,
            )

            normalized[
                asset_index
            ] = normalizers[
                asset_index
            ].transform(
                compute_features(window)
            )

        frames = encoder.encode_sequence(
            normalized,
            frame_count=FRAME_COUNT,
        )

        for stimulus in frames:
            if global_frame in wanted_frames:
                captured[
                    global_frame
                ] = (
                    runtime
                    .effective_activity()
                    .astype(
                        np.float64,
                        copy=True,
                    )
                )

            runtime.step(
                stimulus
                * SENSORY_GAIN
            )

            global_frame += 1

    missing = (
        wanted_frames
        - set(captured)
    )

    if missing:
        raise RuntimeError(
            f"missing requested frames: "
            f"{sorted(missing)}"
        )

    return captured


def best_match_for_edge(
    source: int,
    target: int,
    frame: int,
    effective: np.ndarray,
    connectome,
    causal_nodes: set[int],
    retina: set[int],
    relay: set[int],
    graded: dict[int, str],
    in_degree: np.ndarray,
    out_degree: np.ndarray,
) -> dict:
    source_role = role(
        source,
        retina,
        relay,
        graded,
    )

    source_activity = float(
        effective[source]
    )

    if source_activity <= 0:
        return {
            "available": False,
            "reason":
                "source_inactive_at_causal_frame",
            "source_role":
                source_role[0],
            "source_type":
                source_role[1],
            "source_activity":
                source_activity,
            "active_same_role_count":
                0,
            "in_window_same_role_count":
                0,
        }

    minimum = (
        source_activity
        * MIN_ACTIVITY_RATIO
    )

    maximum = (
        source_activity
        * MAX_ACTIVITY_RATIO
    )

    target_row = (
        connectome
        .getrow(target)
        .tocoo()
    )

    direct_to_target = set(
        int(x)
        for x in target_row.col
    )

    same_role_active = []
    in_window = []
    candidates = []

    source_in = int(
        in_degree[source]
    )

    source_out = int(
        out_degree[source]
    )

    for index in range(
        connectome.shape[0]
    ):
        candidate_role = role(
            index,
            retina,
            relay,
            graded,
        )

        if (
            candidate_role[0]
            != source_role[0]
        ):
            continue

        activity = float(
            effective[index]
        )

        if activity <= 0:
            continue

        same_role_active.append(
            index
        )

        if not (
            minimum
            <= activity
            <= maximum
        ):
            continue

        in_window.append(
            index
        )

        if index in {
            source,
            target,
        }:
            continue

        if index in causal_nodes:
            continue

        if index in direct_to_target:
            continue

        candidate_in = int(
            in_degree[index]
        )

        candidate_out = int(
            out_degree[index]
        )

        activity_distance = abs(
            math.log(
                activity
                / source_activity
            )
        )

        degree_distance = (
            abs(
                math.log(
                    (
                        candidate_in + 1.0
                    )
                    / (
                        source_in + 1.0
                    )
                )
            )
            +
            abs(
                math.log(
                    (
                        candidate_out + 1.0
                    )
                    / (
                        source_out + 1.0
                    )
                )
            )
        )

        candidates.append(
            {
                "model_index":
                    int(index),

                "role":
                    candidate_role[0],

                "graded_type":
                    candidate_role[1],

                "activity":
                    activity,

                "activity_ratio":
                    activity
                    / source_activity,

                "in_degree":
                    candidate_in,

                "out_degree":
                    candidate_out,

                "activity_distance":
                    activity_distance,

                "degree_distance":
                    degree_distance,
            }
        )

    candidates.sort(
        key=lambda item: (
            item[
                "activity_distance"
            ],
            item[
                "degree_distance"
            ],
            item[
                "model_index"
            ],
        )
    )

    return {
        "available":
            bool(candidates),

        "reason":
            (
                "valid_match_found"
                if candidates
                else
                "no_valid_match"
            ),

        "source_role":
            source_role[0],

        "source_type":
            source_role[1],

        "source_activity":
            source_activity,

        "activity_window": [
            minimum,
            maximum,
        ],

        "active_same_role_count":
            len(
                same_role_active
            ),

        "in_window_same_role_count":
            len(
                in_window
            ),

        "selected_control":
            (
                candidates[0]
                if candidates
                else None
            ),

        "candidate_count":
            len(candidates),
    }


def main():
    causal_data = json.loads(
        CAUSAL.read_text(
            encoding="utf-8"
        )
    )

    edges = []

    for edge in causal_data["edges"]:
        frames = [
            int(x)
            for x in edge[
                "observed_frames"
            ]
        ]

        if not frames:
            raise RuntimeError(
                "causal edge has no "
                "observed frames"
            )

        edges.append(
            {
                "source":
                    int(
                        edge[
                            "presynaptic"
                        ]
                    ),

                "target":
                    int(
                        edge[
                            "postsynaptic"
                        ]
                    ),

                "weight":
                    float(
                        edge[
                            "weight"
                        ]
                    ),

                "frame":
                    min(frames),
            }
        )

    wanted_frames = {
        item["frame"]
        for item in edges
    }

    connectome = sparse.load_npz(
        CONNECTOME
    ).tocsr()

    retina_data = np.load(
        RETINA
    )

    retinal_indices = np.asarray(
        retina_data[
            "neuron_index"
        ],
        dtype=np.int32,
    )

    retina = set(
        retinal_indices.astype(
            np.int64
        ).tolist()
    )

    relay = load_index_set(
        RELAY
    )

    graded = graded_type_map()

    causal_nodes = (
        frozen_causal_nodes(
            causal_data
        )
    )

    in_degree = np.asarray(
        connectome.getnnz(
            axis=1
        )
    ).ravel()

    out_degree = np.asarray(
        connectome.getnnz(
            axis=0
        )
    ).ravel()

    effective_by_frame = (
        capture_effective_activity_by_frame(
            connectome,
            retinal_indices,
            wanted_frames,
        )
    )

    rows = []

    print("=" * 112)
    print("MQ-5.2 CONTROL FEASIBILITY SCAN")
    print("=" * 112)

    for item in edges:
        source = item["source"]
        target = item["target"]
        frame = item["frame"]

        result = best_match_for_edge(
            source=source,
            target=target,
            frame=frame,
            effective=effective_by_frame[
                frame
            ],
            connectome=connectome,
            causal_nodes=causal_nodes,
            retina=retina,
            relay=relay,
            graded=graded,
            in_degree=in_degree,
            out_degree=out_degree,
        )

        row = {
            **item,
            **result,
        }

        rows.append(row)

        control = (
            result[
                "selected_control"
            ]
        )

        control_text = (
            str(
                control[
                    "model_index"
                ]
            )
            if control
            else "-"
        )

        print(
            f'{source:6d} -> '
            f'{target:6d} '
            f'F{frame:<3d} '
            f'role={result["source_role"]:<7s} '
            f'type={str(result["source_type"]):<4s} '
            f'A={result["source_activity"]:.9f} '
            f'active={result["active_same_role_count"]:<4d} '
            f'window={result["in_window_same_role_count"]:<4d} '
            f'candidates={result["candidate_count"]:<4d} '
            f'control={control_text}'
        )

    available = sum(
        1
        for row in rows
        if row["available"]
    )

    unavailable = (
        len(rows)
        - available
    )

    artifact = {
        "schema":
            "mq5-control-feasibility-scan-v1",

        "classification":
            "pre-outcome-control-feasibility",

        "activity_ratio_window": [
            MIN_ACTIVITY_RATIO,
            MAX_ACTIVITY_RATIO,
        ],

        "selection_rule":
            (
                "same functional role; "
                "positive activity at causal frame; "
                "activity ratio within frozen window; "
                "exclude source/target; "
                "exclude frozen causal nodes; "
                "exclude direct structural edge to target; "
                "rank by activity distance, then degree distance, "
                "then model index"
            ),

        "edge_count":
            len(rows),

        "matched_control_available":
            available,

        "matched_control_unavailable":
            unavailable,

        "edges":
            rows,

        "intervention_outcomes_used":
            False,

        "financial_semantics_used":
            False,
    }

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    if OUTPUT.exists():
        raise RuntimeError(
            f"refusing to overwrite "
            f"{OUTPUT}"
        )

    OUTPUT.write_text(
        json.dumps(
            artifact,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    print()
    print(
        "matched controls available:",
        available,
    )

    print(
        "matched controls unavailable:",
        unavailable,
    )

    print()
    print(
        "artifact:",
        OUTPUT,
    )


if __name__ == "__main__":
    main()
