from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from config.loader import load_toml
from oracle.credit_assignment import CREDIT_VERSION
from oracle.live_plasticity import LIVE_PLASTICITY_VERSION
from oracle.plasticity_state import PLASTICITY_STATE_VERSION


EXPERIMENT_CONFIG_SCHEMA = "mq7-adaptive-experiment-config/v1"

O1 = "O1_STATIC_ORACLE"
O2 = "O2_ADAPTIVE_ORACLE"


class AdaptiveExperimentConfigError(ValueError):
    pass


@dataclass(frozen=True)
class AdaptiveExperimentConfig:
    schema_version: str
    experiment_id: str
    condition: str
    sc03_config: str

    plasticity_enabled: bool
    live_protocol: str
    credit_protocol: str
    state_protocol: str

    matched_condition: str

    require_identical_seed: bool
    require_identical_market_input: bool
    require_identical_connectome: bool
    require_identical_sensory_config: bool
    require_identical_readout_config: bool
    require_identical_d6_selector: bool
    require_identical_warden_policy: bool

    financial_utility_claim: bool
    biological_learning_claim: bool


def _require_bool(
    table: dict,
    key: str,
) -> bool:
    value = table.get(key)

    if not isinstance(value, bool):
        raise AdaptiveExperimentConfigError(
            f"{key} must be boolean"
        )

    return value


def parse_adaptive_experiment_config(
    payload: dict,
) -> AdaptiveExperimentConfig:
    if not isinstance(payload, dict):
        raise AdaptiveExperimentConfigError(
            "experiment config must be a TOML table"
        )

    if (
        payload.get("schema_version")
        != EXPERIMENT_CONFIG_SCHEMA
    ):
        raise AdaptiveExperimentConfigError(
            "experiment config schema mismatch"
        )

    experiment_id = payload.get(
        "experiment_id"
    )

    condition = payload.get(
        "condition"
    )

    sc03_config = payload.get(
        "sc03_config"
    )

    if not experiment_id:
        raise AdaptiveExperimentConfigError(
            "experiment_id is required"
        )

    if condition not in {O1, O2}:
        raise AdaptiveExperimentConfigError(
            "invalid experiment condition"
        )

    if not sc03_config:
        raise AdaptiveExperimentConfigError(
            "sc03_config is required"
        )

    plasticity = payload.get(
        "plasticity"
    )

    controls = payload.get(
        "controls"
    )

    claims = payload.get(
        "claims"
    )

    if not isinstance(plasticity, dict):
        raise AdaptiveExperimentConfigError(
            "plasticity table is required"
        )

    if not isinstance(controls, dict):
        raise AdaptiveExperimentConfigError(
            "controls table is required"
        )

    if not isinstance(claims, dict):
        raise AdaptiveExperimentConfigError(
            "claims table is required"
        )

    enabled = _require_bool(
        plasticity,
        "enabled",
    )

    live_protocol = plasticity.get(
        "live_protocol"
    )

    credit_protocol = plasticity.get(
        "credit_protocol"
    )

    state_protocol = plasticity.get(
        "state_protocol"
    )

    if live_protocol != LIVE_PLASTICITY_VERSION:
        raise AdaptiveExperimentConfigError(
            "live protocol mismatch"
        )

    if credit_protocol != CREDIT_VERSION:
        raise AdaptiveExperimentConfigError(
            "credit protocol mismatch"
        )

    if state_protocol != PLASTICITY_STATE_VERSION:
        raise AdaptiveExperimentConfigError(
            "state protocol mismatch"
        )

    #
    # Experimental condition determines whether
    # plasticity is permitted.
    #
    if condition == O1 and enabled:
        raise AdaptiveExperimentConfigError(
            "O1 must keep plasticity disabled"
        )

    if condition == O2 and not enabled:
        raise AdaptiveExperimentConfigError(
            "O2 must enable plasticity"
        )

    matched_condition = controls.get(
        "matched_condition"
    )

    expected_match = (
        O2
        if condition == O1
        else O1
    )

    if matched_condition != expected_match:
        raise AdaptiveExperimentConfigError(
            "matched condition mismatch"
        )

    control_fields = (
        "require_identical_seed",
        "require_identical_market_input",
        "require_identical_connectome",
        "require_identical_sensory_config",
        "require_identical_readout_config",
        "require_identical_d6_selector",
        "require_identical_warden_policy",
    )

    control_values = {
        key: _require_bool(
            controls,
            key,
        )
        for key in control_fields
    }

    if not all(
        control_values.values()
    ):
        raise AdaptiveExperimentConfigError(
            "all matched controls must be required"
        )

    financial_utility = _require_bool(
        claims,
        "financial_utility",
    )

    biological_learning = _require_bool(
        claims,
        "biological_learning",
    )

    if financial_utility:
        raise AdaptiveExperimentConfigError(
            "financial utility claim must remain false"
        )

    if biological_learning:
        raise AdaptiveExperimentConfigError(
            "biological learning claim must remain false"
        )

    return AdaptiveExperimentConfig(
        schema_version=EXPERIMENT_CONFIG_SCHEMA,
        experiment_id=experiment_id,
        condition=condition,
        sc03_config=sc03_config,
        plasticity_enabled=enabled,
        live_protocol=live_protocol,
        credit_protocol=credit_protocol,
        state_protocol=state_protocol,
        matched_condition=matched_condition,
        financial_utility_claim=financial_utility,
        biological_learning_claim=biological_learning,
        **control_values,
    )


def load_adaptive_experiment_config(
    path: Path,
) -> AdaptiveExperimentConfig:
    if not path.exists():
        raise AdaptiveExperimentConfigError(
            "experiment config missing"
        )

    return parse_adaptive_experiment_config(
        load_toml(path)
    )


def validate_matched_pair(
    first: AdaptiveExperimentConfig,
    second: AdaptiveExperimentConfig,
) -> None:
    conditions = {
        first.condition,
        second.condition,
    }

    if conditions != {O1, O2}:
        raise AdaptiveExperimentConfigError(
            "matched pair must contain O1 and O2"
        )

    if (
        first.matched_condition
        != second.condition
        or second.matched_condition
        != first.condition
    ):
        raise AdaptiveExperimentConfigError(
            "matched pair references are inconsistent"
        )

    frozen_fields = (
        "live_protocol",
        "credit_protocol",
        "state_protocol",
        "require_identical_seed",
        "require_identical_market_input",
        "require_identical_connectome",
        "require_identical_sensory_config",
        "require_identical_readout_config",
        "require_identical_d6_selector",
        "require_identical_warden_policy",
    )

    for field in frozen_fields:
        if (
            getattr(first, field)
            != getattr(second, field)
        ):
            raise AdaptiveExperimentConfigError(
                f"matched pair differs on {field}"
            )
