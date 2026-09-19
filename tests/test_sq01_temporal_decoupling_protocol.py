import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "experiments" / "sq01_temporal_decoupling_v1.json"
PROTOCOL = ROOT / "docs" / "experiments" / "sq01-temporal-decoupling-protocol.md"
RUNNER = ROOT / "brain" / "sq01_temporal_decoupling.py"


def test_sq01_files_exist():
    assert CONFIG.exists()
    assert PROTOCOL.exists()
    assert RUNNER.exists()


def test_sq01_frozen_matrix():
    data = json.loads(CONFIG.read_text())

    assert data["sidequest_id"] == "SQ-01"

    variants = {item["id"]: item for item in data["variants"]}

    assert variants["BASELINE"] == {
        "id": "BASELINE",
        "frame_count": 16,
        "dt_ms": 1.0,
        "stimulus_scale": 1.0,
        "class": "REFERENCE",
    }

    assert variants["CLOCK_FAST"]["frame_count"] == 16
    assert variants["CLOCK_FAST"]["dt_ms"] == 0.5

    assert variants["CLOCK_SLOW"]["frame_count"] == 16
    assert variants["CLOCK_SLOW"]["dt_ms"] == 2.0

    assert (
        variants["RESAMPLE_8"]["frame_count"]
        * variants["RESAMPLE_8"]["dt_ms"]
        == 16.0
    )
    assert (
        variants["RESAMPLE_32"]["frame_count"]
        * variants["RESAMPLE_32"]["dt_ms"]
        == 16.0
    )

    assert (
        variants["RESAMPLE_8"]["frame_count"]
        * variants["RESAMPLE_8"]["stimulus_scale"]
        == 16.0
    )
    assert (
        variants["RESAMPLE_32"]["frame_count"]
        * variants["RESAMPLE_32"]["stimulus_scale"]
        == 16.0
    )


def test_sq01_is_sidequest_not_phase_gate():
    text = PROTOCOL.read_text()

    assert "science side quest" in text
    assert "does not advance or replace the main MQ phase" in text
    assert "does **not** establish biological timing" in text
