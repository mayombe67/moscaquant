from __future__ import annotations

from dataclasses import dataclass

from oracle.credit_assignment import CreditResult
from oracle.models import OracleState
from oracle.plasticity_adapter import (
    get_plasticity_state,
    with_plasticity_state,
)
from oracle.plasticity_state import (
    PlasticityState,
    apply_plasticity_update,
    build_empty_plasticity_state,
)
from oracle.reinforcement import (
    ReinforcementCondition,
    ReinforcementResult,
)


LIVE_PLASTICITY_VERSION = "sc-03-live-plasticity/v1"


@dataclass(frozen=True)
class LivePlasticityResult:
    status: str
    oracle_state: OracleState
    plasticity_state: PlasticityState | None
    presynaptic: int | None
    postsynaptic: int | None


def apply_live_bad_synapse(
    *,
    oracle_state: OracleState,
    d6_result: ReinforcementResult,
    credit_result: CreditResult,
    baseline_artifact_id: str,
    session_id: str,
    evidence_reference: str,
) -> LivePlasticityResult:
    condition = d6_result.selection.condition

    #
    # Not SC-03: this layer has nothing to do.
    #
    if condition is not ReinforcementCondition.SC_03_BAD_SYNAPSE:
        return LivePlasticityResult(
            status="NOT_SC03",
            oracle_state=oracle_state,
            plasticity_state=get_plasticity_state(
                oracle_state
            ),
            presynaptic=None,
            postsynaptic=None,
        )

    #
    # Selector already decided whether SC-03 is currently
    # scientifically applicable.
    #
    if not d6_result.applicable:
        return LivePlasticityResult(
            status="NOT_APPLICABLE",
            oracle_state=oracle_state,
            plasticity_state=get_plasticity_state(
                oracle_state
            ),
            presynaptic=None,
            postsynaptic=None,
        )

    #
    # Credit ambiguity blocks adaptation.
    #
    if credit_result.status == "AMBIGUOUS_CREDIT":
        return LivePlasticityResult(
            status="NO_UPDATE_AMBIGUOUS_CREDIT",
            oracle_state=oracle_state,
            plasticity_state=get_plasticity_state(
                oracle_state
            ),
            presynaptic=None,
            postsynaptic=None,
        )

    #
    # No recent causal evidence also blocks adaptation.
    #
    if credit_result.status == "NO_ELIGIBLE_PATHWAY":
        return LivePlasticityResult(
            status="NO_UPDATE_NO_ELIGIBLE_PATHWAY",
            oracle_state=oracle_state,
            plasticity_state=get_plasticity_state(
                oracle_state
            ),
            presynaptic=None,
            postsynaptic=None,
        )

    if credit_result.status != "ELIGIBLE":
        raise ValueError(
            f"unexpected credit status: "
            f"{credit_result.status}"
        )

    if len(credit_result.leaders) != 1:
        raise ValueError(
            "ELIGIBLE credit result must have "
            "exactly one leader"
        )

    leader = credit_result.leaders[0]

    plasticity = get_plasticity_state(
        oracle_state
    )

    if plasticity is None:
        plasticity = build_empty_plasticity_state()

    updated_plasticity = apply_plasticity_update(
        plasticity,
        presynaptic=leader.presynaptic,
        postsynaptic=leader.postsynaptic,
        baseline_artifact_id=baseline_artifact_id,
        baseline_weight=leader.weight,
        session_id=session_id,
        evidence_reference=evidence_reference,
    )

    updated_oracle = with_plasticity_state(
        oracle_state,
        updated_plasticity,
    )

    return LivePlasticityResult(
        status="UPDATED",
        oracle_state=updated_oracle,
        plasticity_state=updated_plasticity,
        presynaptic=leader.presynaptic,
        postsynaptic=leader.postsynaptic,
    )
