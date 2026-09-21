from __future__ import annotations

import ctypes
import hashlib
import os
import platform
import shutil
import subprocess
import tempfile
from pathlib import Path

import numpy as np
from scipy import sparse

from brain.mq5_ts_strict_shuffle import StrictShuffleDiagnostics


_NATIVE_SOURCE = r"""
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>

#define EMPTY_KEY UINT64_MAX
#define TOMBSTONE_KEY (UINT64_MAX - 1ULL)

static inline uint64_t mix64(uint64_t x) {
    x += 0x9e3779b97f4a7c15ULL;
    x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9ULL;
    x = (x ^ (x >> 27)) * 0x94d049bb133111ebULL;
    return x ^ (x >> 31);
}

static inline uint64_t rng_next(uint64_t *state) {
    *state += 0x9e3779b97f4a7c15ULL;
    uint64_t z = *state;
    z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ULL;
    z = (z ^ (z >> 27)) * 0x94d049bb133111ebULL;
    return z ^ (z >> 31);
}

static inline uint64_t rng_bounded(uint64_t *state, uint64_t bound) {
    if (bound <= 1ULL) return 0ULL;
    const uint64_t threshold = (uint64_t)(-bound) % bound;
    for (;;) {
        const uint64_t r = rng_next(state);
        if (r >= threshold) return r % bound;
    }
}

static inline uint64_t edge_key(int32_t post, int32_t pre, uint64_t n) {
    return ((uint64_t)(uint32_t)post * n) + (uint64_t)(uint32_t)pre;
}

static inline int table_contains(
    const uint64_t *table,
    uint64_t mask,
    uint64_t key
) {
    uint64_t slot = mix64(key) & mask;
    for (;;) {
        const uint64_t existing = table[slot];
        if (existing == EMPTY_KEY) return 0;
        if (existing == key) return 1;
        slot = (slot + 1ULL) & mask;
    }
}

static inline int table_insert(
    uint64_t *table,
    uint64_t mask,
    uint64_t key
) {
    uint64_t slot = mix64(key) & mask;
    uint64_t first_tombstone = EMPTY_KEY;

    for (;;) {
        const uint64_t existing = table[slot];

        if (existing == key) return 0;

        if (
            existing == TOMBSTONE_KEY
            && first_tombstone == EMPTY_KEY
        ) {
            first_tombstone = slot;
        }

        if (existing == EMPTY_KEY) {
            if (first_tombstone != EMPTY_KEY) slot = first_tombstone;
            table[slot] = key;
            return 1;
        }

        slot = (slot + 1ULL) & mask;
    }
}

static inline int table_erase(
    uint64_t *table,
    uint64_t mask,
    uint64_t key
) {
    uint64_t slot = mix64(key) & mask;

    for (;;) {
        const uint64_t existing = table[slot];

        if (existing == EMPTY_KEY) return 0;

        if (existing == key) {
            table[slot] = TOMBSTONE_KEY;
            return 1;
        }

        slot = (slot + 1ULL) & mask;
    }
}

static uint64_t next_power_of_two(uint64_t value) {
    uint64_t x = 1ULL;

    while (x < value) {
        if (x > (UINT64_MAX >> 1)) return 0ULL;
        x <<= 1;
    }

    return x;
}

/*
Return codes:
  0 success
  1 allocation failure
  2 duplicate input edge
  3 internal erase failure
  4 internal insert failure
  5 target not reached
  6 invalid input
*/
int mq5_strict_shuffle(
    const int32_t *rows,
    int32_t *cols,
    const float *signs,
    const int32_t *eligible_positions,
    int64_t nnz,
    int64_t eligible_count,
    int32_t n,
    uint64_t seed,
    int64_t target,
    int64_t max_attempts,
    int64_t *diag
) {
    if (
        !rows || !cols || !signs || !eligible_positions || !diag ||
        nnz < 0 || eligible_count < 0 || n <= 0 ||
        target < 0 || max_attempts < 0
    ) {
        return 6;
    }

    uint64_t requested = (uint64_t)nnz * 2ULL;
    if (requested < 16ULL) requested = 16ULL;

    const uint64_t capacity = next_power_of_two(requested);
    if (capacity == 0ULL) return 1;

    uint64_t *table = (uint64_t *)malloc(capacity * sizeof(uint64_t));
    if (!table) return 1;

    uint8_t *baseline_self = (uint8_t *)calloc(
        (size_t)n,
        sizeof(uint8_t)
    );
    if (!baseline_self) {
        free(table);
        return 1;
    }

    memset(table, 0xFF, capacity * sizeof(uint64_t));
    const uint64_t mask = capacity - 1ULL;
    const uint64_t n64 = (uint64_t)(uint32_t)n;

    for (int64_t k = 0; k < nnz; ++k) {
        const uint64_t key = edge_key(rows[k], cols[k], n64);
        if (!table_insert(table, mask, key)) {
            free(baseline_self);
            free(table);
            return 2;
        }

        if (rows[k] == cols[k]) {
            baseline_self[rows[k]] = 1U;
        }
    }

    uint64_t rng_state = seed ^ 0xd1b54a32d192ed03ULL;

    int64_t accepted = 0;
    int64_t attempted = 0;
    int64_t rejected_sign = 0;
    int64_t rejected_noop = 0;
    int64_t rejected_self = 0;
    int64_t rejected_duplicate = 0;

    while (accepted < target && attempted < max_attempts) {
        attempted += 1;

        const uint64_t pick_i = rng_bounded(
            &rng_state,
            (uint64_t)eligible_count
        );
        uint64_t pick_j = rng_bounded(
            &rng_state,
            (uint64_t)(eligible_count - 1)
        );
        if (pick_j >= pick_i) pick_j += 1ULL;

        const int64_t i = (int64_t)eligible_positions[pick_i];
        const int64_t j = (int64_t)eligible_positions[pick_j];

        const int32_t x = rows[i];
        const int32_t y = rows[j];
        const int32_t a = cols[i];
        const int32_t b = cols[j];

        if (a == b || x == y) {
            rejected_noop += 1;
            continue;
        }

        if (signs[a] != signs[b]) {
            rejected_sign += 1;
            continue;
        }

        if (
            (b == x && !baseline_self[x])
            || (a == y && !baseline_self[y])
        ) {
            rejected_self += 1;
            continue;
        }

        const uint64_t old1 = edge_key(x, a, n64);
        const uint64_t old2 = edge_key(y, b, n64);
        const uint64_t new1 = edge_key(x, b, n64);
        const uint64_t new2 = edge_key(y, a, n64);

        if (new1 == old1 || new2 == old2 || new1 == new2) {
            rejected_noop += 1;
            continue;
        }

        if (!table_erase(table, mask, old1)) {
            free(baseline_self);
            free(table);
            return 3;
        }

        if (!table_erase(table, mask, old2)) {
            table_insert(table, mask, old1);
            free(baseline_self);
            free(table);
            return 3;
        }

        if (
            table_contains(table, mask, new1)
            || table_contains(table, mask, new2)
        ) {
            table_insert(table, mask, old1);
            table_insert(table, mask, old2);
            rejected_duplicate += 1;
            continue;
        }

        cols[i] = b;
        cols[j] = a;

        if (!table_insert(table, mask, new1)) {
            free(baseline_self);
            free(table);
            return 4;
        }

        if (!table_insert(table, mask, new2)) {
            free(baseline_self);
            free(table);
            return 4;
        }

        accepted += 1;
    }

    free(baseline_self);
    free(table);

    diag[0] = accepted;
    diag[1] = attempted;
    diag[2] = rejected_sign;
    diag[3] = rejected_noop;
    diag[4] = rejected_self;
    diag[5] = rejected_duplicate;

    if (accepted != target) return 5;

    return 0;
}
"""


