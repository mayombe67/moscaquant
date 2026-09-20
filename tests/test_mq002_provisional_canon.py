from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
CHARTER = ROOT / "CHARTER.md"
ROADMAP = ROOT / "ROADMAP.md"
CONFIG = ROOT / "config" / "experiments" / "mq002_identity_check_v1.json"
PROGRAM = ROOT / "docs" / "experiments" / "mq002-comparative-control-program.md"
PROTOCOL = ROOT / "docs" / "experiments" / "mq002-0-identity-check-protocol.md"


def test_mq002_is_provisional_comparative_control():
    charter = CHARTER.read_text()
    assert "MQ-002 — PROVISIONAL COMPARATIVE BIOLOGICAL CONTROL" in charter
    assert "PROVISIONAL / DATA QUALIFICATION REQUIRED" in charter
    assert "not a replacement for SHUFFLED MOSCA" in charter
    assert "no financial authority" in charter
    assert "The comedy target is MQ-001's institutional predicament" in charter


def test_mainline_phase_is_unchanged():
    roadmap = ROADMAP.read_text()
    assert "**Current Phase:** MQ-9 — OPEN THE PANOPTICON" in roadmap
    assert "**Next Phase:** MQ-10 — INTRODUCE THE MONEY" in roadmap
    assert "MQ-9 remains current and MQ-10 remains next." in roadmap


def test_identity_check_is_non_result_bearing():
    data = json.loads(CONFIG.read_text())
    assert data["experiment_id"] == "MQ-002.0"
    assert data["status"] == "FROZEN_BEFORE_DISCOVERY"
    assert data["result_bearing_neural_experiment"] is False
    assert data["automatic_downloads"] == ["mcns_fw_edge_comp_mappings.json"]
    assert data["deferred_downloads"] == ["mcns_fw_edge_comp.feather"]


def test_program_and_protocol_boundaries():
    program = PROGRAM.read_text()
    protocol = PROTOCOL.read_text()
    assert "MQ-002 is canonically named but is not yet a validated second experimental" in program
    assert "The joke is not that one biological sex is inherently better" in program
    assert "run a male/female neural comparison from this discovery script" in protocol
    assert "treat unmatched VNC anatomy as female-matched anatomy" in protocol
