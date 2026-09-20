from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess

import numpy as np
from scipy import sparse

from brain.market_replay import ASSETS, OBSERVATIONS, SENSORY_GAIN, market_window_at, synthetic_series
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
from brain.visual_transduction import VisualTransductionConfig, VisualTransductionRuntime
from market.features import compute_features
from market.normalization import CausalNormalizer


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "experiments" / "sq02_ghost_market_v1.json"
OUTPUT = ROOT / "artifacts" / "sidequests" / "sq02-ghost-market-v1.json"

FRAME_COUNT = 16
DT_MS = 1.0
TAU_MS = 20.0
THRESHOLD = 1.0
RESET = 0.0

# Precommitted runner implementation choices.
CONDITION = "A"
MUTATION_OBSERVATION = OBSERVATIONS // 2
EXTREME_ROW = 0
EXTREME_FEATURE_COLUMN = 1  # momentum; signed and directly used by temporal encoder


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


def mutate_feature_tensor(base: np.ndarray, variant_id: str) -> np.ndarray:
    values = np.array(base, copy=True)

    if variant_id == "BASELINE_VALID":
        return values
    if variant_id == "FEATURE_NAN":
        values[0, 0] = np.float32(np.nan)
        return values
    if variant_id == "FEATURE_POS_INF":
        values[0, 0] = np.float32(np.inf)
        return values
    if variant_id == "FEATURE_NEG_INF":
        values[0, 0] = np.float32(-np.inf)
        return values
    if variant_id == "FEATURE_SHORT_ROW":
        return values[:, :-1]
    if variant_id == "FEATURE_LONG_ROW":
        return np.concatenate(
            [values, np.zeros((values.shape[0], 1), dtype=np.float32)],
            axis=1,
        )

    raise ValueError(f"unknown Stage A variant: {variant_id}")


def mutate_observation_sequence(
    observations: list[np.ndarray],
    variant_id: str,
) -> list[np.ndarray]:
    copied = [np.array(item, copy=True) for item in observations]
    index = MUTATION_OBSERVATION

    if variant_id == "SEQUENCE_BASELINE":
        return copied
    if variant_id == "SEQUENCE_DUPLICATE_FRAME":
        return copied[:index] + [np.array(copied[index], copy=True)] + copied[index:]
    if variant_id == "SEQUENCE_DROP_FRAME":
        return copied[:index] + copied[index + 1:]
    if variant_id == "SEQUENCE_REVERSED":
        return list(reversed(copied))
    if variant_id == "SEQUENCE_FROZEN":
        frozen = np.array(copied[index], copy=True)
        return [np.array(frozen, copy=True) for _ in copied]

    raise ValueError(f"unknown Stage B variant: {variant_id}")


def mutate_finite_extreme(base: np.ndarray, variant_id: str) -> np.ndarray:
    values = np.array(base, copy=True)

    if variant_id == "EXTREME_X10":
        values[EXTREME_ROW, EXTREME_FEATURE_COLUMN] *= np.float32(10.0)
        return values
    if variant_id == "EXTREME_X100":
        values[EXTREME_ROW, EXTREME_FEATURE_COLUMN] *= np.float32(100.0)
        return values
    if variant_id == "ZERO_VECTOR":
        values.fill(np.float32(0.0))
        return values

    raise ValueError(f"unknown Stage C variant: {variant_id}")


def new_runtime(connectome, retinal_indices, release_gain):
    return VisualTransductionRuntime(
        connectome=connectome,
        retinal_indices=retinal_indices,
        relay_artifact=RELAY,
        config=VisualTransductionConfig(
            dt_ms=DT_MS,
            tau_ms=TAU_MS,
            threshold=THRESHOLD,
            reset=RESET,
            release_gain=release_gain,
        ),
    )


