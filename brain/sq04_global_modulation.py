from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess

import numpy as np
from scipy import sparse

from brain.market_replay import (
    ASSETS,
    OBSERVATIONS,
    SENSORY_GAIN,
    market_window_at,
    synthetic_series,
)
from brain.market_temporal import MarketVisionTemporalEncoder
from brain.sq01_temporal_decoupling import (
    CONNECTOME,
    RELAY,
    RETINA,
    TERRITORIES,
    VISUAL_CONFIG,
    load_relay,
    load_release_gain,
    npz_indices,
)
from brain.visual_transduction import (
    VisualTransductionConfig,
    VisualTransductionRuntime,
)
from market.features import compute_features
from market.normalization import CausalNormalizer


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "experiments" / "sq04_global_modulation_v1.json"
OUTPUT = ROOT / "artifacts" / "sidequests" / "sq04-global-modulation-v1.json"

CONDITION = "A"
FRAME_COUNT = 16
DT_MS = 1.0
RESET = 0.0


def source_commit() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    return result.stdout.strip()


def config_digest() -> str:
    return hashlib.sha256(CONFIG_PATH.read_bytes()).hexdigest()


def digest_array(array: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(array).tobytes()).hexdigest()


def build_normalized_observations(condition: str = CONDITION) -> list[np.ndarray]:
    normalizers = [
        CausalNormalizer(window_size=64, min_history=8)
        for _ in ASSETS
    ]
    series = [
        synthetic_series(condition, asset_index)
        for asset_index in range(len(ASSETS))
    ]

    observations: list[np.ndarray] = []

    for observation in range(OBSERVATIONS):
        normalized = np.empty((len(ASSETS), 7), dtype=np.float32)

        for asset_index in range(len(ASSETS)):
            window = market_window_at(series[asset_index], observation)
            features = compute_features(window)
            normalized[asset_index] = normalizers[asset_index].transform(features)

        observations.append(normalized)

    return observations


def run_variant(
    *,
    threshold: float,
    tau_ms: float,
    connectome,
    retinal_indices,
    relay_indices,
    release_gain: float,
    observations: list[np.ndarray],
) -> dict:
    encoder = MarketVisionTemporalEncoder(TERRITORIES)
    runtime = VisualTransductionRuntime(
        connectome=connectome,
        retinal_indices=retinal_indices,
        relay_artifact=RELAY,
        config=VisualTransductionConfig(
            dt_ms=DT_MS,
            tau_ms=float(tau_ms),
            threshold=float(threshold),
            reset=RESET,
            release_gain=release_gain,
        ),
    )

    n = connectome.shape[0]

    retinal_mask = np.zeros(n, dtype=bool)
    retinal_mask[retinal_indices] = True

    relay_mask = np.zeros(n, dtype=bool)
    relay_mask[relay_indices] = True

    wider_mask = ~(retinal_mask | relay_mask)

    retinal_hash = hashlib.sha256()
    neural_hash = hashlib.sha256()
    relay_hash = hashlib.sha256()
    wider_hash = hashlib.sha256()

    retinal_spikes = 0
    relay_spikes = 0
    wider_spikes = 0

    first_relay_frame = None
    first_wider_frame = None
    global_frame = 0

    for normalized in observations:
        retinal_frames = encoder.encode_sequence(
            normalized,
            frame_count=FRAME_COUNT,
        )
        retinal_hash.update(np.ascontiguousarray(retinal_frames).tobytes())

        for stimulus in retinal_frames:
            spikes = runtime.step(stimulus * SENSORY_GAIN) > 0

            retinal_fired = spikes & retinal_mask
            relay_fired = spikes & relay_mask
            wider_fired = spikes & wider_mask

            retinal_hash.update(np.packbits(retinal_fired).tobytes())
            neural_hash.update(np.packbits(spikes).tobytes())
            relay_hash.update(np.packbits(relay_fired).tobytes())
            wider_hash.update(np.packbits(wider_fired).tobytes())

            retinal_count = int(np.count_nonzero(retinal_fired))
            relay_count = int(np.count_nonzero(relay_fired))
            wider_count = int(np.count_nonzero(wider_fired))

            retinal_spikes += retinal_count
            relay_spikes += relay_count
            wider_spikes += wider_count

            if relay_count and first_relay_frame is None:
                first_relay_frame = global_frame

            if wider_count and first_wider_frame is None:
                first_wider_frame = global_frame

            global_frame += 1

    def time_ms(frame):
        return None if frame is None else float(frame) * DT_MS

    return {
        "threshold": float(threshold),
        "tau_ms": float(tau_ms),
        "dt_ms": DT_MS,
        "frame_count": FRAME_COUNT,
        "retinal_hash": retinal_hash.hexdigest(),
        "neural_hash": neural_hash.hexdigest(),
        "relay_hash": relay_hash.hexdigest(),
        "wider_hash": wider_hash.hexdigest(),
        "retinal_spike_count": retinal_spikes,
        "relay_spike_count": relay_spikes,
        "wider_network_spike_count": wider_spikes,
        "first_relay_spike_time_ms_if_any": time_ms(first_relay_frame),
        "first_wider_spike_time_ms_if_any": time_ms(first_wider_frame),
        "final_voltage_hash": digest_array(runtime.voltage),
        "final_voltage_max": float(runtime.voltage.max()),
        "final_voltage_min": float(runtime.voltage.min()),
    }


