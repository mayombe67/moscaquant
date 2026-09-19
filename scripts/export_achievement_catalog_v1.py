"""Export the public v1 achievement catalog with MQ-8.5A semantics."""

from __future__ import annotations

import json
from pathlib import Path

from achievements.semantics_v1 import semantics_for


ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "achievements" / "catalog_v1.json"


def enrich_catalog(payload: dict) -> dict:
    definitions = payload.get("definitions", [])

    for definition in definitions:
        achievement_id = definition["achievement_id"]
        category = definition["category"]

        semantics = semantics_for(achievement_id, category)
        definition.update(semantics)

    payload["schema"] = "moscaquant-achievement-catalog/v1"
    payload["semantics_version"] = "mq8.5a/v1"

    # Canonical namespace capacity is larger than the currently populated
    # v1 definition set. Empty slots remain reserved design space.
    payload["namespace_size"] = 128
    payload["defined_count"] = len(definitions)
    payload["reserved_count"] = payload["namespace_size"] - len(definitions)

    # Backward-compatible alias retained for existing consumers.
    payload["count"] = len(definitions)

    return payload


def main() -> None:
    if not CATALOG_PATH.exists():
        raise SystemExit(f"Missing catalog: {CATALOG_PATH}")

    payload = json.loads(CATALOG_PATH.read_text())
    payload = enrich_catalog(payload)

    CATALOG_PATH.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n"
    )

    historical = [
        row for row in payload["definitions"]
        if row.get("provenance_class") == "HISTORICAL_REPLAY"
    ]

    major = [
        row for row in payload["definitions"]
        if row.get("syndication_class") == "MAJOR"
    ]

    print("=" * 72)
    print("MQ-8.5A ACHIEVEMENT SEMANTICS EXPORT")
    print("=" * 72)
    print("definitions:", len(payload["definitions"]))
    print("historical semantics:", len(historical))
    print("major syndication candidates:", len(major))
    print("output:", CATALOG_PATH)


if __name__ == "__main__":
    main()
