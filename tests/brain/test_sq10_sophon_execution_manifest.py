from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

MANIFEST = (
    ROOT
    / "config/controls/"
    "sq10-sophon-execution-manifest-v1.json"
)

SCIENCE_SHA = (
    "af0db6776cb478e75947292236abd82b3953a778"
)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()

    with path.open("rb") as f:
        for block in iter(
            lambda: f.read(8 * 1024 * 1024),
            b"",
        ):
            h.update(block)

    return h.hexdigest()


def load():
    return json.loads(
        MANIFEST.read_text()
    )


def test_manifest_is_pre_execution_only():
    d = load()

    assert (
        d["status"]
        == "FROZEN_PRE_EXECUTION"
    )

    assert (
        d["science_git_sha"]
        == SCIENCE_SHA
    )

    assert (
        d["neural_execution_authorized"]
        is False
    )

    assert (
        d["execution_boundary"]
        ["authorization_granted"]
        is False
    )


def test_exact_16_unit_cube():
    d = load()

    masks = [
        "000",
        "001",
        "010",
        "011",
        "100",
        "101",
        "110",
        "111",
    ]

    expected = [
        f"sq10:{mask}:r{replicate}"
        for mask in masks
        for replicate in (1, 2)
    ]

    conditions = d["conditions"]

    assert len(conditions) == 16

    assert [
        row["ordinal"]
        for row in conditions
    ] == list(range(16))

    assert [
        row["condition_id"]
        for row in conditions
    ] == expected

    assert (
        len(
            {
                row["condition_id"]
                for row in conditions
            }
        )
        == 16
    )

    for row in conditions:
        mask = row["mask"]

        assert (
            row["edge_zeroed"]
            == {
                "A": int(mask[0]),
                "B": int(mask[1]),
                "C": int(mask[2]),
            }
        )


def test_effective_runtime_contract():
    d = load()

    execution = d[
        "execution_contract"
    ]

    assert execution[
        "frame_count"
    ] == 192

    assert execution[
        "layout"
    ] == "RL"

    runtime = execution[
        "runtime_parameters"
    ]

    assert runtime == {
        "dt_ms": 1.0,
        "tau_ms": 20.0,
        "threshold": 1.0,
        "release_gain":
            0.9981738484618123,
    }


def test_body_identity_is_frozen():
    d = load()

    body = d["body_edges"]

    assert (
        body["A"]["source"],
        body["A"]["responder"],
    ) == (
        65084,
        137122,
    )

    assert (
        body["B"]["source"],
        body["B"]["responder"],
    ) == (
        128590,
        317,
    )

    assert (
        body["C"]["source"],
        body["C"]["responder"],
    ) == (
        135589,
        126002,
    )


def test_all_repo_artifact_hashes_match():
    d = load()

    for section in (
        "frozen_code",
        "frozen_contracts",
    ):
        for name, item in (
            d[section].items()
        ):
            path = ROOT / item["path"]

            assert path.is_file(), (
                name,
                path,
            )

            assert (
                sha256_file(path)
                == item["sha256"]
            ), name


def test_calibrated_ruler_is_bound():
    d = load()

    assert (
        d["numerical_acceptance"]
        == {
            "absolute_tolerance":
                3.814697265625e-06,
            "relative_tolerance":
                0.0,
            "calibration_rule_frozen_before_execution":
                True,
        }
    )


def test_evidence_destination_is_fail_closed():
    d = load()

    destination = d[
        "evidence_destination"
    ]

    assert (
        destination[
            "must_not_exist_before_execution"
        ]
        is True
    )

    assert (
        destination[
            "overwrite_existing"
        ]
        is False
    )


def test_interpretation_authority_is_absent():
    d = load()

    boundary = d[
        "execution_boundary"
    ]

    assert (
        boundary["analysis_authority"]
        is False
    )

    assert (
        boundary[
            "mechanism_interpretation_authority"
        ]
        is False
    )

    assert (
        boundary[
            "result_reclassification_authority"
        ]
        is False
    )
