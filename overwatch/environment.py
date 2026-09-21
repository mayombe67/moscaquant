from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable

from .events import TelemetryEventV1
from .storage import TelemetryStorage


CELL67_STANDARD_ID = "CELL-67.v1"
CELL67_BIRTHDAY_ID = "CELL-67.BIRTHDAY.v1"


@dataclass(frozen=True)
class PropConfigV1:
    prop_id: str
    kind: str
    interactive: bool
    wearable: bool = False
    consumable: bool = False
    attractive: bool = False
    persistent_after_session: bool = False
    presentation_only: bool = False
    metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class EnvironmentConfigV1:
    environment_id: str
    base_environment_id: str
    tether_enabled: bool
    room_roaming_enabled: bool
    temporary: bool
    exploratory_condition: bool
    props: tuple[PropConfigV1, ...]
    restoration_environment_id: str | None = None
    notes: tuple[str, ...] = ()

    def prop(self, prop_id: str) -> PropConfigV1:
        for prop in self.props:
            if prop.prop_id == prop_id:
                return prop
        raise KeyError(prop_id)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["props"] = [p.to_dict() for p in self.props]
        data["notes"] = list(self.notes)
        return data


def _ensure_unique_prop_ids(props: Iterable[PropConfigV1]) -> tuple[PropConfigV1, ...]:
    props = tuple(props)
    ids = [p.prop_id for p in props]
    if len(ids) != len(set(ids)):
        raise ValueError("prop_id values must be unique")
    return props


def cell67_standard() -> EnvironmentConfigV1:
    props = _ensure_unique_prop_ids((
        PropConfigV1(
            prop_id="desk.primary",
            kind="trading_desk",
            interactive=False,
        ),
        PropConfigV1(
            prop_id="monitor.primary",
            kind="science_trading_monitor",
            interactive=False,
            presentation_only=True,
        ),
        PropConfigV1(
            prop_id="monitor.meme",
            kind="meme_monitor",
            interactive=False,
            presentation_only=True,
        ),
    ))

    return EnvironmentConfigV1(
        environment_id=CELL67_STANDARD_ID,
        base_environment_id=CELL67_STANDARD_ID,
        tether_enabled=True,
        room_roaming_enabled=False,
        temporary=False,
        exploratory_condition=False,
        props=props,
        notes=(
            "Canonical containment environment.",
            "Presentation systems must not silently alter experimental state.",
        ),
    )


def cell67_birthday() -> EnvironmentConfigV1:
    props = _ensure_unique_prop_ids((
        PropConfigV1(
            prop_id="desk.primary",
            kind="trading_desk",
            interactive=False,
        ),
        PropConfigV1(
            prop_id="monitor.primary",
            kind="science_trading_monitor",
            interactive=False,
            presentation_only=True,
        ),
        PropConfigV1(
            prop_id="monitor.meme",
            kind="birthday_monitor",
            interactive=False,
            presentation_only=True,
            metadata={"theme": "painfully_wholesome_corporate_birthday"},
        ),
        PropConfigV1(
            prop_id="birthday.cake",
            kind="cake",
            interactive=True,
            consumable=False,
            attractive=True,
            metadata={
                "display_name": "COMPLIMENTARY CELEBRATION RESOURCE",
                "consumption_privileges": "unavailable",
                "cake_is_a_lie": True,
            },
        ),
        PropConfigV1(
            prop_id="birthday.party_hat",
            kind="party_hat",
            interactive=True,
            wearable=True,
            persistent_after_session=False,
            metadata={
                "wear_rule": "only_after_actual_interaction",
                "auto_equip": False,
            },
        ),
        PropConfigV1(
            prop_id="birthday.balloon.cluster_a",
            kind="balloon_cluster",
            interactive=True,
            metadata={"placement": "room"},
        ),
        PropConfigV1(
            prop_id="birthday.banner",
            kind="corporate_banner",
            interactive=False,
            presentation_only=True,
            metadata={"text": "YOUR CONTRIBUTION IS VALUED"},
        ),
        PropConfigV1(
            prop_id="birthday.management_card",
            kind="management_card",
            interactive=True,
            metadata={"sender": "Management"},
        ),
        PropConfigV1(
            prop_id="birthday.appreciation_placard",
            kind="corporate_placard",
            interactive=False,
            presentation_only=True,
            metadata={"text": "BIRTHDAY PRIVILEGE WINDOW ACTIVE"},
        ),
    ))

    return EnvironmentConfigV1(
        environment_id=CELL67_BIRTHDAY_ID,
        base_environment_id=CELL67_STANDARD_ID,
        tether_enabled=False,
        room_roaming_enabled=True,
        temporary=True,
        exploratory_condition=True,
        restoration_environment_id=CELL67_STANDARD_ID,
        props=props,
        notes=(
            "Launch-day special environment.",
            "Tether removal is explicit environment configuration, not presentation.",
            "Birthday condition is exploratory and excluded from baseline inference unless a frozen protocol says otherwise.",
            "Corporate-dystopian visual energy must use original art/assets rather than copied third-party trade dress.",
        ),
    )


