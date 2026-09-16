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
    "mq5-5-convergence-specificity-v1.toml"
)

PROTOCOL = Path(
    "docs/experiments/"
    "mq5-5-convergence-specificity-protocol.md"
)

OUTPUT_JSON = (
    EXPERIMENTS
    / "mq5-5-convergence-specificity-v1.json"
)

OUTPUT_NPZ = (
    EXPERIMENTS
    / "mq5-5-convergence-specificity-v1.npz"
)

RELEASE_GAIN = 0.9981738484618123


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        while True:
            block = handle.read(1024 * 1024)
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

    for path in paths:
        if not path.exists():
            raise FileNotFoundError(path)

    return {
        str(path): sha256_file(path)
        for path in paths
    }


def load_config():
    with CONFIG.open("rb") as handle:
        cfg = tomllib.load(handle)

    systems = []

    for name, row in cfg["systems"].items():
        systems.append(
            {
                "name": name,
                "target": int(row["target"]),
                "input_a": int(row["input_a"]),
                "input_b": int(row["input_b"]),
                "frame_a": int(row["causal_frame_a"]),
                "frame_b": int(row["causal_frame_b"]),
            }
        )

    doses = tuple(
        float(x)
        for x in cfg["interventions"]["attenuation_levels"]
    )

    return cfg, systems, doses


def validate_frozen_edges(systems):
    data = json.loads(
        CAUSAL.read_text(encoding="utf-8")
    )

    frozen = {
        (
            int(edge["presynaptic"]),
            int(edge["postsynaptic"]),
            int(frame),
        )
        for edge in data["edges"]
        for frame in edge["observed_frames"]
    }

    for system in systems:
        a = (
            system["input_a"],
            system["target"],
            system["frame_a"],
        )

        b = (
            system["input_b"],
            system["target"],
            system["frame_b"],
        )

        if a not in frozen:
            raise RuntimeError(
                f"missing frozen edge {a}"
            )

        if b not in frozen:
            raise RuntimeError(
                f"missing frozen edge {b}"
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
        synthetic_series("A", i)
        for i in range(len(ASSETS))
    ]

    encoder = MarketVisionTemporalEncoder(
        TERRITORIES
    )

    stimuli = []

    for observation in range(OBSERVATIONS):
        normalized = np.empty(
            (len(ASSETS), 7),
            dtype=np.float32,
        )

        for asset_index in range(len(ASSETS)):
            window = market_window_at(
                series[asset_index],
                observation,
            )

            normalized[asset_index] = (
                normalizers[
                    asset_index
                ].transform(
                    compute_features(window)
                )
            )

        frames = encoder.encode_sequence(
            normalized,
            frame_count=FRAME_COUNT,
        )

        for stimulus in frames:
            stimuli.append(
                np.asarray(
                    stimulus * SENSORY_GAIN,
                    dtype=np.float32,
                )
            )

    expected = OBSERVATIONS * FRAME_COUNT

    if len(stimuli) != expected:
        raise RuntimeError(
            f"stimulus count {len(stimuli)} "
            f"!= {expected}"
        )

    return stimuli


def make_spec(
    experiment_id,
    node,
    attenuation,
    frame,
):
    if attenuation == 0.0:
        mode = "sham"
    elif attenuation == 1.0:
        mode = "silence"
    else:
        mode = "attenuate"

    return InterventionSpec(
        experiment_id=experiment_id,
        target_model_index=node,
        attenuation=attenuation,
        start_frame=frame,
        end_frame=frame,
        mode=mode,
    )


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
        interventions=tuple(interventions),
    )


def run_case(
    connectome,
    retinal_indices,
    stimuli,
    system,
    interventions=(),
):
    runtime = build_runtime(
        connectome,
        retinal_indices,
        interventions,
    )

    target = system["target"]
    input_a = system["input_a"]
    input_b = system["input_b"]

    target_voltage = []
    target_spikes = []
    a_effective = []
    b_effective = []

    for frame, stimulus in enumerate(stimuli):
        runtime.set_intervention_frame(frame)

        effective = runtime.effective_activity()

        a_effective.append(
            float(effective[input_a])
        )

        b_effective.append(
            float(effective[input_b])
        )

        runtime.step(stimulus)

        target_voltage.append(
            float(runtime.voltage[target])
        )

        target_spikes.append(
            float(runtime.spikes[target])
        )

    return {
        "voltage": np.asarray(
            target_voltage,
            dtype=np.float64,
        ),
        "spikes": np.asarray(
            target_spikes,
            dtype=np.float64,
        ),
        "a_effective": np.asarray(
            a_effective,
            dtype=np.float64,
        ),
        "b_effective": np.asarray(
            b_effective,
            dtype=np.float64,
        ),
    }


