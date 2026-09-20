from achievements.catalog_v1 import V1_REGISTRY
from achievements.overlap_policy_v1 import (
    CANONICAL_PREDICATE_BY_ID,
    LEGACY_ADJUDICATION_V1,
)


def test_legacy_pairs_have_distinct_predicates():
    p = CANONICAL_PREDICATE_BY_ID
    assert p["ACH-008"] != p["ACH-019"]
    assert p["ACH-035"] != p["ACH-036"]
    assert p["ACH-066"] != p["ACH-074"]
    assert p["ACH-001"] != p["ACH-012"]


def test_ach040_was_retargeted():
    d = V1_REGISTRY["ACH-040"]
    assert d.title == "ANYWAY, $4 A POUND."
    assert d.trigger_version == "four-dollars-a-pound/v1"
    assert "practical-relevance" in d.science_text
    assert LEGACY_ADJUDICATION_V1["ACH-040"] == "REPLACED_RETARGETED"


def test_retained_ach035_keeps_positive_modulation_job():
    d = V1_REGISTRY["ACH-035"]
    assert d.title == "BUFF ACTIVE"
    assert "positive" in d.science_text.lower()


def test_all_adjudicated_ids_are_in_predicate_registry():
    expected = {
        "ACH-001", "ACH-008", "ACH-012", "ACH-019",
        "ACH-035", "ACH-036", "ACH-040", "ACH-066", "ACH-074",
    }
    assert expected <= set(CANONICAL_PREDICATE_BY_ID)
    assert expected == set(LEGACY_ADJUDICATION_V1)
