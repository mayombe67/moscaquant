"""Configuration loading for MoscaQuant."""

from __future__ import annotations

import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_toml(path: Path) -> dict:
    with path.open("rb") as fh:
        return tomllib.load(fh)


def expand_path(value: str) -> Path:
    return Path(value).expanduser().resolve()


def load_subject(name: str = "mq001") -> dict:
    return load_toml(ROOT / "config" / f"{name}.toml")


def load_runtime(name: str = "habitat") -> dict:
    config = load_toml(
        ROOT / "config" / "runtime" / f"{name}.toml"
    )

    config["paths"]["data_dir"] = expand_path(
        config["paths"]["data_dir"]
    )
    config["paths"]["scratch_dir"] = expand_path(
        config["paths"]["scratch_dir"]
    )

    return config
