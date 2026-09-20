from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "docs/experiments/sq03f5-turf-war-protocol.md"


def test_sq03f5_protocol_exists_and_is_frozen():
    text = PROTOCOL.read_text()
    assert "# SQ-03F.5 — TURF WAR" in text
    assert "**Status:** FROZEN — NOT YET EXECUTED" in text
    assert "SQ-03F.5 is a downstream-territory convergence test." in text


def test_sq03f5_inherits_sources_without_reselecting_them():
    text = PROTOCOL.read_text()
    assert "derived only from the authoritative frozen" in text
    assert "SQ-03F.4 result artifact" in text
    assert "No source may be added because it looks interesting" in text
    assert "No source may be removed because its downstream behavior weakens the result" in text
    assert "fail closed" in text


def test_sq03f5_randomization_is_frozen():
    text = PROTOCOL.read_text()
    assert "10,000" in text
    assert "314159" in text
    assert "matched randomization null" in text
    assert "preserve the number of eligible sources" in text


def test_sq03f5_claim_boundary_is_explicit():
    text = PROTOCOL.read_text()
    assert "within the frozen MoscaQuant model" in text
    assert "It would not establish:" in text
    assert "biological gang-like organization" in text
    assert "financial usefulness" in text
    assert "trading usefulness" in text


def test_sq03f5_does_not_claim_execution():
    text = PROTOCOL.read_text()
    assert "Creating this protocol does not execute SQ-03F.5." in text
    assert "No SQ-03F.5 result artifact exists merely because this protocol is committed." in text
    assert "must be reviewed and frozen separately before execution" in text
