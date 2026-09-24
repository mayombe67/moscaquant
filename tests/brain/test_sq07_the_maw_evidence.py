from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

import brain.sq07_the_maw_evidence as e


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "brain/sq07_the_maw_evidence.py"


@pytest.fixture(scope="module")
def zero_result():
    return {
        "positive_voltage": np.zeros((192, 1191), dtype=np.float32),
        "spikes": np.zeros((192, 1191), dtype=np.uint8),
        "channel_mean_positive_voltage": np.zeros(
            (3, 192), dtype=np.float64
        ),
        "channel_positive_fraction": np.zeros(
            (3, 192), dtype=np.float64
        ),
        "channel_spike_count": np.zeros(
            (3, 192), dtype=np.int32
        ),
        "channel_spike_rate": np.zeros(
            (3, 192), dtype=np.float64
        ),
    }


def make_records(zero_result, shard_index=0):
    shard = e.canonical_shard(shard_index)
    records = []

    for ordinal, condition_id in enumerate(
        shard["condition_ids"],
        start=shard["start_ordinal"],
    ):
        mask13, layout, replicate = e.parse_condition_id(condition_id)

        records.append(
            {
                "condition": {
                    "ordinal": ordinal,
                    "condition_id": condition_id,
                    "mask13": mask13,
                    "layout": layout,
                    "replicate": replicate,
                },
                "topology_provenance": {
                    "artifact": "synthetic-tooth-five-test",
                    "mask13": mask13,
                },
                "result": zero_result,
                "timing": {
                    "started_at_utc": "2026-09-24T00:00:00Z",
                    "completed_at_utc": "2026-09-24T00:00:01Z",
                    "elapsed_seconds": 1.0,
                },
            }
        )

    return records


def shard_timing():
    return {
        "started_at_utc": "2026-09-24T00:00:00Z",
        "completed_at_utc": "2026-09-24T00:01:04Z",
        "elapsed_seconds": 64.0,
    }


def test_frozen_dependencies_are_exact():
    e.verify_frozen_dependencies.cache_clear()
    observed = e.verify_frozen_dependencies()

    assert observed["evidence_schema_sha256"] == (
        "c1065506a90b26856896e0a522c7023738de13b0ac5af7a17cea7973774d2f01"
    )

    assert observed["shard_plan_sha256"] == (
        "9039b8e708c2ffdb74436e5c6fdc8f7d2f38f3f3fb27fd7478dd2cc8101d2a55"
    )


def test_first_canonical_shard_matches_frozen_descriptor():
    shard = e.canonical_shard(0)

    assert shard["shard_id"] == "sq07-shard-000"
    assert shard["start_ordinal"] == 0
    assert shard["end_ordinal_exclusive"] == 64
    assert shard["condition_count"] == 64
    assert shard["mask_count"] == 16

    assert shard["condition_membership_sha256"] == (
        "8b2b19e006a4a0d9f255d485c0e8e8ef176a254428bcbb3f8f8e15a748ebf237"
    )


def test_synthetic_shard_round_trip(
    tmp_path,
    zero_result,
):
    records = make_records(zero_result)

    manifest, sidecar = e.write_shard_evidence(
        shard_index=0,
        records=records,
        dn_indices=np.arange(1191, dtype=np.int32),
        shard_timing=shard_timing(),
        output_dir=tmp_path,
    )

    assert manifest.is_file()
    assert sidecar.is_file()

    verified = e.verify_shard_evidence(manifest)

    assert verified["valid"] is True
    assert verified["shard_id"] == "sq07-shard-000"
    assert verified["condition_count"] == 64
    assert verified["duplicate_pairs_checked"] == 32
    assert verified["duplicate_replay_all_exact"] is True


def test_wrong_condition_identity_hard_fails(
    tmp_path,
    zero_result,
):
    records = make_records(zero_result)
    records[7] = dict(records[7])
    records[7]["condition"] = dict(records[7]["condition"])
    records[7]["condition"]["replicate"] = 99

    with pytest.raises(e.Refusal, match="replicate"):
        e.write_shard_evidence(
            shard_index=0,
            records=records,
            dn_indices=np.arange(1191, dtype=np.int32),
            shard_timing=shard_timing(),
            output_dir=tmp_path,
        )


