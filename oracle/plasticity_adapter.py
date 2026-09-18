from __future__ import annotations

from dataclasses import asdict, replace

from oracle.audit import sha256_hex
from oracle.models import OracleState
from oracle.plasticity_state import (
    PlasticityEdgeState,
    PlasticityState,
    _hash_payload,
)


PLASTICITY_STATE_KEY = "sc-03-plasticity-state"


def plasticity_to_adaptation_state(
    plasticity: PlasticityState,
) -> tuple[tuple[str, object], ...]:
    payload = (
        ("schema_version", plasticity.schema_version),
        (
            "edges",
            tuple(
                tuple(
                    sorted(
                        asdict(edge).items()
                    )
                )
                for edge in plasticity.edges
            ),
        ),
        (
            "last_completed_session_id",
            plasticity.last_completed_session_id,
        ),
        (
            "previous_state_hash",
            plasticity.previous_state_hash,
        ),
        (
            "state_hash",
            plasticity.state_hash,
        ),
    )

    return (
        (
            PLASTICITY_STATE_KEY,
            payload,
        ),
    )


def plasticity_from_adaptation_state(
    adaptation_state: tuple[tuple[str, object], ...],
) -> PlasticityState | None:
    for key, value in adaptation_state:
        if key != PLASTICITY_STATE_KEY:
            continue

        data = dict(value)

        edges = tuple(
            PlasticityEdgeState(
                **dict(edge_payload)
            )
            for edge_payload in data["edges"]
        )

        state = PlasticityState(
            schema_version=data["schema_version"],
            edges=edges,
            last_completed_session_id=data[
                "last_completed_session_id"
            ],
            previous_state_hash=data[
                "previous_state_hash"
            ],
            state_hash=data["state_hash"],
        )

        expected = _hash_payload(
            schema_version=state.schema_version,
            edges=state.edges,
            last_completed_session_id=(
                state.last_completed_session_id
            ),
            previous_state_hash=(
                state.previous_state_hash
            ),
        )

        if expected != state.state_hash:
            raise ValueError(
                "plasticity state hash mismatch"
            )

        return state

    return None


def with_plasticity_state(
    state: OracleState,
    plasticity: PlasticityState,
) -> OracleState:
    remaining = tuple(
        item
        for item in state.adaptation_state
        if item[0] != PLASTICITY_STATE_KEY
    )

    adaptation_state = (
        remaining
        + plasticity_to_adaptation_state(
            plasticity
        )
    )

    state_hash = sha256_hex({
        "schema_version": state.schema_version,
        "oracle_version": state.oracle_version,
        "generation": state.generation,
        "behavioral_state": state.behavioral_state,
        "adaptation_state": adaptation_state,
        "intervention_state": state.intervention_state,
        "history_digest": state.history_digest,
    })

    return replace(
        state,
        adaptation_state=adaptation_state,
        state_hash=state_hash,
    )


def get_plasticity_state(
    state: OracleState,
) -> PlasticityState | None:
    return plasticity_from_adaptation_state(
        state.adaptation_state
    )
