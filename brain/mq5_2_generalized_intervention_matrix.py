from __future__ import annotations

import hashlib
import json
import os
import subprocess
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
EXPERIMENTS = DATA_ROOT / "experiments"

CONNECTOME = PROCESSED / "connectome-baseline-v1.npz"
RETINA = PROCESSED / "visual-r1-r6-map-v1.npz"
RELAY = PROCESSED / "visual-relay-map-v1.npz"
TERRITORIES = PROCESSED / "market-retinal-territories-v1.npz"
GRADED = PROCESSED / "mq3-2-graded-visual-types-v1.npz"
CAUSAL = PROCESSED / "mq3-2-first-onset-causal-edges-v1.json"

CONTROL_MAP = Path(
    "config/controls/"
    "mq5-2-generalized-control-map-v1.json"
)

TIMING_MAP = Path(
    "config/controls/"
    "mq5-2-generalized-timing-map-v1.json"
)

OUTPUT_JSON = (
    EXPERIMENTS
    / "mq5-generalized-intervention-matrix-v1.json"
)

OUTPUT_NPZ = (
    EXPERIMENTS
    / "mq5-generalized-intervention-matrix-v1.npz"
)

RELEASE_GAIN = 0.9981738484618123

ATTENUATIONS = (
    0.25,
    0.50,
    0.75,
    1.00,
)


def sha256_file(path: Path) -> str:
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
            ["git", "rev-parse", "HEAD"],
            text=True,
        ).strip()
    except Exception:
        return "UNKNOWN"


def snapshot_hashes():
    paths = (
        CONNECTOME,
        RETINA,
        RELAY,
        TERRITORIES,
        GRADED,
        CAUSAL,
        CONTROL_MAP,
        TIMING_MAP,
    )

    result = {}

    for path in paths:
        if not path.exists():
            raise FileNotFoundError(path)

        result[str(path)] = sha256_file(
            path
        )

    return result


def load_json(path: Path):
    return json.loads(
        path.read_text(
            encoding="utf-8"
        )
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


def build_input():
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
        for i in range(
            len(ASSETS)
        )
    ]

    encoder = MarketVisionTemporalEncoder(
        TERRITORIES
    )

    stimuli = []

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
            stimuli.append(
                np.asarray(
                    stimulus
                    * SENSORY_GAIN,
                    dtype=np.float32,
                )
            )

    expected = (
        OBSERVATIONS
        * FRAME_COUNT
    )

    if len(stimuli) != expected:
        raise RuntimeError(
            "unexpected stimulus count"
        )

    return stimuli


