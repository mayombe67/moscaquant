from __future__ import annotations

from dataclasses import replace

from oracle.audit import sha256_hex
from oracle.d6_scar import (
    ScarPhase,
    ScarTissueState,
)
from oracle.models import OracleState
from oracle.protocol import validate_state
from oracle.reinforcement import ReinforcementCondition


SCAR_STATE_KEY = "sc-05-scar-tissue"


def scar_to_intervention_state(
    scar: ScarTissueState,
) -> tuple[tuple[str, object], ...]:
    return (
        ("schema_version", scar.schema_version),
        ("condition", scar.condition.value),
        ("origin_session_id", scar.origin_session_id),
        ("following_session_id", scar.following_session_id),
        ("activated_generation", scar.activated_generation),
        ("phase", scar.phase.value),
        ("active", scar.active),
    )


def scar_from_intervention_state(
    values: tuple[tuple[str, object], ...],
) -> ScarTissueState:
    payload = dict(values)

    return ScarTissueState(
        schema_version=str(
            payload["schema_version"]
        ),
        condition=ReinforcementCondition(
            str(payload["condition"])
        ),
        origin_session_id=str(
            payload["origin_session_id"]
        ),
        following_session_id=(
            None
            if payload["following_session_id"] is None
            else str(payload["following_session_id"])
        ),
        activated_generation=int(
            payload["activated_generation"]
        ),
        phase=ScarPhase(
            str(payload["phase"])
        ),
        active=bool(
            payload["active"]
        ),
    )


def with_scar_state(
    *,
    oracle_state: OracleState,
    scar: ScarTissueState,
) -> OracleState:
    intervention_state = (
        (
            SCAR_STATE_KEY,
            scar_to_intervention_state(scar),
        ),
    )

    provisional = replace(
        oracle_state,
        intervention_state=intervention_state,
        state_hash="0" * 64,
    )

    state_hash = sha256_hex({
        "schema_version": provisional.schema_version,
        "oracle_version": provisional.oracle_version,
        "generation": provisional.generation,
        "behavioral_state": provisional.behavioral_state,
        "adaptation_state": provisional.adaptation_state,
        "intervention_state": provisional.intervention_state,
        "history_digest": provisional.history_digest,
    })

    result = replace(
        provisional,
        state_hash=state_hash,
    )

    validate_state(result)
    return result


def get_scar_state(
    oracle_state: OracleState,
) -> ScarTissueState | None:
    values = dict(
        oracle_state.intervention_state
    )

    raw = values.get(
        SCAR_STATE_KEY
    )

    if raw is None:
        return None

    return scar_from_intervention_state(
        tuple(raw)
    )
