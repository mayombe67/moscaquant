from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tomllib

import numpy as np
from scipy import sparse

from config.paths import data_path
from brain.market_replay import (
    ASSETS,
    FRAME_COUNT,
    OBSERVATIONS,
    SENSORY_GAIN,
    synthetic_series,
    market_window_at,
)
from brain.market_temporal import MarketVisionTemporalEncoder
from brain.physiology_constrained_visual_transduction import (
    PhysiologyConstrainedVisualTransductionRuntime,
)
from brain.visual_transduction import VisualTransductionConfig
from market.features import compute_features
from market.normalization import CausalNormalizer

CONNECTOME = data_path("processed", "connectome-baseline-v1.npz")
RETINA = data_path("processed", "visual-r1-r6-map-v1.npz")
RELAY = data_path("processed", "visual-relay-map-v1.npz")
TERRITORIES = data_path("processed", "market-retinal-territories-v1.npz")
GRADED = data_path("processed", "mq3-2-graded-visual-types-v1.npz")
CAUSAL = data_path("experiments", "mq3-2-causal-path-decomposition-v1.json")
OUTPUT = data_path("experiments", "mq3-pd-propagation-depth-v1.json")

CONFIG = Path("config/controls/mq3-pd-propagation-depth-v1.toml")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            block = handle.read(1024 * 1024)
            if not block:
                break
            digest.update(block)
    return digest.hexdigest()


def load_protocol(path: Path = CONFIG) -> dict:
    with path.open("rb") as handle:
        return tomllib.load(handle)


def build_hop_sets(causal: dict) -> dict[int, np.ndarray]:
    """Union nodes by source-relative hop from frozen first-positive paths."""
    hops: dict[int, set[int]] = {}

    for target in causal["targets"]:
        frame_record = next(
            frame
            for frame in target["frames"]
            if frame["label"] == "first_positive"
        )

        for path in frame_record["paths"]:
            nodes = [int(x) for x in path["nodes"]]
            for hop, node in enumerate(nodes):
                hops.setdefault(hop, set()).add(node)

    if not hops:
        raise RuntimeError("no first-positive causal paths found")

    return {
        hop: np.asarray(sorted(nodes), dtype=np.int32)
        for hop, nodes in sorted(hops.items())
    }


def summarize_hop_frame(
    voltage: np.ndarray,
    spikes: np.ndarray,
    effective: np.ndarray,
    indices: np.ndarray,
) -> dict:
    local_voltage = np.asarray(voltage[indices], dtype=np.float64)
    local_spikes = np.asarray(spikes[indices], dtype=bool)
    local_effective = np.asarray(effective[indices], dtype=np.float64)

    positive_voltage = np.maximum(local_voltage, 0.0)
    positive_effective = np.maximum(local_effective, 0.0)

    return {
        "integrated_positive_voltage": float(positive_voltage.sum()),
        "mean_positive_voltage": float(positive_voltage.mean()),
        "maximum_voltage": float(local_voltage.max()),
        "active_neuron_count": int(np.count_nonzero(local_effective > 0.0)),
        "active_neuron_fraction": float(np.mean(local_effective > 0.0)),
        "integrated_effective_activity": float(positive_effective.sum()),
        "mean_effective_activity": float(positive_effective.mean()),
        "spike_count": int(np.count_nonzero(local_spikes)),
    }


def finalize_hop(acc: dict, frames: int) -> dict:
    integrated_v = float(acc["integrated_positive_voltage"])
    integrated_a = float(acc["integrated_effective_activity"])

    return {
        "node_count": int(acc["node_count"]),
        "frames": int(frames),
        "integrated_positive_voltage": integrated_v,
        "episode_mean_positive_voltage": integrated_v / frames,
        "maximum_voltage": float(acc["maximum_voltage"]),
        "integrated_effective_activity": integrated_a,
        "episode_mean_effective_activity": integrated_a / frames,
        "active_neuron_frame_count": int(acc["active_neuron_frame_count"]),
        "active_neuron_fraction_mean": (
            float(acc["active_neuron_fraction_sum"]) / frames
        ),
        "spike_count": int(acc["spike_count"]),
        "first_positive_frame": acc["first_positive_frame"],
        "first_effective_frame": acc["first_effective_frame"],
    }


