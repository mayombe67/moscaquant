from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import random

from oracle.models import OracleInput, OracleProposal, OracleState
from oracle.state import transition


class OracleControlError(ValueError):
    pass


class OracleControl(StrEnum):
    O0_NO_ORACLE = "O0_NO_ORACLE"
    O1_STATIC_ORACLE = "O1_STATIC_ORACLE"
    O2_ADAPTIVE_ORACLE = "O2_ADAPTIVE_ORACLE"
    O3_SHUFFLED_ORACLE = "O3_SHUFFLED_ORACLE"


@dataclass(frozen=True)
class ControlProvenance:
    control: OracleControl
    shuffle_algorithm: str | None = None
    shuffle_seed: int | None = None
    original_evidence_refs: tuple[str, ...] = ()
    transformed_evidence_refs: tuple[str, ...] = ()


@dataclass(frozen=True)
class ControlResult:
    control: OracleControl
    oracle_input: OracleInput
    state: OracleState
    proposal: OracleProposal | None
    provenance: ControlProvenance


def parse_control(value: str | OracleControl) -> OracleControl:
    if isinstance(value, OracleControl):
        return value

    try:
        return OracleControl(value)
    except ValueError as exc:
        raise OracleControlError(
            f"unknown Oracle control condition: {value}"
        ) from exc


def _shuffle_evidence(
    refs: tuple[str, ...],
    *,
    seed: int,
) -> tuple[str, ...]:
    items = list(refs)

    rng = random.Random(seed)
    rng.shuffle(items)

    return tuple(items)


def apply_control(
    *,
    control: str | OracleControl,
    oracle_input: OracleInput,
    prior_state: OracleState,
    shuffle_seed: int | None = None,
) -> ControlResult:
    selected = parse_control(control)

    if selected is OracleControl.O0_NO_ORACLE:
        provenance = ControlProvenance(
            control=selected,
            original_evidence_refs=oracle_input.evidence_refs,
            transformed_evidence_refs=oracle_input.evidence_refs,
        )

        return ControlResult(
            control=selected,
            oracle_input=oracle_input,
            state=prior_state,
            proposal=None,
            provenance=provenance,
        )

    if selected in {
        OracleControl.O1_STATIC_ORACLE,
        OracleControl.O2_ADAPTIVE_ORACLE,
    }:
        next_state, proposal = transition(
            oracle_input=oracle_input,
            prior_state=prior_state,
        )

        provenance = ControlProvenance(
            control=selected,
            original_evidence_refs=oracle_input.evidence_refs,
            transformed_evidence_refs=oracle_input.evidence_refs,
        )

        return ControlResult(
            control=selected,
            oracle_input=oracle_input,
            state=next_state,
            proposal=proposal,
            provenance=provenance,
        )

    if selected is OracleControl.O3_SHUFFLED_ORACLE:
        if shuffle_seed is None:
            raise OracleControlError(
                "O3_SHUFFLED_ORACLE requires an explicit shuffle seed"
            )

        shuffled = _shuffle_evidence(
            oracle_input.evidence_refs,
            seed=shuffle_seed,
        )

        transformed = OracleInput(
            schema_version=oracle_input.schema_version,
            experiment_id=oracle_input.experiment_id,
            session_id=oracle_input.session_id,
            frame_id=oracle_input.frame_id,
            timestamp=oracle_input.timestamp,
            mq001_version=oracle_input.mq001_version,
            scientific_config_hash=oracle_input.scientific_config_hash,
            evidence_refs=shuffled,
            derived_features=oracle_input.derived_features,
            prior_oracle_state_hash=oracle_input.prior_oracle_state_hash,
            warden_history=oracle_input.warden_history,
        )

        next_state, proposal = transition(
            oracle_input=transformed,
            prior_state=prior_state,
        )

        provenance = ControlProvenance(
            control=selected,
            shuffle_algorithm="python-random/v1",
            shuffle_seed=shuffle_seed,
            original_evidence_refs=oracle_input.evidence_refs,
            transformed_evidence_refs=shuffled,
        )

        return ControlResult(
            control=selected,
            oracle_input=transformed,
            state=next_state,
            proposal=proposal,
            provenance=provenance,
        )

    raise OracleControlError(
        f"unsupported Oracle control: {selected}"
    )
