from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from config.paths import data_path
from brain.market_replay import (
    ASSETS,
    FRAME_COUNT,
    OBSERVATIONS,
    SENSORY_GAIN,
    market_window_at,
    synthetic_series,
)
from brain.market_temporal import MarketVisionTemporalEncoder
from brain.mq5_er_encoder import (
    ARM_A,
    ARM_B,
    ARM_C,
    ARM_D,
    ARM_E,
    EncodingVariant,
    MQ5EREncodingVariantEncoder,
    balanced_asset_territory_mappings,
)
from market.features import compute_features
from market.normalization import CausalNormalizer


TERRITORIES = data_path("processed", "market-retinal-territories-v1.npz")
OUTPUT = Path("artifacts/mq5-er-encoding-real-artifact-verification-v1.json")
EXPECTED_FRAMES = 192


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_array(array: np.ndarray) -> str:
    arr = np.ascontiguousarray(array)
    return sha256_bytes(arr.tobytes())


def build_normalized_episode() -> list[np.ndarray]:
    normalizers = [
        CausalNormalizer(window_size=64, min_history=8)
        for _ in ASSETS
    ]

    series = [
        synthetic_series("A", asset_index)
        for asset_index in range(len(ASSETS))
    ]

    episode: list[np.ndarray] = []

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
            normalized[asset_index] = normalizers[
                asset_index
            ].transform(
                compute_features(window)
            )

        episode.append(normalized)

    return episode


def encode_episode_reference(
    episode: list[np.ndarray],
) -> np.ndarray:
    encoder = MarketVisionTemporalEncoder(TERRITORIES)
    frames = []

    for normalized in episode:
        encoded = encoder.encode_sequence(
            normalized,
            frame_count=FRAME_COUNT,
        )
        frames.append(
            np.asarray(
                encoded * SENSORY_GAIN,
                dtype=np.float32,
            )
        )

    result = np.concatenate(frames, axis=0)

    if result.shape[0] != EXPECTED_FRAMES:
        raise RuntimeError(
            f"expected {EXPECTED_FRAMES} frames, got {result.shape[0]}"
        )

    return result


def encode_episode_variant(
    episode: list[np.ndarray],
    variant: EncodingVariant,
) -> np.ndarray:
    encoder = MQ5EREncodingVariantEncoder(
        TERRITORIES,
        variant=variant,
    )
    frames = []

    for normalized in episode:
        encoded = encoder.encode_sequence(
            normalized,
            frame_count=FRAME_COUNT,
        )
        frames.append(
            np.asarray(
                encoded * SENSORY_GAIN,
                dtype=np.float32,
            )
        )

    result = np.concatenate(frames, axis=0)

    if result.shape[0] != EXPECTED_FRAMES:
        raise RuntimeError(
            f"expected {EXPECTED_FRAMES} frames, got {result.shape[0]}"
        )

    return result


def load_territory_indices() -> dict[int, np.ndarray]:
    data = np.load(TERRITORIES)

    neuron_index = np.asarray(
        data["neuron_index"],
        dtype=np.int32,
    )
    territory = np.asarray(
        data["territory"],
        dtype=np.int8,
    )

    result = {}

    for t in range(1, 7):
        rows = np.flatnonzero(territory == t)
        result[t] = neuron_index[rows]

    return result


def territory_energy_diagnostics(
    sequence: np.ndarray,
    territory_indices: dict[int, np.ndarray],
) -> dict:
    diagnostics = {}

    for territory, indices in territory_indices.items():
        energy = np.asarray(
            sequence[:, indices].sum(axis=1),
            dtype=np.float64,
        )

        diagnostics[str(territory)] = {
            "mean": float(energy.mean()),
            "min": float(energy.min()),
            "max": float(energy.max()),
            "sha256": sha256_array(energy),
        }

    return diagnostics


def nonzero_support(sequence: np.ndarray) -> np.ndarray:
    return np.flatnonzero(
        np.any(sequence != 0.0, axis=0)
    ).astype(np.int32)


def variant_record(
    name: str,
    sequence: np.ndarray,
    territory_indices: dict[int, np.ndarray],
    reference_support: np.ndarray,
) -> dict:
    support = nonzero_support(sequence)

    if not np.array_equal(support, reference_support):
        raise RuntimeError(
            f"{name}: retinal support differs from reference"
        )

    energies = territory_energy_diagnostics(
        sequence,
        territory_indices,
    )

    expected_mean = float(SENSORY_GAIN)

    for territory, record in energies.items():
        if not np.isclose(
            record["mean"],
            expected_mean,
            rtol=1e-6,
            atol=1e-6,
        ):
            raise RuntimeError(
                f"{name}: T{territory} mean energy "
                f"{record['mean']} != {expected_mean}"
            )

    return {
        "shape": list(sequence.shape),
        "dtype": str(sequence.dtype),
        "sha256": sha256_array(sequence),
        "nonzero_support_count": int(len(support)),
        "nonzero_support_sha256": sha256_array(support),
        "territory_energy": energies,
    }


