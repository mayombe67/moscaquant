from __future__ import annotations

import time

import numpy as np
from scipy import sparse

from config.paths import data_path
from brain.mq5_ts_strict_shuffle_native import (
    build_strict_matched_control_native,
)
from brain.mq5_ts_strict_shuffle_verify import (
    verify_strict_matched_control_scalable,
)


CONNECTOME = data_path(
    "processed",
    "connectome-baseline-v1.npz",
)
TRANSMITTER = data_path(
    "processed",
    "transmitter_sign.npy",
)
RETINA = data_path(
    "processed",
    "visual-r1-r6-map-v1.npz",
)

# Explicitly outside frozen result-bearing ranges:
# Arm B: 20262000..20262019
# Arm C: 20263000..20263019
SMOKE_SEED = 991337001

# 0.01% of full preregistered swap density.
SMOKE_SWAPS_PER_ELIGIBLE_EDGE = 0.0001

# Same fail-closed attempt policy as preregistration.
MAX_ATTEMPT_MULTIPLIER = 20


def main() -> None:
    print("=" * 88)
    print("MQ-5.TS ARM C FULL-CONNECTOME SMOKE")
    print("=" * 88)
    print("NON-RESULT-BEARING: YES")
    print("result seed used: NO")
    print("experiment artifact written: NO")
    print("smoke seed:", SMOKE_SEED)
    print(
        "swap fraction:",
        SMOKE_SWAPS_PER_ELIGIBLE_EDGE,
    )
    print()

    original = sparse.load_npz(
        CONNECTOME
    ).tocsr()

    signs = np.load(
        TRANSMITTER,
    )

    retina = np.load(
        RETINA,
    )

    protected = np.asarray(
        retina["neuron_index"],
        dtype=np.int32,
    )

    print("shape:", original.shape)
    print("nnz:", original.nnz)
    print(
        "protected retinal neurons:",
        len(protected),
    )
    print()

    start = time.perf_counter()

    shuffled, diagnostics = (
        build_strict_matched_control_native(
            original,
            signs,
            protected,
            seed=SMOKE_SEED,
            accepted_swaps_per_eligible_edge=(
                SMOKE_SWAPS_PER_ELIGIBLE_EDGE
            ),
            max_attempt_multiplier=(
                MAX_ATTEMPT_MULTIPLIER
            ),
        )
    )

    construction_seconds = (
        time.perf_counter() - start
    )

    print("CONSTRUCTION")
    print("eligible edges:", diagnostics.eligible_edges)
    print(
        "target accepted swaps:",
        diagnostics.target_accepted_swaps,
    )
    print(
        "accepted swaps:",
        diagnostics.accepted_swaps,
    )
    print(
        "attempted swaps:",
        diagnostics.attempted_swaps,
    )
    print(
        "rejected sign:",
        diagnostics.rejected_sign,
    )
    print(
        "rejected noop:",
        diagnostics.rejected_noop,
    )
    print(
        "rejected self-edge:",
        diagnostics.rejected_self_edge,
    )
    print(
        "rejected duplicate:",
        diagnostics.rejected_duplicate,
    )
    print(
        "construction seconds:",
        f"{construction_seconds:.3f}",
    )
    print()

    verify_start = time.perf_counter()

    report = (
        verify_strict_matched_control_scalable(
            original,
            shuffled,
            signs,
            protected,
        )
    )

    verification_seconds = (
        time.perf_counter()
        - verify_start
    )

    print("FULL-SCALE INVARIANTS")
    for key, value in report.items():
        print(
            f"{key:42s}",
            value,
        )

    print()
    print(
        "verification seconds:",
        f"{verification_seconds:.3f}",
    )
    print()

    if not all(report.values()):
        failed = [
            key
            for key, value
            in report.items()
            if not value
        ]
        raise RuntimeError(
            "full-connectome smoke invariant failure: "
            + ", ".join(failed)
        )

    if (
        diagnostics.accepted_swaps
        != diagnostics.target_accepted_swaps
    ):
        raise RuntimeError(
            "smoke did not reach requested swap target"
        )

    print("=" * 88)
    print("FULL-CONNECTOME SMOKE PASSED")
    print("=" * 88)
    print("NO EXPERIMENT EXECUTED")
    print("NO RESULT-BEARING SEED EXECUTED")
    print("NO RESULT ARTIFACT WRITTEN")


if __name__ == "__main__":
    main()
