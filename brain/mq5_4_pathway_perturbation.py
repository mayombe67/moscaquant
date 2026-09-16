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

CONFIG = Path(
    "config/controls/"
    "mq5-4-pathway-56393-68045-1273-v1.toml"
)

PROTOCOL = Path(
    "docs/experiments/"
    "mq5-4-pathway-protocol.md"
)

OUTPUT_JSON = (
    EXPERIMENTS
    / "mq5-4-pathway-56393-68045-1273-v1.json"
)

OUTPUT_NPZ = (
    EXPERIMENTS
    / "mq5-4-pathway-56393-68045-1273-v1.npz"
)

UPSTREAM = 56393
INTERMEDIATE = 68045
DOWNSTREAM = 1273

UPSTREAM_FRAME = 146
INTERMEDIATE_FRAME = 147

ATTENUATIONS = (
    0.25,
    0.50,
    0.75,
    1.00,
)

RELEASE_GAIN = 0.9981738484618123


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


def frozen_hashes():
    paths = (
        CONNECTOME,
        RETINA,
        RELAY,
        TERRITORIES,
        GRADED,
        CAUSAL,
        CONFIG,
        PROTOCOL,
    )

    result = {}

    for path in paths:
        if not path.exists():
            raise FileNotFoundError(path)

        result[str(path)] = sha256_file(
            path
        )

    return result


def validate_frozen_path():
    data = json.loads(
        CAUSAL.read_text(
            encoding="utf-8"
        )
    )

    found = set()

    for edge in data["edges"]:
        source = int(
            edge["presynaptic"]
        )

        target = int(
            edge["postsynaptic"]
        )

        frames = {
            int(x)
            for x in edge[
                "observed_frames"
            ]
        }

        if (
            source == UPSTREAM
            and target == INTERMEDIATE
            and UPSTREAM_FRAME in frames
        ):
            found.add(
                "upstream"
            )

        if (
            source == INTERMEDIATE
            and target == DOWNSTREAM
            and INTERMEDIATE_FRAME in frames
        ):
            found.add(
                "intermediate"
            )

    if found != {
        "upstream",
        "intermediate",
    }:
        raise RuntimeError(
            "frozen two-hop pathway "
            "could not be validated"
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
            f"unexpected stimulus count: "
            f"{len(stimuli)} != {expected}"
        )

    return stimuli


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


def run_case(
    connectome,
    retinal_indices,
    stimuli,
    intervention=None,
):
    runtime = build_runtime(
        connectome,
        retinal_indices,
        intervention,
    )

    effective = {
        UPSTREAM: [],
        INTERMEDIATE: [],
    }

    voltage = {
        INTERMEDIATE: [],
        DOWNSTREAM: [],
    }

    spikes = {
        INTERMEDIATE: [],
        DOWNSTREAM: [],
    }

    for frame, stimulus in enumerate(
        stimuli
    ):
        runtime.set_intervention_frame(
            frame
        )

        activity = (
            runtime.effective_activity()
        )

        effective[
            UPSTREAM
        ].append(
            float(
                activity[
                    UPSTREAM
                ]
            )
        )

        effective[
            INTERMEDIATE
        ].append(
            float(
                activity[
                    INTERMEDIATE
                ]
            )
        )

        runtime.step(
            stimulus
        )

        for node in (
            INTERMEDIATE,
            DOWNSTREAM,
        ):
            voltage[node].append(
                float(
                    runtime.voltage[
                        node
                    ]
                )
            )

            spikes[node].append(
                float(
                    runtime.spikes[
                        node
                    ]
                )
            )

    return {
        "effective": {
            node: np.asarray(
                values,
                dtype=np.float64,
            )
            for node, values
            in effective.items()
        },

        "voltage": {
            node: np.asarray(
                values,
                dtype=np.float64,
            )
            for node, values
            in voltage.items()
        },

        "spikes": {
            node: np.asarray(
                values,
                dtype=np.float64,
            )
            for node, values
            in spikes.items()
        },
    }


def metrics(
    voltage,
    spikes,
):
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

        "spike_count":
            int(
                np.count_nonzero(
                    spikes > 0.0
                )
            ),
    }


