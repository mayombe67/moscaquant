from achievements.catalog_v1 import V1_REGISTRY, V1_DEFINITIONS, STATUS_BY_ID
from achievements.models import Category
from achievements.overlap_policy_v1 import (
    CANONICAL_PREDICATE_BY_ID,
    COMEDIC_OVERLAP_GROUPS,
    SOPRANOS_PACK_REVIEW_V1,
)


def test_three_new_definitions_added():
    assert len(V1_DEFINITIONS) == 87
    assert len(STATUS_BY_ID) == 87


def test_salads_science_achievement():
    d = V1_REGISTRY["ACH-021"]
    assert d.category is Category.SCIENCE
    assert d.title == "I THINK IT'S TIME YOU STARTED SERIOUSLY CONSIDERING SALADS."
    assert "matched comparison" in d.science_text
    assert "comparable opportunity" in d.science_text


def test_doctors_note_is_specific_containment_predicate():
    d = V1_REGISTRY["ACH-057"]
    assert d.category is Category.CONTAINMENT
    assert d.title == "A NOTE FROM YOUR DOCTOR SAYING YOU DON'T LIKE TO SUCK COCK?"
    assert "exception" in d.science_text.lower()
    assert "valid evidence" in d.science_text.lower()


def test_car_flip_is_lore_only_comedic_followup():
    d = V1_REGISTRY["ACH-097"]
    assert d.category is Category.LORE
    assert d.evidence_level.value == "E0"
    assert "ACH-021" in d.science_text
    assert "no biological" in d.claim_boundary


def test_salads_car_flip_overlap_is_explicit():
    assert COMEDIC_OVERLAP_GROUPS["SALADS_CAR_FLIP"] == ("ACH-021", "ACH-097")
    assert SOPRANOS_PACK_REVIEW_V1["ACH-097"] == "INTENTIONAL_COMEDIC_OVERLAP"


def test_new_predicates_are_distinct():
    p = CANONICAL_PREDICATE_BY_ID
    assert p["ACH-021"] != p["ACH-057"]
    assert p["ACH-021"] != p["ACH-097"]
    assert p["ACH-057"] != p["ACH-097"]
