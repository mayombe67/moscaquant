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
from market.normalization import (
    CausalNormalizer,
)
from market.robust_normalization import (
    RobustCausalNormalizer,
)


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
GRADED = PROCESSED / "mq3-2-graded-visual-types-v1.npz"
TERRITORIES = PROCESSED / "market-retinal-territories-v1.npz"
CAUSAL = PROCESSED / "mq3-2-first-onset-causal-edges-v1.json"

OUTPUT = (
    EXPERIMENTS
    / "conf-004a-encoder-difference-audit-v1.json"
)

RELEASE_GAIN = 0.9981738484618123


def load_edges():
    data = json.loads(
        CAUSAL.read_text(
            encoding="utf-8"
        )
    )

    return [
        {
            "source": int(
                edge["presynaptic"]
            ),
            "target": int(
                edge["postsynaptic"]
            ),
            "frame": min(
                int(x)
                for x in edge[
                    "observed_frames"
                ]
            ),
        }
        for edge in data["edges"]
    ]


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
            f"refusing to overwrite {OUTPUT}"
        )

    edges = load_edges()

    frozen_frames = {
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
        retina_data["neuron_index"],
        dtype=np.int32,
    )

    runtime_a = build_runtime(
        connectome,
        retinal_indices,
    )

    runtime_b = build_runtime(
        connectome,
        retinal_indices,
    )

    encoder_a = MarketVisionTemporalEncoder(
        TERRITORIES
    )

    encoder_b = MarketVisionTemporalEncoder(
        TERRITORIES
    )

    normalizers_a = [
        CausalNormalizer(
            window_size=64,
            min_history=8,
        )
        for _ in ASSETS
    ]

    normalizers_b = [
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

    normalized_vectors_total = 0
    normalized_vectors_different = 0
    normalized_values_different = 0

    max_normalized_abs_diff = 0.0

    stimulus_frames_total = 0
    stimulus_frames_different = 0
    stimulus_values_different = 0

    max_stimulus_abs_diff = 0.0
    sum_stimulus_abs_diff = 0.0

    neural_frames_different = 0
    max_neural_effective_abs_diff = 0.0

    relevant_frames = {}

    global_frame = 0

    for observation in range(
        OBSERVATIONS
    ):
        normalized_a = np.empty(
            (
                len(ASSETS),
                7,
            ),
            dtype=np.float32,
        )

        normalized_b = np.empty_like(
            normalized_a
        )

        for asset_index in range(
            len(ASSETS)
        ):
            window = market_window_at(
                series[asset_index],
                observation,
            )

            features = compute_features(
                window
            )

            normalized_a[
                asset_index
            ] = normalizers_a[
                asset_index
            ].transform(
                features
            )

            normalized_b[
                asset_index
            ] = normalizers_b[
                asset_index
            ].transform(
                features
            )

        normalized_vectors_total += 1

        normalized_diff = np.abs(
            normalized_a.astype(
                np.float64
            )
            - normalized_b.astype(
                np.float64
            )
        )

        if np.any(
            normalized_diff > 0.0
        ):
            normalized_vectors_different += 1

        normalized_values_different += int(
            np.count_nonzero(
                normalized_diff > 0.0
            )
        )

        if normalized_diff.size:
            max_normalized_abs_diff = max(
                max_normalized_abs_diff,
                float(
                    normalized_diff.max()
                ),
            )

        frames_a = (
            encoder_a.encode_sequence(
                normalized_a,
                frame_count=FRAME_COUNT,
            )
            * SENSORY_GAIN
        ).astype(
            np.float32
        )

        frames_b = (
            encoder_b.encode_sequence(
                normalized_b,
                frame_count=FRAME_COUNT,
            )
            * SENSORY_GAIN
        ).astype(
            np.float32
        )

        for local_frame in range(
            FRAME_COUNT
        ):
            stimulus_a = frames_a[
                local_frame
            ]

            stimulus_b = frames_b[
                local_frame
            ]

            stimulus_frames_total += 1

            stimulus_diff = np.abs(
                stimulus_a.astype(
                    np.float64
                )
                - stimulus_b.astype(
                    np.float64
                )
            )

            if np.any(
                stimulus_diff > 0.0
            ):
                stimulus_frames_different += 1

            stimulus_values_different += int(
                np.count_nonzero(
                    stimulus_diff > 0.0
                )
            )

            if stimulus_diff.size:
                max_stimulus_abs_diff = max(
                    max_stimulus_abs_diff,
                    float(
                        stimulus_diff.max()
                    ),
                )

                sum_stimulus_abs_diff += float(
                    stimulus_diff.sum()
                )

            effective_a = (
                runtime_a
                .effective_activity()
                .astype(
                    np.float64,
                    copy=True,
                )
            )

            effective_b = (
                runtime_b
                .effective_activity()
                .astype(
                    np.float64,
                    copy=True,
                )
            )

            neural_diff = np.abs(
                effective_a
                - effective_b
            )

            if np.any(
                neural_diff > 0.0
            ):
                neural_frames_different += 1

            if neural_diff.size:
                max_neural_effective_abs_diff = max(
                    max_neural_effective_abs_diff,
                    float(
                        neural_diff.max()
                    ),
                )

            if global_frame in frozen_frames:
                frame_rows = []

                for edge in edges:
                    if (
                        edge["frame"]
                        != global_frame
                    ):
                        continue

                    source = edge["source"]

                    frame_rows.append(
                        {
                            "source":
                                source,

                            "target":
                                edge[
                                    "target"
                                ],

                            "a_effective":
                                float(
                                    effective_a[
                                        source
                                    ]
                                ),

                            "b_effective":
                                float(
                                    effective_b[
                                        source
                                    ]
                                ),

                            "difference":
                                float(
                                    effective_b[
                                        source
                                    ]
                                    - effective_a[
                                        source
                                    ]
                                ),
                        }
                    )

                relevant_frames[
                    str(global_frame)
                ] = {
                    "normalized_max_abs_diff":
                        float(
                            normalized_diff.max()
                        ),

                    "stimulus_max_abs_diff":
                        float(
                            stimulus_diff.max()
                        ),

                    "stimulus_l1_difference":
                        float(
                            stimulus_diff.sum()
                        ),

                    "sources":
                        frame_rows,
                }

            runtime_a.step(
                stimulus_a
            )

            runtime_b.step(
                stimulus_b
            )

            global_frame += 1

    artifact = {
        "schema":
            "conf-004a-encoder-difference-audit-v1",

        "classification":
            "pre-intervention-encoder-difference-audit",

        "normalized": {
            "observation_count":
                normalized_vectors_total,

            "observations_with_any_difference":
                normalized_vectors_different,

            "values_with_any_difference":
                normalized_values_different,

            "max_absolute_difference":
                max_normalized_abs_diff,
        },

        "stimulus": {
            "frame_count":
                stimulus_frames_total,

            "frames_with_any_difference":
                stimulus_frames_different,

            "values_with_any_difference":
                stimulus_values_different,

            "max_absolute_difference":
                max_stimulus_abs_diff,

            "total_l1_difference":
                sum_stimulus_abs_diff,
        },

        "neural_effective_activity": {
            "frames_with_any_difference":
                neural_frames_different,

            "max_absolute_difference":
                max_neural_effective_abs_diff,
        },

        "frozen_frames":
            relevant_frames,

        "intervention_outcomes_used":
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

    print("=" * 100)
    print("CONF-004A ENCODER A/B DIFFERENCE AUDIT")
    print("=" * 100)

    print()
    print("NORMALIZED FEATURES")
    print(
        "observations:",
        normalized_vectors_total,
    )
    print(
        "observations different:",
        normalized_vectors_different,
    )
    print(
        "values different:",
        normalized_values_different,
    )
    print(
        "max abs diff:",
        max_normalized_abs_diff,
    )

    print()
    print("RETINAL STIMULUS")
    print(
        "frames:",
        stimulus_frames_total,
    )
    print(
        "frames different:",
        stimulus_frames_different,
    )
    print(
        "values different:",
        stimulus_values_different,
    )
    print(
        "max abs diff:",
        max_stimulus_abs_diff,
    )
    print(
        "total L1 diff:",
        sum_stimulus_abs_diff,
    )

    print()
    print("NEURAL EFFECTIVE ACTIVITY")
    print(
        "frames different:",
        neural_frames_different,
    )
    print(
        "max abs diff:",
        max_neural_effective_abs_diff,
    )

    print()
    print("FROZEN CAUSAL FRAMES")

    for frame in sorted(
        relevant_frames,
        key=int,
    ):
        row = relevant_frames[
            frame
        ]

        print()
        print(
            f"F{frame}: "
            f"stimulus max Δ="
            f'{row["stimulus_max_abs_diff"]:.12g}'
        )

        for source in row[
            "sources"
        ]:
            print(
                f'  {source["source"]:6d} -> '
                f'{source["target"]:6d} '
                f'A={source["a_effective"]:.12g} '
                f'B={source["b_effective"]:.12g} '
                f'Δ={source["difference"]:.12g}'
            )

    print()
    print(
        "artifact:",
        OUTPUT,
    )


if __name__ == "__main__":
    main()