def _compiler() -> str:
    for candidate in (
        os.environ.get("CC"),
        "cc",
        "gcc",
        "clang",
    ):
        if candidate and shutil.which(candidate):
            return candidate

    raise RuntimeError(
        "MQ-5.TS native Arm C backend requires "
        "cc, gcc, or clang"
    )


def _native_library_path() -> Path:
    digest = hashlib.sha256(
        (
            _NATIVE_SOURCE
            + "\n"
            + platform.machine()
            + "\n"
            + platform.system()
        ).encode("utf-8")
    ).hexdigest()[:20]

    cache = (
        Path.home()
        / ".cache"
        / "moscaquant"
        / "mq5_ts_native"
    )
    cache.mkdir(parents=True, exist_ok=True)

    return cache / f"mq5_ts_strict_shuffle_{digest}.so"


def _build_native_library() -> Path:
    output = _native_library_path()

    if output.exists():
        return output

    compiler = _compiler()

    with tempfile.TemporaryDirectory(
        prefix="mq5_ts_native_build_"
    ) as tmp:
        source = Path(tmp) / "mq5_ts_strict_shuffle.c"
        candidate = Path(tmp) / "mq5_ts_strict_shuffle.so"

        source.write_text(
            _NATIVE_SOURCE,
            encoding="utf-8",
        )

        completed = subprocess.run(
            [
                compiler,
                "-O3",
                "-std=c11",
                "-fPIC",
                "-shared",
                str(source),
                "-o",
                str(candidate),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )

        if completed.returncode != 0:
            raise RuntimeError(
                "failed to compile MQ-5.TS native backend:\n"
                + completed.stdout
            )

        os.replace(candidate, output)

    return output


def _load_native():
    library = ctypes.CDLL(
        str(_build_native_library())
    )

    fn = library.mq5_strict_shuffle

    i32p = ctypes.POINTER(ctypes.c_int32)
    f32p = ctypes.POINTER(ctypes.c_float)
    i64p = ctypes.POINTER(ctypes.c_int64)

    fn.argtypes = [
        i32p,
        i32p,
        f32p,
        i32p,
        ctypes.c_int64,
        ctypes.c_int64,
        ctypes.c_int32,
        ctypes.c_uint64,
        ctypes.c_int64,
        ctypes.c_int64,
        i64p,
    ]
    fn.restype = ctypes.c_int

    return fn


def native_backend_available() -> bool:
    try:
        _build_native_library()
    except Exception:
        return False

    return True


def build_strict_matched_control_native(
    original: sparse.csr_matrix,
    transmitter_sign: np.ndarray,
    protected_indices: np.ndarray,
    seed: int,
    *,
    accepted_swaps_per_eligible_edge: float = 1.0,
    max_attempt_multiplier: int = 20,
) -> tuple[sparse.csr_matrix, StrictShuffleDiagnostics]:
    """Production MQ-5.TS Arm C constructor.

    Operation:
        a -> x, b -> y  =>  b -> x, a -> y

    with sign(a) == sign(b), excluding protected retinal-origin
    edges from selection.

    The scientific operation matches the bounded reference implementation.
    Only the hot sequential loop and dynamic edge-membership table are moved
    into native C.

    Production uses a fixed SplitMix64 stream seeded by the preregistered
    integer seed.  Therefore it is deterministic, but it is not expected to
    generate the bit-identical realization produced by NumPy's RNG in the
    reference constructor.  The reference is the invariant oracle.
    """
    matrix = original.tocsr(copy=True)
    matrix.sum_duplicates()
    matrix.sort_indices()

    if matrix.shape[0] != matrix.shape[1]:
        raise ValueError(
            "strict shuffle requires a square connectome"
        )

    n = int(matrix.shape[0])

    if n > np.iinfo(np.int32).max:
        raise ValueError(
            "native backend requires int32 neuron indices"
        )

    sign = np.ascontiguousarray(
        transmitter_sign,
        dtype=np.float32,
    )

    if sign.shape != (n,):
        raise ValueError(
            "transmitter_sign length does not match connectome"
        )

    protected = np.asarray(
        protected_indices,
        dtype=np.int32,
    )

    if np.any(protected < 0) or np.any(protected >= n):
        raise ValueError(
            "protected index out of range"
        )

    if len(np.unique(protected)) != len(protected):
        raise ValueError(
            "duplicate protected indices"
        )

    if accepted_swaps_per_eligible_edge < 0:
        raise ValueError(
            "accepted_swaps_per_eligible_edge must be nonnegative"
        )

    if max_attempt_multiplier < 1:
        raise ValueError(
            "max_attempt_multiplier must be >= 1"
        )

    rows = np.repeat(
        np.arange(n, dtype=np.int32),
        np.diff(matrix.indptr),
    )

    cols = np.ascontiguousarray(
        matrix.indices,
        dtype=np.int32,
    ).copy()

    protected_mask = np.zeros(
        n,
        dtype=bool,
    )
    protected_mask[protected] = True

    eligible_positions = np.ascontiguousarray(
        np.flatnonzero(
            ~protected_mask[cols]
        ).astype(
            np.int32,
            copy=False,
        )
    )

    eligible_edges = int(
        len(eligible_positions)
    )

    target = int(
        np.floor(
            eligible_edges
            * float(
                accepted_swaps_per_eligible_edge
            )
        )
    )

    max_attempts = int(
        target
        * int(max_attempt_multiplier)
    )

    if target == 0:
        return matrix, StrictShuffleDiagnostics(
            seed=int(seed),
            eligible_edges=eligible_edges,
            target_accepted_swaps=0,
            accepted_swaps=0,
            attempted_swaps=0,
            rejected_sign=0,
            rejected_noop=0,
            rejected_self_edge=0,
            rejected_duplicate=0,
        )

    if eligible_edges < 2:
        raise RuntimeError(
            "strict shuffle needs at least two eligible edges"
        )

    diagnostics_raw = np.zeros(
        6,
        dtype=np.int64,
    )

    fn = _load_native()

    code = fn(
        rows.ctypes.data_as(
            ctypes.POINTER(ctypes.c_int32)
        ),
        cols.ctypes.data_as(
            ctypes.POINTER(ctypes.c_int32)
        ),
        sign.ctypes.data_as(
            ctypes.POINTER(ctypes.c_float)
        ),
        eligible_positions.ctypes.data_as(
            ctypes.POINTER(ctypes.c_int32)
        ),
        ctypes.c_int64(int(matrix.nnz)),
        ctypes.c_int64(eligible_edges),
        ctypes.c_int32(n),
        ctypes.c_uint64(
            int(seed) & ((1 << 64) - 1)
        ),
        ctypes.c_int64(target),
        ctypes.c_int64(max_attempts),
        diagnostics_raw.ctypes.data_as(
            ctypes.POINTER(ctypes.c_int64)
        ),
    )

    errors = {
        1: "native hash-table allocation failed",
        2: "source graph contains a duplicate edge",
        3: "native edge-table erase invariant failed",
        4: "native edge-table insert invariant failed",
        5: "strict shuffle failed to reach preregistered target",
        6: "invalid native-backend input",
    }

    if code != 0:
        detail = errors.get(
            int(code),
            f"unknown native backend error {code}",
        )

        if code == 5:
            detail += (
                f": accepted={int(diagnostics_raw[0])}, "
                f"target={target}, "
                f"attempted={int(diagnostics_raw[1])}, "
                f"max_attempts={max_attempts}"
            )

        raise RuntimeError(detail)

    shuffled = sparse.csr_matrix(
        (
            matrix.data.copy(),
            cols,
            matrix.indptr.copy(),
        ),
        shape=matrix.shape,
        dtype=matrix.dtype,
    )
    shuffled.sort_indices()

    diagnostics = StrictShuffleDiagnostics(
        seed=int(seed),
        eligible_edges=eligible_edges,
        target_accepted_swaps=target,
        accepted_swaps=int(diagnostics_raw[0]),
        attempted_swaps=int(diagnostics_raw[1]),
        rejected_sign=int(diagnostics_raw[2]),
        rejected_noop=int(diagnostics_raw[3]),
        rejected_self_edge=int(diagnostics_raw[4]),
        rejected_duplicate=int(diagnostics_raw[5]),
    )

    return shuffled, diagnostics
