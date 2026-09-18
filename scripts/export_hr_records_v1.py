"""Export public-safe canonical HR records."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from hr.canonical_records_v1 import CANONICAL_HR_RECORDS
from hr.registry import validate_registry


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "hr" / "canonical_records_v1.json"


def main() -> None:
    validate_registry(CANONICAL_HR_RECORDS)

    payload = {
        "schema": "moscaquant-hr-records/v1",
        "count": len(CANONICAL_HR_RECORDS),
        "records": [asdict(record) for record in CANONICAL_HR_RECORDS],
    }

    OUTPUT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n"
    )

    print("=" * 72)
    print("MQ-8.5B.1 CANONICAL HR RECORD EXPORT")
    print("=" * 72)
    print("records:", len(CANONICAL_HR_RECORDS))
    print("output:", OUTPUT)


if __name__ == "__main__":
    main()