def node_summary(
    result,
    node,
    baseline,
):
    current = metrics(
        result["voltage"][node],
        result["spikes"][node],
    )

    base = metrics(
        baseline["voltage"][node],
        baseline["spikes"][node],
    )

    current[
        "delta_integrated_positive_vs_baseline"
    ] = (
        current[
            "integrated_positive_voltage"
        ]
        - base[
            "integrated_positive_voltage"
        ]
    )

    current[
        "delta_peak_voltage_vs_baseline"
    ] = (
        current[
            "peak_voltage"
        ]
        - base[
            "peak_voltage"
        ]
    )

    return current


def make_spec(
    experiment_id,
    node,
    attenuation,
    frame,
):
    mode = (
        "silence"
        if attenuation == 1.0
        else (
            "sham"
            if attenuation == 0.0
            else "attenuate"
        )
    )

    return InterventionSpec(
        experiment_id=experiment_id,
        target_model_index=node,
        attenuation=attenuation,
        start_frame=frame,
        end_frame=frame,
        mode=mode,
    )


def verify_dose(
    baseline_activity,
    observed_activity,
    attenuation,
    label,
):
    expected = (
        baseline_activity
        * (
            1.0
            - attenuation
        )
    )

    if not np.isclose(
        observed_activity,
        expected,
        rtol=1e-6,
        atol=1e-15,
    ):
        raise RuntimeError(
            f"{label}: dose telemetry failed: "
            f"{observed_activity} != {expected}"
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

    validate_frozen_path()

    hashes_before = frozen_hashes()

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
    print("MQ-5.4 PATHWAY PERTURBATION")
    print("=" * 100)
    print()
    print(
        f"{UPSTREAM} -> "
        f"{INTERMEDIATE} -> "
        f"{DOWNSTREAM}"
    )
    print()

    #
    # BASELINE
    #
    print("baseline")

    baseline = run_case(
        connectome,
        retinal_indices,
        stimuli,
    )

    upstream_baseline_activity = float(
        baseline[
            "effective"
        ][UPSTREAM][
            UPSTREAM_FRAME
        ]
    )

    intermediate_baseline_activity = float(
        baseline[
            "effective"
        ][INTERMEDIATE][
            INTERMEDIATE_FRAME
        ]
    )

    if upstream_baseline_activity <= 0:
        raise RuntimeError(
            "upstream inactive at F146"
        )

    if intermediate_baseline_activity <= 0:
        raise RuntimeError(
            "intermediate inactive at F147"
        )

    #
    # UPSTREAM SHAM
    #
    print("upstream sham")

    upstream_sham = run_case(
        connectome,
        retinal_indices,
        stimuli,
        make_spec(
            "mq5-4-upstream-sham",
            UPSTREAM,
            0.0,
            UPSTREAM_FRAME,
        ),
    )

    upstream_sham_exact = (
        np.array_equal(
            baseline[
                "voltage"
            ][INTERMEDIATE],
            upstream_sham[
                "voltage"
            ][INTERMEDIATE],
        )
        and np.array_equal(
            baseline[
                "voltage"
            ][DOWNSTREAM],
            upstream_sham[
                "voltage"
            ][DOWNSTREAM],
        )
        and np.array_equal(
            baseline[
                "effective"
            ][UPSTREAM],
            upstream_sham[
                "effective"
            ][UPSTREAM],
        )
        and np.array_equal(
            baseline[
                "effective"
            ][INTERMEDIATE],
            upstream_sham[
                "effective"
            ][INTERMEDIATE],
        )
    )

    if not upstream_sham_exact:
        raise RuntimeError(
            "upstream sham != baseline"
        )

    #
    # INTERMEDIATE SHAM
    #
    print("intermediate sham")

    intermediate_sham = run_case(
        connectome,
        retinal_indices,
        stimuli,
        make_spec(
            "mq5-4-intermediate-sham",
            INTERMEDIATE,
            0.0,
            INTERMEDIATE_FRAME,
        ),
    )

    intermediate_sham_exact = (
        np.array_equal(
            baseline[
                "voltage"
            ][DOWNSTREAM],
            intermediate_sham[
                "voltage"
            ][DOWNSTREAM],
        )
        and np.array_equal(
            baseline[
                "effective"
            ][INTERMEDIATE],
            intermediate_sham[
                "effective"
            ][INTERMEDIATE],
        )
    )

    if not intermediate_sham_exact:
        raise RuntimeError(
            "intermediate sham != baseline"
        )

    upstream_runs = {}
    intermediate_runs = {}

    #
    # UPSTREAM DOSE SERIES
    #
    for attenuation in ATTENUATIONS:
        percent = int(
            attenuation * 100
        )

        print(
            f"upstream attenuation "
            f"{percent}%"
        )

        result = run_case(
            connectome,
            retinal_indices,
            stimuli,
            make_spec(
                (
                    "mq5-4-upstream-"
                    f"{percent}"
                ),
                UPSTREAM,
                attenuation,
                UPSTREAM_FRAME,
            ),
        )

        observed = float(
            result[
                "effective"
            ][UPSTREAM][
                UPSTREAM_FRAME
            ]
        )

        verify_dose(
            upstream_baseline_activity,
            observed,
            attenuation,
            (
                "upstream "
                f"{percent}%"
            ),
        )

        upstream_runs[
            percent
        ] = result

    #
    # INTERMEDIATE DOSE SERIES
    #
    for attenuation in ATTENUATIONS:
        percent = int(
            attenuation * 100
        )

        print(
            f"intermediate attenuation "
            f"{percent}%"
        )

        result = run_case(
            connectome,
            retinal_indices,
            stimuli,
            make_spec(
                (
                    "mq5-4-intermediate-"
                    f"{percent}"
                ),
                INTERMEDIATE,
                attenuation,
                INTERMEDIATE_FRAME,
            ),
        )

        observed = float(
            result[
                "effective"
            ][INTERMEDIATE][
                INTERMEDIATE_FRAME
            ]
        )

        verify_dose(
            intermediate_baseline_activity,
            observed,
            attenuation,
            (
                "intermediate "
                f"{percent}%"
            ),
        )

        intermediate_runs[
            percent
        ] = result

    #
    # DETERMINISTIC FULL-SILENCING
    # REPLICATES
    #
    print(
        "upstream deterministic "
        "100% replicate"
    )

    upstream_replicate = run_case(
        connectome,
        retinal_indices,
        stimuli,
        make_spec(
            "mq5-4-upstream-100-replicate",
            UPSTREAM,
            1.0,
            UPSTREAM_FRAME,
        ),
    )

    upstream_reproducible = (
        np.array_equal(
            upstream_runs[
                100
            ][
                "voltage"
            ][INTERMEDIATE],
            upstream_replicate[
                "voltage"
            ][INTERMEDIATE],
        )
        and np.array_equal(
            upstream_runs[
                100
            ][
                "voltage"
            ][DOWNSTREAM],
            upstream_replicate[
                "voltage"
            ][DOWNSTREAM],
        )
        and np.array_equal(
            upstream_runs[
                100
            ][
                "effective"
            ][INTERMEDIATE],
            upstream_replicate[
                "effective"
            ][INTERMEDIATE],
        )
    )

    if not upstream_reproducible:
        raise RuntimeError(
            "upstream deterministic "
            "replicate failed"
        )

    print(
        "intermediate deterministic "
        "100% replicate"
    )

    intermediate_replicate = run_case(
        connectome,
        retinal_indices,
        stimuli,
        make_spec(
            (
                "mq5-4-intermediate-"
                "100-replicate"
            ),
            INTERMEDIATE,
            1.0,
            INTERMEDIATE_FRAME,
        ),
    )

    intermediate_reproducible = (
        np.array_equal(
            intermediate_runs[
                100
            ][
                "voltage"
            ][DOWNSTREAM],
            intermediate_replicate[
                "voltage"
            ][DOWNSTREAM],
        )
    )

    if not intermediate_reproducible:
        raise RuntimeError(
            "intermediate deterministic "
            "replicate failed"
        )

    #
    # FROZEN ARTIFACT INVARIANCE
    #
    hashes_after = frozen_hashes()

    if hashes_before != hashes_after:
        raise RuntimeError(
            "frozen artifact hash changed"
        )

    #
    # SERIALIZATION
    #
    baseline_intermediate_metrics = (
        metrics(
            baseline[
                "voltage"
            ][INTERMEDIATE],
            baseline[
                "spikes"
            ][INTERMEDIATE],
        )
    )

    baseline_downstream_metrics = (
        metrics(
            baseline[
                "voltage"
            ][DOWNSTREAM],
            baseline[
                "spikes"
            ][DOWNSTREAM],
        )
    )

    upstream_json = {}

    for percent, result in (
        upstream_runs.items()
    ):
        upstream_json[
            str(percent)
        ] = {
            "upstream_effective_at_F146":
                float(
                    result[
                        "effective"
                    ][UPSTREAM][
                        UPSTREAM_FRAME
                    ]
                ),

            "intermediate_voltage_at_F146":
                float(
                    result[
                        "voltage"
                    ][INTERMEDIATE][
                        UPSTREAM_FRAME
                    ]
                ),

            "intermediate_effective_at_F147":
                float(
                    result[
                        "effective"
                    ][INTERMEDIATE][
                        INTERMEDIATE_FRAME
                    ]
                ),

            "downstream_voltage_at_F147":
                float(
                    result[
                        "voltage"
                    ][DOWNSTREAM][
                        INTERMEDIATE_FRAME
                    ]
                ),

            "intermediate_metrics":
                node_summary(
                    result,
                    INTERMEDIATE,
                    baseline,
                ),

            "downstream_metrics":
                node_summary(
                    result,
                    DOWNSTREAM,
                    baseline,
                ),
        }

    intermediate_json = {}

    for percent, result in (
        intermediate_runs.items()
    ):
        intermediate_json[
            str(percent)
        ] = {
            "intermediate_effective_at_F147":
                float(
                    result[
                        "effective"
                    ][INTERMEDIATE][
                        INTERMEDIATE_FRAME
                    ]
                ),

            "downstream_voltage_at_F147":
                float(
                    result[
                        "voltage"
                    ][DOWNSTREAM][
                        INTERMEDIATE_FRAME
                    ]
                ),

            "downstream_metrics":
                node_summary(
                    result,
                    DOWNSTREAM,
                    baseline,
                ),
        }

    npz_payload = {
        "baseline_upstream_effective":
            baseline[
                "effective"
            ][UPSTREAM].astype(
                np.float32
            ),

        "baseline_intermediate_effective":
            baseline[
                "effective"
            ][INTERMEDIATE].astype(
                np.float32
            ),

        "baseline_intermediate_voltage":
            baseline[
                "voltage"
            ][INTERMEDIATE].astype(
                np.float32
            ),

        "baseline_downstream_voltage":
            baseline[
                "voltage"
            ][DOWNSTREAM].astype(
                np.float32
            ),
    }

    for percent, result in (
        upstream_runs.items()
    ):
        prefix = (
            f"upstream_{percent}"
        )

        npz_payload[
            f"{prefix}_upstream_effective"
        ] = result[
            "effective"
        ][UPSTREAM].astype(
            np.float32
        )

        npz_payload[
            f"{prefix}_intermediate_effective"
        ] = result[
            "effective"
        ][INTERMEDIATE].astype(
            np.float32
        )

        npz_payload[
            f"{prefix}_intermediate_voltage"
        ] = result[
            "voltage"
        ][INTERMEDIATE].astype(
            np.float32
        )

        npz_payload[
            f"{prefix}_downstream_voltage"
        ] = result[
            "voltage"
        ][DOWNSTREAM].astype(
            np.float32
        )

    for percent, result in (
        intermediate_runs.items()
    ):
        prefix = (
            f"intermediate_{percent}"
        )

        npz_payload[
            f"{prefix}_intermediate_effective"
        ] = result[
            "effective"
        ][INTERMEDIATE].astype(
            np.float32
        )

        npz_payload[
            f"{prefix}_downstream_voltage"
        ] = result[
            "voltage"
        ][DOWNSTREAM].astype(
            np.float32
        )

    np.savez_compressed(
        OUTPUT_NPZ,
        **npz_payload,
    )

    artifact = {
        "schema":
            "mq5-4-pathway-56393-68045-1273-v1",

        "experiment_id":
            "mq5-4-pathway-56393-68045-1273-v1",

        "phase":
            "MQ-5.4",

        "classification":
            "confirmatory",

        "condition":
            "A",

        "software_commit":
            git_commit(),

        "path": {
            "upstream":
                UPSTREAM,

            "intermediate":
                INTERMEDIATE,

            "downstream":
                DOWNSTREAM,

            "upstream_causal_frame":
                UPSTREAM_FRAME,

            "intermediate_causal_frame":
                INTERMEDIATE_FRAME,
        },

        "baseline": {
            "upstream_effective_at_F146":
                upstream_baseline_activity,

            "intermediate_voltage_at_F146":
                float(
                    baseline[
                        "voltage"
                    ][INTERMEDIATE][
                        UPSTREAM_FRAME
                    ]
                ),

            "intermediate_effective_at_F147":
                intermediate_baseline_activity,

            "downstream_voltage_at_F147":
                float(
                    baseline[
                        "voltage"
                    ][DOWNSTREAM][
                        INTERMEDIATE_FRAME
                    ]
                ),

            "intermediate_metrics":
                baseline_intermediate_metrics,

            "downstream_metrics":
                baseline_downstream_metrics,
        },

        "upstream_interventions":
            upstream_json,

        "intermediate_interventions":
            intermediate_json,

        "validation": {
            "frozen_path_verified":
                True,

            "upstream_sham_exact":
                upstream_sham_exact,

            "intermediate_sham_exact":
                intermediate_sham_exact,

            "upstream_dose_telemetry_verified":
                True,

            "intermediate_dose_telemetry_verified":
                True,

            "upstream_100pct_replicate_exact":
                upstream_reproducible,

            "intermediate_100pct_replicate_exact":
                intermediate_reproducible,

            "frozen_artifacts_unchanged":
                True,
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
                    "activity used during simulation "
                    "step F; post-step state is "
                    "recorded as frame F"
                ),
        },

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
    print("MQ-5.4 PATHWAY RUN COMPLETE")
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
    print("BASELINE PATH TELEMETRY")
    print(
        "56393 effective F146:",
        upstream_baseline_activity,
    )
    print(
        "68045 voltage F146:  ",
        artifact[
            "baseline"
        ][
            "intermediate_voltage_at_F146"
        ],
    )
    print(
        "68045 effective F147:",
        intermediate_baseline_activity,
    )
    print(
        "1273 voltage F147:   ",
        artifact[
            "baseline"
        ][
            "downstream_voltage_at_F147"
        ],
    )

    print()
    print("UPSTREAM 56393 INTERVENTION")
    print(
        "dose    68045 V@146       "
        "68045 eff@147     "
        "1273 V@147         "
        "Δ1273 integrated"
    )

    for percent in (
        25,
        50,
        75,
        100,
    ):
        row = upstream_json[
            str(percent)
        ]

        print(
            f"{percent:3d}%  "
            f'{row["intermediate_voltage_at_F146"]:<17.10g} '
            f'{row["intermediate_effective_at_F147"]:<17.10g} '
            f'{row["downstream_voltage_at_F147"]:<17.10g} '
            f'{row["downstream_metrics"]["delta_integrated_positive_vs_baseline"]:.10g}'
        )

    print()
    print("INTERMEDIATE 68045 INTERVENTION")
    print(
        "dose    68045 eff@147     "
        "1273 V@147         "
        "Δ1273 integrated"
    )

    for percent in (
        25,
        50,
        75,
        100,
    ):
        row = intermediate_json[
            str(percent)
        ]

        print(
            f"{percent:3d}%  "
            f'{row["intermediate_effective_at_F147"]:<17.10g} '
            f'{row["downstream_voltage_at_F147"]:<17.10g} '
            f'{row["downstream_metrics"]["delta_integrated_positive_vs_baseline"]:.10g}'
        )

    print()
    print(
        "JSON:",
        OUTPUT_JSON,
    )

    print(
        "NPZ: ",
        OUTPUT_NPZ,
    )


if __name__ == "__main__":
    main()
