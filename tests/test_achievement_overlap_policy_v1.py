from achievements.overlap_policy_v1 import (
    CANONICAL_PREDICATE_BY_ID,
    COMEDIC_OVERLAP_GROUPS,
    REVIEW_STATE_BY_ID,
)

def test_modern_overlap_policy_covers_129_through_152():
    expected = {f"ACH-{n:03d}" for n in range(129, 153)}
    assert set(CANONICAL_PREDICATE_BY_ID) == expected
    assert set(REVIEW_STATE_BY_ID) == expected

def test_reviewed_predicates_are_unique_unless_explicitly_comedic():
    owners = {}
    for aid, predicate in CANONICAL_PREDICATE_BY_ID.items():
        owners.setdefault(predicate, []).append(aid)

    allowed_sets = {
        frozenset(members)
        for members in COMEDIC_OVERLAP_GROUPS.values()
    }
    for predicate, ids in owners.items():
        if len(ids) > 1:
            assert frozenset(ids) in allowed_sets, (
                f"accidental canonical predicate overlap: {predicate}: {ids}"
            )

def test_no_modern_entry_is_silently_unreviewed():
    assert set(REVIEW_STATE_BY_ID.values()) == {"REVIEWED_DISTINCT"}

def test_known_boundaries_stay_distinct():
    p = CANONICAL_PREDICATE_BY_ID
    assert p["ACH-130"] != p["ACH-152"]
    assert p["ACH-136"] != p["ACH-143"]
    assert p["ACH-138"] != p["ACH-146"]
    assert p["ACH-129"] != p["ACH-147"]