def run_neural_sequence(
    feature_sequence: list[np.ndarray],
    *,
    connectome,
    retinal_indices,
    relay_indices,
    release_gain,
) -> dict:
    encoder = MarketVisionTemporalEncoder(TERRITORIES)
    runtime = new_runtime(connectome, retinal_indices, release_gain)

    n = connectome.shape[0]
    retinal_mask = np.zeros(n, dtype=bool)
    retinal_mask[retinal_indices] = True

    relay_mask = np.zeros(n, dtype=bool)
    relay_mask[relay_indices] = True

    wider_mask = ~(retinal_mask | relay_mask)

    retinal_spikes = 0
    relay_spikes = 0
    wider_spikes = 0
    first_relay_frame = None
    global_frame = 0

    retinal_digest = hashlib.sha256()
    neural_digest = hashlib.sha256()

    retinal_energy_sum = 0.0
    retinal_energy_max = 0.0
    encoded_frame_count = 0

    for features in feature_sequence:
        frames = encoder.encode_sequence(features, frame_count=FRAME_COUNT)
        retinal_digest.update(np.ascontiguousarray(frames).tobytes())

        encoded_frame_count += int(frames.shape[0])
        frame_energy = frames.sum(axis=1, dtype=np.float64)
        retinal_energy_sum += float(frame_energy.sum())
        if len(frame_energy):
            retinal_energy_max = max(retinal_energy_max, float(frame_energy.max()))

        for stimulus in frames:
            spikes = runtime.step(stimulus * SENSORY_GAIN) > 0
            neural_digest.update(np.packbits(spikes).tobytes())

            retinal_count = int(np.count_nonzero(spikes & retinal_mask))
            relay_count = int(np.count_nonzero(spikes & relay_mask))
            wider_count = int(np.count_nonzero(spikes & wider_mask))

            retinal_spikes += retinal_count
            relay_spikes += relay_count
            wider_spikes += wider_count

            if relay_count and first_relay_frame is None:
                first_relay_frame = global_frame

            global_frame += 1

    first_relay_time_ms = (
        None
        if first_relay_frame is None
        else float(first_relay_frame) * DT_MS
    )

    return {
        "accepted_or_rejected": "ACCEPTED",
        "exception_type_if_rejected": None,
        "encoded_frame_count": encoded_frame_count,
        "retinal_stimulus_summary": {
            "sha256": retinal_digest.hexdigest(),
            "total_energy": retinal_energy_sum,
            "max_frame_energy": retinal_energy_max,
        },
        "neural_sha256": neural_digest.hexdigest(),
        "retinal_spike_count": retinal_spikes,
        "relay_spike_count": relay_spikes,
        "wider_network_spike_count": wider_spikes,
        "first_relay_spike_time_ms_if_any": first_relay_time_ms,
        "final_voltage_sha256": digest_array(runtime.voltage),
    }


DETERMINISM_KEYS = (
    "accepted_or_rejected",
    "exception_type_if_rejected",
    "encoded_frame_count",
    "retinal_stimulus_summary",
    "neural_sha256",
    "retinal_spike_count",
    "relay_spike_count",
    "wider_network_spike_count",
    "first_relay_spike_time_ms_if_any",
    "final_voltage_sha256",
)


def deterministic_equal(a: dict, b: dict) -> bool:
    return all(a.get(key) == b.get(key) for key in DETERMINISM_KEYS)


def run_stage_a_variant(
    variant_id: str,
    base_feature_tensor: np.ndarray,
    *,
    connectome,
    retinal_indices,
    relay_indices,
    release_gain,
) -> dict:
    encoder = MarketVisionTemporalEncoder(TERRITORIES)
    mutated = mutate_feature_tensor(base_feature_tensor, variant_id)

    try:
        # Explicitly test the real frozen encoder boundary first.
        frames = encoder.encode_sequence(mutated, frame_count=FRAME_COUNT)
    except Exception as exc:
        return {
            "accepted_or_rejected": "REJECTED",
            "exception_type_if_rejected": type(exc).__name__,
            "exception_message": str(exc),
            "encoded_frame_count": 0,
            "retinal_stimulus_summary": None,
            "neural_execution_reached": False,
            "relay_spike_count": None,
            "wider_network_spike_count": None,
            "first_relay_spike_time_ms_if_any": None,
        }

    # The malformed tensor crossed the encoder boundary. Execute only this isolated
    # observation in a fresh runtime so contamination cannot leak between variants.
    result = run_neural_sequence(
        [mutated],
        connectome=connectome,
        retinal_indices=retinal_indices,
        relay_indices=relay_indices,
        release_gain=release_gain,
    )
    result["neural_execution_reached"] = True
    result["preflight_retinal_sha256"] = digest_array(frames)
    return result


def run_stage_b_variant(
    variant_id: str,
    observations: list[np.ndarray],
    **kwargs,
) -> dict:
    return run_neural_sequence(
        mutate_observation_sequence(observations, variant_id),
        **kwargs,
    )


def run_stage_c_variant(
    variant_id: str,
    observations: list[np.ndarray],
    **kwargs,
) -> dict:
    mutated = [np.array(item, copy=True) for item in observations]
    mutated[MUTATION_OBSERVATION] = mutate_finite_extreme(
        mutated[MUTATION_OBSERVATION],
        variant_id,
    )
    return run_neural_sequence(mutated, **kwargs)


