from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
from scipy import sparse

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
from brain.physiology_constrained_visual_transduction import (
    PhysiologyConstrainedVisualTransductionRuntime,
)
from brain.shuffled_connectome_v2 import build_interface_preserving_permutation
from brain.visual_transduction import VisualTransductionConfig
from market.features import compute_features
from market.normalization import CausalNormalizer

from brain.mq5_ts_metrics import (
    accepted_causal_edge_survival,
    first_positive_onsets,
    lagged_mutual_information,
    positive_voltage_fingerprint,
    responder_identity,
)
from brain.mq5_ts_strict_shuffle_native import build_strict_matched_control_native
from brain.mq5_ts_strict_shuffle_verify import verify_strict_matched_control_scalable

CONNECTOME = data_path("processed", "connectome-baseline-v1.npz")
RETINA = data_path("processed", "visual-r1-r6-map-v1.npz")
RELAY = data_path("processed", "visual-relay-map-v1.npz")
GRADED = data_path("processed", "mq3-2-graded-visual-types-v1.npz")
TERRITORIES = data_path("processed", "market-retinal-territories-v1.npz")
TRANSMITTER = data_path("processed", "transmitter_sign.npy")
CAUSAL = data_path("processed", "mq3-2-first-onset-causal-edges-v1.json")

EXPECTED_CAUSAL_SHA256 = "23cc19a39c30e554671bdf92b904865311d2f7df4dd9ef82af1eaf66638c3a2b"
EXPECTED_FRAMES = 192
RELEASE_GAIN = 0.9981738484618123


@dataclass(frozen=True)
class RuntimeResult:
    responder_indices: list[int]
    responder_voltage: list[list[float]]
    responder_spikes: list[list[float]]
    responder_identity: dict
    first_positive_onsets: dict[int, int | None]
    positive_voltage_fingerprint: list[float]
    stimulus_trace: list[float]
    dn_trace: list[float]
    mutual_information: dict
    causal_edge_survival: dict
    frame_count: int


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_frozen_causal_artifact() -> dict:
    actual = sha256_file(CAUSAL)
    if actual != EXPECTED_CAUSAL_SHA256:
        raise RuntimeError(f"frozen MQ-3.2 causal artifact hash mismatch: {actual}")

    payload = json.loads(CAUSAL.read_text(encoding="utf-8"))
    if len(payload.get("edges", [])) != 13:
        raise RuntimeError("expected 13 frozen causal edges")
    if len(payload.get("targets", [])) != 9:
        raise RuntimeError("expected 9 frozen responder targets")
    return payload


def frozen_responders(payload: dict | None = None) -> np.ndarray:
    payload = load_frozen_causal_artifact() if payload is None else payload
    return np.asarray(
        sorted(int(x["model_index"]) for x in payload["targets"]),
        dtype=np.int32,
    )


def frozen_edges(payload: dict | None = None) -> list[tuple[int, int, float]]:
    payload = load_frozen_causal_artifact() if payload is None else payload
    return [
        (
            int(edge["presynaptic"]),
            int(edge["postsynaptic"]),
            float(edge["weight"]),
        )
        for edge in payload["edges"]
    ]


def build_condition_a_stimuli() -> list[np.ndarray]:
    encoder = MarketVisionTemporalEncoder(TERRITORIES)

    normalizers = [
        CausalNormalizer(window_size=64, min_history=8)
        for _ in ASSETS
    ]

    series = [
        synthetic_series("A", asset_index)
        for asset_index in range(len(ASSETS))
    ]

    stimuli = []

    for observation in range(OBSERVATIONS):
        normalized = np.empty((len(ASSETS), 7), dtype=np.float32)

        for asset_index in range(len(ASSETS)):
            window = market_window_at(series[asset_index], observation)
            normalized[asset_index] = normalizers[asset_index].transform(
                compute_features(window)
            )

        frames = encoder.encode_sequence(
            normalized,
            frame_count=FRAME_COUNT,
        )

        for stimulus in frames:
            stimuli.append(
                np.asarray(stimulus * SENSORY_GAIN, dtype=np.float32)
            )

    if len(stimuli) != EXPECTED_FRAMES:
        raise RuntimeError(
            f"expected {EXPECTED_FRAMES} frozen frames, got {len(stimuli)}"
        )

    return stimuli


