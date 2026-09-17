from __future__ import annotations

import json
import math
import os
import tomllib
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


CONFIG = Path(
    "config/controls/"
    "mq5-2-matched-noncausal-v1.toml"
)

DATA_ROOT = Path(
    os.environ.get(
        "MOSCAQUANT_DATA_ROOT",
        str(Path.home() / "moscaquant-data"),
    )
)

PROCESSED = DATA_ROOT / "processed"

CONNECTOME = PROCESSED / "connectome-baseline-v1.npz"
RETINA = PROCESSED / "visual-r1-r6-map-v1.npz"
RELAY = PROCESSED / "visual-relay-map-v1.npz"
TERRITORIES = PROCESSED / "market-retinal-territories-v1.npz"
GRADED = PROCESSED / "mq3-2-graded-visual-types-v1.npz"

CAUSAL = (
    PROCESSED
    / "mq3-2-first-onset-causal-edges-v1.json"
)

RELEASE_GAIN = 0.9981738484618123


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


def causal_nodes() -> set[int]:
    data = json.loads(
        CAUSAL.read_text(
            encoding="utf-8"
        )
    )

    nodes = set()

    for edge in data["edges"]:
        nodes.add(
            int(edge["presynaptic"])
        )
        nodes.add(
            int(edge["postsynaptic"])
        )

    return nodes


