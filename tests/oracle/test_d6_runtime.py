from __future__ import annotations

from pathlib import Path

from oracle.d6_runtime import (
    select_d6_from_scientific_config,
)


def write_config(
    path: Path,
    *,
    enabled: bool,
):
    path.write_text(
        "\n".join([
            'schema_version = "sc-03-plasticity-config/v1"',
            f"enabled = {'true' if enabled else 'false'}",
            'live_protocol = "sc-03-live-plasticity/v1"',
            'credit_protocol = "mq7-credit-assignment/v1"',
            'state_protocol = "sc-03-plasticity-state/v1"',
            "",
        ]),
        encoding="utf-8",
    )


def find_sc03_seed(
    *,
    config_path: Path,
):
    for seed in range(10000):
        runtime = select_d6_from_scientific_config(
            seed=seed,
            experiment_id="mq7-runtime",
            session_id="session-A",
            config_path=config_path,
        )

        if (
            runtime.result.selection.condition.value
            == "SC-03"
        ):
            return runtime

    raise AssertionError(
        "could not select SC-03"
    )


def test_missing_config_keeps_sc03_not_applicable(
    tmp_path: Path,
):
    runtime = find_sc03_seed(
        config_path=tmp_path / "missing.toml",
    )

    assert runtime.plasticity_config.enabled is False
    assert runtime.result.applicable is False
    assert runtime.result.status == "NOT_APPLICABLE"


def test_disabled_config_keeps_sc03_not_applicable(
    tmp_path: Path,
):
    path = tmp_path / "sc03.toml"

    write_config(
        path,
        enabled=False,
    )

    runtime = find_sc03_seed(
        config_path=path,
    )

    assert runtime.plasticity_config.enabled is False
    assert runtime.result.applicable is False
    assert runtime.result.status == "NOT_APPLICABLE"


def test_explicit_valid_config_allows_sc03(
    tmp_path: Path,
):
    path = tmp_path / "sc03.toml"

    write_config(
        path,
        enabled=True,
    )

    runtime = find_sc03_seed(
        config_path=path,
    )

    assert runtime.plasticity_config.enabled is True
    assert runtime.result.applicable is True
    assert runtime.result.status == "SELECTED"


def test_runtime_uses_config_not_caller_boolean(
    tmp_path: Path,
):
    path = tmp_path / "sc03.toml"

    write_config(
        path,
        enabled=False,
    )

    runtime = find_sc03_seed(
        config_path=path,
    )

    assert runtime.result.applicable is False
