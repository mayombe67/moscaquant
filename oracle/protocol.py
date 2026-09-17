from __future__ import annotations

import re

from oracle.models import OracleInput, OracleProposal, OracleState


SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class OracleProtocolError(ValueError):
    pass


def _require_nonempty(name: str, value: str) -> None:
    if not value or not value.strip():
        raise OracleProtocolError(f"{name} must not be empty")


def _require_sha256(name: str, value: str) -> None:
    if not SHA256_RE.fullmatch(value):
        raise OracleProtocolError(
            f"{name} must be a lowercase SHA-256 hex digest"
        )


def validate_input(value: OracleInput) -> None:
    _require_nonempty("schema_version", value.schema_version)
    _require_nonempty("experiment_id", value.experiment_id)
    _require_nonempty("session_id", value.session_id)
    _require_nonempty("frame_id", value.frame_id)
    _require_nonempty("timestamp", value.timestamp)
    _require_nonempty("mq001_version", value.mq001_version)

    _require_sha256(
        "scientific_config_hash",
        value.scientific_config_hash,
    )

    if value.prior_oracle_state_hash is not None:
        _require_sha256(
            "prior_oracle_state_hash",
            value.prior_oracle_state_hash,
        )

    for ref in value.evidence_refs:
        _require_nonempty("evidence_ref", ref)


def validate_state(value: OracleState) -> None:
    _require_nonempty("schema_version", value.schema_version)
    _require_nonempty("oracle_version", value.oracle_version)

    if value.generation < 0:
        raise OracleProtocolError(
            "generation must be non-negative"
        )

    _require_sha256(
        "history_digest",
        value.history_digest,
    )

    _require_sha256(
        "state_hash",
        value.state_hash,
    )


def validate_proposal(value: OracleProposal) -> None:
    _require_nonempty("schema_version", value.schema_version)
    _require_nonempty("experiment_id", value.experiment_id)
    _require_nonempty("session_id", value.session_id)
    _require_nonempty("oracle_version", value.oracle_version)
    _require_nonempty("proposal_id", value.proposal_id)
    _require_nonempty("proposal_type", value.proposal_type)

    if not 0.0 <= value.confidence <= 1.0:
        raise OracleProtocolError(
            "confidence must be between 0.0 and 1.0"
        )

    _require_sha256(
        "oracle_state_hash",
        value.oracle_state_hash,
    )

    if not value.abstain and not value.evidence_refs:
        raise OracleProtocolError(
            "non-abstaining proposals require evidence"
        )

    forbidden_fields = {
        "authorized",
        "authority",
        "execute",
        "execution",
        "broker",
        "credentials",
        "wallet",
        "signing_key",
    }

    for key, _ in value.proposal_payload:
        if key.lower() in forbidden_fields:
            raise OracleProtocolError(
                f"forbidden proposal field: {key}"
            )
