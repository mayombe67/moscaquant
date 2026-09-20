from __future__ import annotations
import json
from pathlib import Path
from .events import TelemetryEventV1

class JsonlTelemetryWriter:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def emit(self, event: TelemetryEventV1) -> None:
        line = json.dumps(event.to_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")
            fh.flush()
