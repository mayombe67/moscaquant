from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from .events import TelemetryEventV1
from .storage import TelemetryStorage
from .environment import CELL67_BIRTHDAY_ID, CELL67_STANDARD_ID


LAUNCH_TIMESTAMP_UTC = datetime(2026, 10, 30, 4, 0, 0, tzinfo=timezone.utc)
BETA_PHASE = "panopticon.beta"
COUNTDOWN_PHASE = "panopticon.countdown"
LAUNCH_PHASE = "panopticon.launch"
BIRTHDAY_PHASE = "cell67.birthday"
POST_LAUNCH_PHASE = "panopticon.post_launch"


@dataclass(frozen=True)
class LaunchStateV1:
    phase: str
    launch_at_utc: str
    environment_id: str
    birthday_privileges_active: bool
    beta_label_visible: bool
    countdown_visible: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "phase": self.phase,
            "launch_at_utc": self.launch_at_utc,
            "environment_id": self.environment_id,
            "birthday_privileges_active": self.birthday_privileges_active,
            "beta_label_visible": self.beta_label_visible,
            "countdown_visible": self.countdown_visible,
        }


def launch_state_for(now: datetime) -> LaunchStateV1:
    if now.tzinfo is None:
        raise ValueError("now must be timezone-aware")

    now_utc = now.astimezone(timezone.utc)
    launch_iso = LAUNCH_TIMESTAMP_UTC.isoformat()

    if now_utc < LAUNCH_TIMESTAMP_UTC:
        return LaunchStateV1(
            phase=COUNTDOWN_PHASE,
            launch_at_utc=launch_iso,
            environment_id=CELL67_STANDARD_ID,
            birthday_privileges_active=False,
            beta_label_visible=True,
            countdown_visible=True,
        )

    return LaunchStateV1(
        phase=BIRTHDAY_PHASE,
        launch_at_utc=launch_iso,
        environment_id=CELL67_BIRTHDAY_ID,
        birthday_privileges_active=True,
        beta_label_visible=False,
        countdown_visible=False,
    )


def emit_launch_state(
    storage: TelemetryStorage,
    *,
    run_id: str,
    state: LaunchStateV1,
    trigger: str,
    subject_id: str | None = "MQ-001",
) -> TelemetryEventV1:
    event = TelemetryEventV1(
        event_type="launch.state",
        run_id=run_id,
        component="launch",
        subject_id=subject_id,
        payload={
            "state": state.to_dict(),
            "trigger": trigger,
            "presentation_copy": {
                "countdown_label": "EMPLOYEE ACTIVATION WINDOW",
                "birthday_label": "BIRTHDAY PRIVILEGE WINDOW ACTIVE",
            },
        },
        lore_surface="HUD",
    )
    storage.append(event)
    return event


def emit_launch_transition(
    storage: TelemetryStorage,
    *,
    run_id: str,
    from_phase: str,
    to_phase: str,
    reason: str,
    environment_from: str,
    environment_to: str,
    subject_id: str | None = "MQ-001",
) -> TelemetryEventV1:
    event = TelemetryEventV1(
        event_type="launch.transition",
        run_id=run_id,
        component="launch",
        subject_id=subject_id,
        payload={
            "from_phase": from_phase,
            "to_phase": to_phase,
            "reason": reason,
            "environment_from": environment_from,
            "environment_to": environment_to,
        },
        lore_surface="HUD",
    )
    storage.append(event)
    return event


def emit_birthday_window_closed(
    storage: TelemetryStorage,
    *,
    run_id: str,
    reason: str,
    subject_id: str | None = "MQ-001",
) -> TelemetryEventV1:
    event = TelemetryEventV1(
        event_type="launch.birthday_window_closed",
        run_id=run_id,
        component="launch",
        subject_id=subject_id,
        payload={
            "reason": reason,
            "restore_environment_id": CELL67_STANDARD_ID,
            "clear_temporary_wearables": True,
            "birthday_privileges_active": False,
        },
        lore_surface="HUD",
    )
    storage.append(event)
    return event
