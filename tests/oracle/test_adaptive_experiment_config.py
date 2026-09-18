from __future__ import annotations

from pathlib import Path

import pytest

from oracle.adaptive_experiment_config import (
    AdaptiveExperimentConfigError,
    load_adaptive_experiment_config,
    validate_matched_pair,
)


ROOT = Path(__file__).resolve().parents[2]

O1_PATH = (
    ROOT
    / "config"
    / "experiments"
    / "mq7-o1-static-v1.toml"
)

O2_PATH = (
    ROOT
    / "config"
    / "experiments"
    / "mq7-o2-adaptive-v1.toml"
)


def test_checked_in_o1_is_valid():
    config = load_adaptive_experiment_config(
        O1_PATH
    )

    assert config.condition == "O1_STATIC_ORACLE"
    assert config.plasticity_enabled is False


def test_checked_in_o2_is_valid():
    config = load_adaptive_experiment_config(
        O2_PATH
    )

    assert config.condition == "O2_ADAPTIVE_ORACLE"
    assert config.plasticity_enabled is True


def test_checked_in_pair_is_valid():
    o1 = load_adaptive_experiment_config(
        O1_PATH
    )

    o2 = load_adaptive_experiment_config(
        O2_PATH
    )

    validate_matched_pair(
        o1,
        o2,
    )


def test_o1_cannot_enable_plasticity(
    tmp_path: Path,
):
    text = O1_PATH.read_text(
        encoding="utf-8"
    )

    text = text.replace(
        "enabled = false",
        "enabled = true",
    )

    path = tmp_path / "o1.toml"

    path.write_text(
        text,
        encoding="utf-8",
    )

    with pytest.raises(
        AdaptiveExperimentConfigError,
        match="O1 must keep plasticity disabled",
    ):
        load_adaptive_experiment_config(
            path
        )


def test_o2_cannot_disable_plasticity(
    tmp_path: Path,
):
    text = O2_PATH.read_text(
        encoding="utf-8"
    )

    text = text.replace(
        "enabled = true",
        "enabled = false",
    )

    path = tmp_path / "o2.toml"

    path.write_text(
        text,
        encoding="utf-8",
    )

    with pytest.raises(
        AdaptiveExperimentConfigError,
        match="O2 must enable plasticity",
    ):
        load_adaptive_experiment_config(
            path
        )


def test_protocol_drift_is_rejected(
    tmp_path: Path,
):
    text = O2_PATH.read_text(
        encoding="utf-8"
    )

    text = text.replace(
        'credit_protocol = "mq7-credit-assignment/v1"',
        'credit_protocol = "future-version"',
    )

    path = tmp_path / "o2.toml"

    path.write_text(
        text,
        encoding="utf-8",
    )

    with pytest.raises(
        AdaptiveExperimentConfigError,
        match="credit protocol mismatch",
    ):
        load_adaptive_experiment_config(
            path
        )


def test_financial_utility_claim_cannot_be_enabled(
    tmp_path: Path,
):
    text = O2_PATH.read_text(
        encoding="utf-8"
    )

    text = text.replace(
        "financial_utility = false",
        "financial_utility = true",
    )

    path = tmp_path / "o2.toml"

    path.write_text(
        text,
        encoding="utf-8",
    )

    with pytest.raises(
        AdaptiveExperimentConfigError,
        match="financial utility claim",
    ):
        load_adaptive_experiment_config(
            path
        )