def build_verification_payload() -> dict:
    episode = build_normalized_episode()
    episode_hash = sha256_array(
        np.stack(episode, axis=0)
    )

    reference = encode_episode_reference(episode)
    arm_a = encode_episode_variant(
        episode,
        EncodingVariant(ARM_A),
    )

    if reference.tobytes() != arm_a.tobytes():
        raise RuntimeError(
            "Arm A is not byte-identical to frozen encoder"
        )

    # Determinism: rebuild the complete reference episode independently.
    reference_repeat = encode_episode_reference(
        build_normalized_episode()
    )

    if reference.tobytes() != reference_repeat.tobytes():
        raise RuntimeError(
            "frozen reference encoder failed deterministic replay"
        )

    territory_indices = load_territory_indices()
    reference_support = nonzero_support(reference)

    records = {
        "A": variant_record(
            "A",
            arm_a,
            territory_indices,
            reference_support,
        ),
        "B": variant_record(
            "B",
            encode_episode_variant(
                episode,
                EncodingVariant(ARM_B),
            ),
            territory_indices,
            reference_support,
        ),
        "C": variant_record(
            "C",
            encode_episode_variant(
                episode,
                EncodingVariant(ARM_C),
            ),
            territory_indices,
            reference_support,
        ),
        "E": variant_record(
            "E",
            encode_episode_variant(
                episode,
                EncodingVariant(ARM_E),
            ),
            territory_indices,
            reference_support,
        ),
    }

    d_records = []
    mappings = balanced_asset_territory_mappings()

    for name, mapping in mappings:
        sequence = encode_episode_variant(
            episode,
            EncodingVariant(
                ARM_D,
                asset_mapping=mapping,
            ),
        )

        record = variant_record(
            f"D:{name}",
            sequence,
            territory_indices,
            reference_support,
        )
        record["mapping_name"] = name
        record["mapping"] = list(mapping)
        record["identity"] = (
            mapping == (0, 1, 2, 3, 4, 5)
        )
        d_records.append(record)

    # Identity mapping must be exactly reference-equivalent.
    identity = next(
        item for item in d_records
        if item["identity"]
    )

    if identity["sha256"] != records["A"]["sha256"]:
        raise RuntimeError(
            "Arm D identity mapping is not byte-identical to Arm A"
        )

    # Determinism on every non-reference arm.
    repeat_checks = {}

    for arm in (ARM_B, ARM_C, ARM_E):
        first = encode_episode_variant(
            episode,
            EncodingVariant(arm),
        )
        second = encode_episode_variant(
            build_normalized_episode(),
            EncodingVariant(arm),
        )
        repeat_checks[arm] = (
            sha256_array(first) == sha256_array(second)
        )

    for name, mapping in mappings:
        first = encode_episode_variant(
            episode,
            EncodingVariant(
                ARM_D,
                asset_mapping=mapping,
            ),
        )
        second = encode_episode_variant(
            build_normalized_episode(),
            EncodingVariant(
                ARM_D,
                asset_mapping=mapping,
            ),
        )
        repeat_checks[f"D:{name}"] = (
            sha256_array(first) == sha256_array(second)
        )

    if not all(repeat_checks.values()):
        failed = [
            name for name, ok in repeat_checks.items()
            if not ok
        ]
        raise RuntimeError(
            f"determinism failure: {failed}"
        )

    return {
        "experiment": "mq5-er-encoding-robustness-v1",
        "verification": (
            "real-artifact-encoding-only-v1"
        ),
        "neural_runtime_used": False,
        "connectome_used": False,
        "financial_semantics": False,
        "frames": EXPECTED_FRAMES,
        "observations": OBSERVATIONS,
        "frames_per_observation": FRAME_COUNT,
        "sensory_gain": float(SENSORY_GAIN),
        "normalized_episode_sha256": episode_hash,
        "arm_a_byte_identical_to_frozen_encoder": True,
        "arm_a_deterministic_replay": True,
        "repeat_checks": repeat_checks,
        "arms": records,
        "arm_d_mappings": d_records,
        "status": "PASS",
    }


def write_verification() -> Path:
    payload = build_verification_payload()

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    if OUTPUT.exists():
        raise RuntimeError(
            f"refusing to overwrite existing verification artifact: {OUTPUT}"
        )

    OUTPUT.write_text(
        json.dumps(
            payload,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    return OUTPUT


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--verify-real-artifacts",
        action="store_true",
    )
    args = parser.parse_args()

    if not args.verify_real_artifacts:
        raise SystemExit(
            "refusing to run without --verify-real-artifacts"
        )

    path = write_verification()
    payload = json.loads(path.read_text(encoding="utf-8"))

    print("MQ-5.ER REAL-ARTIFACT ENCODING VERIFICATION PASS")
    print("frames:", payload["frames"])
    print(
        "Arm A byte-identical:",
        payload["arm_a_byte_identical_to_frozen_encoder"],
    )
    print(
        "Arm A deterministic:",
        payload["arm_a_deterministic_replay"],
    )
    print("Arm D mappings:", len(payload["arm_d_mappings"]))
    print("artifact:", path)
    print("artifact sha256:", hashlib.sha256(path.read_bytes()).hexdigest())
    print("CONNECTOME USED: NO")
    print("NEURAL RUNTIME USED: NO")
    print("MQ-5.ER RESULT GENERATED: NO")


if __name__ == "__main__":
    main()
