import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "artifacts" / "sidequests" / "sq01-temporal-decoupling-v1.json"
RESULTS = ROOT / "docs" / "experiments" / "sq01-temporal-decoupling-results.md"

EXPECTED = {
    "BASELINE": (40, 0),
    "CLOCK_FAST": (226, 106),
    "CLOCK_SLOW": (3, 0),
    "RESAMPLE_8": (35, 1),
    "RESAMPLE_32": (38, 0),
    "RAW_8": (14, 0),
    "RAW_32": (76, 3),
}

def test_sq01_recorded_artifact_integrity():
    data = json.loads(ARTIFACT.read_text())
    assert data["sidequest_id"] == "SQ-01"
    assert data["baseline_harness_parity"] is True

    rows = {row["variant"]["id"]: row for row in data["rows"]}
    assert set(rows) == set(EXPECTED)
    assert all(row["deterministic"] is True for row in rows.values())

    for variant, (a_spikes, b_spikes) in EXPECTED.items():
        assert rows[variant]["A"]["relay_spikes"] == a_spikes
        assert rows[variant]["B"]["relay_spikes"] == b_spikes
        assert rows[variant]["ab_relay_discrimination"] is True
        assert rows[variant]["ab_wider_discrimination"] is False

def test_sq01_result_record_matches_frozen_run():
    data = json.loads(ARTIFACT.read_text())
    text = RESULTS.read_text()

    assert data["source_commit"] == "dad63a384a5bd23be0823c81ea2eaf410d160f53"
    assert data["config_sha256"] == "ee87df86bee3d2a7456ec4833e034eef75b869f04df7b695d095797ae2b22733"
    normalized_claim = " ".join(data["claim_boundary"].split())
    normalized_text = " ".join(text.split())
    assert normalized_claim in normalized_text
    assert "wall-clock execution rate" in text
    assert "simulated neural time" in text
    assert "post-run interpretation" in text
