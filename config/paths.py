from __future__ import annotations

import os
from pathlib import Path

_ENV = "MOSCAQUANT_DATA_ROOT"


def data_root() -> Path:
    """Return the external MoscaQuant data root."""
    configured = os.environ.get(_ENV)
    if configured:
        return Path(configured).expanduser().resolve()
    return (Path.home() / "moscaquant-data").resolve()


def data_path(*parts: str) -> Path:
    """Build a path under the configured MoscaQuant data root."""
    return data_root().joinpath(*parts)
