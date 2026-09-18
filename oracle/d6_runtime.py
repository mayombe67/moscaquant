from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from oracle.plasticity_config import (
    PlasticityConfig,
    load_plasticity_config,
)
from oracle.reinforcement import ReinforcementResult
from oracle.selector import select_d6


DEFAULT_SC03_CONFIG = Path(
    "config/oracle/sc03-plasticity-v1.toml"
)


@dataclass(frozen=True)
class D6RuntimeSelection:
    result: ReinforcementResult
    plasticity_config: PlasticityConfig


def select_d6_from_scientific_config(
    *,
    seed: int,
    experiment_id: str,
    session_id: str,
    config_path: Path = DEFAULT_SC03_CONFIG,
) -> D6RuntimeSelection:
    config = load_plasticity_config(
        config_path
    )

    result = select_d6(
        seed=seed,
        experiment_id=experiment_id,
        session_id=session_id,
        plasticity_active=config.enabled,
    )

    return D6RuntimeSelection(
        result=result,
        plasticity_config=config,
    )
