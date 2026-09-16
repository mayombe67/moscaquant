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
from brain.mq5_intervention_runtime import (
    InterventionSpec,
    MQ5InterventionRuntime,
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

CONNECTOME = PROCESSED / "connectome-baseline-v1.npz"
RETINA = PROCESSED / "visual-r1-r6-map-v1.npz"
RELAY = PROCESSED / "visual-relay-map-v1.npz"
TERRITORIES = PROCESSED / "market-retinal-territories-v1.npz"
GRADED = PROCESSED / "mq3-2-graded-visual-types-v1.npz"

RELEASE_GAIN = 0.9981738484618123

SOURCE = 43417
TARGET = 656

TEST_FRAMES = (
    143,
    144,
    145,
    146,
    147,
)


def build_runtime(
    connectome,
    retinal_indices,
    intervention=None,
):
    interventions = (
        ()
        if intervention is None
        else (intervention,)
    )

    return MQ5InterventionRuntime(
        connectome=connectome,
        retinal_indices=retinal_indices,
        relay_artifact=RELAY,
        graded_artifact=GRADED,
        config=VisualTransductionConfig(
            release_gain=RELEASE_GAIN,
        ),
        interventions=interventions,
    )


def run(
    connectome,
    retinal_indices,
    intervention=None,
):
    runtime = build_runtime(
        connectome,
        retinal_indices,
        intervention,
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

    voltage = []
    source_effective = []

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

            features = compute_features(
                window
            )

            normalized[
                asset_index
            ] = normalizers[
                asset_index
            ].transform(
                features
            )

        frames = encoder.encode_sequence(
            normalized,
            frame_count=FRAME_COUNT,
        )

        for stimulus in frames:
            runtime.set_intervention_frame(
                global_frame
            )

            effective = (
                runtime.effective_activity()
            )

            source_effective.append(
                float(
                    effective[
                        SOURCE
                    ]
                )
            )

            runtime.step(
                stimulus
                * SENSORY_GAIN
            )

            voltage.append(
                float(
                    runtime.voltage[
                        TARGET
                    ]
                )
            )

            global_frame += 1

    voltage = np.asarray(
        voltage,
        dtype=np.float64,
    )

    source_effective = np.asarray(
        source_effective,
        dtype=np.float64,
    )

    positive = np.flatnonzero(
        voltage > 0.0
    )

    first_positive = (
        int(positive[0])
        if len(positive)
        else None
    )

    peak_frame = int(
        np.argmax(voltage)
    )

    return {
        "voltage":
            voltage,

        "source_effective":
            source_effective,

        "first_positive_frame":
            first_positive,

        "peak_frame":
            peak_frame,

        "peak_voltage":
            float(
                voltage[
                    peak_frame
                ]
            ),

        "integrated_positive_voltage":
            float(
                np.maximum(
                    voltage,
                    0.0,
                ).sum()
            ),

        "positive_frame_count":
            int(
                np.count_nonzero(
                    voltage > 0.0
                )
            ),
    }


def main():
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

    baseline = run(
        connectome,
        retinal_indices,
    )

    print("=" * 88)
    print("MQ-5.2 TIMING-SHIFT CONTROL")
    print("=" * 88)

    print()
    print("BASELINE")
    print(
        "first=",
        baseline[
            "first_positive_frame"
        ],
        "peak_frame=",
        baseline[
            "peak_frame"
        ],
        "peak=",
        baseline[
            "peak_voltage"
        ],
        "integrated=",
        baseline[
            "integrated_positive_voltage"
        ],
    )

    results = {}

    for frame in TEST_FRAMES:
        spec = InterventionSpec(
            experiment_id=(
                "mq5-2-timing-shift-"
                f"{frame}"
            ),
            target_model_index=SOURCE,
            attenuation=1.0,
            start_frame=frame,
            end_frame=frame,
            mode="silence",
        )

        result = run(
            connectome,
            retinal_indices,
            spec,
        )

        results[str(frame)] = {
            "source_effective_at_frame":
                float(
                    result[
                        "source_effective"
                    ][
                        frame
                    ]
                ),

            "target_voltage_at_145":
                float(
                    result[
                        "voltage"
                    ][145]
                ),

            "first_positive_frame":
                result[
                    "first_positive_frame"
                ],

            "peak_frame":
                result[
                    "peak_frame"
                ],

            "peak_voltage":
                result[
                    "peak_voltage"
                ],

            "integrated_positive_voltage":
                result[
                    "integrated_positive_voltage"
                ],

            "positive_frame_count":
                result[
                    "positive_frame_count"
                ],
        }

        print()
        print(
            "silence @",
            frame,
        )

        print(
            "source@frame=",
            result[
                "source_effective"
            ][
                frame
            ],
            "targetV@145=",
            result[
                "voltage"
            ][145],
            "first=",
            result[
                "first_positive_frame"
            ],
            "peak_frame=",
            result[
                "peak_frame"
            ],
            "peak=",
            result[
                "peak_voltage"
            ],
            "integrated=",
            result[
                "integrated_positive_voltage"
            ],
        )

    output = (
        DATA_ROOT
        / "experiments"
        / "mq5-timing-shift-43417-to-656-v1.json"
    )

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    if output.exists():
        raise RuntimeError(
            f"refusing to overwrite {output}"
        )

    output.write_text(
        json.dumps(
            {
                "schema":
                    "mq5-timing-shift-v1",

                "source":
                    SOURCE,

                "target":
                    TARGET,

                "causal_frame":
                    145,

                "tested_frames":
                    list(TEST_FRAMES),

                "baseline": {
                    "first_positive_frame":
                        baseline[
                            "first_positive_frame"
                        ],

                    "peak_frame":
                        baseline[
                            "peak_frame"
                        ],

                    "peak_voltage":
                        baseline[
                            "peak_voltage"
                        ],

                    "integrated_positive_voltage":
                        baseline[
                            "integrated_positive_voltage"
                        ],

                    "positive_frame_count":
                        baseline[
                            "positive_frame_count"
                        ],
                },

                "results":
                    results,

                "interpretation_status":
                    "NOT_YET_INTERPRETED",

                "financial_semantics_used":
                    False,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    print()
    print("artifact:", output)


if __name__ == "__main__":
    main()