def add_survival_ratios(hops: list[dict]) -> list[dict]:
    if not hops:
        return hops

    base_v = hops[0]["integrated_positive_voltage"]
    base_a = hops[0]["integrated_effective_activity"]

    previous_v = None
    previous_a = None

    for item in hops:
        v = item["integrated_positive_voltage"]
        a = item["integrated_effective_activity"]

        item["voltage_survival_vs_hop0"] = (
            None if base_v <= 0.0 else float(v / base_v)
        )
        item["effective_survival_vs_hop0"] = (
            None if base_a <= 0.0 else float(a / base_a)
        )
        item["voltage_survival_vs_previous"] = (
            None if previous_v is None or previous_v <= 0.0
            else float(v / previous_v)
        )
        item["effective_survival_vs_previous"] = (
            None if previous_a is None or previous_a <= 0.0
            else float(a / previous_a)
        )

        previous_v = v
        previous_a = a

    return hops


def run_condition_a(
    *,
    connectome,
    retinal_indices,
    hop_sets,
    release_gain: float,
) -> dict:
    runtime = PhysiologyConstrainedVisualTransductionRuntime(
        connectome=connectome,
        retinal_indices=retinal_indices,
        relay_artifact=RELAY,
        graded_artifact=GRADED,
        config=VisualTransductionConfig(release_gain=release_gain),
    )

    normalizers = [
        CausalNormalizer(window_size=64, min_history=8)
        for _ in ASSETS
    ]
    series = [
        synthetic_series("A", asset_index)
        for asset_index in range(6)
    ]
    encoder = MarketVisionTemporalEncoder(TERRITORIES)

    accumulators = {}
    for hop, indices in hop_sets.items():
        accumulators[hop] = {
            "node_count": len(indices),
            "integrated_positive_voltage": 0.0,
            "maximum_voltage": 0.0,
            "integrated_effective_activity": 0.0,
            "active_neuron_frame_count": 0,
            "active_neuron_fraction_sum": 0.0,
            "spike_count": 0,
            "first_positive_frame": None,
            "first_effective_frame": None,
        }

    voltage_digest = hashlib.sha256()
    spike_digest = hashlib.sha256()
    frame_number = 0

    for observation in range(OBSERVATIONS):
        normalized = np.empty((6, 7), dtype=np.float32)

        for asset_index in range(6):
            window = market_window_at(
                series[asset_index],
                observation,
            )
            features = compute_features(window)
            normalized[asset_index] = normalizers[
                asset_index
            ].transform(features)

        frames = encoder.encode_sequence(
            normalized,
            frame_count=FRAME_COUNT,
        )

        for stimulus in frames:
            spikes = (
                runtime.step(
                    stimulus * SENSORY_GAIN,
                    generation=frame_number,
                ) > 0
            )
            effective = runtime.effective_activity()

            voltage_digest.update(
                np.ascontiguousarray(runtime.voltage).tobytes()
            )
            spike_digest.update(
                np.packbits(spikes).tobytes()
            )

            for hop, indices in hop_sets.items():
                metrics = summarize_hop_frame(
                    runtime.voltage,
                    spikes,
                    effective,
                    indices,
                )
                acc = accumulators[hop]

                acc["integrated_positive_voltage"] += (
                    metrics["integrated_positive_voltage"]
                )
                acc["maximum_voltage"] = max(
                    acc["maximum_voltage"],
                    metrics["maximum_voltage"],
                )
                acc["integrated_effective_activity"] += (
                    metrics["integrated_effective_activity"]
                )
                acc["active_neuron_frame_count"] += (
                    metrics["active_neuron_count"]
                )
                acc["active_neuron_fraction_sum"] += (
                    metrics["active_neuron_fraction"]
                )
                acc["spike_count"] += metrics["spike_count"]

                if (
                    acc["first_positive_frame"] is None
                    and metrics["integrated_positive_voltage"] > 0.0
                ):
                    acc["first_positive_frame"] = frame_number

                if (
                    acc["first_effective_frame"] is None
                    and metrics["integrated_effective_activity"] > 0.0
                ):
                    acc["first_effective_frame"] = frame_number

            frame_number += 1

    expected_frames = OBSERVATIONS * FRAME_COUNT
    if frame_number != expected_frames:
        raise RuntimeError(
            f"expected {expected_frames} frames, got {frame_number}"
        )

    hop_records = []
    for hop, indices in hop_sets.items():
        record = finalize_hop(
            accumulators[hop],
            frame_number,
        )
        record["hop"] = int(hop)
        record["model_indices"] = [int(x) for x in indices]
        hop_records.append(record)

    add_survival_ratios(hop_records)

    return {
        "condition": "A",
        "release_gain": float(release_gain),
        "frames": frame_number,
        "hops": hop_records,
        "voltage_trace_sha256": voltage_digest.hexdigest(),
        "spike_trace_sha256": spike_digest.hexdigest(),
    }


