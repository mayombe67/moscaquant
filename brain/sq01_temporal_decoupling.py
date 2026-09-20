from __future__ import annotations
from config.paths import data_path


import hashlib
import json
from pathlib import Path
import subprocess
import tomllib

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
from brain.mq2_1_market_replay import run_replay as reference_run_replay
from brain.visual_transduction import (
    VisualTransductionConfig,
    VisualTransductionRuntime,
)
from market.features import compute_features
from market.normalization import CausalNormalizer


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "experiments" / "sq01_temporal_decoupling_v1.json"

CONNECTOME = data_path('processed', 'connectome-baseline-v1.npz')
RETINA = data_path('processed', 'visual-r1-r6-map-v1.npz')
RELAY = data_path('processed', 'visual-relay-map-v1.npz')
TERRITORIES = data_path('processed', 'market-retinal-territories-v1.npz')
VISUAL_CONFIG = ROOT / "config" / "sensory" / "visual-transduction-v1.toml"

OUTPUT = ROOT / "artifacts" / "sidequests" / "sq01-temporal-decoupling-v1.json"


def digest_array(digest, array):
    digest.update(np.ascontiguousarray(array).tobytes())


def find_release_gain(value, path=""):
    matches = []

    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}" if path else key
            if key in {"release_gain", "release_gain_v1"} and isinstance(child, (int, float)):
                matches.append((child_path, float(child)))
            matches.extend(find_release_gain(child, child_path))

    return matches


def load_release_gain():
    with VISUAL_CONFIG.open("rb") as handle:
        data = tomllib.load(handle)

    matches = find_release_gain(data)
    unique = {(path, value) for path, value in matches}

    if len(unique) != 1:
        raise RuntimeError(
            "Expected exactly one numeric release_gain/release_gain_v1 "
            f"in {VISUAL_CONFIG}; found {sorted(unique)}"
        )

    path, value = next(iter(unique))
    return value, path


def npz_indices(path):
    with np.load(path, allow_pickle=False) as data:
        if "neuron_index" not in data.files:
            raise RuntimeError(f"{path} lacks neuron_index; keys={data.files}")
        return np.asarray(data["neuron_index"], dtype=np.int32)


def load_relay():
    with np.load(RELAY, allow_pickle=False) as data:
        for key in ("neuron_index", "type"):
            if key not in data.files:
                raise RuntimeError(f"{RELAY} lacks {key}; keys={data.files}")
        return (
            np.asarray(data["neuron_index"], dtype=np.int32),
            np.asarray(data["type"]),
        )


def source_commit():
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    return result.stdout.strip()


def config_digest():
    return hashlib.sha256(CONFIG_PATH.read_bytes()).hexdigest()