def main():
    config = json.loads(CONFIG_PATH.read_text())

    connectome = sparse.load_npz(CONNECTOME).tocsr()
    retinal_indices = npz_indices(RETINA)
    relay_indices, _relay_types = load_relay()
    release_gain, release_gain_path = load_release_gain()

    observations = build_normalized_observations()
    base_feature_tensor = observations[MUTATION_OBSERVATION]

    print("=" * 72)
    print("SQ-02 GHOST MARKET // ADVERSARIAL INPUT ROBUSTNESS")
    print("=" * 72)
    print("source commit:", source_commit())
    print("config sha256:", config_digest())
    print("condition:", CONDITION)
    print("dt_ms:", DT_MS)
    print("mutation observation:", MUTATION_OBSERVATION)
    print("extreme feature:", f"row={EXTREME_ROW}, column={EXTREME_FEATURE_COLUMN} (momentum)")
    print("release gain path:", release_gain_path)
    print("release gain:", release_gain)

    rows = []

    for stage in config["stages"]:
        print()
        print(stage["id"], stage["name"])

        for variant in stage["variants"]:
            variant_id = variant["id"]

            if stage["id"] == "A":
                first = run_stage_a_variant(
                    variant_id,
                    base_feature_tensor,
                    connectome=connectome,
                    retinal_indices=retinal_indices,
                    relay_indices=relay_indices,
                    release_gain=release_gain,
                )
                second = run_stage_a_variant(
                    variant_id,
                    base_feature_tensor,
                    connectome=connectome,
                    retinal_indices=retinal_indices,
                    relay_indices=relay_indices,
                    release_gain=release_gain,
                )
            elif stage["id"] == "B":
                first = run_stage_b_variant(
                    variant_id,
                    observations,
                    connectome=connectome,
                    retinal_indices=retinal_indices,
                    relay_indices=relay_indices,
                    release_gain=release_gain,
                )
                second = run_stage_b_variant(
                    variant_id,
                    observations,
                    connectome=connectome,
                    retinal_indices=retinal_indices,
                    relay_indices=relay_indices,
                    release_gain=release_gain,
                )
            elif stage["id"] == "C":
                first = run_stage_c_variant(
                    variant_id,
                    observations,
                    connectome=connectome,
                    retinal_indices=retinal_indices,
                    relay_indices=relay_indices,
                    release_gain=release_gain,
                )
                second = run_stage_c_variant(
                    variant_id,
                    observations,
                    connectome=connectome,
                    retinal_indices=retinal_indices,
                    relay_indices=relay_indices,
                    release_gain=release_gain,
                )
            else:
                raise RuntimeError(f"unknown stage: {stage['id']}")

            deterministic = deterministic_equal(first, second)

            print(
                f"  {variant_id}:",
                first["accepted_or_rejected"],
                "| deterministic:",
                "PASS" if deterministic else "FAIL",
                "| relay:",
                first.get("relay_spike_count"),
                "| wider:",
                first.get("wider_network_spike_count"),
            )

            if not deterministic:
                raise RuntimeError(f"determinism failed for {variant_id}")

            rows.append(
                {
                    "stage_id": stage["id"],
                    "stage_name": stage["name"],
                    "variant": variant,
                    "deterministic_AA_replay": deterministic,
                    "result": first,
                }
            )

    artifact = {
        "schema_version": "moscaquant.sidequest.ghost_market_result/v1",
        "sidequest_id": config["sidequest_id"],
        "name": config["name"],
        "subtitle": config["subtitle"],
        "source_commit": source_commit(),
        "config_path": str(CONFIG_PATH.relative_to(ROOT)),
        "config_sha256": config_digest(),
        "implementation": {
            "condition": CONDITION,
            "frame_count": FRAME_COUNT,
            "dt_ms": DT_MS,
            "tau_ms": TAU_MS,
            "threshold": THRESHOLD,
            "reset": RESET,
            "mutation_observation": MUTATION_OBSERVATION,
            "sequence_semantics": (
                "Stage B mutates the ordered sequence of normalized 6x7 market-feature "
                "observation tensors before each tensor enters the frozen 16-frame temporal encoder."
            ),
            "extreme_row": EXTREME_ROW,
            "extreme_feature_column": EXTREME_FEATURE_COLUMN,
            "extreme_feature_name": "momentum",
            "release_gain_config_path": str(VISUAL_CONFIG.relative_to(ROOT)),
            "release_gain_key": release_gain_path,
            "release_gain": release_gain,
        },
        "claim_boundary": config["claim_boundary"],
        "rows": rows,
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(artifact, indent=2) + "\n")

    print()
    print("=" * 72)
    print("SQ-02 RUN COMPLETE")
    print("=" * 72)
    print("artifact:", OUTPUT)
    print("all repeated-variant determinism checks: PASS")
    print("Interpret only after reviewing the complete artifact.")


if __name__ == "__main__":
    main()