def run_case(
    connectome,
    retinal_indices,
    stimuli,
    target: int,
    monitor_nodes,
    intervention=None,
):
    runtime = build_runtime(
        connectome,
        retinal_indices,
        intervention,
    )

    monitor_nodes = tuple(
        sorted(
            set(
                int(x)
                for x in monitor_nodes
            )
        )
    )

    effective = {
        node: []
        for node in monitor_nodes
    }

    target_voltage = []
    target_spikes = []

    for frame, stimulus in enumerate(
        stimuli
    ):
        runtime.set_intervention_frame(
            frame
        )

        activity = (
            runtime.effective_activity()
        )

        for node in monitor_nodes:
            effective[node].append(
                float(
                    activity[node]
                )
            )

        runtime.step(
            stimulus
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

    voltage = np.asarray(
        target_voltage,
        dtype=np.float64,
    )

    spikes = np.asarray(
        target_spikes,
        dtype=np.float64,
    )

    effective = {
        node: np.asarray(
            values,
            dtype=np.float64,
        )
        for node, values
        in effective.items()
    }

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

    metrics = {
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

        "target_spike_count":
            int(
                np.count_nonzero(
                    spikes > 0.0
                )
            ),
    }

    return {
        "voltage":
            voltage,

        "spikes":
            spikes,

        "effective":
            effective,

        "metrics":
            metrics,
    }


def edge_key(
    source,
    target,
    frame,
):
    return (
        f"{source}_to_{target}_F{frame}"
    )


def main():
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

    control_map = load_json(
        CONTROL_MAP
    )

    timing_map = load_json(
        TIMING_MAP
    )

    causal_data = load_json(
        CAUSAL
    )

    control_lookup = {
        (
            int(row["presynaptic"]),
            int(row["postsynaptic"]),
            int(row["causal_frame"]),
        ):
        row
        for row in control_map[
            "edges"
        ]
    }

    timing_lookup = {
        (
            int(row["presynaptic"]),
            int(row["postsynaptic"]),
            int(row["causal_frame"]),
        ):
        row
        for row in timing_map[
            "edges"
        ]
    }

    edges = []

    for edge in causal_data[
        "edges"
    ]:
        observed = sorted(
            int(x)
            for x in edge[
                "observed_frames"
            ]
        )

        frame = observed[0]

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

                "frame":
                    frame,

                "weight":
                    float(
                        edge[
                            "weight"
                        ]
                    ),

                "observed_frames":
                    observed,
            }
        )

    if len(edges) != 13:
        raise RuntimeError(
            f"expected 13 edges, "
            f"got {len(edges)}"
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

    stimuli = build_input()

    print("=" * 100)
    print("MQ-5.2 GENERALIZED INTERVENTION MATRIX")
    print("=" * 100)

    artifact_edges = []
    npz_payload = {}

    for number, edge in enumerate(
        edges,
        start=1,
    ):
        source = edge["source"]
        target = edge["target"]
        frame = edge["frame"]

        key_tuple = (
            source,
            target,
            frame,
        )

        control_cfg = control_lookup[
            key_tuple
        ]

        timing_cfg = timing_lookup[
            key_tuple
        ]

        matched_control = (
            control_cfg[
                "matched_control_model_index"
            ]
        )

        timing_frame = (
            timing_cfg[
                "timing_control_frame"
            ]
        )

        monitor_nodes = {
            source,
        }

        if matched_control is not None:
            monitor_nodes.add(
                int(matched_control)
            )

        label = edge_key(
            source,
            target,
            frame,
        )

        print()
        print(
            f"[{number:02d}/13] "
            f"{source} -> {target} "
            f"@ F{frame}"
        )

        #
        # BASELINE
        #
        print("  baseline")

        baseline = run_case(
            connectome,
            retinal_indices,
            stimuli,
            target,
            monitor_nodes,
            intervention=None,
        )

        baseline_source = float(
            baseline[
                "effective"
            ][source][frame]
        )

        if baseline_source <= 0.0:
            raise RuntimeError(
                f"{label}: source inactive "
                "at causal frame"
            )

        #
        # SHAM
        #
        print("  sham")

        sham_spec = InterventionSpec(
            experiment_id=(
                f"mq5-2-{label}-sham"
            ),
            target_model_index=source,
            attenuation=0.0,
            start_frame=frame,
            end_frame=frame,
            mode="sham",
        )

        sham = run_case(
            connectome,
            retinal_indices,
            stimuli,
            target,
            monitor_nodes,
            intervention=sham_spec,
        )

        sham_exact = (
            np.array_equal(
                baseline[
                    "voltage"
                ],
                sham[
                    "voltage"
                ],
            )
            and np.array_equal(
                baseline[
                    "effective"
                ][source],
                sham[
                    "effective"
                ][source],
            )
        )

        if not sham_exact:
            raise RuntimeError(
                f"{label}: sham differs "
                "from baseline"
            )

        #
        # DOSE SERIES
        #
        doses = {}

        for attenuation in (
            ATTENUATIONS
        ):
            percent = int(
                round(
                    attenuation
                    * 100
                )
            )

            print(
                f"  attenuation {percent}%"
            )

            mode = (
                "silence"
                if attenuation == 1.0
                else "attenuate"
            )

            spec = InterventionSpec(
                experiment_id=(
                    f"mq5-2-{label}-"
                    f"{percent}"
                ),
                target_model_index=source,
                attenuation=attenuation,
                start_frame=frame,
                end_frame=frame,
                mode=mode,
            )

            result = run_case(
                connectome,
                retinal_indices,
                stimuli,
                target,
                monitor_nodes,
                intervention=spec,
            )

            actual = float(
                result[
                    "effective"
                ][source][frame]
            )

            expected = (
                baseline_source
                * (
                    1.0
                    - attenuation
                )
            )

            if not np.isclose(
                actual,
                expected,
                rtol=1e-6,
                atol=1e-15,
            ):
                raise RuntimeError(
                    f"{label}: dose telemetry "
                    f"failed at {percent}%: "
                    f"{actual} != {expected}"
                )

            doses[percent] = result

        #
        # TIMING SHIFT
        #
        if timing_frame is None:
            timing = None

        else:
            print(
                f"  timing control F"
                f"{timing_frame}"
            )

            baseline_timing_activity = float(
                baseline[
                    "effective"
                ][source][
                    timing_frame
                ]
            )

            if (
                baseline_timing_activity
                <= 0.0
            ):
                raise RuntimeError(
                    f"{label}: frozen timing "
                    "control source inactive"
                )

            timing_spec = InterventionSpec(
                experiment_id=(
                    f"mq5-2-{label}-timing"
                ),
                target_model_index=source,
                attenuation=1.0,
                start_frame=timing_frame,
                end_frame=timing_frame,
                mode="silence",
            )

            timing = run_case(
                connectome,
                retinal_indices,
                stimuli,
                target,
                monitor_nodes,
                intervention=timing_spec,
            )

            if not np.isclose(
                timing[
                    "effective"
                ][source][
                    timing_frame
                ],
                0.0,
                atol=1e-15,
            ):
                raise RuntimeError(
                    f"{label}: timing "
                    "silencing telemetry failed"
                )

        #
        # MATCHED CONTROL
        #
        if matched_control is None:
            matched = None

        else:
            matched_control = int(
                matched_control
            )

            print(
                f"  matched control "
                f"{matched_control}"
            )

            baseline_control_activity = float(
                baseline[
                    "effective"
                ][
                    matched_control
                ][frame]
            )

            if (
                baseline_control_activity
                <= 0.0
            ):
                raise RuntimeError(
                    f"{label}: frozen matched "
                    "control inactive"
                )

            matched_spec = InterventionSpec(
                experiment_id=(
                    f"mq5-2-{label}-matched"
                ),
                target_model_index=(
                    matched_control
                ),
                attenuation=1.0,
                start_frame=frame,
                end_frame=frame,
                mode="silence",
            )

            matched = run_case(
                connectome,
                retinal_indices,
                stimuli,
                target,
                monitor_nodes,
                intervention=matched_spec,
            )

            if not np.isclose(
                matched[
                    "effective"
                ][
                    matched_control
                ][frame],
                0.0,
                atol=1e-15,
            ):
                raise RuntimeError(
                    f"{label}: matched-control "
                    "silencing telemetry failed"
                )

        #
        # DETERMINISTIC REPLICATE:
        # full causal-frame silencing.
        #
        print(
            "  deterministic 100% replicate"
        )

        replicate_spec = InterventionSpec(
            experiment_id=(
                f"mq5-2-{label}-"
                "100-replicate"
            ),
            target_model_index=source,
            attenuation=1.0,
            start_frame=frame,
            end_frame=frame,
            mode="silence",
        )

        replicate = run_case(
            connectome,
            retinal_indices,
            stimuli,
            target,
            monitor_nodes,
            intervention=replicate_spec,
        )

        reproducible = (
            np.array_equal(
                doses[100][
                    "voltage"
                ],
                replicate[
                    "voltage"
                ],
            )
            and np.array_equal(
                doses[100][
                    "effective"
                ][source],
                replicate[
                    "effective"
                ][source],
            )
        )

        if not reproducible:
            raise RuntimeError(
                f"{label}: deterministic "
                "replicate failed"
            )

        #
        # RESULT SERIALIZATION
        #
        def summarize(
            result,
        ):
            if result is None:
                return None

            metrics = dict(
                result[
                    "metrics"
                ]
            )

            metrics[
                "target_voltage_at_causal_frame"
            ] = float(
                result[
                    "voltage"
                ][frame]
            )

            metrics[
                "delta_integrated_positive_vs_baseline"
            ] = (
                float(
                    metrics[
                        "integrated_positive_voltage"
                    ]
                )
                - float(
                    baseline[
                        "metrics"
                    ][
                        "integrated_positive_voltage"
                    ]
                )
            )

            metrics[
                "delta_peak_voltage_vs_baseline"
            ] = (
                float(
                    metrics[
                        "peak_voltage"
                    ]
                )
                - float(
                    baseline[
                        "metrics"
                    ][
                        "peak_voltage"
                    ]
                )
            )

            return metrics

        dose_json = {}

        for percent, result in (
            doses.items()
        ):
            summary = summarize(
                result
            )

            summary[
                "source_effective_at_causal_frame"
            ] = float(
                result[
                    "effective"
                ][source][frame]
            )

            dose_json[
                str(percent)
            ] = summary

        edge_result = {
            "source":
                source,

            "target":
                target,

            "causal_frame":
                frame,

            "observed_frames":
                edge[
                    "observed_frames"
                ],

            "frozen_weight":
                edge[
                    "weight"
                ],

            "baseline_source_effective_at_causal_frame":
                baseline_source,

            "baseline":
                summarize(
                    baseline
                ),

            "sham":
                summarize(
                    sham
                ),

            "doses":
                dose_json,

            "timing_control": {
                "available":
                    timing is not None,

                "frame":
                    timing_frame,

                "baseline_source_activity_at_control_frame":
                    (
                        float(
                            baseline[
                                "effective"
                            ][source][
                                timing_frame
                            ]
                        )
                        if timing_frame
                        is not None
                        else None
                    ),

                "metrics":
                    summarize(
                        timing
                    ),
            },

            "matched_control": {
                "available":
                    matched is not None,

                "model_index":
                    matched_control,

                "baseline_control_activity_at_causal_frame":
                    (
                        float(
                            baseline[
                                "effective"
                            ][
                                matched_control
                            ][frame]
                        )
                        if matched_control
                        is not None
                        else None
                    ),

                "metrics":
                    summarize(
                        matched
                    ),
            },

            "validation": {
                "sham_exact":
                    sham_exact,

                "dose_telemetry_verified":
                    True,

                "timing_telemetry_verified":
                    timing is not None,

                "matched_control_telemetry_verified":
                    (
                        matched is not None
                    ),

                "deterministic_100pct_replicate":
                    reproducible,
            },
        }

        artifact_edges.append(
            edge_result
        )

        #
        # Raw traces.
        #
        prefix = label

        npz_payload[
            f"{prefix}_baseline_voltage"
        ] = baseline[
            "voltage"
        ].astype(
            np.float32
        )

        npz_payload[
            f"{prefix}_sham_voltage"
        ] = sham[
            "voltage"
        ].astype(
            np.float32
        )

        npz_payload[
            f"{prefix}_baseline_source"
        ] = baseline[
            "effective"
        ][source].astype(
            np.float32
        )

        for percent, result in (
            doses.items()
        ):
            npz_payload[
                f"{prefix}_dose_{percent}_voltage"
            ] = result[
                "voltage"
            ].astype(
                np.float32
            )

            npz_payload[
                f"{prefix}_dose_{percent}_source"
            ] = result[
                "effective"
            ][source].astype(
                np.float32
            )

        if timing is not None:
            npz_payload[
                f"{prefix}_timing_voltage"
            ] = timing[
                "voltage"
            ].astype(
                np.float32
            )

        if matched is not None:
            npz_payload[
                f"{prefix}_matched_voltage"
            ] = matched[
                "voltage"
            ].astype(
                np.float32
            )

        print(
            "  PASS validation"
        )

    hashes_after = snapshot_hashes()

    if hashes_before != hashes_after:
        raise RuntimeError(
            "frozen artifact hash changed"
        )

    if len(artifact_edges) != 13:
        raise RuntimeError(
            "unexpected completed edge count"
        )

    np.savez_compressed(
        OUTPUT_NPZ,
        **npz_payload,
    )

    artifact = {
        "schema":
            "mq5-generalized-intervention-matrix-v1",

        "experiment_id":
            "mq5-2-generalized-13-edge-v1",

        "phase":
            "MQ-5.2",

        "classification":
            "confirmatory",

        "condition":
            "A",

        "software_commit":
            git_commit(),

        "edge_count":
            13,

        "attenuation_levels": [
            0.25,
            0.50,
            0.75,
            1.00,
        ],

        "control_maps": {
            "matched":
                str(CONTROL_MAP),

            "timing":
                str(TIMING_MAP),
        },

        "runtime": {
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
                    "step F"
                ),
        },

        "validation": {
            "all_13_completed":
                True,

            "all_shams_exact":
                all(
                    row[
                        "validation"
                    ][
                        "sham_exact"
                    ]
                    for row
                    in artifact_edges
                ),

            "all_dose_telemetry_verified":
                all(
                    row[
                        "validation"
                    ][
                        "dose_telemetry_verified"
                    ]
                    for row
                    in artifact_edges
                ),

            "all_deterministic_replicates_exact":
                all(
                    row[
                        "validation"
                    ][
                        "deterministic_100pct_replicate"
                    ]
                    for row
                    in artifact_edges
                ),

            "frozen_artifacts_unchanged":
                True,

            "timing_controls_available":
                sum(
                    int(
                        row[
                            "timing_control"
                        ][
                            "available"
                        ]
                    )
                    for row
                    in artifact_edges
                ),

            "matched_controls_available":
                sum(
                    int(
                        row[
                            "matched_control"
                        ][
                            "available"
                        ]
                    )
                    for row
                    in artifact_edges
                ),
        },

        "edges":
            artifact_edges,

        "frozen_artifact_sha256":
            hashes_before,

        "npz_sha256":
            sha256_file(
                OUTPUT_NPZ
            ),

        "interpretation_status":
            "NOT_YET_INTERPRETED",

        "biological_causality_claim":
            False,

        "financial_semantics_used":
            False,
    }

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
    print("=" * 100)
    print("MQ-5.2 GENERALIZED MATRIX COMPLETE")
    print("=" * 100)

    for key, value in (
        artifact[
            "validation"
        ].items()
    ):
        print(
            f"{key:42s}",
            value,
        )

    print()
    print("JSON:", OUTPUT_JSON)
    print("NPZ: ", OUTPUT_NPZ)


if __name__ == "__main__":
    main()
