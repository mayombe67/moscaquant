from __future__ import annotations

from dataclasses import asdict, dataclass, replace
import hashlib
import json
import math


PLASTICITY_STATE_VERSION = "sc-03-plasticity-state/v1"

UPDATE_MULTIPLIER = 0.95
MIN_MULTIPLIER = 0.80
RECOVERY_SESSION_BLOCK = 5


class PlasticityStateError(ValueError):
    pass


@dataclass(frozen=True)
class PlasticityEdgeState:
    presynaptic: int
    postsynaptic: int

    baseline_artifact_id: str
    baseline_weight: float

    multiplier: float
    update_count: int

    first_update_session: str
    most_recent_update_session: str
    most_recent_evidence_reference: str

    inactive_completed_sessions: int


@dataclass(frozen=True)
class PlasticityState:
    schema_version: str
    edges: tuple[PlasticityEdgeState, ...]

    last_completed_session_id: str | None

    previous_state_hash: str | None
    state_hash: str


def _canonical_json(payload: object) -> bytes:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")


def _hash_payload(
    *,
    schema_version: str,
    edges: tuple[PlasticityEdgeState, ...],
    last_completed_session_id: str | None,
    previous_state_hash: str | None,
) -> str:
    payload = {
        "schema_version": schema_version,
        "edges": [
            asdict(edge)
            for edge in edges
        ],
        "last_completed_session_id": last_completed_session_id,
        "previous_state_hash": previous_state_hash,
    }

    return hashlib.sha256(
        _canonical_json(payload)
    ).hexdigest()


def _sorted_edges(
    edges: tuple[PlasticityEdgeState, ...],
) -> tuple[PlasticityEdgeState, ...]:
    return tuple(
        sorted(
            edges,
            key=lambda edge: (
                edge.presynaptic,
                edge.postsynaptic,
            ),
        )
    )


def build_empty_plasticity_state() -> PlasticityState:
    edges: tuple[PlasticityEdgeState, ...] = ()

    state_hash = _hash_payload(
        schema_version=PLASTICITY_STATE_VERSION,
        edges=edges,
        last_completed_session_id=None,
        previous_state_hash=None,
    )

    return PlasticityState(
        schema_version=PLASTICITY_STATE_VERSION,
        edges=edges,
        last_completed_session_id=None,
        previous_state_hash=None,
        state_hash=state_hash,
    )


def _transition(
    state: PlasticityState,
    *,
    edges: tuple[PlasticityEdgeState, ...],
    last_completed_session_id: str | None,
) -> PlasticityState:
    ordered = _sorted_edges(edges)

    new_hash = _hash_payload(
        schema_version=PLASTICITY_STATE_VERSION,
        edges=ordered,
        last_completed_session_id=last_completed_session_id,
        previous_state_hash=state.state_hash,
    )

    return PlasticityState(
        schema_version=PLASTICITY_STATE_VERSION,
        edges=ordered,
        last_completed_session_id=last_completed_session_id,
        previous_state_hash=state.state_hash,
        state_hash=new_hash,
    )


def get_edge_state(
    state: PlasticityState,
    *,
    presynaptic: int,
    postsynaptic: int,
) -> PlasticityEdgeState | None:
    for edge in state.edges:
        if (
            edge.presynaptic == presynaptic
            and edge.postsynaptic == postsynaptic
        ):
            return edge

    return None


def apply_plasticity_update(
    state: PlasticityState,
    *,
    presynaptic: int,
    postsynaptic: int,
    baseline_artifact_id: str,
    baseline_weight: float,
    session_id: str,
    evidence_reference: str,
) -> PlasticityState:
    if not baseline_artifact_id:
        raise PlasticityStateError(
            "baseline_artifact_id is required"
        )

    if not session_id:
        raise PlasticityStateError(
            "session_id is required"
        )

    if not evidence_reference:
        raise PlasticityStateError(
            "evidence_reference is required"
        )

    if not math.isfinite(baseline_weight):
        raise PlasticityStateError(
            "baseline_weight must be finite"
        )

    if baseline_weight == 0.0:
        raise PlasticityStateError(
            "baseline edge must exist"
        )

    existing = get_edge_state(
        state,
        presynaptic=presynaptic,
        postsynaptic=postsynaptic,
    )

    if existing is None:
        next_multiplier = max(
            MIN_MULTIPLIER,
            UPDATE_MULTIPLIER,
        )

        updated = PlasticityEdgeState(
            presynaptic=presynaptic,
            postsynaptic=postsynaptic,
            baseline_artifact_id=baseline_artifact_id,
            baseline_weight=float(baseline_weight),
            multiplier=next_multiplier,
            update_count=1,
            first_update_session=session_id,
            most_recent_update_session=session_id,
            most_recent_evidence_reference=evidence_reference,
            inactive_completed_sessions=0,
        )

        edges = state.edges + (updated,)

    else:
        if (
            existing.baseline_artifact_id
            != baseline_artifact_id
        ):
            raise PlasticityStateError(
                "baseline artifact changed for existing edge"
            )

        if not math.isclose(
            existing.baseline_weight,
            float(baseline_weight),
            rel_tol=0.0,
            abs_tol=0.0,
        ):
            raise PlasticityStateError(
                "baseline weight changed for existing edge"
            )

        next_multiplier = max(
            MIN_MULTIPLIER,
            existing.multiplier
            * UPDATE_MULTIPLIER,
        )

        updated = replace(
            existing,
            multiplier=next_multiplier,
            update_count=existing.update_count + 1,
            most_recent_update_session=session_id,
            most_recent_evidence_reference=evidence_reference,
            inactive_completed_sessions=0,
        )

        edges = tuple(
            updated
            if (
                edge.presynaptic == presynaptic
                and edge.postsynaptic == postsynaptic
            )
            else edge
            for edge in state.edges
        )

    return _transition(
        state,
        edges=edges,
        last_completed_session_id=(
            state.last_completed_session_id
        ),
    )


def complete_trading_session(
    state: PlasticityState,
    *,
    session_id: str,
) -> PlasticityState:
    if not session_id:
        raise PlasticityStateError(
            "session_id is required"
        )

    if (
        state.last_completed_session_id
        == session_id
    ):
        raise PlasticityStateError(
            "session already completed"
        )

    updated_edges: list[PlasticityEdgeState] = []

    for edge in state.edges:
        #
        # An edge updated during this session has
        # accumulated zero completed inactive sessions.
        #
        if edge.most_recent_update_session == session_id:
            updated_edges.append(
                replace(
                    edge,
                    inactive_completed_sessions=0,
                )
            )
            continue

        #
        # Fully recovered edges remain historical records
        # but no longer accumulate recovery time.
        #
        if math.isclose(
            edge.multiplier,
            1.0,
            rel_tol=0.0,
            abs_tol=1e-15,
        ):
            updated_edges.append(
                replace(
                    edge,
                    multiplier=1.0,
                    inactive_completed_sessions=0,
                )
            )
            continue

        inactive = (
            edge.inactive_completed_sessions
            + 1
        )

        multiplier = edge.multiplier

        if inactive >= RECOVERY_SESSION_BLOCK:
            multiplier = min(
                1.0,
                multiplier / UPDATE_MULTIPLIER,
            )
            inactive = 0

        updated_edges.append(
            replace(
                edge,
                multiplier=multiplier,
                inactive_completed_sessions=inactive,
            )
        )

    return _transition(
        state,
        edges=tuple(updated_edges),
        last_completed_session_id=session_id,
    )
