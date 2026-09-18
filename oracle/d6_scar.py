from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from oracle.reinforcement import ReinforcementCondition


SCAR_VERSION = "sc-05-scar-tissue/v1"


class ScarError(ValueError):
    pass


class ScarPhase(StrEnum):
    CURRENT_SESSION = "CURRENT_SESSION"
    FOLLOWING_SESSION = "FOLLOWING_SESSION"
    RECOVERED = "RECOVERED"


@dataclass(frozen=True)
class ScarTissueState:
    schema_version: str
    condition: ReinforcementCondition
    origin_session_id: str
    following_session_id: str | None
    activated_generation: int
    phase: ScarPhase
    active: bool


def build_scar(
    *,
    session_id: str,
    current_generation: int,
) -> ScarTissueState:
    if not session_id:
        raise ScarError(
            "session_id must be non-empty"
        )

    if current_generation < 0:
        raise ScarError(
            "current_generation must be >= 0"
        )

    return ScarTissueState(
        schema_version=SCAR_VERSION,
        condition=ReinforcementCondition.SC_05_SCAR_TISSUE,
        origin_session_id=session_id,
        following_session_id=None,
        activated_generation=current_generation,
        phase=ScarPhase.CURRENT_SESSION,
        active=True,
    )


def advance_scar(
    *,
    state: ScarTissueState,
    session_id: str,
) -> ScarTissueState:
    if not session_id:
        raise ScarError(
            "session_id must be non-empty"
        )

    if state.phase is ScarPhase.RECOVERED:
        return state

    if state.phase is ScarPhase.CURRENT_SESSION:
        if session_id == state.origin_session_id:
            return state

        return ScarTissueState(
            schema_version=state.schema_version,
            condition=state.condition,
            origin_session_id=state.origin_session_id,
            following_session_id=session_id,
            activated_generation=state.activated_generation,
            phase=ScarPhase.FOLLOWING_SESSION,
            active=True,
        )

    if state.phase is ScarPhase.FOLLOWING_SESSION:
        if session_id == state.following_session_id:
            return state

        return ScarTissueState(
            schema_version=state.schema_version,
            condition=state.condition,
            origin_session_id=state.origin_session_id,
            following_session_id=state.following_session_id,
            activated_generation=state.activated_generation,
            phase=ScarPhase.RECOVERED,
            active=False,
        )

    raise ScarError(
        f"unsupported scar phase: {state.phase}"
    )


def scar_can_stack(
    state: ScarTissueState,
) -> bool:
    return not state.active
