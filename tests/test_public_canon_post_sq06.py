from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def text(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def test_rasputin_public_status_is_operational_not_planned():
    charter = text("CHARTER.md")
    roadmap = text("ROADMAP.md")
    rasputin = text("docs/infrastructure/PROJECT_RASPUTIN.md")

    expected = "OPERATIONAL — FIRST AUTHORITATIVE WORKLOAD COMPLETE"
    assert expected in charter
    assert expected in roadmap
    assert expected in rasputin

    assert "**Canonical status:** PLANNED / INFRASTRUCTURE PRIORITY" not in charter
    assert "**Status:** NEXT INFRASTRUCTURE CAMPAIGN" not in roadmap


def test_public_docs_surface_sq05_and_sq06_sealed_results():
    readme = text("README.md")
    ledger = text("docs/EXPERIMENT_LEDGER.md")

    for marker in (
        "SQ-05 — TWO BETRAYALS",
        "SQ-06 — SILENT CARTOGRAPHER",
        "fbd902de5ddae4913af337e3d9a1a77ed55750edfe808a6863d8fb24c949f48a",
        "de7129a812a4520706512234be19543a51df64fa9879f50bee8d8a2045b5b816",
    ):
        assert marker in ledger

    assert "SQ-05 — TWO BETRAYALS" in readme
    assert "SQ-06 — SILENT CARTOGRAPHER" in readme

    normalized_readme = " ".join(readme.split())
    assert "prospective validation of an SQ-05-derived grouping" in normalized_readme


def test_rasputin_execution_chain_is_public_but_ops_remain_private():
    rasputin = text("docs/infrastructure/PROJECT_RASPUTIN.md")
    matrix = text("docs/PUBLIC_PRIVATE_COMPONENT_MATRIX_V1.md")
    boundary = text("docs/OPEN_CORE_BOUNDARY_V1.md")
    cloud = text("docs/cloud-deployment.md")

    assert "Authoritative scientific execution chain" in rasputin
    assert "immutable OCI image digest" in rasputin
    assert "Private `moscaquant-ops` remains authoritative" in rasputin

    assert "Authoritative scientific execution contract" in matrix
    assert "RASPUTIN provider IaC / operator internals" in matrix

    assert "RASPUTIN public/private boundary" in boundary
    assert "provider-specific cloud/deployment overlays" in boundary

    assert "PUBLIC WEB PLANE" in cloud
    assert "AUTHORITATIVE SCIENCE PLANE" in cloud


def test_sq06_claim_boundary_language_is_preserved():
    readme = text("README.md")
    ledger = text("docs/EXPERIMENT_LEDGER.md")

    assert "not independent discovery or a" in readme
    assert "biological orientation-circuit claim" in readme
    assert "not independent discovery" in ledger
    assert "does not establish a biological" in ledger
    assert "No minimum meaningful-effect floor was defined" in ledger
