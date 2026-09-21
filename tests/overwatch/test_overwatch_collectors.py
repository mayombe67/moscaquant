from pathlib import Path

from overwatch.collectors import memory_snapshot, thermal_snapshot
from overwatch.timing import Stopwatch, throughput


def test_memory_snapshot_parses_linux_meminfo(tmp_path):
    p = tmp_path / "meminfo"
    p.write_text(
        "MemTotal:       1000 kB\n"
        "MemAvailable:    400 kB\n",
        encoding="utf-8",
    )

    snap = memory_snapshot(p)

    assert snap == {
        "total_bytes": 1000 * 1024,
        "available_bytes": 400 * 1024,
        "used_bytes": 600 * 1024,
    }


def test_thermal_snapshot_is_best_effort(tmp_path):
    root = tmp_path / "thermal"
    root.mkdir()
    zone = root / "thermal_zone0"
    zone.mkdir()
    (zone / "temp").write_text("42500\n", encoding="utf-8")
    (zone / "type").write_text("cpu-thermal\n", encoding="utf-8")

    assert thermal_snapshot(root) == [
        {
            "zone": "thermal_zone0",
            "type": "cpu-thermal",
            "celsius": 42.5,
        }
    ]


def test_stopwatch_uses_monotonic_clock():
    ticks = iter([10.0, 12.5])
    timer = Stopwatch(clock=lambda: next(ticks)).start()
    assert timer.stop() == 2.5


def test_throughput_handles_zero_elapsed():
    assert throughput(100, 0.0) is None
    assert throughput(100, 4.0) == 25.0