def main() -> None:
    protocol = load_protocol()
    frozen_gain = float(protocol["gain"]["frozen_release_gain"])
    sweep_multipliers = [
        float(x)
        for x in protocol["gain"]["diagnostic_multipliers"]
    ]

    causal = json.loads(CAUSAL.read_text(encoding="utf-8"))
    if causal.get("condition") != "A":
        raise RuntimeError(
            "expected frozen causal decomposition for Condition A"
        )

    hop_sets = build_hop_sets(causal)

    connectome = sparse.load_npz(CONNECTOME).tocsr()
    retina = np.load(RETINA)
    retinal_indices = np.asarray(
        retina["neuron_index"],
        dtype=np.int32,
    )

    print("=" * 88)
    print("MQ-3.PD PROPAGATION-DEPTH DIAGNOSTIC")
    print("=" * 88)
    print("condition: A")
    print("frozen release gain:", frozen_gain)
    print("hop sets:", {k: len(v) for k, v in hop_sets.items()})
    print()

    frozen = run_condition_a(
        connectome=connectome,
        retinal_indices=retinal_indices,
        hop_sets=hop_sets,
        release_gain=frozen_gain,
    )

    sweep = []
    for multiplier in sweep_multipliers:
        gain = frozen_gain * multiplier
        print(
            "diagnostic gain:",
            gain,
            f"({multiplier:g}x)",
        )
        result = run_condition_a(
            connectome=connectome,
            retinal_indices=retinal_indices,
            hop_sets=hop_sets,
            release_gain=gain,
        )
        result["gain_multiplier"] = multiplier
        sweep.append(result)

    output = {
        "experiment": "mq3-pd-propagation-depth-v1",
        "status": "DIAGNOSTIC",
        "condition": "A",
        "authoritative_subject_data": True,
        "modifies_frozen_model": False,
        "financial_semantics_used": False,
        "path_basis": (
            "union of frozen MQ-3.2 first-positive "
            "activity-supported causal paths"
        ),
        "hop_semantics": (
            "hop 0 is a frozen path source; hop N is N "
            "directed edges downstream within those frozen paths"
        ),
        "frozen_gain_run": frozen,
        "diagnostic_gain_sweep": sweep,
        "sources": {
            "causal_path_decomposition": str(CAUSAL),
            "causal_path_decomposition_sha256": sha256_file(CAUSAL),
            "connectome": str(CONNECTOME),
            "connectome_sha256": sha256_file(CONNECTOME),
            "retina": str(RETINA),
            "retina_sha256": sha256_file(RETINA),
            "graded_population": str(GRADED),
            "graded_population_sha256": sha256_file(GRADED),
            "protocol": str(CONFIG),
            "protocol_sha256": sha256_file(CONFIG),
        },
        "interpretation_limits": [
            (
                "This diagnostic measures propagation in the frozen "
                "MoscaQuant computational model."
            ),
            (
                "It does not establish a universal MaleCNS biological "
                "propagation-depth limit."
            ),
            (
                "Diagnostic gain-sweep runs are sensitivity analyses "
                "and do not modify the frozen MQ-3.2 model."
            ),
            (
                "Hop sets are derived from previously accepted "
                "first-positive causal paths and are not a new route search."
            ),
        ],
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print()
    print("FROZEN GAIN SUMMARY")
    for hop in frozen["hops"]:
        print(
            f"hop {hop['hop']}:",
            "nodes=", hop["node_count"],
            "V=", hop["integrated_positive_voltage"],
            "A=", hop["integrated_effective_activity"],
            "spikes=", hop["spike_count"],
            "firstV=", hop["first_positive_frame"],
            "survivalV=", hop["voltage_survival_vs_hop0"],
        )

    print()
    print("artifact:", OUTPUT)
    print("sha256:", sha256_file(OUTPUT))
    print("FROZEN MODEL MODIFIED: NO")
    print("FINANCIAL SEMANTICS USED: NO")


if __name__ == "__main__":
    main()