def test_wrong_evidence_dtype_hard_fails(
    tmp_path,
    zero_result,
):
    records = make_records(zero_result)
    records[0] = dict(records[0])
    records[0]["result"] = dict(records[0]["result"])
    records[0]["result"]["spikes"] = np.zeros(
        (192, 1191),
        dtype=np.int32,
    )

    with pytest.raises(e.Refusal, match="dtype drift"):
        e.write_shard_evidence(
            shard_index=0,
            records=records,
            dn_indices=np.arange(1191, dtype=np.int32),
            shard_timing=shard_timing(),
            output_dir=tmp_path,
        )


def test_wrong_evidence_shape_hard_fails(
    tmp_path,
    zero_result,
):
    records = make_records(zero_result)
    records[0] = dict(records[0])
    records[0]["result"] = dict(records[0]["result"])
    records[0]["result"]["positive_voltage"] = np.zeros(
        (191, 1191),
        dtype=np.float32,
    )

    with pytest.raises(e.Refusal, match="shape drift"):
        e.write_shard_evidence(
            shard_index=0,
            records=records,
            dn_indices=np.arange(1191, dtype=np.int32),
            shard_timing=shard_timing(),
            output_dir=tmp_path,
        )


def test_numerical_duplicate_mismatch_is_preserved_not_erased(
    tmp_path,
    zero_result,
):
    records = make_records(zero_result)

    changed = {
        key: np.array(value, copy=True)
        for key, value in zero_result.items()
    }
    changed["positive_voltage"][0, 0] = 1.0

    records[1] = dict(records[1])
    records[1]["result"] = changed

    manifest, _ = e.write_shard_evidence(
        shard_index=0,
        records=records,
        dn_indices=np.arange(1191, dtype=np.int32),
        shard_timing=shard_timing(),
        output_dir=tmp_path,
    )

    verified = e.verify_shard_evidence(manifest)

    assert verified["valid"] is True
    assert verified["duplicate_replay_all_exact"] is False


def test_manifest_identity_tampering_hard_fails(
    tmp_path,
    zero_result,
):
    records = make_records(zero_result)

    manifest_path, _ = e.write_shard_evidence(
        shard_index=0,
        records=records,
        dn_indices=np.arange(1191, dtype=np.int32),
        shard_timing=shard_timing(),
        output_dir=tmp_path,
    )

    payload = json.loads(
        manifest_path.read_text(encoding="utf-8")
    )

    payload["shard_identity"]["condition_membership_sha256"] = (
        "0" * 64
    )

    manifest_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(
        e.Refusal,
        match="canonical plan",
    ):
        e.verify_shard_evidence(manifest_path)


def test_sidecar_byte_tampering_hard_fails(
    tmp_path,
    zero_result,
):
    records = make_records(zero_result)

    manifest_path, sidecar_path = e.write_shard_evidence(
        shard_index=0,
        records=records,
        dn_indices=np.arange(1191, dtype=np.int32),
        shard_timing=shard_timing(),
        output_dir=tmp_path,
    )

    data = bytearray(sidecar_path.read_bytes())
    data[-1] ^= 0x01
    sidecar_path.write_bytes(data)

    with pytest.raises(
        e.Refusal,
        match="SHA-256 mismatch",
    ):
        e.verify_shard_evidence(manifest_path)


def test_writer_refuses_overwrite(
    tmp_path,
    zero_result,
):
    records = make_records(zero_result)

    e.write_shard_evidence(
        shard_index=0,
        records=records,
        dn_indices=np.arange(1191, dtype=np.int32),
        shard_timing=shard_timing(),
        output_dir=tmp_path,
    )

    with pytest.raises(
        e.Refusal,
        match="overwrite",
    ):
        e.write_shard_evidence(
            shard_index=0,
            records=records,
            dn_indices=np.arange(1191, dtype=np.int32),
            shard_timing=shard_timing(),
            output_dir=tmp_path,
        )


def test_source_has_no_neural_execution_or_analysis_surface():
    source = SOURCE.read_text(encoding="utf-8")

    forbidden = [
        "sq07_the_maw_episode",
        "run_episode",
        "build_stimuli",
        "build_mask_subset",
        "PhysiologyConstrainedVisualTransductionRuntime",
        "--run-frozen",
        "argparse",
        "EXACT_INTACT",
        "EXACT_FULL13",
        "INTERMEDIATE",
        "minimal_recapitulator",
        "strict_subset_separability",
    ]

    for token in forbidden:
        assert token not in source