def metrics(result):
    voltage = result["voltage"]
    spikes = result["spikes"]

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
            float(voltage[peak_frame]),

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


def verify_activity(
    baseline,
    observed,
    attenuation,
    label,
):
    expected = (
        baseline
        * (1.0 - attenuation)
    )

    if not np.isclose(
        observed,
        expected,
        rtol=1e-6,
        atol=1e-15,
    ):
        raise RuntimeError(
            f"{label}: telemetry mismatch "
            f"{observed} != {expected}"
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

    cfg, systems, doses = load_config()

    if len(systems) != 3:
        raise RuntimeError(
            f"expected 3 convergence systems, "
            f"got {len(systems)}"
        )

    validate_frozen_edges(systems)

    hashes_before = frozen_hashes()

    connectome = sparse.load_npz(
        CONNECTOME
    ).tocsr()

    retina_data = np.load(RETINA)

    retinal_indices = np.asarray(
        retina_data["neuron_index"],
        dtype=np.int32,
    )

    stimuli = build_input()

    artifact_systems = []
    npz_payload = {}

    print("=" * 110)
    print("MQ-5.5 CONVERGENCE AND SPECIFICITY")
    print("=" * 110)

    for system in systems:
        target = system["target"]
        a = system["input_a"]
        b = system["input_b"]
        frame_a = system["frame_a"]
        frame_b = system["frame_b"]

        print()
        print(
            f"{a} ─┐"
        )
        print(
            f"       ├→ {target}"
        )
        print(
            f"{b} ─┘"
        )

        #
        # BASELINE
        #
        print("  baseline")

        baseline = run_case(
            connectome,
            retinal_indices,
            stimuli,
            system,
        )

        base_metrics = metrics(
            baseline
        )

        base_integrated = (
            base_metrics[
                "integrated_positive_voltage"
            ]
        )

        base_a = float(
            baseline[
                "a_effective"
            ][frame_a]
        )

        base_b = float(
            baseline[
                "b_effective"
            ][frame_b]
        )

        if base_a <= 0.0:
            raise RuntimeError(
                f"{a}: inactive at F{frame_a}"
            )

        if base_b <= 0.0:
            raise RuntimeError(
                f"{b}: inactive at F{frame_b}"
            )

        #
        # TWO-NODE ZERO-EFFECT SHAM
        #
        print("  combined sham")

        sham_specs = (
            make_spec(
                f"mq5-5-{target}-a-sham",
                a,
                0.0,
                frame_a,
            ),
            make_spec(
                f"mq5-5-{target}-b-sham",
                b,
                0.0,
                frame_b,
            ),
        )

        sham = run_case(
            connectome,
            retinal_indices,
            stimuli,
            system,
            sham_specs,
        )

        sham_exact = (
            np.array_equal(
                baseline["voltage"],
                sham["voltage"],
            )
            and np.array_equal(
                baseline["a_effective"],
                sham["a_effective"],
            )
            and np.array_equal(
                baseline["b_effective"],
                sham["b_effective"],
            )
        )

        if not sham_exact:
            raise RuntimeError(
                f"target {target}: sham "
                "differs from baseline"
            )

        dose_rows = {}

        for attenuation in doses:
            percent = int(
                round(
                    attenuation * 100
                )
            )

            print(
                f"  {percent}%: A-only"
            )

            a_run = run_case(
                connectome,
                retinal_indices,
                stimuli,
                system,
                (
                    make_spec(
                        (
                            f"mq5-5-{target}-"
                            f"a-{percent}"
                        ),
                        a,
                        attenuation,
                        frame_a,
                    ),
                ),
            )

            verify_activity(
                base_a,
                float(
                    a_run[
                        "a_effective"
                    ][frame_a]
                ),
                attenuation,
                f"{target} A-only {percent}%",
            )

            #
            # B must remain baseline during
            # the A-only manipulation.
            #
            if not np.isclose(
                float(
                    a_run[
                        "b_effective"
                    ][frame_b]
                ),
                base_b,
                rtol=1e-6,
                atol=1e-15,
            ):
                raise RuntimeError(
                    f"{target}: A-only altered "
                    "B intervention telemetry"
                )

            print(
                f"  {percent}%: B-only"
            )

            b_run = run_case(
                connectome,
                retinal_indices,
                stimuli,
                system,
                (
                    make_spec(
                        (
                            f"mq5-5-{target}-"
                            f"b-{percent}"
                        ),
                        b,
                        attenuation,
                        frame_b,
                    ),
                ),
            )

            verify_activity(
                base_b,
                float(
                    b_run[
                        "b_effective"
                    ][frame_b]
                ),
                attenuation,
                f"{target} B-only {percent}%",
            )

            if not np.isclose(
                float(
                    b_run[
                        "a_effective"
                    ][frame_a]
                ),
                base_a,
                rtol=1e-6,
                atol=1e-15,
            ):
                raise RuntimeError(
                    f"{target}: B-only altered "
                    "A intervention telemetry"
                )

            print(
                f"  {percent}%: A+B"
            )

            ab_specs = (
                make_spec(
                    (
                        f"mq5-5-{target}-"
                        f"ab-a-{percent}"
                    ),
                    a,
                    attenuation,
                    frame_a,
                ),
                make_spec(
                    (
                        f"mq5-5-{target}-"
                        f"ab-b-{percent}"
                    ),
                    b,
                    attenuation,
                    frame_b,
                ),
            )

            ab_run = run_case(
                connectome,
                retinal_indices,
                stimuli,
                system,
                ab_specs,
            )

            verify_activity(
                base_a,
                float(
                    ab_run[
                        "a_effective"
                    ][frame_a]
                ),
                attenuation,
                (
                    f"{target} A+B/A "
                    f"{percent}%"
                ),
            )

            verify_activity(
                base_b,
                float(
                    ab_run[
                        "b_effective"
                    ][frame_b]
                ),
                attenuation,
                (
                    f"{target} A+B/B "
                    f"{percent}%"
                ),
            )

            a_metrics = metrics(a_run)
            b_metrics = metrics(b_run)
            ab_metrics = metrics(ab_run)

            e_a = (
                base_integrated
                - a_metrics[
                    "integrated_positive_voltage"
                ]
            )

            e_b = (
                base_integrated
                - b_metrics[
                    "integrated_positive_voltage"
                ]
            )

            e_ab = (
                base_integrated
                - ab_metrics[
                    "integrated_positive_voltage"
                ]
            )

            additive = e_a + e_b

            dose_rows[
                str(percent)
            ] = {
                "attenuation":
                    attenuation,

                "a_only": {
                    "input_effective":
                        float(
                            a_run[
                                "a_effective"
                            ][frame_a]
                        ),
                    "metrics":
                        a_metrics,
                    "effect_magnitude":
                        e_a,
                },

                "b_only": {
                    "input_effective":
                        float(
                            b_run[
                                "b_effective"
                            ][frame_b]
                        ),
                    "metrics":
                        b_metrics,
                    "effect_magnitude":
                        e_b,
                },

                "combined": {
                    "input_a_effective":
                        float(
                            ab_run[
                                "a_effective"
                            ][frame_a]
                        ),
                    "input_b_effective":
                        float(
                            ab_run[
                                "b_effective"
                            ][frame_b]
                        ),
                    "metrics":
                        ab_metrics,
                    "effect_magnitude":
                        e_ab,
                },

                "combined_exceeds_each_single":
                    bool(
                        e_ab > max(
                            e_a,
                            e_b,
                        )
                    ),

                "descriptive_additive_reference":
                    additive,

                "combined_minus_additive_reference":
                    e_ab - additive,
            }

            prefix = (
                f"target_{target}_"
                f"dose_{percent}"
            )

            npz_payload[
                f"{prefix}_a_voltage"
            ] = a_run[
                "voltage"
            ].astype(
                np.float32
            )

            npz_payload[
                f"{prefix}_b_voltage"
            ] = b_run[
                "voltage"
            ].astype(
                np.float32
            )

            npz_payload[
                f"{prefix}_ab_voltage"
            ] = ab_run[
                "voltage"
            ].astype(
                np.float32
            )

        #
        # Deterministic replicate of
        # full combined silencing.
        #
        print(
            "  100% A+B deterministic replicate"
        )

        replicate_specs = (
            make_spec(
                f"mq5-5-{target}-rep-a",
                a,
                1.0,
                frame_a,
            ),
            make_spec(
                f"mq5-5-{target}-rep-b",
                b,
                1.0,
                frame_b,
            ),
        )

        replicate = run_case(
            connectome,
            retinal_indices,
            stimuli,
            system,
            replicate_specs,
        )

        #
        # Recreate the stored 100% combined
        # condition for exact comparison.
        #
        full_specs = (
            make_spec(
                f"mq5-5-{target}-check-a",
                a,
                1.0,
                frame_a,
            ),
            make_spec(
                f"mq5-5-{target}-check-b",
                b,
                1.0,
                frame_b,
            ),
        )

        full_again = run_case(
            connectome,
            retinal_indices,
            stimuli,
            system,
            full_specs,
        )

        reproducible = (
            np.array_equal(
                replicate["voltage"],
                full_again["voltage"],
            )
            and np.array_equal(
                replicate["a_effective"],
                full_again["a_effective"],
            )
            and np.array_equal(
                replicate["b_effective"],
                full_again["b_effective"],
            )
        )

        if not reproducible:
            raise RuntimeError(
                f"{target}: deterministic "
                "combined replicate failed"
            )

        #
        # Combined dose monotonicity.
        #
        combined_effects = [
            dose_rows[
                str(int(round(d * 100)))
            ][
                "combined"
            ][
                "effect_magnitude"
            ]
            for d in doses
        ]

        combined_monotonic = all(
            later >= earlier
            for earlier, later
            in zip(
                combined_effects,
                combined_effects[1:],
            )
        )

        artifact_systems.append(
            {
                "target":
                    target,

                "input_a":
                    a,

                "input_b":
                    b,

                "causal_frame_a":
                    frame_a,

                "causal_frame_b":
                    frame_b,

                "baseline": {
                    "input_a_effective":
                        base_a,

                    "input_b_effective":
                        base_b,

                    "metrics":
                        base_metrics,
                },

                "doses":
                    dose_rows,

                "validation": {
                    "sham_exact":
                        sham_exact,

                    "all_intervention_telemetry_verified":
                        True,

                    "combined_100pct_replicate_exact":
                        reproducible,
                },

                "combined_dose_monotonic":
                    combined_monotonic,
            }
        )

        prefix = f"target_{target}"

        npz_payload[
            f"{prefix}_baseline_voltage"
        ] = baseline[
            "voltage"
        ].astype(
            np.float32
        )

        npz_payload[
            f"{prefix}_baseline_a_effective"
        ] = baseline[
            "a_effective"
        ].astype(
            np.float32
        )

        npz_payload[
            f"{prefix}_baseline_b_effective"
        ] = baseline[
            "b_effective"
        ].astype(
            np.float32
        )

        print(
            "  PASS validation"
        )

    hashes_after = frozen_hashes()

    if hashes_before != hashes_after:
        raise RuntimeError(
            "frozen artifact hash changed"
        )

    np.savez_compressed(
        OUTPUT_NPZ,
        **npz_payload,
    )

    artifact = {
        "schema":
            "mq5-5-convergence-specificity-v1",

        "experiment_id":
            "mq5-5-convergence-specificity-v1",

        "phase":
            "MQ-5.5",

        "classification":
            "confirmatory",

        "condition":
            "A",

        "software_commit":
            git_commit(),

        "system_count":
            len(artifact_systems),

        "attenuation_levels":
            list(doses),

        "systems":
            artifact_systems,

        "validation": {
            "all_systems_completed":
                len(artifact_systems) == 3,

            "all_shams_exact":
                all(
                    x["validation"][
                        "sham_exact"
                    ]
                    for x in artifact_systems
                ),

            "all_intervention_telemetry_verified":
                all(
                    x["validation"][
                        "all_intervention_telemetry_verified"
                    ]
                    for x in artifact_systems
                ),

            "all_combined_replicates_exact":
                all(
                    x["validation"][
                        "combined_100pct_replicate_exact"
                    ]
                    for x in artifact_systems
                ),

            "frozen_artifacts_unchanged":
                True,
        },

        "interpretation": {
            "status":
                "NOT_YET_INTERPRETED",

            "statistical_synergy_claim":
                False,

            "statistical_subadditivity_claim":
                False,

            "biological_causality_claim":
                False,

            "financial_semantics_used":
                False,
        },

        "frozen_artifact_sha256":
            hashes_before,

        "npz_sha256":
            sha256_file(
                OUTPUT_NPZ
            ),
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
    print("=" * 110)
    print("MQ-5.5 CONVERGENCE RUN COMPLETE")
    print("=" * 110)

    for key, value in artifact[
        "validation"
    ].items():
        print(
            f"{key:42s}",
            value,
        )

    print()

    for system in artifact_systems:
        target = system["target"]
        a = system["input_a"]
        b = system["input_b"]

        print(
            f"{a} + {b} -> {target}"
        )

        print(
            "dose      E_A             E_B             "
            "E_AB            E_A+E_B         "
            "AB-(A+B)        AB>single"
        )

        for percent in (
            25,
            50,
            75,
            100,
        ):
            row = system[
                "doses"
            ][str(percent)]

            e_a = row[
                "a_only"
            ][
                "effect_magnitude"
            ]

            e_b = row[
                "b_only"
            ][
                "effect_magnitude"
            ]

            e_ab = row[
                "combined"
            ][
                "effect_magnitude"
            ]

            additive = row[
                "descriptive_additive_reference"
            ]

            delta = row[
                "combined_minus_additive_reference"
            ]

            exceeds = row[
                "combined_exceeds_each_single"
            ]

            print(
                f"{percent:3d}%  "
                f"{e_a:14.7g} "
                f"{e_b:14.7g} "
                f"{e_ab:14.7g} "
                f"{additive:14.7g} "
                f"{delta:14.7g} "
                f"{str(exceeds):>9s}"
            )

        print(
            "combined dose monotonic:",
            system[
                "combined_dose_monotonic"
            ],
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
