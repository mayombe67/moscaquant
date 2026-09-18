from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from config.loader import load_toml
from oracle.credit_assignment import CREDIT_VERSION
from oracle.live_plasticity import LIVE_PLASTICITY_VERSION
from oracle.plasticity_state import PLASTICITY_STATE_VERSION


SC03_CONFIG_SCHEMA = "sc-03-plasticity-config/v1"


class PlasticityConfigError(ValueError):
    pass


@dataclass(frozen=True)
class PlasticityConfig:
    schema_version: str
    enabled: bool
    live_protocol: str
    credit_protocol: str
    state_protocol: str


def parse_plasticity_config(
    payload: dict,
) -> PlasticityConfig:
    if not isinstance(payload, dict):
        raise PlasticityConfigError(
            "SC-03 config must be a TOML table"
        )

    #
    # Missing activation flag fails closed.
    #
    enabled = payload.get(
        "enabled",
        False,
    )

    if not isinstance(enabled, bool):
        raise PlasticityConfigError(
            "enabled must be boolean"
        )

    schema_version = payload.get(
        "schema_version"
    )

    live_protocol = payload.get(
        "live_protocol"
    )

    credit_protocol = payload.get(
        "credit_protocol"
    )

    state_protocol = payload.get(
        "state_protocol"
    )

    #
    # Disabled config may be incomplete without
    # accidentally enabling plasticity.
    #
    if not enabled:
        return PlasticityConfig(
            schema_version=(
                schema_version
                or SC03_CONFIG_SCHEMA
            ),
            enabled=False,
            live_protocol=(
                live_protocol
                or LIVE_PLASTICITY_VERSION
            ),
            credit_protocol=(
                credit_protocol
                or CREDIT_VERSION
            ),
            state_protocol=(
                state_protocol
                or PLASTICITY_STATE_VERSION
            ),
        )

    #
    # Explicit activation requires exact protocol
    # identity. No silent version drift.
    #
    if schema_version != SC03_CONFIG_SCHEMA:
        raise PlasticityConfigError(
            "SC-03 config schema mismatch"
        )

    if live_protocol != LIVE_PLASTICITY_VERSION:
        raise PlasticityConfigError(
            "SC-03 live protocol mismatch"
        )

    if credit_protocol != CREDIT_VERSION:
        raise PlasticityConfigError(
            "SC-03 credit protocol mismatch"
        )

    if state_protocol != PLASTICITY_STATE_VERSION:
        raise PlasticityConfigError(
            "SC-03 state protocol mismatch"
        )

    return PlasticityConfig(
        schema_version=schema_version,
        enabled=True,
        live_protocol=live_protocol,
        credit_protocol=credit_protocol,
        state_protocol=state_protocol,
    )


def load_plasticity_config(
    path: Path,
) -> PlasticityConfig:
    if not path.exists():
        #
        # Missing file fails closed.
        #
        return parse_plasticity_config(
            {}
        )

    payload = load_toml(path)

    return parse_plasticity_config(
        payload
    )
