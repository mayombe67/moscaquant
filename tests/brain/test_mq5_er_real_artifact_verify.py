from __future__ import annotations

import numpy as np

from brain.mq5_er_real_artifact_verify import (
    nonzero_support,
    sha256_array,
    territory_energy_diagnostics,
)


def test_sha256_array_is_deterministic():
    a = np.arange(12, dtype=np.float32).reshape(3, 4)
    assert sha256_array(a) == sha256_array(a.copy())


def test_nonzero_support_uses_any_frame():
    x = np.zeros((3, 5), dtype=np.float32)
    x[0, 1] = 1.0
    x[2, 4] = 2.0
    assert np.array_equal(
        nonzero_support(x),
        np.array([1, 4], dtype=np.int32),
    )


def test_territory_energy_diagnostics():
    x = np.zeros((2, 6), dtype=np.float32)
    x[:, [0, 1]] = 1.0
    x[:, [2, 3]] = 2.0
    x[:, [4, 5]] = 3.0

    d = territory_energy_diagnostics(
        x,
        {
            1: np.array([0, 1]),
            2: np.array([2, 3]),
            3: np.array([4, 5]),
        },
    )

    assert d["1"]["mean"] == 2.0
    assert d["2"]["mean"] == 4.0
    assert d["3"]["mean"] == 6.0
