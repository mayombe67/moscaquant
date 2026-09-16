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
from brain.market_temporal import (
    MarketVisionTemporalEncoder,
)
from brain.physiology_constrained_visual_transduction import (
    PhysiologyConstrainedVisualTransductionRuntime,
)
from brain.visual_transduction import (
    VisualTransductionConfig,
)
from market.features import compute_features
from market.robust_normalization import (
    RobustCausalNormalizer,
)


DATA_ROOT = Path(
    os.environ.get(
        "MOSCAQUANT_DATA_ROOT",
        str(
            Path.home()
            / "moscaquant-data"
        ),
    )
)

PROCESSED = (
    DATA_ROOT
    / "processed"
)

EXPERIMENTS = (
    DATA_ROOT
    / "experiments"
)

CONNECTOME = (
    PROCESSED
    / "connectome-baseline-v1.npz"
)

RETINA = (
    PROCESSED
    / "visual-r1-r6-map-v1.npz"
)

RELAY = (
    PROCESSED
    / "visual-relay-map-v1.npz"
)

GRADED = (
    PROCESSED
    / "mq3-2-graded-visual-types-v1.npz"
)

TERRITORIES = (
    PROCESSED
    / "market-retinal-territories-v1.npz"
)

CAUSAL = (
    PROCESSED
    / "mq3-2-first-onset-causal-edges-v1.json"
)

OUTPUT = (
    EXPERIMENTS
    / "conf-004a-engagement-audit-v1.json"
)

RELEASE_GAIN = (
    0.9981738484618123
)


def load_edges():
    data = json.loads(
        CAUSAL.read_text(
            encoding="utf-8"
        )
    )

    rows = []

    for edge in data["edges"]:
        frames = sorted(
            int(x)
            for x in edge[
                "observed_frames"
            ]
        )

        if not frames:
            raise RuntimeError(
                "causal edge has no "
                "observed frame"
            )

        rows.append(
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

                "frame":
                    frames[0],
            }
        )

    if len(rows) != 13:
        raise RuntimeError(
            f"expected 13 edges, "
            f"got {len(rows)}"
        )

    return rows


def build_runtime(
    connectome,
    retinal_indices,
):
    return (
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


def main():
    if OUTPUT.exists():
        raise RuntimeError(
            f"refusing to overwrite "
            f"{OUTPUT}"
        )

    edges = load_edges()

    wanted_frames = {
        row["frame"]
        for row in edges
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

    runtime = build_runtime(
        connectome,
        retinal_indices,
    )

    encoder = (
        MarketVisionTemporalEncoder(
            TERRITORIES
        )
    )

    normalizers = [
        RobustCausalNormalizer(
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
        for i in range(
            len(ASSETS)
        )
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
                compute_features(
                    window
                )
            )

        frames = (
            encoder.encode_sequence(
                normalized,
                frame_count=FRAME_COUNT,
            )
        )

        for stimulus in frames:
            if (
                global_frame
                in wanted_frames
            ):
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
                np.asarray(
                    stimulus
                    * SENSORY_GAIN,
                    dtype=np.float32,
                )
            )

            global_frame += 1

    missing = (
        wanted_frames
        - set(captured)
    )

    if missing:
        raise RuntimeError(
            "missing frozen frames: "
            f"{sorted(missing)}"
        )

    rows = []

    print("=" * 100)
    print(
        "CONF-004A ENCODER-B "
        "ENGAGEMENT AUDIT"
    )
    print("=" * 100)

    for edge in edges:
        source = edge[
            "source"
        ]

        target = edge[
            "target"
        ]

        frame = edge[
            "frame"
        ]

        value = float(
            captured[
                frame
            ][source]
        )

        engaged = (
            value > 0.0
        )

        status = (
            "ENGAGED"
            if engaged
            else
            "NOT_ENGAGED_AT_FROZEN_FRAME"
        )

        row = {
            **edge,

            "source_effective_activity":
                value,

            "engagement_status":
                status,
        }

        rows.append(row)

        print(
            f"{source:6d} -> "
            f"{target:6d} "
            f"F{frame:<3d} "
            f"A={value:.12g} "
            f"{status}"
        )

    engaged_count = sum(
        row[
            "engagement_status"
        ] == "ENGAGED"
        for row in rows
    )

    artifact = {
        "schema":
            "conf-004a-engagement-audit-v1",

        "experiment":
            "CONF-004A",

        "encoder":
            "RobustCausalNormalizer",

        "classification":
            "pre-intervention-engagement-audit",

        "edge_count":
            len(rows),

        "engaged_count":
            engaged_count,

        "not_engaged_count":
            len(rows)
            - engaged_count,

        "edges":
            rows,

        "intervention_outcomes_used":
            False,

        "causal_frames_reselected":
            False,

        "matched_controls_reselected":
            False,

        "financial_semantics_used":
            False,
    }

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
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
        "engaged:",
        f"{engaged_count}/13",
    )

    print(
        "not engaged:",
        f"{13 - engaged_count}/13",
    )

    print()
    print(
        "artifact:",
        OUTPUT,
    )


if __name__ == "__main__":
    main()
