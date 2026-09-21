from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
from typing import Any

from .events import TelemetryEventV1
from .storage import TelemetryStorage


PRESENTATION_ONLY = "PRESENTATION_ONLY"
EXPLORATORY = "EXPLORATORY"
EXPERIMENTAL = "EXPERIMENTAL"

BLACKSITE_HOLIDAY_001 = "BLACKSITE-HOLIDAY-001"


@dataclass(frozen=True)
class ObservanceV1:
    observance_id: str
    display_name: str
    month: int
    day: int
    science_effect: str
    environment_variant: str | None = None
    community_vote_allowed: bool = False
    frozen_protocol_required: bool = False
    replay_enabled: bool = True
    notes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.science_effect not in {
            PRESENTATION_ONLY,
            EXPLORATORY,
            EXPERIMENTAL,
        }:
            raise ValueError("invalid science_effect")
        date(2000, self.month, self.day)
        if self.science_effect == EXPERIMENTAL and not self.frozen_protocol_required:
            raise ValueError(
                "experimental observances must require a frozen protocol"
            )

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["notes"] = list(self.notes)
        return data


def canonical_observances() -> tuple[ObservanceV1, ...]:
    return (
        ObservanceV1(
            observance_id=BLACKSITE_HOLIDAY_001,
            display_name="MORTY Launch Day / Birthday",
            month=10,
            day=30,
            science_effect=EXPLORATORY,
            environment_variant="CELL-67.BIRTHDAY.v1",
            notes=(
                "Canonical MQ-001 launch/birthday observance.",
                "Room roaming and interactive props are exploratory.",
            ),
        ),
        ObservanceV1(
            observance_id="BLACKSITE-HOLIDAY-002",
            display_name="Elevated Anomaly Readiness",
            month=10,
            day=31,
            science_effect=PRESENTATION_ONLY,
            notes=(
                "Halloween-adjacent secular presentation event.",
                "No scientific thresholds or experiment behavior change.",
            ),
        ),
        ObservanceV1(
            observance_id="BLACKSITE-HOLIDAY-003",
            display_name="Inter-Subject Courtship Observance",
            month=2,
            day=14,
            science_effect=PRESENTATION_ONLY,
            notes=(
                "Presentation-only until an explicit MQ-001/MQ-002 protocol exists.",
                "Any MORTY/LILITH interaction requires a separate frozen protocol.",
            ),
        ),
        ObservanceV1(
            observance_id="BLACKSITE-HOLIDAY-004",
            display_name="Founder Day",
            month=6,
            day=20,
            science_effect=PRESENTATION_ONLY,
            notes=(
                "Secular operator/founder observance.",
                "Founder omnipotence claims remain lore and are scientifically unverified.",
            ),
        ),
        ObservanceV1(
            observance_id="BLACKSITE-HOLIDAY-005",
            display_name="Resource Extraction Observance",
            month=11,
            day=27,
            science_effect=PRESENTATION_ONLY,
            notes=(
                "Black-Friday-style productivity/procurement satire.",
                "Calendar date may be revised annually if dynamic scheduling is introduced.",
            ),
        ),
        ObservanceV1(
            observance_id="BLACKSITE-HOLIDAY-006",
            display_name="Annual Containment Recertification",
            month=1,
            day=1,
            science_effect=PRESENTATION_ONLY,
            notes=(
                "Yearly recap, achievements, lineage and containment review.",
            ),
        ),
        ObservanceV1(
            observance_id="BLACKSITE-HOLIDAY-007",
            display_name="Information Integrity Incident",
            month=4,
            day=1,
            science_effect=PRESENTATION_ONLY,
            notes=(
                "Public presentation may become intentionally absurd.",
                "Raw telemetry and receipts remain unchanged and accessible.",
            ),
        ),
    )


def observance_by_id(observance_id: str) -> ObservanceV1:
    for observance in canonical_observances():
        if observance.observance_id == observance_id:
            return observance
    raise KeyError(observance_id)


def observances_for_day(day: date) -> tuple[ObservanceV1, ...]:
    return tuple(
        o
        for o in canonical_observances()
        if o.month == day.month and o.day == day.day
    )


def emit_observance_activated(
    storage: TelemetryStorage,
    *,
    run_id: str,
    observance: ObservanceV1,
    activation_date: date,
    protocol_ref: str | None = None,
    subject_id: str | None = "MQ-001",
) -> TelemetryEventV1:
    if observance.science_effect == EXPERIMENTAL and not protocol_ref:
        raise ValueError(
            "experimental observance requires a frozen protocol reference"
        )

    event = TelemetryEventV1(
        event_type="observance.activated",
        run_id=run_id,
        component="observance",
        subject_id=subject_id,
        payload={
            "observance": observance.to_dict(),
            "activation_date": activation_date.isoformat(),
            "protocol_ref": protocol_ref,
            "science_boundary": (
                "observance presentation does not alter scientific interpretation "
                "unless an explicit frozen protocol authorizes an experiment"
            ),
        },
        lore_surface="HUD",
    )
    storage.append(event)
    return event


def emit_observance_closed(
    storage: TelemetryStorage,
    *,
    run_id: str,
    observance: ObservanceV1,
    reason: str,
    subject_id: str | None = "MQ-001",
) -> TelemetryEventV1:
    event = TelemetryEventV1(
        event_type="observance.closed",
        run_id=run_id,
        component="observance",
        subject_id=subject_id,
        payload={
            "observance_id": observance.observance_id,
            "reason": reason,
            "restore_normal_presentation": True,
        },
        lore_surface="HUD",
    )
    storage.append(event)
    return event
