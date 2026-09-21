from __future__ import annotations

from dataclasses import dataclass, field
from time import monotonic
from typing import Callable


@dataclass
class Stopwatch:
    """Monotonic timer for operational telemetry only."""

    clock: Callable[[], float] = field(default=monotonic)
    _started_at: float | None = None

    def start(self) -> "Stopwatch":
        self._started_at = self.clock()
        return self

    def elapsed_seconds(self) -> float:
        if self._started_at is None:
            raise RuntimeError("Stopwatch has not been started")
        return self.clock() - self._started_at

    def stop(self) -> float:
        elapsed = self.elapsed_seconds()
        self._started_at = None
        return elapsed


def throughput(completed_units: int, elapsed_seconds: float) -> float | None:
    """Return units/second, or None when elapsed time is not positive."""
    if elapsed_seconds <= 0:
        return None
    return completed_units / elapsed_seconds
