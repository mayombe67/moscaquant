from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable

from .events import TelemetryEventV1
from .storage import TelemetryStorage
from .observances import PRESENTATION_ONLY, EXPLORATORY, EXPERIMENTAL


CLASSIFIED = "CLASSIFIED"
DISCLOSED = "DISCLOSED"
UNLOCKED = "UNLOCKED"
ACTIVE = "ACTIVE"
RETIRED = "RETIRED"


@dataclass(frozen=True)
class ModifierVisualProfileV1:
    hud_badge: str
    room_theme: str | None = None
    morty_accessory: str | None = None
    monitor_treatment: str | None = None
    signage: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["signage"] = list(self.signage)
        return data


@dataclass(frozen=True)
class ContainmentModifierV1:
    modifier_id: str
    display_name: str
    science_effect: str
    tagline: str
    visual_profile: ModifierVisualProfileV1
    frozen_protocol_required: bool = False
    sponsor_eligible: bool = True
    notes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.science_effect not in {
            PRESENTATION_ONLY,
            EXPLORATORY,
            EXPERIMENTAL,
        }:
            raise ValueError("invalid science_effect")
        if self.science_effect == EXPERIMENTAL and not self.frozen_protocol_required:
            raise ValueError(
                "experimental modifiers must require a frozen protocol"
            )

    def to_public_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["visual_profile"] = self.visual_profile.to_dict()
        data["notes"] = list(self.notes)
        return data


@dataclass(frozen=True)
class SponsorV1:
    sponsor_id: str
    display_name: str
    sponsor_type: str  # individual | company

    def __post_init__(self) -> None:
        if self.sponsor_type not in {"individual", "company"}:
            raise ValueError("sponsor_type must be individual or company")


@dataclass(frozen=True)
class ReferendumV1:
    referendum_id: str
    candidate_ids: tuple[str, str, str]
    sponsor: SponsorV1 | None = None
    sponsor_scope: str | None = None

    def __post_init__(self) -> None:
        if len(self.candidate_ids) != 3:
            raise ValueError("referendum must disclose exactly three candidates")
        if len(set(self.candidate_ids)) != 3:
            raise ValueError("referendum candidates must be unique")
        if self.sponsor_scope not in {
            None,
            "event",
            "one_candidate",
            "full_slate",
        }:
            raise ValueError("invalid sponsor_scope")


def canonical_modifier_catalog() -> tuple[ContainmentModifierV1, ...]:
    """Private/internal catalog.

    Public UI must never expose this complete list or its total size.
    """
    return (
        ContainmentModifierV1(
            modifier_id="MOD-MGMT-CONSULTANT",
            display_name="MANAGEMENT CONSULTANT",
            science_effect=PRESENTATION_ONLY,
            tagline="Synergy has entered the containment zone.",
            visual_profile=ModifierVisualProfileV1(
                hud_badge="MANAGEMENT CONSULTANT",
                room_theme="corporate_optimization",
                morty_accessory="consultant_tie",
                monitor_treatment="kpi_overload",
                signage=("SYNERGY TARGET", "VALUE CREATION"),
            ),
        ),
        ContainmentModifierV1(
            modifier_id="MOD-CONSTANT-ORGASM",
            display_name="CONSTANT ORGASM",
            science_effect=PRESENTATION_ONLY,
            tagline="The telemetry team regrets the naming committee.",
            visual_profile=ModifierVisualProfileV1(
                hud_badge="CONSTANT ORGASM",
                room_theme="aggressive_celebration",
                monitor_treatment="courtship_telemetry",
                signage=("STATE VARIABLE VISIBILITY ENHANCED",),
            ),
            notes=(
                "Presentation label only unless a separately frozen protocol exists.",
            ),
        ),
        ContainmentModifierV1(
            modifier_id="MOD-THE-AUDIT",
            display_name="THE AUDIT",
            science_effect=PRESENTATION_ONLY,
            tagline="Every object has a receipt.",
            visual_profile=ModifierVisualProfileV1(
                hud_badge="THE AUDIT",
                room_theme="compliance_inspection",
                monitor_treatment="receipts_manifest",
                signage=("PROVENANCE REVIEW IN PROGRESS",),
            ),
        ),
        ContainmentModifierV1(
            modifier_id="MOD-WELLNESS",
            display_name="MANDATORY WELLNESS INITIATIVE",
            science_effect=PRESENTATION_ONLY,
            tagline="Participation in wellness remains strongly encouraged.",
            visual_profile=ModifierVisualProfileV1(
                hud_badge="MANDATORY WELLNESS",
                room_theme="corporate_wellness",
                monitor_treatment="wellness_kiosk",
                signage=("YOUR WELLBEING IS A KPI",),
            ),
        ),
        ContainmentModifierV1(
            modifier_id="MOD-PIP",
            display_name="PERFORMANCE IMPROVEMENT PLAN",
            science_effect=PRESENTATION_ONLY,
            tagline="Management has identified opportunities.",
            visual_profile=ModifierVisualProfileV1(
                hud_badge="PIP ACTIVE",
                room_theme="performance_review",
                monitor_treatment="metric_escalation",
                signage=("IMPROVEMENT OPPORTUNITY IDENTIFIED",),
            ),
        ),
        ContainmentModifierV1(
            modifier_id="MOD-RTO",
            display_name="RETURN TO OFFICE",
            science_effect=PRESENTATION_ONLY,
            tagline="Collaboration requires fluorescent lighting.",
            visual_profile=ModifierVisualProfileV1(
                hud_badge="RTO",
                room_theme="cubicle_redeployment",
                monitor_treatment="attendance_dashboard",
                signage=("CULTURE HAPPENS IN PERSON",),
            ),
        ),
    )


