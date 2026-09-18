from __future__ import annotations

from pathlib import Path

import pytest

from oracle.credit_assignment import CREDIT_VERSION
from oracle.live_plasticity import LIVE_PLASTICITY_VERSION
from oracle.plasticity_config import (
    SC03_CONFIG_SCHEMA,
    PlasticityConfigError,
    load_plasticity_config,
    parse_plasticity_config,
)
from oracle.plasticity_state import PLASTICITY_STATE_VERSION


def valid_enabled_payload():
    return {
        "schema_version": SC03_CONFIG_SCHEMA,
        "enabled": True,
        "live_protocol": LIVE_PLASTICITY_VERSION,
        "credit_protocol": CREDIT_VERSION,
        "state_protocol": PLASTICITY_STATE_VERSION,
    }


def test_missing_enabled_flag_fails_closed():
    config = parse_plasticity_config(
        {}
    )

    assert config.enabled is False


def test_explicit_false_remains_disabled():
    config = parse_plasticity_config({
        "enabled": False,
    })

    assert config.enabled is False


def test_missing_file_fails_closed(
    tmp_path: Path,
):
    config = load_plasticity_config(
        tmp_path / "missing.toml"
    )

    assert config.enabled is False


def test_explicit_true_with_exact_versions_enables():
    config = parse_plasticity_config(
        valid_enabled_payload()
    )

    assert config.enabled is True


def test_malformed_enabled_value_is_rejected():
    payload = valid_enabled_payload()
    payload["enabled"] = "true"

    with pytest.raises(
        PlasticityConfigError,
        match="enabled must be boolean",
    ):
        parse_plasticity_config(
            payload
        )


def test_live_protocol_mismatch_is_rejected():
    payload = valid_enabled_payload()
    payload["live_protocol"] = "wrong"

    with pytest.raises(
        PlasticityConfigError,
        match="live protocol mismatch",
    ):
        parse_plasticity_config(
            payload
        )


def test_credit_protocol_mismatch_is_rejected():
    payload = valid_enabled_payload()
    payload["credit_protocol"] = "wrong"

    with pytest.raises(
        PlasticityConfigError,
        match="credit protocol mismatch",
    ):
        parse_plasticity_config(
            payload
        )


def test_state_protocol_mismatch_is_rejected():
    payload = valid_enabled_payload()
    payload["state_protocol"] = "wrong"

    with pytest.raises(
        PlasticityConfigError,
        match="state protocol mismatch",
    ):
        parse_plasticity_config(
            payload
        )


def test_schema_mismatch_is_rejected():
    payload = valid_enabled_payload()
    payload["schema_version"] = "wrong"

    with pytest.raises(
        PlasticityConfigError,
        match="schema mismatch",
    ):
        parse_plasticity_config(
            payload
        )
