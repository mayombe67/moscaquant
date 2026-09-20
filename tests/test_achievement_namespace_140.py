from achievements.catalog_v1 import STATUS_BY_ID, V1_DEFINITIONS, V1_REGISTRY
from achievements.models import Category
from achievements.registry import expected_category, achievement_number

def test_namespace_capacity_140():
    assert achievement_number("ACH-140") == 140

def test_populated_count_87():
    assert len(V1_DEFINITIONS) == 87
    assert len(V1_REGISTRY) == 87
    assert len(STATUS_BY_ID) == 87

def test_extension_categories():
    assert expected_category("ACH-129") is Category.SCIENCE
    assert expected_category("ACH-131") is Category.CONTAINMENT
    assert expected_category("ACH-135") is Category.ORACLE
    assert expected_category("ACH-138") is Category.LORE
    assert expected_category("ACH-140") is Category.SECRET_ODDITY

def test_ach128_stays_locked():
    d = V1_REGISTRY["ACH-128"]
    assert d.title == "HALF-LIFE 3 CONFIRMED"
    assert d.permanently_locked is True
    assert d.public_text == "Nice try."

def test_ach139_manual_canon_not_hr():
    d = V1_REGISTRY["ACH-139"]
    assert STATUS_BY_ID["ACH-139"] == "MANUAL_CANON"
    assert "not an HR action" in d.claim_boundary
