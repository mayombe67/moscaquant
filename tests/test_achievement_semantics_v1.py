import json
from pathlib import Path

from achievements.semantics_v1 import semantics_for


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "achievements" / "catalog_v1.json"

HISTORICAL_IDS = {
    "ACH-001",
    "ACH-002",
    "ACH-003",
    "ACH-004",
    "ACH-005",
    "ACH-006",
    "ACH-007",
    "ACH-008",
    "ACH-009",
    "ACH-019",
    "ACH-020",
}

REQUIRED_FIELDS = {
    "claim_boundary",
    "family",
    "tags",
    "related_achievement_ids",
    "provenance_class",
    "social_eligible",
    "syndication_class",
    "dossier_priority",
}


def _catalog():
    return json.loads(CATALOG.read_text())


def test_all_60_definitions_have_complete_semantics():
    payload = _catalog()
    assert payload["count"] == 60
    assert payload["semantics_version"] == "mq8.5a/v1"

    assert len(payload["definitions"]) == 60

    for row in payload["definitions"]:
        assert REQUIRED_FIELDS <= set(row)


def test_historical_achievements_have_nonempty_claim_boundaries():
    payload = _catalog()
    by_id = {
        row["achievement_id"]: row
        for row in payload["definitions"]
    }

    for achievement_id in HISTORICAL_IDS:
        row = by_id[achievement_id]
        assert row["provenance_class"] == "HISTORICAL_REPLAY"
        assert row["claim_boundary"].strip()
        assert row["family"] != "UNCLASSIFIED"


def test_historical_related_ids_exist():
    payload = _catalog()
    known = {
        row["achievement_id"]
        for row in payload["definitions"]
    }

    for row in payload["definitions"]:
        for related in row["related_achievement_ids"]:
            assert related in known
            assert related != row["achievement_id"]


def test_social_semantics_are_bounded():
    payload = _catalog()

    for row in payload["definitions"]:
        assert row["syndication_class"] in {"MAJOR", "NOTABLE", "NOISE"}
        assert row["dossier_priority"] in {"NORMAL", "HIGH", "CRITICAL"}

        if row["syndication_class"] in {"MAJOR", "NOTABLE"}:
            assert row["social_eligible"] is True


def test_semantics_overlay_has_safe_defaults():
    row = semantics_for("ACH-128", "SECRET_ODDITY")

    assert row["family"] == "SECRET_ODDITY"
    assert row["social_eligible"] is False
    assert row["syndication_class"] == "NOISE"
    assert row["related_achievement_ids"] == []

def test_namespace_capacity_is_explicit():
    payload = _catalog()

    assert payload["namespace_size"] == 128
    assert payload["defined_count"] == 60
    assert payload["reserved_count"] == 68
    assert payload["defined_count"] + payload["reserved_count"] == payload["namespace_size"]
    assert payload["count"] == payload["defined_count"]
