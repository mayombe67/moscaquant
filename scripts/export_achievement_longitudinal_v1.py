"""Materialize the MQ-8 achievement occurrence ledger and longitudinal projection."""

from __future__ import annotations

import json
from pathlib import Path

from achievements.catalog_v1 import V1_REGISTRY
from achievements.historical_replay_v1 import (
    historical_replay_occurrences,
    occurrence_to_dict,
)
from achievements.ledger_v1 import load_occurrence_jsonl
from achievements.longitudinal_v1 import build_longitudinal_projection
from achievements.semantics_v1 import semantics_for


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "achievements" / "occurrences_v1.jsonl"
PUBLIC = ROOT / "public_data" / "achievement_longitudinal_v1.json"
NEUROSCOPE = ROOT / "neuroscope" / "web" / "public_data" / "achievement_longitudinal_v1.json"


def build_semantics():
    return {
        achievement_id: semantics_for(
            achievement_id,
            definition.category.value,
        )
        for achievement_id, definition in V1_REGISTRY.items()
    }


def materialize_historical_ledger() -> None:
    rows = historical_replay_occurrences()
    payload = "".join(
        json.dumps(occurrence_to_dict(row), sort_keys=True) + "\n"
        for row in rows
    )
    LEDGER.write_text(payload)


def main() -> None:
    materialize_historical_ledger()

    store = load_occurrence_jsonl(LEDGER)
    projection = build_longitudinal_projection(
        definitions=V1_REGISTRY.values(),
        store=store,
        semantics_by_id=build_semantics(),
    )

    text = json.dumps(projection, indent=2, sort_keys=True) + "\n"
    PUBLIC.parent.mkdir(parents=True, exist_ok=True)
    NEUROSCOPE.parent.mkdir(parents=True, exist_ok=True)
    PUBLIC.write_text(text)
    NEUROSCOPE.write_text(text)

    print("=" * 72)
    print("MQ-8.7 LONGITUDINAL ACHIEVEMENT EXPORT")
    print("=" * 72)
    print("occurrences:", sum(
        row["stack_count"] for row in projection["achievements"]
    ))
    print("achievements:", projection["achievement_count"])
    print("families:", len(projection["families"]))
    print("ledger:", LEDGER)
    print("public:", PUBLIC)
    print("neuroscope:", NEUROSCOPE)


if __name__ == "__main__":
    main()
