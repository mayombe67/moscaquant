from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from oracle.models import OracleEvent, OracleState
from oracle.persistence import (
    load_events,
    load_metadata,
    load_state,
    verify_persisted_state,
)


@dataclass(frozen=True)
class OracleReplay:
    events: tuple[OracleEvent, ...]
    state: OracleState
    metadata: dict


def load_replay(base_dir: Path) -> OracleReplay:
    events = load_events(
        base_dir / "events.jsonl"
    )

    state = load_state(
        base_dir / "state.json"
    )

    metadata = load_metadata(
        base_dir / "metadata.json"
    )

    verify_persisted_state(
        events=events,
        state=state,
        metadata=metadata,
    )

    return OracleReplay(
        events=events,
        state=state,
        metadata=metadata,
    )
