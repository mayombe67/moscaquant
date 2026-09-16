from __future__ import annotations

import hashlib
import json
import os
import subprocess
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
from brain.market_temporal import (
    MarketVisionTemporalEncoder,
)
from brain.mq5_intervention_runtime import (
    InterventionSpec,
    MQ5InterventionRuntime,
)
from brain.visual_transduction import (
    VisualTransductionConfig,
)
from market.features import compute_features
from market.normalization import CausalNormalizer


CONFIG_PATH = Path(
    "config/controls/"
    "mq5-2-intervention-harness-v1.toml"
)

DATA_ROOT = Path(
    os.environ.get(
        "MOSCAQUANT_DATA_ROOT",
        str(Path.home() / "moscaquant-data"),
    )
)

PROCESSED = DATA_ROOT / "processed"
EXPERIMENTS = DATA_ROOT / "experiments"

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

TERRITORIES = (
    PROCESSED
    / "market-retinal-territories-v1.npz"
)

GRADED = (
    PROCESSED
    / "mq3-2-graded-visual-types-v1.npz"
)

CAUSAL_EDGES = (
    PROCESSED
    / "mq3-2-first-onset-causal-edges-v1.json"
)

RELEASE_GAIN = 0.9981738484618123

OUTPUT_JSON = (
    EXPERIMENTS
    / "mq5-intervention-43417-to-656-v1.json"
)

OUTPUT_NPZ = (
    EXPERIMENTS
    / "mq5-intervention-43417-to-656-v1.npz"
)


def sha256_file(
    path: Path,
) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        while True:
            block = handle.read(
                1024 * 1024
            )

            if not block:
                break

            digest.update(block)

    return digest.hexdigest()


def git_commit() -> str:
    try:
        return subprocess.check_output(
            [
                "git",
                "rev-parse",
                "HEAD",
            ],
            text=True,
        ).strip()
    except Exception:
        return "UNKNOWN"


def load_config() -> dict:
    with CONFIG_PATH.open("rb") as handle:
        return tomllib.load(handle)


def frozen_paths() -> tuple[Path, ...]:
    return (
        CONNECTOME,
        RETINA,
        RELAY,
        TERRITORIES,
        GRADED,
        CAUSAL_EDGES,
    )


def snapshot_hashes() -> dict[str, str]:
    result = {}

    for path in frozen_paths():
        if not path.exists():
            raise FileNotFoundError(path)

        result[str(path)] = (
            sha256_file(path)
        )

    return result


def validate_edge(
    source: int,
    target: int,
    frame: int,
) -> dict:
    data = json.loads(
        CAUSAL_EDGES.read_text(
            encoding="utf-8"
        )
    )

    matches = [
        edge
        for edge in data["edges"]
        if (
            int(edge["presynaptic"])
            == source
            and int(edge["postsynaptic"])
            == target
        )
    ]

    if len(matches) != 1:
        raise RuntimeError(
            "expected exactly one frozen "
            f"causal edge {source}->{target}; "
            f"found {len(matches)}"
        )

    edge = matches[0]

    observed_frames = [
        int(x)
        for x in edge[
            "observed_frames"
        ]
    ]

    if frame not in observed_frames:
        raise RuntimeError(
            f"frozen edge {source}->{target} "
            f"does not contain frame {frame}: "
            f"{observed_frames}"
        )

    return edge


def build_runtime(
    connectome,
    retinal_indices,
    interventions=(),
):
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


