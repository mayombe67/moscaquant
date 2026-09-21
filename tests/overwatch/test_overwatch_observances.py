from datetime import date

import pytest

from overwatch.observances import (
    BLACKSITE_HOLIDAY_001,
    EXPERIMENTAL,
    ObservanceV1,
    canonical_observances,
    emit_observance_activated,
    observance_by_id,
    observances_for_day,
)
from overwatch.storage import LocalJsonlStorage


def test_launch_day_is_blacksite_holiday_001():
    observance = observance_by_id(BLACKSITE_HOLIDAY_001)

    assert observance.month == 10
    assert observance.day == 30
    assert observance.environment_variant == "CELL-67.BIRTHDAY.v1"


def test_founder_day_is_june_20_and_presentation_only():
    observance = observance_by_id("BLACKSITE-HOLIDAY-004")

    assert observance.display_name == "Founder Day"
    assert observance.month == 6
    assert observance.day == 20
    assert observance.science_effect == "PRESENTATION_ONLY"


def test_courtship_observance_does_not_enable_interaction_protocol():
    observance = observance_by_id("BLACKSITE-HOLIDAY-003")

    assert observance.month == 2
    assert observance.day == 14
    assert observance.science_effect == "PRESENTATION_ONLY"
    assert "separate frozen protocol" in observance.notes[1]


def test_observances_for_day_matches_calendar_date():
    matches = observances_for_day(date(2027, 6, 20))

    assert len(matches) == 1
    assert matches[0].display_name == "Founder Day"


def test_experimental_observance_requires_frozen_protocol_flag():
    with pytest.raises(ValueError):
        ObservanceV1(
            observance_id="TEST",
            display_name="Test",
            month=7,
            day=7,
            science_effect=EXPERIMENTAL,
            frozen_protocol_required=False,
        )


def test_experimental_activation_requires_protocol_reference(tmp_path):
    storage = LocalJsonlStorage(tmp_path / "observance.jsonl")
    observance = ObservanceV1(
        observance_id="TEST-EXP",
        display_name="Test Experimental Observance",
        month=7,
        day=7,
        science_effect=EXPERIMENTAL,
        frozen_protocol_required=True,
    )

    with pytest.raises(ValueError):
        emit_observance_activated(
            storage,
            run_id="run-1",
            observance=observance,
            activation_date=date(2027, 7, 7),
        )


def test_canonical_calendar_is_secular_by_design():
    text = " ".join(
        [o.display_name for o in canonical_observances()]
        + [note for o in canonical_observances() for note in o.notes]
    ).lower()

    forbidden = (
        "christmas",
        "easter",
        "sol invictus",
        "saint ",
        "religious holiday",
    )
    assert all(term not in text for term in forbidden)
