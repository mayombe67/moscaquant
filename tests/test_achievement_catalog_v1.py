from achievements.catalog_v1 import STATUS_BY_ID, V1_DEFINITIONS, V1_REGISTRY
from achievements.models import Category


def test_v1_has_exactly_87_populated_definitions():
    assert len(V1_DEFINITIONS) == 87
    assert len(V1_REGISTRY) == 87


def test_v1_spans_all_reserved_categories():
    assert {d.category for d in V1_DEFINITIONS} == {
        Category.SCIENCE,
        Category.ORACLE,
        Category.CONTAINMENT,
        Category.BEHAVIOR,
        Category.LORE,
        Category.ANOMALOUS_OBSERVANCE,
        Category.SECRET_ODDITY,
    }


def test_v1_contains_requested_canon():
    assert V1_REGISTRY["ACH-065"].title == "PAPER HANDS"
    assert V1_REGISTRY["ACH-015"].title == "THERE ARE FOUR LIGHTS"
    assert V1_REGISTRY["ACH-090"].title == "BEFORE GTA VI"
    assert V1_REGISTRY["ACH-091"].title == "SKIBIDI CONNECTOME"
    assert V1_REGISTRY["ACH-092"].title == "TRIPLE T IS IN THE LAB"
    assert V1_REGISTRY["ACH-095"].title == "HOW McDOCTORATE LOOKS AT YOU"
    assert V1_REGISTRY["ACH-128"].permanently_locked is True


def test_historical_replay_entries_have_evidence_refs():
    for definition in V1_DEFINITIONS:
        if STATUS_BY_ID[definition.achievement_id] == "HISTORICAL_REPLAY_ELIGIBLE":
            assert definition.evidence_refs
