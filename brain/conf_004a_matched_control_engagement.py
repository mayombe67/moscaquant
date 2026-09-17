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
from market.robust_normalization import RobustCausalNormalizer


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

CONTROL_MAP = Path(
    "config/controls/"
    "mq5-2-generalized-control-map-v1.json"
)

OUTPUT = (
    EXPERIMENTS
    / "conf-004a-matched-control-engagement-v1.json"
)

RELEASE_GAIN = 0.9981738484618123


def main():
    if OUTPUT.exists():
        raise RuntimeError(
            f"refusing to overwrite {OUTPUT}"
        )

    control_data = json.loads(
        CONTROL_MAP.read_text(
            encoding="utf-8"
        )
    )

    rows = [
        row
        for row in control_data["edges"]
        if row[
            "matched_control_model_index"
        ] is not None
    ]

    if len(rows) != 12:
        raise RuntimeError(
            f"expected 12 matched controls, "
            f"got {len(rows)}"
        )

    wanted_frames = {
        int(row["causal_frame"])
        for row in rows
    }

    connectome = sparse.load_npz(
        CONNECTOME
    ).tocsr()

    retina_data = np.load(RETINA)

    retinal_indices = np.asarray(
        retina_data["neuron_index"],
        dtype=np.int32,
    )

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
        RobustCausalNormalizer(
            window_size=64,
            min_history=8,
        )
        for _ in ASSETS
    ]

    series = [
        synthetic_series("A", i)
        for i in range(len(ASSETS))
    ]

    captured = {}
    global_frame = 0

    for observation in range(
        OBSERVATIONS
    ):
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
                np.asarray(
                    stimulus * SENSORY_GAIN,
                    dtype=np.float32,
                )
            )

            global_frame += 1

    result_rows = []

    print("=" * 112)
    print(
        "CONF-004A FROZEN MATCHED-CONTROL "
        "ENGAGEMENT"
    )
    print("=" * 112)

    for row in rows:
        source = int(
            row["presynaptic"]
        )

        target = int(
            row["postsynaptic"]
        )

        frame = int(
            row["causal_frame"]
        )

        control = int(
            row[
                "matched_control_model_index"
            ]
        )

        value = float(
            captured[frame][control]
        )

        engaged = value > 0.0

        status = (
            "ENGAGED"
            if engaged
            else
            "NOT_ENGAGED_AT_FROZEN_FRAME"
        )

        result_rows.append(
            {
                "source":
                    source,

                "target":
                    target,

                "frame":
                    frame,

                "matched_control":
                    control,

                "matched_control_effective_activity":
                    value,

                "engagement_status":
                    status,
            }
        )

        print(
            f"{source:6d} -> "
            f"{target:6d} "
            f"F{frame:<3d} "
            f"control={control:<6d} "
            f"A={value:.12g} "
            f"{status}"
        )

    engaged_count = sum(
        row[
            "engagement_status"
        ] == "ENGAGED"
        for row in result_rows
    )

    artifact = {
        "schema":
            "conf-004a-matched-control-engagement-v1",

        "classification":
            "pre-intervention-control-engagement-audit",

        "frozen_control_count":
            12,

        "engaged_count":
            engaged_count,

        "not_engaged_count":
            12 - engaged_count,

        "controls":
            result_rows,

        "control_identities_reselected":
            False,

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

    print()
    print(
        "matched controls engaged:",
        f"{engaged_count}/12",
    )

    print(
        "matched controls not engaged:",
        f"{12 - engaged_count}/12",
    )

    print()
    print(
        "artifact:",
        OUTPUT,
    )


if __name__ == "__main__":
    main()
