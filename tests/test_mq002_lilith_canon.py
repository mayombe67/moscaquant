from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]


def test_mq002_lilith_is_canonical_codename():
    charter = (ROOT / "CHARTER.md").read_text()
    roadmap = (ROOT / "ROADMAP.md").read_text()
    program = (ROOT / "docs" / "experiments" / "mq002-comparative-control-program.md").read_text()

    assert "MQ-002 — LILITH / PROVISIONAL COMPARATIVE BIOLOGICAL CONTROL" in charter
    assert "Canonical codename:\n\nLILITH" in charter
    assert "MQ-002 // LILITH" in roadmap
    assert "MQ-002 // LILITH" in program


def test_mq002_configs_lock_lilith_when_present():
    for rel in (
        "config/experiments/mq002_identity_check_v1.json",
        "config/experiments/mq002_matched_subgraph_v1.json",
    ):
        path = ROOT / rel
        if path.exists():
            data = json.loads(path.read_text())
            assert data["codename"] == "LILITH"
