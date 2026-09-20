from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "docs/experiments/sq03f6-the-commission-protocol.md"


def text():
    return PROTOCOL.read_text()


def test_sq03f6_protocol_identity_and_status():
    t = text()
    assert "# SQ-03F.6 — THE COMMISSION" in t
    assert "**Status:** FROZEN — NOT YET EXECUTED" in t
    assert "downstream-target concentration test" in t


def test_sq03f6_inherits_f5_without_retesting_it():
    t = text()
    assert "does not retest whether the SQ-03F.4 shared sources converge downstream" in t
    assert "authoritative SQ-03F.5 result artifact" in t
    assert "maximum depth of two hops" in t
    assert "same frozen conservative graph" in t
    assert "same frozen candidate-source universe" in t


def test_sq03f6_target_participation_is_defined_prospectively():
    t = text()
    assert "participation count as the number of eligible SQ-03F.5 sources" in t
    assert "contains that target" in t
    assert "MUST be frozen before observed concentration is interpreted" in t


def test_sq03f6_null_is_inherited_and_frozen():
    t = text()
    assert "inherit the SQ-03F.5 matched-source randomization framework" in t
    assert "10,000" in t
    assert "314159" in t
    assert "preserve the observed source count" in t


def test_sq03f6_classification_family_is_frozen():
    t = text()
    assert "GREATER_THAN_NULL_TARGET_CONCENTRATION" in t
    assert "NO_CLEAR_EVIDENCE_OF_UNUSUAL_TARGET_CONCENTRATION" in t
    assert "LESS_THAN_NULL_TARGET_CONCENTRATION" in t
    assert "No threshold may be moved after inspecting the observed result" in t


def test_sq03f6_claim_boundary_is_narrow():
    t = text()
    assert "literal biological command hierarchy" in t
    assert 'anatomical governing bodies or "commissions"' in t
    assert "consciousness, agency, intent, or coordination" in t
    assert "financial usefulness" in t
    assert "trading usefulness" in t


def test_sq03f6_protocol_does_not_execute():
    t = text()
    assert "It does NOT:" in t
    assert "calculate target participation" in t
    assert "rank downstream targets" in t
    assert "execute randomizations" in t
    assert "create an SQ-03F.6 result artifact" in t
    assert "analyzer contract SHALL be reviewed and frozen separately" in t