def modifier_by_id(modifier_id: str) -> ContainmentModifierV1:
    for modifier in canonical_modifier_catalog():
        if modifier.modifier_id == modifier_id:
            return modifier
    raise KeyError(modifier_id)


def disclose_referendum(
    referendum_id: str,
    candidate_ids: Iterable[str],
    *,
    sponsor: SponsorV1 | None = None,
    sponsor_scope: str | None = None,
) -> ReferendumV1:
    candidate_ids = tuple(candidate_ids)
    if len(candidate_ids) != 3:
        raise ValueError("exactly three candidate IDs are required")

    for modifier_id in candidate_ids:
        modifier_by_id(modifier_id)

    return ReferendumV1(
        referendum_id=referendum_id,
        candidate_ids=(
            candidate_ids[0],
            candidate_ids[1],
            candidate_ids[2],
        ),
        sponsor=sponsor,
        sponsor_scope=sponsor_scope,
    )


def public_referendum_payload(referendum: ReferendumV1) -> dict[str, Any]:
    """Return only the three disclosed modifiers.

    Hidden catalog contents and total catalog size are intentionally absent.
    """
    return {
        "referendum_id": referendum.referendum_id,
        "candidates": [
            modifier_by_id(modifier_id).to_public_dict()
            for modifier_id in referendum.candidate_ids
        ],
        "sponsor": (
            asdict(referendum.sponsor) if referendum.sponsor is not None else None
        ),
        "sponsor_scope": referendum.sponsor_scope,
        "catalog_disclosure": "exactly_three_candidates_only",
    }


def emit_referendum_opened(
    storage: TelemetryStorage,
    *,
    run_id: str,
    referendum: ReferendumV1,
) -> TelemetryEventV1:
    event = TelemetryEventV1(
        event_type="referendum.opened",
        run_id=run_id,
        component="modifier",
        payload=public_referendum_payload(referendum),
        lore_surface="HUD",
    )
    storage.append(event)
    return event


def emit_modifier_unlocked(
    storage: TelemetryStorage,
    *,
    run_id: str,
    referendum: ReferendumV1,
    winner_id: str,
    vote_receipt_ref: str | None = None,
) -> TelemetryEventV1:
    if winner_id not in referendum.candidate_ids:
        raise ValueError("winner must be one of the disclosed candidates")

    modifier = modifier_by_id(winner_id)
    event = TelemetryEventV1(
        event_type="modifier.unlocked",
        run_id=run_id,
        component="modifier",
        payload={
            "referendum_id": referendum.referendum_id,
            "modifier": modifier.to_public_dict(),
            "status": UNLOCKED,
            "vote_receipt_ref": vote_receipt_ref,
            "persistence": "permanent_until_explicit_retirement",
            "losers_return_to": CLASSIFIED,
        },
        lore_surface="HUD",
    )
    storage.append(event)
    return event


def emit_modifier_activated(
    storage: TelemetryStorage,
    *,
    run_id: str,
    modifier_id: str,
    unlock_event_id: str,
    sponsor: SponsorV1 | None = None,
    protocol_ref: str | None = None,
) -> TelemetryEventV1:
    modifier = modifier_by_id(modifier_id)

    if modifier.science_effect == EXPERIMENTAL and not protocol_ref:
        raise ValueError("experimental modifier requires frozen protocol reference")

    event = TelemetryEventV1(
        event_type="modifier.activated",
        run_id=run_id,
        component="modifier",
        payload={
            "modifier": modifier.to_public_dict(),
            "status": ACTIVE,
            "unlock_event_id": unlock_event_id,
            "sponsor": asdict(sponsor) if sponsor is not None else None,
            "protocol_ref": protocol_ref,
            "main_page_surface": {
                "show": True,
                "fields": (
                    "display_name",
                    "science_effect",
                    "sponsor",
                ),
                "detail_location": "modifier_detail",
            },
            "science_boundary": (
                "sponsorship may fund presentation or pre-approved activation; "
                "it cannot alter scientific interpretation, Warden authority, "
                "result retention, or protocol outcomes"
            ),
        },
        lore_surface="HUD",
    )
    storage.append(event)
    return event
