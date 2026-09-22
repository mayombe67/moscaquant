from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_project_rasputin_canon_present():
    charter = (ROOT / "CHARTER.md").read_text()
    roadmap = (ROOT / "ROADMAP.md").read_text()
    design = (ROOT / "docs/infrastructure/PROJECT_RASPUTIN.md").read_text()

    assert "PROJECT RASPUTIN — Elastic Scientific Execution Plane" in charter
    assert "RASPUTIN may change horsepower. It may never change experimental meaning." in charter
    assert "PROJECT RASPUTIN — AWAKEN RASPUTIN" in roadmap
    assert "RAID — WRATH OF THE MACHINE" in roadmap
    assert "RAID BOSS — AKSIS, ARCHON PRIME" in roadmap
    assert "MQ-5.ER.5 — THE GREEK" in roadmap
    assert "AWS Batch" in design
    assert "Spot" in design


def test_rasputin_strike_sequence_is_complete():
    roadmap = (ROOT / "ROADMAP.md").read_text()

    required = (
        "RSP-01 — STRIKE: SERAPH'S SHIELD",
        "RSP-02 — STRIKE: OFF-WORLD RECOVERY",
        "RSP-03 — STRIKE: WARMIND NETWORK",
        "RSP-04 — STRIKE: THE TYRANT'S TEST",
        "RSP-05 — STRIKE: ABHORRENT IMPERATIVE",
        "RSP-06 — STRIKE: SERAPH STATION",
    )
    for item in required:
        assert item in roadmap


def test_greek_remains_scientifically_frozen():
    charter = (ROOT / "CHARTER.md").read_text()
    roadmap = (ROOT / "ROADMAP.md").read_text()

    assert "Habitat non-completion is an execution-layer limitation, not an experimental" in charter
    assert "no change to THE GREEK scientific semantics" in roadmap