def build_arm_b_topology(original, transmitter_sign, protected_indices, seed):
    matrix = original.tocsr(copy=True)
    matrix.sum_duplicates()
    matrix.sort_indices()

    permutation = build_interface_preserving_permutation(
        transmitter_sign,
        protected_indices,
        int(seed),
    )

    shuffled = sparse.csr_matrix(
        (
            matrix.data.copy(),
            permutation[matrix.indices].astype(np.int32, copy=False),
            matrix.indptr.copy(),
        ),
        shape=matrix.shape,
        dtype=matrix.dtype,
    )

    shuffled.sum_duplicates()
    shuffled.sort_indices()

    if shuffled.nnz != matrix.nnz:
        raise RuntimeError("Arm B edge count changed")

    return shuffled


def lesion_frozen_edges(original, edges):
    modified = original.tolil(copy=True)

    for pre, post, expected_weight in edges:
        pre = int(pre)
        post = int(post)
        expected_weight = float(expected_weight)

        current = float(modified[post, pre])

        if current <= 0.0:
            raise RuntimeError(
                f"frozen causal edge missing/nonpositive: {pre}->{post}"
            )

        if not np.isclose(
            current,
            expected_weight,
            rtol=1e-6,
            atol=1e-12,
        ):
            raise RuntimeError(
                f"frozen causal weight mismatch {pre}->{post}: "
                f"{current} != {expected_weight}"
            )

        modified[post, pre] = 0.0

    result = modified.tocsr()
    result.eliminate_zeros()
    result.sort_indices()
    return result


def build_arm_c_topology(original, transmitter_sign, protected_indices, seed):
    candidate, diagnostics = build_strict_matched_control_native(
        original,
        transmitter_sign,
        protected_indices,
        seed=int(seed),
        accepted_swaps_per_eligible_edge=1.0,
        max_attempt_multiplier=20,
    )

    report = verify_strict_matched_control_scalable(
        original,
        candidate,
        transmitter_sign,
        protected_indices,
    )

    if not all(report.values()):
        failed = [key for key, value in report.items() if not value]
        raise RuntimeError("Arm C invariant failure: " + ", ".join(failed))

    return candidate, diagnostics, report


def evaluate_topology(
    connectome,
    retinal_indices,
    responder_indices,
    causal_edges,
    stimuli,
):
    matrix = connectome.tocsr(copy=False)
    retinal_indices = np.asarray(retinal_indices, dtype=np.int32)
    responder_indices = np.asarray(responder_indices, dtype=np.int32)

    if len(stimuli) != EXPECTED_FRAMES:
        raise ValueError(
            f"expected {EXPECTED_FRAMES} stimuli, got {len(stimuli)}"
        )

    runtime = PhysiologyConstrainedVisualTransductionRuntime(
        connectome=matrix,
        retinal_indices=retinal_indices,
        relay_artifact=RELAY,
        graded_artifact=GRADED,
        config=VisualTransductionConfig(release_gain=RELEASE_GAIN),
    )

    voltage_frames = np.empty(
        (EXPECTED_FRAMES, len(responder_indices)),
        dtype=np.float64,
    )
    spike_frames = np.empty_like(voltage_frames)
    stimulus_trace = np.empty(EXPECTED_FRAMES, dtype=np.float64)

    for frame, stimulus in enumerate(stimuli):
        local_retinal = np.asarray(
            stimulus[retinal_indices],
            dtype=np.float64,
        )

        stimulus_trace[frame] = float(
            np.maximum(local_retinal, 0.0).mean()
        )

        runtime.step(stimulus)

        voltage_frames[frame] = np.asarray(
            runtime.voltage[responder_indices],
            dtype=np.float64,
        )
        spike_frames[frame] = np.asarray(
            runtime.spikes[responder_indices],
            dtype=np.float64,
        )

    dn_trace = np.maximum(voltage_frames, 0.0).mean(axis=1)

    identity = responder_identity(
        voltage_frames,
        responder_indices,
    )
    onsets = first_positive_onsets(
        voltage_frames,
        responder_indices,
    )
    fingerprint = positive_voltage_fingerprint(
        voltage_frames,
    )
    mi = lagged_mutual_information(
        stimulus_trace,
        dn_trace,
    )
    survival = accepted_causal_edge_survival(
        matrix,
        causal_edges,
    )

    return RuntimeResult(
        responder_indices=[int(x) for x in responder_indices],
        responder_voltage=voltage_frames.tolist(),
        responder_spikes=spike_frames.tolist(),
        responder_identity=identity,
        first_positive_onsets=onsets,
        positive_voltage_fingerprint=fingerprint.tolist(),
        stimulus_trace=stimulus_trace.tolist(),
        dn_trace=dn_trace.tolist(),
        mutual_information=mi,
        causal_edge_survival=survival,
        frame_count=EXPECTED_FRAMES,
    )


def runtime_result_as_dict(result: RuntimeResult) -> dict:
    return asdict(result)