DETERMINISM_KEYS = (
    "retinal_hash",
    "neural_hash",
    "relay_hash",
    "wider_hash",
    "retinal_spike_count",
    "relay_spike_count",
    "wider_network_spike_count",
    "first_relay_spike_time_ms_if_any",
    "first_wider_spike_time_ms_if_any",
    "final_voltage_hash",
    "final_voltage_max",
    "final_voltage_min",
)


def deterministic_equal(a: dict, b: dict) -> bool:
    return all(a[key] == b[key] for key in DETERMINISM_KEYS)


def main():
    config = json.loads(CONFIG_PATH.read_text())

    connectome = sparse.load_npz(CONNECTOME).tocsr()
    retinal_indices = npz_indices(RETINA)
    relay_indices, _relay_types = load_relay()
    release_gain, release_gain_path = load_release_gain()
    observations = build_normalized_observations()

    print("=" * 72)
    print("SQ-04 GLOBAL MODULATION SENSITIVITY")
    print("=" * 72)
    print("source commit:", source_commit())
    print("config sha256:", config_digest())
    print("condition:", CONDITION)
    print("frame_count:", FRAME_COUNT)
    print("dt_ms:", DT_MS)
    print("release gain path:", release_gain_path)
    print("release gain:", release_gain)
    print()

    rows = []

    for variant in config["variants"]:
        print(
            variant["id"],
            f"threshold={variant['threshold']}",
            f"tau_ms={variant['tau_ms']}",
        )

        first = run_variant(
            threshold=variant["threshold"],
            tau_ms=variant["tau_ms"],
            connectome=connectome,
            retinal_indices=retinal_indices,
            relay_indices=relay_indices,
            release_gain=release_gain,
            observations=observations,
        )
        second = run_variant(
            threshold=variant["threshold"],
            tau_ms=variant["tau_ms"],
            connectome=connectome,
            retinal_indices=retinal_indices,
            relay_indices=relay_indices,
            release_gain=release_gain,
            observations=observations,
        )

        deterministic = deterministic_equal(first, second)

        print("  A/A exact:", "PASS" if deterministic else "FAIL")
        print(
            "  retinal/relay/wider spikes:",
            first["retinal_spike_count"],
            "/",
            first["relay_spike_count"],
            "/",
            first["wider_network_spike_count"],
        )
        print(
            "  first relay/wider ms:",
            first["first_relay_spike_time_ms_if_any"],
            "/",
            first["first_wider_spike_time_ms_if_any"],
        )
        print(
            "  final voltage min/max:",
            first["final_voltage_min"],
            "/",
            first["final_voltage_max"],
        )
        print()

        if not deterministic:
            raise RuntimeError(f"determinism failed for {variant['id']}")

        rows.append({
            "variant": variant,
            "deterministic_AA_replay": deterministic,
            "result": first,
        })

    reference = next(
        row["result"]
        for row in rows
        if row["variant"]["id"] == "REFERENCE"
    )

    for row in rows:
        result = row["result"]
        row["differs_from_reference"] = {
            key: result[key] != reference[key]
            for key in DETERMINISM_KEYS
        }

    artifact = {
        "schema_version": "moscaquant.sidequest.global_modulation_result/v1",
        "sidequest_id": config["sidequest_id"],
        "name": config["name"],
        "source_commit": source_commit(),
        "config_path": str(CONFIG_PATH.relative_to(ROOT)),
        "config_sha256": config_digest(),
        "implementation": {
            "condition": CONDITION,
            "frame_count": FRAME_COUNT,
            "dt_ms": DT_MS,
            "reset": RESET,
            "release_gain_config_path": str(VISUAL_CONFIG.relative_to(ROOT)),
            "release_gain_key": release_gain_path,
            "release_gain": release_gain,
        },
        "claim_boundary": config["claim_boundary"],
        "rows": rows,
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(artifact, indent=2) + "\n")

    print("=" * 72)
    print("SQ-04 RUN COMPLETE")
    print("=" * 72)
    print("artifact:", OUTPUT)
    print("all A/A determinism checks: PASS")
    print("Interpret only after reviewing the complete artifact.")


if __name__ == "__main__":
    main()
