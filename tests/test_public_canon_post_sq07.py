from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

SEAL = (
    ROOT
    / "artifacts/experiments"
    / "sq07-the-maw-result-seal-v1.json"
)

DOC = (
    ROOT
    / "docs/experiments"
    / "sq07-the-maw-result.md"
)

SCHEMA = (
    ROOT
    / "config/controls"
    / "sq07-the-maw-result-schema-v1.json"
)


def test_sq07_public_canon_files_exist():
    assert SEAL.is_file()
    assert DOC.is_file()
    assert SCHEMA.is_file()


def test_sq07_result_identity_is_frozen():
    seal = json.loads(
        SEAL.read_text(encoding="utf-8")
    )

    assert seal["experiment"] == {
        "codename": "THE MAW",
        "id": "SQ-07",
        "run_id": "sq07-maw-20260924-01",
        "status": "SEALED_RESULT",
    }

    assert (
        seal["authoritative_analysis"]["sha256"]
        == "2db405151cc8771ccd0c50080bcd6a83ca3824e5487c666d22e01db8bed6d80c"
    )

    verification = seal["independent_verification"]

    assert verification["status"] == "PASS"

    assert (
        verification["reduction_sha256"]
        == "107e2780602c3ab8531afdf15dda4057a093ed4716bb1a7e2236c7536e38adf7"
    )

    assert verification["shard_summary_count"] == 512
    assert verification["shards_verified"] == 512
    assert verification["episodes_verified"] == 32768
    assert verification["reported_result_agreement"] is True


def test_sq07_preregistered_flags_are_frozen():
    seal = json.loads(
        SEAL.read_text(encoding="utf-8")
    )

    assert seal["result"]["flags"] == {
        "ALL_MINIMAL_FULL13_RECAPITULATORS_ACTIVE_ONLY": True,
        "INACTIVE_SUBSET_CLOSURE_SUPPORTED": True,
        "INACTIVE_SUBSET_EFFECT_PRESENT": False,
        "MIXED_GROUP_MINIMAL_RECAPITULATOR_PRESENT": False,
        "SQ06_PARTITION_REPLICATED": True,
        "STRICT_SUBSET_SEPARABILITY_SUPPORTED": True,
    }


def test_sq07_minimal_recapitulators_are_frozen():
    seal = json.loads(
        SEAL.read_text(encoding="utf-8")
    )

    result = seal["result"]

    assert result["minimal_full13_recapitulators"]["LR"] == [
        {
            "active_group_only": True,
            "hamming_weight": 9,
            "mask13": "1111011111000",
            "mixed_group": False,
        }
    ]

    assert result["minimal_full13_recapitulators"]["RL"] == [
        {
            "active_group_only": True,
            "hamming_weight": 3,
            "mask13": "0000000000111",
            "mixed_group": False,
        }
    ]

    assert result["inactive_subset_failures"] == {
        "LR": 0,
        "RL": 0,
    }

    assert result["single_overall_winner"] is None

    assert (
        result["minimum_meaningful_effect_floor"]
        == "NOT_DEFINED"
    )


def test_sq07_public_narrative_preserves_claim_boundary():
    text = DOC.read_text(encoding="utf-8")

    assert "These findings are properties of the frozen SQ-07 computational model" in text
    assert "There is no single overall scientific winner." in text
    assert "E04 is omitted" in text
    assert "do **not** establish" in text
