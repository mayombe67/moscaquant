from __future__ import annotations

import numpy as np
import pytest

from brain.sq08_three_body_evidence import (
    write_evidence,
)
from brain.sq08_three_body_independent_verify import (
    VerificationFailure,
    verify_manifest,
)
from brain.sq08_three_body_plan import (
    build_conditions,
)


def synthetic_result():
    return {
        "positive_voltage":
            np.zeros(
                (192, 1191),
                dtype=np.float32,
            ),

        "spikes":
            np.zeros(
                (192, 1191),
                dtype=np.uint8,
            ),

        "body_responder_voltage":
            np.zeros(
                (192, 3),
                dtype=np.float32,
            ),

        "body_responder_spikes":
            np.zeros(
                (192, 3),
                dtype=np.uint8,
            ),

        "frontier_voltage":
            np.zeros(
                (192, 18),
                dtype=np.float32,
            ),

        "frontier_spikes":
            np.zeros(
                (192, 18),
                dtype=np.uint8,
            ),

        "channel_mean_positive_voltage":
            np.zeros(
                (3, 192),
                dtype=np.float64,
            ),

        "channel_positive_fraction":
            np.zeros(
                (3, 192),
                dtype=np.float64,
            ),

        "channel_spike_count":
            np.zeros(
                (3, 192),
                dtype=np.int32,
            ),

        "channel_spike_rate":
            np.zeros(
                (3, 192),
                dtype=np.float64,
            ),
    }


def synthetic_records():
    rows = []

    for condition in build_conditions():
        rows.append({
            "condition": dict(condition),

            "topology_provenance": {
                "synthetic": True,
            },

            "result":
                synthetic_result(),

            "timing": {
                "started_at_utc":
                    "2026-01-01T00:00:00Z",
                "completed_at_utc":
                    "2026-01-01T00:00:01Z",
                "elapsed_seconds":
                    1.0,
            },
        })

    return rows


def test_independent_verifier_accepts_writer_output(
    tmp_path,
):
    manifest, _sidecar = write_evidence(
        records=synthetic_records(),
        dn_indices=np.arange(
            1191,
            dtype=np.int32,
        ),
        output_dir=tmp_path / "evidence",
        run_metadata={
            "synthetic": True,
        },
    )

    report = verify_manifest(
        manifest
    )

    assert (
        report["status"]
        == "INDEPENDENT_VERIFICATION_PASS"
    )

    assert (
        report["npz"]["episode_count"]
        == 16
    )

    assert (
        report["npz"]["duplicate_pair_count"]
        == 8
    )


def test_independent_verifier_refuses_tampered_sidecar(
    tmp_path,
):
    manifest, sidecar = write_evidence(
        records=synthetic_records(),
        dn_indices=np.arange(
            1191,
            dtype=np.int32,
        ),
        output_dir=tmp_path / "evidence",
        run_metadata={
            "synthetic": True,
        },
    )

    with sidecar.open("ab") as handle:
        handle.write(b"tamper")

    with pytest.raises(
        VerificationFailure
    ):
        verify_manifest(
            manifest
        )