def run_variant(
    condition,
    connectome,
    retinal_indices,
    relay_indices,
    relay_types,
    release_gain,
    *,
    frame_count,
    dt_ms,
    stimulus_scale,
):
    normalizers = [
        CausalNormalizer(window_size=64, min_history=8)
        for _ in ASSETS
    ]

    series = [
        synthetic_series(condition, asset_index)
        for asset_index in range(len(ASSETS))
    ]

    encoder = MarketVisionTemporalEncoder(TERRITORIES)

    runtime = VisualTransductionRuntime(
        connectome=connectome,
        retinal_indices=retinal_indices,
        relay_artifact=RELAY,
        config=VisualTransductionConfig(
            dt_ms=float(dt_ms),
            tau_ms=20.0,
            threshold=1.0,
            reset=0.0,
            release_gain=release_gain,
        ),
    )

    n = connectome.shape[0]

    retinal_mask = np.zeros(n, dtype=bool)
    retinal_mask[retinal_indices] = True

    relay_mask = np.zeros(n, dtype=bool)
    relay_mask[relay_indices] = True
    wider_mask = ~(retinal_mask | relay_mask)

    excitatory_relay_mask = np.isin(relay_types, ("L2", "L3"))

    normalized_hash = hashlib.sha256()
    retinal_hash = hashlib.sha256()
    neural_hash = hashlib.sha256()
    relay_hash = hashlib.sha256()
    wider_hash = hashlib.sha256()

    retinal_spikes = 0
    relay_spikes = 0
    wider_spikes = 0

    unique_retinal = np.zeros(n, dtype=bool)
    unique_relay = np.zeros(n, dtype=bool)
    unique_wider = np.zeros(n, dtype=bool)

    frame_spike_counts = []
    relay_frame_counts = []
    wider_frame_counts = []

    first_relay_frame = None
    first_excitatory_relay_frame = None
    first_wider_frame = None

    global_frame = 0

    for observation in range(OBSERVATIONS):
        normalized = np.empty((6, 7), dtype=np.float32)

        for asset_index in range(6):
            window = market_window_at(series[asset_index], observation)
            features = compute_features(window)
            normalized[asset_index] = normalizers[asset_index].transform(features)

        digest_array(normalized_hash, normalized)

        retinal_frames = encoder.encode_sequence(
            normalized,
            frame_count=int(frame_count),
        )

        # Experimental scaling is applied after the frozen encoder.
        # This leaves encoder semantics untouched while making the declared
        # matched-resampling arm preserve the baseline summed stimulus multiplier.
        if float(stimulus_scale) != 1.0:
            retinal_frames = retinal_frames * np.float32(stimulus_scale)

        digest_array(retinal_hash, retinal_frames)

        for stimulus in retinal_frames:
            spikes = runtime.step(stimulus * SENSORY_GAIN) > 0

            retinal_fired = spikes & retinal_mask
            relay_fired = spikes & relay_mask
            wider_fired = spikes & wider_mask
            local_relay = spikes[relay_indices]

            digest_array(neural_hash, np.packbits(spikes))
            digest_array(relay_hash, np.packbits(local_relay))
            digest_array(wider_hash, np.packbits(wider_fired))

            retinal_count = int(np.count_nonzero(retinal_fired))
            relay_count = int(np.count_nonzero(relay_fired))
            wider_count = int(np.count_nonzero(wider_fired))

            retinal_spikes += retinal_count
            relay_spikes += relay_count
            wider_spikes += wider_count

            unique_retinal |= retinal_fired
            unique_relay |= relay_fired
            unique_wider |= wider_fired

            frame_spike_counts.append(int(np.count_nonzero(spikes)))
            relay_frame_counts.append(relay_count)
            wider_frame_counts.append(wider_count)

            if relay_count and first_relay_frame is None:
                first_relay_frame = global_frame

            if (
                first_excitatory_relay_frame is None
                and np.any(local_relay & excitatory_relay_mask)
            ):
                first_excitatory_relay_frame = global_frame

            if wider_count and first_wider_frame is None:
                first_wider_frame = global_frame

            global_frame += 1

    def time_ms(frame):
        if frame is None:
            return None
        return float(frame) * float(dt_ms)

    return {
        "condition": condition,
        "frame_count": int(frame_count),
        "dt_ms": float(dt_ms),
        "stimulus_scale": float(stimulus_scale),
        "observation_duration_ms": float(frame_count) * float(dt_ms),
        "summed_stimulus_multiplier": float(frame_count) * float(stimulus_scale),
        "normalized_hash": normalized_hash.hexdigest(),
        "retinal_hash": retinal_hash.hexdigest(),
        "neural_hash": neural_hash.hexdigest(),
        "relay_hash": relay_hash.hexdigest(),
        "wider_hash": wider_hash.hexdigest(),
        "final_voltage_hash": hashlib.sha256(runtime.voltage.tobytes()).hexdigest(),
        "retinal_spikes": retinal_spikes,
        "relay_spikes": relay_spikes,
        "wider_spikes": wider_spikes,
        "unique_retinal": int(np.count_nonzero(unique_retinal)),
        "unique_relay": int(np.count_nonzero(unique_relay)),
        "unique_wider": int(np.count_nonzero(unique_wider)),
        "first_relay_frame": first_relay_frame,
        "first_relay_time_ms": time_ms(first_relay_frame),
        "first_excitatory_relay_frame": first_excitatory_relay_frame,
        "first_excitatory_relay_time_ms": time_ms(first_excitatory_relay_frame),
        "first_wider_frame": first_wider_frame,
        "first_wider_time_ms": time_ms(first_wider_frame),
        "frame_spike_counts": frame_spike_counts,
        "relay_frame_counts": relay_frame_counts,
        "wider_frame_counts": wider_frame_counts,
        "final_voltage_max": float(runtime.voltage.max()),
        "final_voltage_min": float(runtime.voltage.min()),
    }


PARITY_KEYS = (
    "normalized_hash",
    "retinal_hash",
    "neural_hash",
    "relay_hash",
    "wider_hash",
    "final_voltage_hash",
    "retinal_spikes",
    "relay_spikes",
    "wider_spikes",
    "unique_retinal",
    "unique_relay",
    "unique_wider",
    "first_relay_frame",
    "first_excitatory_relay_frame",
    "first_wider_frame",
    "frame_spike_counts",
    "relay_frame_counts",
    "wider_frame_counts",
    "final_voltage_max",
    "final_voltage_min",
)


DETERMINISM_KEYS = PARITY_KEYS


def exact_subset_equal(a, b, keys):
    return all(a[key] == b[key] for key in keys)


