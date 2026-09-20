import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "artifacts" / "sidequests" / "sq04-global-modulation-v1.json"
RESULTS = ROOT / "docs" / "experiments" / "sq04-global-modulation-results.md"

SOURCE_COMMIT = "f4d2949012abd1a2db33df264fa0ecf3415f1a25"
CONFIG_SHA256 = "f764888910fd49887ec2f2d203eea9424c54aa74fdd13d77cf93ea93bfb0940f"

EXPECTED = {
    "REFERENCE": (2605, 40, 0, 131.0, None),
    "THRESHOLD_LOW_10": (3685, 70, 0, 48.0, None),
    "THRESHOLD_HIGH_10": (1816, 17, 0, 138.0, None),
    "TAU_FAST_25": (1094, 15, 0, 139.0, None),
    "TAU_SLOW_25": (4010, 66, 0, 65.0, None),
}


def rows(data):
    return {row["variant"]["id"]: row for row in data["rows"]}


def test_sq04_artifact_identity_and_determinism():
    data = json.loads(ARTIFACT.read_text())
    assert data["sidequest_id"] == "SQ-04"
    assert data["source_commit"] == SOURCE_COMMIT
    assert data["config_sha256"] == CONFIG_SHA256
    assert all(row["deterministic_AA_replay"] is True for row in data["rows"])


def test_sq04_primary_recorded_measurements():
    data = json.loads(ARTIFACT.read_text())
    by_variant = rows(data)
    for variant, expected in EXPECTED.items():
        r = by_variant[variant]["result"]
        observed = (
            r["retinal_spike_count"],
            r["relay_spike_count"],
            r["wider_network_spike_count"],
            r["first_relay_spike_time_ms_if_any"],
            r["first_wider_spike_time_ms_if_any"],
        )
        assert observed == expected


def test_sq04_threshold_count_ordering():
    data = json.loads(ARTIFACT.read_text())
    r = rows(data)
    assert (
        r["THRESHOLD_LOW_10"]["result"]["retinal_spike_count"]
        > r["REFERENCE"]["result"]["retinal_spike_count"]
        > r["THRESHOLD_HIGH_10"]["result"]["retinal_spike_count"]
    )
    assert (
        r["THRESHOLD_LOW_10"]["result"]["relay_spike_count"]
        > r["REFERENCE"]["result"]["relay_spike_count"]
        > r["THRESHOLD_HIGH_10"]["result"]["relay_spike_count"]
    )


def test_sq04_tau_count_ordering():
    data = json.loads(ARTIFACT.read_text())
    r = rows(data)
    assert (
        r["TAU_SLOW_25"]["result"]["retinal_spike_count"]
        > r["REFERENCE"]["result"]["retinal_spike_count"]
        > r["TAU_FAST_25"]["result"]["retinal_spike_count"]
    )
    assert (
        r["TAU_SLOW_25"]["result"]["relay_spike_count"]
        > r["REFERENCE"]["result"]["relay_spike_count"]
        > r["TAU_FAST_25"]["result"]["relay_spike_count"]
    )


def test_sq04_no_wider_network_propagation():
    data = json.loads(ARTIFACT.read_text())
    for row in data["rows"]:
        r = row["result"]
        assert r["wider_network_spike_count"] == 0
        assert r["first_wider_spike_time_ms_if_any"] is None


def test_sq04_results_preserve_boundaries_and_runner_hash_note():
    data = json.loads(ARTIFACT.read_text())
    text = RESULTS.read_text()
    assert data["claim_boundary"] in text
    assert "Global threshold sensitivity:** SUPPORTED" in text
    assert "Membrane time-constant sensitivity:** SUPPORTED" in text
    assert "Wider-network propagation:** NOT OBSERVED" in text
    assert "must not be interpreted as a pure input-stimulus hash" in text
    assert "No retuning was performed after observing these results." in text
