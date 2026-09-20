from achievements.catalog_v1 import STATUS_BY_ID, V1_DEFINITIONS, V1_REGISTRY
from achievements.models import Category
from achievements.registry import achievement_number, expected_category

EXPECTED = {
    "ACH-141": ("LIGHT WEIGHT, BABY!", Category.CONTAINMENT),
    "ACH-142": ("YEAH BUDDY!", Category.LORE),
    "ACH-143": ("DO YOU EVEN LIFT?", Category.SCIENCE),
    "ACH-144": ("PR OR ER", Category.SCIENCE),
    "ACH-145": ("FORM CHECK", Category.CONTAINMENT),
    "ACH-146": ("EGO LIFT", Category.SCIENCE),
    "ACH-147": ("SKIPPED LEG DAY", Category.SCIENCE),
    "ACH-148": ("BRO SPLIT", Category.SCIENCE),
    "ACH-149": ("ONE MORE REP", Category.LORE),
    "ACH-150": ("PLATE MATH", Category.ORACLE),
    "ACH-151": ("REST DAY IS A SOCIAL CONSTRUCT", Category.ANOMALOUS_OBSERVANCE),
    "ACH-152": ("NATTY OR NOT?", Category.SECRET_ODDITY),
}

def test_namespace_capacity_ends_at_152():
    assert achievement_number("ACH-152") == 152

def test_populated_catalog_is_84():
    assert len(V1_DEFINITIONS) == 84
    assert len(V1_REGISTRY) == 84
    assert len(STATUS_BY_ID) == 84

def test_gym_pack_titles_and_categories():
    for aid, (title, category) in EXPECTED.items():
        assert V1_REGISTRY[aid].title == title
        assert V1_REGISTRY[aid].category is category
        assert expected_category(aid) is category

def test_ach128_still_locked():
    d = V1_REGISTRY["ACH-128"]
    assert d.permanently_locked is True
    assert d.title == "HALF-LIFE 3 CONFIRMED"
    assert d.public_text == "Nice try."
