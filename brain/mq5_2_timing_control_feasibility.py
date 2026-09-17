from __future__ import annotations

import json
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
    / "mq5-timing-control-feasibility-v1.json"
)

FROZEN_MAP = Path(
    "config/controls/"
    "mq5-2-generalized-timing-map-v1.json"
)

RELEASE_GAIN = 0.9981738484618123
MAX_OFFSET = 4


def capture_activity(
    connectome,
    retinal_indices,
    wanted_frames,
):
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

    for observation in range(OBSERVATIONS):
        normalized = np.empty(
            (len(ASSETS), 7),
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

    return captured


def candidate_order(
    causal_frame,
):
    #
    # Nearest first.
    # Earlier frame wins equal-distance tie.
    #
    result = []

    for distance in range(
        1,
        MAX_OFFSET + 1,
    ):
        result.extend(
            (
                causal_frame - distance,
                causal_frame + distance,
            )
        )

    return result


def main():
    causal_data = json.loads(
        CAUSAL.read_text(
            encoding="utf-8"
        )
    )

    edges = []

    wanted_frames = set()

    for edge in causal_data["edges"]:
        observed = sorted(
            int(x)
            for x in edge[
                "observed_frames"
            ]
        )

        if not observed:
            raise RuntimeError(
                "causal edge without observed frame"
            )

        causal_frame = observed[0]

        item = {
            "source":
                int(edge["presynaptic"]),

            "target":
                int(edge["postsynaptic"]),

            "observed_frames":
                observed,

            "causal_frame":
                causal_frame,
        }

        edges.append(item)

        wanted_frames.add(
            causal_frame
        )

        for frame in candidate_order(
            causal_frame
        ):
            if frame >= 0:
                wanted_frames.add(frame)

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

    activity = capture_activity(
        connectome,
        retinal_indices,
        wanted_frames,
    )

    rows = []

    print("=" * 104)
    print("MQ-5.2 TIMING-CONTROL FEASIBILITY")
    print("=" * 104)

    for edge in edges:
        source = edge["source"]
        target = edge["target"]
        causal_frame = edge[
            "causal_frame"
        ]

        observed = set(
            edge["observed_frames"]
        )

        source_at_causal = float(
            activity[
                causal_frame
            ][
                source
            ]
        )

        selected = None
        candidates = []

        for frame in candidate_order(
            causal_frame
        ):
            if frame < 0:
                continue

            if frame in observed:
                continue

            if frame not in activity:
                continue

            value = float(
                activity[
                    frame
                ][
                    source
                ]
            )

            candidate = {
                "frame":
                    frame,

                "offset":
                    frame - causal_frame,

                "source_activity":
                    value,

                "activity_ratio_to_causal":
                    (
                        value
                        / source_at_causal
                        if source_at_causal > 0
                        else None
                    ),
            }

            candidates.append(
                candidate
            )

            if (
                selected is None
                and value > 0.0
            ):
                selected = candidate

        row = {
            **edge,

            "source_activity_at_causal_frame":
                source_at_causal,

            "timing_control_available":
                selected is not None,

            "selected_timing_control":
                selected,

            "candidate_frames":
                candidates,
        }

        rows.append(row)

        if selected:
            control_text = (
                f'F{selected["frame"]} '
                f'({selected["offset"]:+d}) '
                f'A={selected["source_activity"]:.12g}'
            )
        else:
            control_text = "NONE"

        print(
            f'{source:6d} -> '
            f'{target:6d} '
            f'causal=F{causal_frame:<3d} '
            f'A={source_at_causal:.12g} '
            f'timing={control_text}'
        )

    available = sum(
        int(
            row[
                "timing_control_available"
            ]
        )
        for row in rows
    )

    artifact = {
        "schema":
            "mq5-timing-control-feasibility-v1",

        "classification":
            "pre-outcome-control-feasibility",

        "selection_rule":
            (
                "nearest baseline frame outside "
                "the edge's frozen observed frames "
                "where the same source has positive "
                "effective activity; search +/-4; "
                "earlier frame wins equal-distance tie"
            ),

        "maximum_offset":
            MAX_OFFSET,

        "edge_count":
            len(rows),

        "timing_control_available":
            available,

        "timing_control_unavailable":
            len(rows) - available,

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
            f"refusing to overwrite {OUTPUT}"
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

    frozen = {
        "schema":
            "mq5-2-generalized-timing-map-v1",

        "status":
            "FROZEN_BEFORE_GENERALIZED_INTERVENTION_OUTCOMES",

        "selection_rule":
            artifact[
                "selection_rule"
            ],

        "maximum_offset":
            MAX_OFFSET,

        "edges": [
            {
                "presynaptic":
                    row["source"],

                "postsynaptic":
                    row["target"],

                "causal_frame":
                    row["causal_frame"],

                "observed_frames":
                    row["observed_frames"],

                "timing_control_available":
                    row[
                        "timing_control_available"
                    ],

                "timing_control_frame":
                    (
                        row[
                            "selected_timing_control"
                        ][
                            "frame"
                        ]
                        if row[
                            "selected_timing_control"
                        ]
                        else None
                    ),

                "timing_control_offset":
                    (
                        row[
                            "selected_timing_control"
                        ][
                            "offset"
                        ]
                        if row[
                            "selected_timing_control"
                        ]
                        else None
                    ),
            }
            for row in rows
        ],

        "intervention_outcomes_used":
            False,

        "financial_semantics_used":
            False,
    }

    if FROZEN_MAP.exists():
        raise RuntimeError(
            f"refusing to overwrite "
            f"{FROZEN_MAP}"
        )

    FROZEN_MAP.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    FROZEN_MAP.write_text(
        json.dumps(
            frozen,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    print()
    print(
        "timing controls available:",
        available,
    )

    print(
        "timing controls unavailable:",
        len(rows) - available,
    )

    print()
    print("audit:", OUTPUT)
    print("frozen map:", FROZEN_MAP)


if __name__ == "__main__":
    main()
