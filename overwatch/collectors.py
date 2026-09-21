from __future__ import annotations

import os
import resource
import shutil
from pathlib import Path
from typing import Any


def _read_meminfo(path: Path = Path("/proc/meminfo")) -> dict[str, int]:
    """Return selected Linux /proc/meminfo values in bytes.

    Missing/unavailable procfs returns an empty mapping so OVERWATCH remains
    portable rather than failing an experiment for observability reasons.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return {}

    values: dict[str, int] = {}
    for line in text.splitlines():
        if ":" not in line:
            continue
        key, raw = line.split(":", 1)
        parts = raw.strip().split()
        if not parts:
            continue
        try:
            value = int(parts[0])
        except ValueError:
            continue
        multiplier = 1024 if len(parts) > 1 and parts[1].lower() == "kb" else 1
        values[key] = value * multiplier
    return values


def memory_snapshot(meminfo_path: Path = Path("/proc/meminfo")) -> dict[str, int | None]:
    info = _read_meminfo(meminfo_path)
    total = info.get("MemTotal")
    available = info.get("MemAvailable")
    used = total - available if total is not None and available is not None else None
    return {
        "total_bytes": total,
        "available_bytes": available,
        "used_bytes": used,
    }


def load_snapshot() -> dict[str, float | None]:
    try:
        one, five, fifteen = os.getloadavg()
    except (AttributeError, OSError):
        return {"load_1m": None, "load_5m": None, "load_15m": None}
    return {
        "load_1m": float(one),
        "load_5m": float(five),
        "load_15m": float(fifteen),
    }


def disk_snapshot(path: str | Path = ".") -> dict[str, int]:
    usage = shutil.disk_usage(path)
    return {
        "total_bytes": int(usage.total),
        "used_bytes": int(usage.used),
        "free_bytes": int(usage.free),
    }


def process_snapshot() -> dict[str, int | float]:
    usage = resource.getrusage(resource.RUSAGE_SELF)

    # Linux reports ru_maxrss in KiB. Other Unix platforms may differ, so the
    # field name explicitly describes the normalized byte value we expose.
    max_rss_bytes = int(usage.ru_maxrss) * 1024

    return {
        "pid": os.getpid(),
        "user_cpu_seconds": float(usage.ru_utime),
        "system_cpu_seconds": float(usage.ru_stime),
        "max_rss_bytes": max_rss_bytes,
    }


def thermal_snapshot(root: Path = Path("/sys/class/thermal")) -> list[dict[str, Any]]:
    """Return available Linux thermal zones without failing when absent."""
    if not root.exists():
        return []

    zones: list[dict[str, Any]] = []
    for zone in sorted(root.glob("thermal_zone*")):
        try:
            raw_temp = (zone / "temp").read_text(encoding="utf-8").strip()
            temp_millideg = int(raw_temp)
        except (OSError, ValueError):
            continue

        try:
            zone_type = (zone / "type").read_text(encoding="utf-8").strip()
        except OSError:
            zone_type = None

        zones.append(
            {
                "zone": zone.name,
                "type": zone_type,
                "celsius": temp_millideg / 1000.0,
            }
        )
    return zones


def runtime_snapshot(disk_path: str | Path = ".") -> dict[str, Any]:
    """Collect a best-effort OVERWATCH runtime snapshot."""
    return {
        "load": load_snapshot(),
        "memory": memory_snapshot(),
        "disk": disk_snapshot(disk_path),
        "process": process_snapshot(),
        "thermals": thermal_snapshot(),
    }
