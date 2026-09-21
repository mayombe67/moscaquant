import pytest

from overwatch.modifiers import (
    CLASSIFIED,
    UNLOCKED,
    SponsorV1,
    disclose_referendum,
    emit_modifier_activated,
    emit_modifier_unlocked,
    public_referendum_payload,
)
from overwatch.storage import LocalJsonlStorage


THREE = (
    "MOD-MGMT-CONSULTANT",
    "MOD-THE-AUDIT",
    "MOD-WELLNESS",
)


def test_referendum_discloses_exactly_three_candidates():
    referendum = disclose_referendum("REF-001", THREE)
    payload = public_referendum_payload(referendum)

    assert len(payload["candidates"]) == 3
    assert payload["catalog_disclosure"] == "exactly_three_candidates_only"
    assert "catalog_size" not in payload


def test_referendum_rejects_more_than_three_candidates():
    with pytest.raises(ValueError):
        disclose_referendum(
            "REF-002",
            (
                "MOD-MGMT-CONSULTANT",
                "MOD-THE-AUDIT",
                "MOD-WELLNESS",
                "MOD-PIP",
            ),
        )


def test_referendum_rejects_duplicate_candidates():
    with pytest.raises(ValueError):
        disclose_referendum(
            "REF-003",
            (
                "MOD-MGMT-CONSULTANT",
                "MOD-MGMT-CONSULTANT",
                "MOD-THE-AUDIT",
            ),
        )


def test_winner_becomes_persistently_unlocked_and_losers_reclassify(tmp_path):
    storage = LocalJsonlStorage(tmp_path / "mods.jsonl")
    referendum = disclose_referendum("REF-004", THREE)

    event = emit_modifier_unlocked(
        storage,
        run_id="run-1",
        referendum=referendum,
        winner_id="MOD-THE-AUDIT",
        vote_receipt_ref="receipt://vote-004",
    )

    assert event.payload["status"] == UNLOCKED
    assert event.payload["persistence"] == "permanent_until_explicit_retirement"
    assert event.payload["losers_return_to"] == CLASSIFIED


def test_sponsor_can_be_attached_without_scientific_authority(tmp_path):
    storage = LocalJsonlStorage(tmp_path / "mods.jsonl")
    sponsor = SponsorV1(
        sponsor_id="sponsor-example",
        display_name="Example Corp",
        sponsor_type="company",
    )

    event = emit_modifier_activated(
        storage,
        run_id="run-2",
        modifier_id="MOD-WELLNESS",
        unlock_event_id="unlock-123",
        sponsor=sponsor,
    )

    assert event.payload["sponsor"]["display_name"] == "Example Corp"
    assert "cannot alter scientific interpretation" in event.payload["science_boundary"]


def test_main_page_surface_is_compact(tmp_path):
    storage = LocalJsonlStorage(tmp_path / "mods.jsonl")

    event = emit_modifier_activated(
        storage,
        run_id="run-3",
        modifier_id="MOD-MGMT-CONSULTANT",
        unlock_event_id="unlock-456",
    )

    surface = event.payload["main_page_surface"]
    assert surface["show"] is True
    assert surface["detail_location"] == "modifier_detail"
    assert tuple(surface["fields"]) == (
        "display_name",
        "science_effect",
        "sponsor",
    )