def main():
    config = json.loads(CONFIG_PATH.read_text())

    connectome = sparse.load_npz(CONNECTOME).tocsr()
    retinal_indices = npz_indices(RETINA)
    relay_indices, relay_types = load_relay()
    release_gain, release_gain_path = load_release_gain()

    baseline_variant = next(
        item for item in config["variants"]
        if item["id"] == "BASELINE"
    )

    print("=" * 72)
    print("SQ-01 TEMPORAL DECOUPLING // TEMPORAL JETLAG")
    print("=" * 72)
    print("source commit:", source_commit())
    print("config sha256:", config_digest())
    print("release gain path:", release_gain_path)
    print("release gain:", release_gain)
    print()

    print("BASELINE HARNESS PARITY")
    reference = {}
    sidequest_baseline = {}

    for condition in config["conditions"]:
        reference[condition] = reference_run_replay(
            condition,
            connectome,
            retinal_indices,
            relay_indices,
            relay_types,
            release_gain,
        )

        sidequest_baseline[condition] = run_variant(
            condition,
            connectome,
            retinal_indices,
            relay_indices,
            relay_types,
            release_gain,
            frame_count=baseline_variant["frame_count"],
            dt_ms=baseline_variant["dt_ms"],
            stimulus_scale=baseline_variant["stimulus_scale"],
        )

        passed = exact_subset_equal(
            reference[condition],
            sidequest_baseline[condition],
            PARITY_KEYS,
        )

        print(f"  condition {condition}: {'PASS' if passed else 'FAIL'}")

        if not passed:
            differing = [
                key for key in PARITY_KEYS
                if reference[condition][key] != sidequest_baseline[condition][key]
            ]
            raise RuntimeError(
                f"SQ-01 baseline parity failed for {condition}: {differing}"
            )

    print()
    print("VARIANT MATRIX")

    rows = []

    for variant in config["variants"]:
        print()
        print(
            variant["id"],
            f"frames={variant['frame_count']}",
            f"dt={variant['dt_ms']}ms",
            f"scale={variant['stimulus_scale']}",
        )

        a1 = run_variant(
            "A",
            connectome,
            retinal_indices,
            relay_indices,
            relay_types,
            release_gain,
            frame_count=variant["frame_count"],
            dt_ms=variant["dt_ms"],
            stimulus_scale=variant["stimulus_scale"],
        )
        a2 = run_variant(
            "A",
            connectome,
            retinal_indices,
            relay_indices,
            relay_types,
            release_gain,
            frame_count=variant["frame_count"],
            dt_ms=variant["dt_ms"],
            stimulus_scale=variant["stimulus_scale"],
        )
        b = run_variant(
            "B",
            connectome,
            retinal_indices,
            relay_indices,
            relay_types,
            release_gain,
            frame_count=variant["frame_count"],
            dt_ms=variant["dt_ms"],
            stimulus_scale=variant["stimulus_scale"],
        )

        deterministic = exact_subset_equal(a1, a2, DETERMINISM_KEYS)
        ab_relay_discrimination = a1["relay_hash"] != b["relay_hash"]
        ab_wider_discrimination = a1["wider_hash"] != b["wider_hash"]

        print("  A/A exact:", "PASS" if deterministic else "FAIL")
        print(
            "  A/B relay discrimination:",
            "YES" if ab_relay_discrimination else "NO",
        )
        print(
            "  A/B wider discrimination:",
            "YES" if ab_wider_discrimination else "NO",
        )
        print(
            "  A relay/wider spikes:",
            a1["relay_spikes"],
            "/",
            a1["wider_spikes"],
        )
        print(
            "  B relay/wider spikes:",
            b["relay_spikes"],
            "/",
            b["wider_spikes"],
        )
        print(
            "  A first relay/wider ms:",
            a1["first_relay_time_ms"],
            "/",
            a1["first_wider_time_ms"],
        )
        print(
            "  B first relay/wider ms:",
            b["first_relay_time_ms"],
            "/",
            b["first_wider_time_ms"],
        )

        if not deterministic:
            raise RuntimeError(f"A/A determinism failed for {variant['id']}")

        rows.append({
            "variant": variant,
            "deterministic": deterministic,
            "ab_relay_discrimination": ab_relay_discrimination,
            "ab_wider_discrimination": ab_wider_discrimination,
            "A": a1,
            "B": b,
        })

    artifact = {
        "schema_version": "moscaquant.sidequest.temporal_decoupling_result/v1",
        "sidequest_id": config["sidequest_id"],
        "title": config["title"],
        "lore_name": config["lore_name"],
        "source_commit": source_commit(),
        "config_path": str(CONFIG_PATH.relative_to(ROOT)),
        "config_sha256": config_digest(),
        "release_gain_config_path": str(VISUAL_CONFIG.relative_to(ROOT)),
        "release_gain_key": release_gain_path,
        "release_gain": release_gain,
        "baseline_harness_parity": True,
        "claim_boundary": config["claim_boundary"],
        "rows": rows,
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(artifact, indent=2) + "\n")

    print()
    print("=" * 72)
    print("SQ-01 RUN COMPLETE")
    print("=" * 72)
    print("artifact:", OUTPUT)
    print("baseline harness parity: PASS")
    print("all A/A determinism checks: PASS")
    print()
    print("Interpret only after reviewing the complete artifact.")


if __name__ == "__main__":
    main()