def run_condition(
    connectome,
    retinal_indices,
    condition: str,
    source: int,
    target: int,
    intervention: InterventionSpec | None,
) -> dict:
    runtime = build_runtime(
        connectome,
        retinal_indices,
        interventions=(
            ()
            if intervention is None
            else (intervention,)
        ),
    )

    encoder = MarketVisionTemporalEncoder(
        TERRITORIES
    )

    if condition != "neutral":
        normalizers = [
            CausalNormalizer(
                window_size=64,
                min_history=8,
            )
            for _ in ASSETS
        ]

        series = [
            synthetic_series(
                condition,
                i,
            )
            for i in range(
                len(ASSETS)
            )
        ]

    source_effective = []
    target_voltage = []
    target_spikes = []

    global_frame = 0

    for observation in range(
        OBSERVATIONS
    ):
        if condition == "neutral":
            normalized = np.zeros(
                (
                    len(ASSETS),
                    7,
                ),
                dtype=np.float32,
            )

        else:
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
                    series[
                        asset_index
                    ],
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

            #
            # This is the exact presynaptic
            # effective activity that runtime.step()
            # will use for this frame.
            #
            effective = (
                runtime.effective_activity()
            )

            source_effective.append(
                float(
                    effective[
                        source
                    ]
                )
            )

            runtime.step(
                stimulus
                * SENSORY_GAIN
            )

            target_voltage.append(
                float(
                    runtime.voltage[
                        target
                    ]
                )
            )

            target_spikes.append(
                float(
                    runtime.spikes[
                        target
                    ]
                )
            )

            global_frame += 1

    expected_frames = (
        OBSERVATIONS
        * FRAME_COUNT
    )

    if global_frame != expected_frames:
        raise RuntimeError(
            "unexpected replay frame count: "
            f"{global_frame} != "
            f"{expected_frames}"
        )

    voltage = np.asarray(
        target_voltage,
        dtype=np.float64,
    )

    source_activity = np.asarray(
        source_effective,
        dtype=np.float64,
    )

    spikes = np.asarray(
        target_spikes,
        dtype=np.float64,
    )

    positive_frames = np.flatnonzero(
        voltage > 0.0
    )

    first_positive = (
        int(positive_frames[0])
        if len(positive_frames)
        else None
    )

    peak_frame = int(
        np.argmax(voltage)
    )

    return {
        "source_effective":
            source_activity,

        "target_voltage":
            voltage,

        "target_spikes":
            spikes,

        "metrics": {
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

            "positive_frame_count":
                int(
                    np.count_nonzero(
                        voltage > 0.0
                    )
                ),

            "integrated_positive_voltage":
                float(
                    np.maximum(
                        voltage,
                        0.0,
                    ).sum()
                ),

            "target_spike_count":
                int(
                    np.count_nonzero(
                        spikes > 0.0
                    )
                ),
        },
    }


