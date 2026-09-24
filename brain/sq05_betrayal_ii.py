from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
from scipy import sparse

from brain.mq5_ts_strict_shuffle_native import build_strict_matched_control_native
from brain.mq5_ts_strict_shuffle_verify import verify_strict_matched_control_scalable

ROOT = Path(__file__).resolve().parents[1]
WARTHOG_SEAL = ROOT / "artifacts/mq5-ts-arm-c-mixing-depth-result-seal-v1.json"
NATIVE = ROOT / "brain/mq5_ts_strict_shuffle_native.py"
VERIFIER = ROOT / "brain/mq5_ts_strict_shuffle_verify.py"

WARTHOG_SEAL_SHA256 = "a070680ea01a1c73272ec6179ef1e7e8103af32d7058fe14a8ebb088d937733e"
WARTHOG_RESULT_SHA256 = "fe5d9c718a80aee41ed66af43bbd1c091250c972eb9ad7f41bdb2de5df7aff31"
WARTHOG_CLASSIFICATION = "CURRENT_1X_ADEQUATE_FOR_SQ05"
NATIVE_SHA256 = "81283fe0790e6f27ea6c879fc10a9dcb952b44f32fb2857cfef1a3f62dce2316"
VERIFIER_SHA256 = "4ba7154447de204ea00af548aa46805f53b953057fbe4e5f134a2d59cd113460"

ACCEPTED_SWAPS_PER_ELIGIBLE_EDGE = 1.0
MAX_ATTEMPT_MULTIPLIER = 20
FORBIDDEN_HISTORICAL_SEEDS = frozenset(
    list(range(20263000, 20263020)) + [20264000, 20264001, 20264002]
)


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def assert_betrayal_ii_dependencies() -> dict[str, object]:
    expected = {
        WARTHOG_SEAL: WARTHOG_SEAL_SHA256,
        NATIVE: NATIVE_SHA256,
        VERIFIER: VERIFIER_SHA256,
    }
    for path, expected_sha in expected.items():
        if not path.is_file():
            raise RuntimeError(f"missing frozen BETRAYAL II dependency: {path}")
        actual = _sha256_file(path)
        if actual != expected_sha:
            raise RuntimeError(
                f"BETRAYAL II dependency SHA mismatch for {path}: "
                f"{actual} != {expected_sha}"
            )

    seal = json.loads(WARTHOG_SEAL.read_text(encoding="utf-8"))
    if seal.get("classification") != WARTHOG_CLASSIFICATION:
        raise RuntimeError("WARTHOG classification no longer authorizes 1.0x")
    if seal.get("result_sha256") != WARTHOG_RESULT_SHA256:
        raise RuntimeError("WARTHOG result identity drift")
    if seal.get("audit", {}).get("classification_matches_result") is not True:
        raise RuntimeError("WARTHOG seal lost classification audit")
    if seal.get("audit", {}).get("all_invariants_passed") is not True:
        raise RuntimeError("WARTHOG seal lost invariant audit")

    return {
        "warthog_seal_sha256": WARTHOG_SEAL_SHA256,
        "warthog_result_sha256": WARTHOG_RESULT_SHA256,
        "warthog_classification": WARTHOG_CLASSIFICATION,
        "native_sha256": NATIVE_SHA256,
        "verifier_sha256": VERIFIER_SHA256,
        "accepted_swaps_per_eligible_edge": ACCEPTED_SWAPS_PER_ELIGIBLE_EDGE,
        "max_attempt_multiplier": MAX_ATTEMPT_MULTIPLIER,
    }


def _validate_future_sq05_seed(seed: int) -> int:
    if isinstance(seed, bool) or not isinstance(seed, (int, np.integer)):
        raise TypeError("BETRAYAL II seed must be an integer")
    value = int(seed)
    if value < 0:
        raise ValueError("BETRAYAL II seed must be nonnegative")
    if value in FORBIDDEN_HISTORICAL_SEEDS:
        raise ValueError(
            "BETRAYAL II requires a fresh SQ-05 seed; "
            f"historical seed {value} is forbidden"
        )
    return value


def build_betrayal_ii(
    baseline: sparse.csr_matrix,
    transmitter_sign: np.ndarray,
    protected_indices: np.ndarray,
    *,
    seed: int,
):
    authority = assert_betrayal_ii_dependencies()
    frozen_seed = _validate_future_sq05_seed(seed)

    candidate, diagnostics = build_strict_matched_control_native(
        baseline,
        transmitter_sign,
        protected_indices,
        seed=frozen_seed,
        accepted_swaps_per_eligible_edge=ACCEPTED_SWAPS_PER_ELIGIBLE_EDGE,
        max_attempt_multiplier=MAX_ATTEMPT_MULTIPLIER,
    )

    invariants = verify_strict_matched_control_scalable(
        baseline,
        candidate,
        transmitter_sign,
        protected_indices,
    )
    if not invariants or not all(bool(v) for v in invariants.values()):
        failed = [k for k, v in invariants.items() if not v]
        raise RuntimeError(
            "BETRAYAL II strict topology-null invariant failure: "
            + ", ".join(failed)
        )

    provenance = {
        **authority,
        "sq05_seed": frozen_seed,
        "arm": "BETRAYAL_II_SHUFFLED",
        "scope": "strict_matched_topology_null_only",
        "neural_execution_authorized_here": False,
        "result_execution_authorized_here": False,
    }
    return candidate, diagnostics, invariants, provenance