def activity_at_frame(
    connectome,
    retinal_indices,
    target_frame: int,
) -> np.ndarray:
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
            if global_frame == target_frame:
                return (
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

    raise RuntimeError(
        f"frame {target_frame} not reached"
    )


def ratio_ok(
    candidate: float,
    source: float,
    minimum: float,
    maximum: float,
) -> bool:
    if source <= 0:
        raise RuntimeError(
            "source matching value must "
            "be positive"
        )

    ratio = candidate / source

    return (
        minimum
        <= ratio
        <= maximum
    )


def main():
    with CONFIG.open("rb") as handle:
        cfg = tomllib.load(handle)

    source = int(
        cfg["source"]["model_index"]
    )

    target = int(
        cfg["source"][
            "target_model_index"
        ]
    )

    frame = int(
        cfg["source"]["match_frame"]
    )

    connectome = sparse.load_npz(
        CONNECTOME
    ).tocsr()

    retina_data = np.load(RETINA)

    retinal_indices = np.asarray(
        retina_data["neuron_index"],
        dtype=np.int32,
    )

    retina = set(
        retinal_indices.astype(
            np.int64
        ).tolist()
    )

    relay = load_index_set(RELAY)
    graded = graded_type_map()

    source_role = role(
        source,
        retina,
        relay,
        graded,
    )

    effective = activity_at_frame(
        connectome,
        retinal_indices,
        frame,
    )

    source_activity = float(
        effective[source]
    )

    if source_activity <= 0:
        raise RuntimeError(
            "source is not active at "
            "matching frame"
        )

    #
    # connectome[post, pre]
    #
    in_degree = np.asarray(
        connectome.getnnz(axis=1)
    ).ravel()

    out_degree = np.asarray(
        connectome.getnnz(axis=0)
    ).ravel()

    source_in = int(
        in_degree[source]
    )

    source_out = int(
        out_degree[source]
    )

    frozen_nodes = causal_nodes()

    #
    # Any nonzero [target, candidate]
    # means candidate has a direct
    # structural connection to target.
    #
    target_row = (
        connectome
        .getrow(target)
        .tocoo()
    )

    direct_to_target = set(
        int(x)
        for x in target_row.col
    )

    acceptance = cfg[
        "acceptance"
    ]

    min_activity = float(
        acceptance[
            "minimum_activity_ratio"
        ]
    )

    max_activity = float(
        acceptance[
            "maximum_activity_ratio"
        ]
    )

    min_in = float(
        acceptance[
            "minimum_in_degree_ratio"
        ]
    )

    max_in = float(
        acceptance[
            "maximum_in_degree_ratio"
        ]
    )

    min_out = float(
        acceptance[
            "minimum_out_degree_ratio"
        ]
    )

    max_out = float(
        acceptance[
            "maximum_out_degree_ratio"
        ]
    )

    candidates = []

    for index in range(
        connectome.shape[0]
    ):
        if index == source:
            continue

        if index == target:
            continue

        if index in frozen_nodes:
            continue

        if index in direct_to_target:
            continue

        candidate_role = role(
            index,
            retina,
            relay,
            graded,
        )

        #
        # Amendment 3:
        # Require the same functional role
        # (graded), but not exact Tm subtype.
        #
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

        candidate_in = int(
            in_degree[index]
        )

        candidate_out = int(
            out_degree[index]
        )

        if not ratio_ok(
            activity,
            source_activity,
            min_activity,
            max_activity,
        ):
            continue

        if not ratio_ok(
            candidate_in + 1.0,
            source_in + 1.0,
            min_in,
            max_in,
        ):
            continue

        if not ratio_ok(
            candidate_out + 1.0,
            source_out + 1.0,
            min_out,
            max_out,
        ):
            continue

        activity_term = abs(
            math.log(
                activity
                / source_activity
            )
        )

        in_term = abs(
            math.log(
                (candidate_in + 1.0)
                / (source_in + 1.0)
            )
        )

        out_term = abs(
            math.log(
                (candidate_out + 1.0)
                / (source_out + 1.0)
            )
        )

        degree_distance = (
            in_term
            + out_term
        )

        candidates.append(
            {
                "model_index":
                    index,

                "role":
                    source_role[0],

                "graded_type":
                    candidate_role[1],

                "activity":
                    activity,

                "in_degree":
                    candidate_in,

                "out_degree":
                    candidate_out,

                "activity_ratio":
                    activity
                    / source_activity,

                "in_degree_ratio":
                    (
                        candidate_in + 1.0
                    )
                    / (
                        source_in + 1.0
                    ),

                "out_degree_ratio":
                    (
                        candidate_out + 1.0
                    )
                    / (
                        source_out + 1.0
                    ),

                "activity_distance":
                    activity_term,

                "degree_distance":
                    degree_distance,
            }
        )

    candidates.sort(
        key=lambda item: (
            item["activity_distance"],
            item["degree_distance"],
            item["model_index"],
        )
    )

    print("=" * 80)
    print("MQ-5.2 MATCHED NON-CAUSAL CONTROL SELECTION")
    print("=" * 80)

    print()
    print("SOURCE")
    print("model index:", source)
    print("role:", source_role)
    print("activity @ frame:", source_activity)
    print("in-degree:", source_in)
    print("out-degree:", source_out)

    print()
    print(
        "eligible candidates:",
        len(candidates),
    )

    if not candidates:
        print()
        print(
            "NO VALID MATCH UNDER "
            "PRE-REGISTERED RULE"
        )
        raise SystemExit(2)

    print()
    print("TOP 10")
    print()

    for rank, item in enumerate(
        candidates[:10],
        start=1,
    ):
        print(
            rank,
            "node=",
            item["model_index"],
            "activity=",
            f'{item["activity"]:.9f}',
            "A-ratio=",
            f'{item["activity_ratio"]:.4f}',
            "in=",
            item["in_degree"],
            "in-ratio=",
            f'{item["in_degree_ratio"]:.4f}',
            "out=",
            item["out_degree"],
            "out-ratio=",
            f'{item["out_degree_ratio"]:.4f}',
            "A-dist=",
            f'{item["activity_distance"]:.8f}',
            "D-dist=",
            f'{item["degree_distance"]:.8f}',
        )

    winner = candidates[0]

    print()
    print("=" * 80)
    print("SELECTED CONTROL")
    print("=" * 80)

    for key, value in winner.items():
        print(
            f"{key}: {value}"
        )

    print()
    print(
        "Selection used frozen structure "
        "and baseline activity only."
    )

    print(
        "No intervention outcome was "
        "used in candidate selection."
    )


if __name__ == "__main__":
    main()