def emit_environment_activated(
    storage: TelemetryStorage,
    *,
    run_id: str,
    environment: EnvironmentConfigV1,
    activation_reason: str,
    experiment_id: str | None = None,
    subject_id: str | None = "MQ-001",
) -> TelemetryEventV1:
    event = TelemetryEventV1(
        event_type="environment.activated",
        run_id=run_id,
        component="environment",
        experiment_id=experiment_id,
        subject_id=subject_id,
        payload={
            "environment": environment.to_dict(),
            "activation_reason": activation_reason,
        },
        lore_surface="HUD",
    )
    storage.append(event)
    return event


def emit_prop_interaction(
    storage: TelemetryStorage,
    *,
    run_id: str,
    environment: EnvironmentConfigV1,
    prop_id: str,
    interaction: str,
    source_motor_event_id: str | None = None,
    distance_m: float | None = None,
    experiment_id: str | None = None,
    subject_id: str | None = "MQ-001",
) -> TelemetryEventV1:
    prop = environment.prop(prop_id)
    if not prop.interactive:
        raise ValueError(f"{prop_id} is not interactive")

    denied_reason = None
    if interaction == "consume" and not prop.consumable:
        denied_reason = "prop_not_consumable"

    payload = {
        "environment_id": environment.environment_id,
        "prop_id": prop_id,
        "prop_kind": prop.kind,
        "interaction": interaction,
        "source_motor_event_id": source_motor_event_id,
        "distance_m": distance_m,
        "allowed": denied_reason is None,
        "denied_reason": denied_reason,
    }

    event = TelemetryEventV1(
        event_type="environment.prop_interaction",
        run_id=run_id,
        component="environment",
        experiment_id=experiment_id,
        subject_id=subject_id,
        payload=payload,
        lore_surface="HUD",
    )
    storage.append(event)
    return event


def emit_wearable_state(
    storage: TelemetryStorage,
    *,
    run_id: str,
    environment: EnvironmentConfigV1,
    prop_id: str,
    equipped: bool,
    interaction_event_id: str | None,
    experiment_id: str | None = None,
    subject_id: str | None = "MQ-001",
) -> TelemetryEventV1:
    prop = environment.prop(prop_id)
    if not prop.wearable:
        raise ValueError(f"{prop_id} is not wearable")
    if equipped and not interaction_event_id:
        raise ValueError(
            "wearable may only be equipped from an actual interaction event"
        )

    event = TelemetryEventV1(
        event_type="environment.wearable_state",
        run_id=run_id,
        component="environment",
        experiment_id=experiment_id,
        subject_id=subject_id,
        payload={
            "environment_id": environment.environment_id,
            "prop_id": prop_id,
            "equipped": bool(equipped),
            "interaction_event_id": interaction_event_id,
            "temporary": not prop.persistent_after_session,
        },
        lore_surface="HUD",
    )
    storage.append(event)
    return event


def emit_environment_restored(
    storage: TelemetryStorage,
    *,
    run_id: str,
    from_environment: EnvironmentConfigV1,
    reason: str,
    experiment_id: str | None = None,
    subject_id: str | None = "MQ-001",
) -> TelemetryEventV1:
    if not from_environment.restoration_environment_id:
        raise ValueError("environment has no restoration target")

    event = TelemetryEventV1(
        event_type="environment.restored",
        run_id=run_id,
        component="environment",
        experiment_id=experiment_id,
        subject_id=subject_id,
        payload={
            "from_environment_id": from_environment.environment_id,
            "to_environment_id": from_environment.restoration_environment_id,
            "reason": reason,
            "clear_temporary_wearables": True,
        },
        lore_surface="HUD",
    )
    storage.append(event)
    return event