def main() -> None:
    config = load_config()

    experiment = config[
        "experiment"
    ]

    edge_config = config[
        "causal_edge"
    ]

    intervention_config = config[
        "intervention"
    ]

    source = int(
        edge_config[
            "presynaptic_model_index"
        ]
    )

    target = int(
        edge_config[
            "postsynaptic_model_index"
        ]
    )

    causal_frame = int(
        edge_config[
            "causal_frame"
        ]
    )

    condition = str(
        experiment[
            "condition"
        ]
    )

    start_frame = int(
        intervention_config[
            "start_frame"
        ]
    )

    end_frame = int(
        intervention_config[
            "end_frame"
        ]
    )

    if (
        start_frame != causal_frame
        or end_frame != causal_frame
    ):
        raise RuntimeError(
            "MQ-5.2 first validation must "
            "intervene exactly at causal frame"
        )

    attenuation_levels = [
        float(x)
        for x in intervention_config[
            "attenuation_levels"
        ]
    ]

    if attenuation_levels != [
        0.0,
        0.25,
        0.50,
        0.75,
        1.0,
    ]:
        raise RuntimeError(
            "unexpected preregistered "
            "attenuation levels"
        )

    EXPERIMENTS.mkdir(
        parents=True,
        exist_ok=True,
    )

    if OUTPUT_JSON.exists():
        raise RuntimeError(
            f"refusing to overwrite "
            f"{OUTPUT_JSON}"
        )

    if OUTPUT_NPZ.exists():
        raise RuntimeError(
            f"refusing to overwrite "
            f"{OUTPUT_NPZ}"
        )

    hashes_before = snapshot_hashes()

    edge = validate_edge(
        source,
        target,
        causal_frame,
    )

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

    print("=" * 80)
    print("MQ-5.2 INTERVENTION HARNESS")
    print("=" * 80)

    print(
        "experiment:",
        experiment["id"],
    )

    print(
        "edge:",
        source,
        "->",
        target,
    )

    print(
        "causal frame:",
        causal_frame,
    )

    print(
        "frozen weight:",
        edge["weight"],
    )

    print()
    print("running baseline...")

    baseline = run_condition(
        connectome,
        retinal_indices,
        condition,
        source,
        target,
        intervention=None,
    )

    print("running sham...")

    sham_spec = InterventionSpec(
        experiment_id=(
            experiment["id"]
            + "-sham"
        ),
        target_model_index=source,
        attenuation=0.0,
        start_frame=start_frame,
        end_frame=end_frame,
        mode="sham",
    )

    sham = run_condition(
        connectome,
        retinal_indices,
        condition,
        source,
        target,
        intervention=sham_spec,
    )

    baseline_sham_voltage_exact = (
        np.array_equal(
            baseline[
                "target_voltage"
            ],
            sham[
                "target_voltage"
            ],
        )
    )

    baseline_sham_source_exact = (
        np.array_equal(
            baseline[
                "source_effective"
            ],
            sham[
                "source_effective"
            ],
        )
    )

    if not (
        baseline_sham_voltage_exact
        and baseline_sham_source_exact
    ):
        raise RuntimeError(
            "ZERO-EFFECT SHAM FAILED: "
            "baseline and sham differ"
        )

    baseline_source_at_frame = float(
        baseline[
            "source_effective"
        ][
            causal_frame
        ]
    )

    if baseline_source_at_frame <= 0.0:
        raise RuntimeError(
            "frozen causal source is not "
            "active at causal frame"
        )

    runs = {
        "baseline": baseline,
        "sham": sham,
    }

    dose_keys = []

    for attenuation in (
        0.25,
        0.50,
        0.75,
        1.00,
    ):
        percent = int(
            round(
                attenuation
                * 100
            )
        )

        key = (
            f"attenuation_{percent}"
        )

        mode = (
            "silence"
            if attenuation == 1.0
            else "attenuate"
        )

        spec = InterventionSpec(
            experiment_id=(
                experiment["id"]
                + f"-{percent}"
            ),
            target_model_index=source,
            attenuation=attenuation,
            start_frame=start_frame,
            end_frame=end_frame,
            mode=mode,
        )

        print(
            f"running {percent}% "
            "attenuation..."
        )

        result = run_condition(
            connectome,
            retinal_indices,
            condition,
            source,
            target,
            intervention=spec,
        )

        expected_source = (
            baseline_source_at_frame
            * (
                1.0
                - attenuation
            )
        )

        actual_source = float(
            result[
                "source_effective"
            ][
                causal_frame
            ]
        )

        if not np.isclose(
            actual_source,
            expected_source,
            rtol=1e-6,
            atol=1e-12,
        ):
            raise RuntimeError(
                "intervention telemetry "
                f"mismatch at {percent}%: "
                f"{actual_source} != "
                f"{expected_source}"
            )

        runs[key] = result
        dose_keys.append(key)

    #
    # Deterministic reproducibility check.
    #
    print(
        "running deterministic "
        "100% replicate..."
    )

    replicate_spec = InterventionSpec(
        experiment_id=(
            experiment["id"]
            + "-100-replicate"
        ),
        target_model_index=source,
        attenuation=1.0,
        start_frame=start_frame,
        end_frame=end_frame,
        mode="silence",
    )

    replicate_100 = run_condition(
        connectome,
        retinal_indices,
        condition,
        source,
        target,
        intervention=replicate_spec,
    )

    reproducible_100 = (
        np.array_equal(
            runs[
                "attenuation_100"
            ][
                "target_voltage"
            ],
            replicate_100[
                "target_voltage"
            ],
        )
        and np.array_equal(
            runs[
                "attenuation_100"
            ][
                "source_effective"
            ],
            replicate_100[
                "source_effective"
            ],
        )
    )

    if not reproducible_100:
        raise RuntimeError(
            "deterministic 100% "
            "replicate failed"
        )

    hashes_after = snapshot_hashes()

    frozen_unchanged = (
        hashes_before
        == hashes_after
    )

    if not frozen_unchanged:
        raise RuntimeError(
            "FROZEN ARTIFACT HASH CHANGED"
        )

    conditions_json = {}

    for key, result in runs.items():
        metrics = dict(
            result[
                "metrics"
            ]
        )

        metrics[
            "source_effective_at_causal_frame"
        ] = float(
            result[
                "source_effective"
            ][
                causal_frame
            ]
        )

        metrics[
            "target_voltage_at_causal_frame"
        ] = float(
            result[
                "target_voltage"
            ][
                causal_frame
            ]
        )

        conditions_json[
            key
        ] = metrics

    baseline_v = float(
        baseline[
            "target_voltage"
        ][
            causal_frame
        ]
    )

    for key in dose_keys:
        intervention_v = float(
            runs[
                key
            ][
                "target_voltage"
            ][
                causal_frame
            ]
        )

        conditions_json[
            key
        ][
            "delta_target_voltage_vs_baseline_at_causal_frame"
        ] = (
            intervention_v
            - baseline_v
        )

    artifact = {
        "schema":
            "mq5-intervention-v1",

        "experiment_id":
            experiment["id"],

        "phase":
            experiment["phase"],

        "classification":
            experiment[
                "classification"
            ],

        "condition":
            condition,

        "software_commit":
            git_commit(),

        "runtime":
            {
                "class":
                    "MQ5InterventionRuntime",

                "overlay":
                    "presynaptic_effective_activity",

                "connectome_weights_modified":
                    False,

                "frame_semantics":
                    (
                        "intervention at frame F "
                        "modifies presynaptic effective "
                        "activity used by simulation "
                        "step F; post-step target state "
                        "is recorded as frame F"
                    ),
            },

        "causal_edge":
            {
                "presynaptic_model_index":
                    source,

                "postsynaptic_model_index":
                    target,

                "causal_frame":
                    causal_frame,

                "frozen_weight":
                    float(
                        edge[
                            "weight"
                        ]
                    ),

                "observed_frames":
                    [
                        int(x)
                        for x in edge[
                            "observed_frames"
                        ]
                    ],
            },

        "attenuation_levels":
            attenuation_levels,

        "validation":
            {
                "baseline_sham_voltage_exact":
                    baseline_sham_voltage_exact,

                "baseline_sham_source_exact":
                    baseline_sham_source_exact,

                "source_active_at_causal_frame":
                    bool(
                        baseline_source_at_frame
                        > 0.0
                    ),

                "dose_application_verified":
                    True,

                "deterministic_100pct_replicate":
                    reproducible_100,

                "frozen_artifacts_unchanged":
                    frozen_unchanged,
            },

        "conditions":
            conditions_json,

        "frozen_artifact_sha256":
            hashes_before,

        "financial_semantics_used":
            False,

        "biological_causality_claim":
            False,

        "interpretation_status":
            "NOT_YET_INTERPRETED",
    }

    npz_payload = {}

    for key, result in runs.items():
        npz_payload[
            f"{key}_source_effective"
        ] = result[
            "source_effective"
        ].astype(
            np.float32
        )

        npz_payload[
            f"{key}_target_voltage"
        ] = result[
            "target_voltage"
        ].astype(
            np.float32
        )

        npz_payload[
            f"{key}_target_spikes"
        ] = result[
            "target_spikes"
        ].astype(
            np.float32
        )

    np.savez_compressed(
        OUTPUT_NPZ,
        **npz_payload,
    )

    artifact[
        "npz_sha256"
    ] = sha256_file(
        OUTPUT_NPZ
    )

    OUTPUT_JSON.write_text(
        json.dumps(
            artifact,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    print()
    print("=" * 80)
    print("VALIDATION")
    print("=" * 80)

    print(
        "baseline == sham voltage:",
        baseline_sham_voltage_exact,
    )

    print(
        "baseline == sham source:",
        baseline_sham_source_exact,
    )

    print(
        "source effective @ F145:",
        baseline_source_at_frame,
    )

    print(
        "100% deterministic replicate:",
        reproducible_100,
    )

    print(
        "frozen artifacts unchanged:",
        frozen_unchanged,
    )

    print()
    print("=" * 80)
    print("CAUSAL FRAME RESULTS")
    print("=" * 80)

    for key in (
        "baseline",
        "sham",
        "attenuation_25",
        "attenuation_50",
        "attenuation_75",
        "attenuation_100",
    ):
        result = runs[key]

        print(
            key,
            "source=",
            result[
                "source_effective"
            ][
                causal_frame
            ],
            "targetV=",
            result[
                "target_voltage"
            ][
                causal_frame
            ],
        )

    print()
    print("JSON:", OUTPUT_JSON)
    print("NPZ: ", OUTPUT_NPZ)
    print()
    print(
        "MQ-5.2 HARNESS VALIDATION COMPLETE"
    )


if __name__ == "__main__":
    main()
