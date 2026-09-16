from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(
    __file__
).resolve().parents[1]


@dataclass(frozen=True)
class RuntimeProfile:
    name: str
    data_dir: Path
    scratch_dir: Path
    edge_batch_rows: int
    max_memory_gb: int
    workers: int
    device: str
    config_path: Path


def load_runtime_profile() -> RuntimeProfile:
    """
    Load the non-scientific machine/runtime profile.

    Selection order:

        MOSCAQUANT_RUNTIME environment variable
        otherwise: habitat

    Examples:

        MOSCAQUANT_RUNTIME=habitat
        MOSCAQUANT_RUNTIME=workstation
        MOSCAQUANT_RUNTIME=cloud

    Runtime profiles may change machine resources and paths.
    They must not change scientific model behavior.
    """

    name = os.environ.get(
        "MOSCAQUANT_RUNTIME",
        "habitat",
    )

    config_path = (
        PROJECT_ROOT
        / "config"
        / "runtime"
        / f"{name}.toml"
    )

    if not config_path.exists():
        raise RuntimeError(
            "Runtime profile does not exist: "
            f"{config_path}"
        )

    with config_path.open(
        "rb"
    ) as handle:
        config = tomllib.load(
            handle
        )

    runtime = config[
        "runtime"
    ]

    paths = config[
        "paths"
    ]

    data_dir = Path(
        paths[
            "data_dir"
        ]
    ).expanduser()

    scratch_dir = Path(
        paths[
            "scratch_dir"
        ]
    ).expanduser()

    return RuntimeProfile(
        name=str(
            runtime[
                "name"
            ]
        ),
        data_dir=data_dir,
        scratch_dir=scratch_dir,
        edge_batch_rows=int(
            runtime[
                "edge_batch_rows"
            ]
        ),
        max_memory_gb=int(
            runtime[
                "max_memory_gb"
            ]
        ),
        workers=int(
            runtime[
                "workers"
            ]
        ),
        device=str(
            runtime[
                "device"
            ]
        ),
        config_path=config_path,
    )
