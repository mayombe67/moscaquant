# OVERWATCH Runtime Collectors v1

## Purpose

Phase 2 adds best-effort operational telemetry beneath the frozen OVERWATCH event contract.

Collectors observe runtime state. Failure to collect a metric must not fail, retune, restart,
or otherwise modify an experiment.

## Initial collectors

- system load averages;
- memory totals / available / used;
- disk total / used / free;
- current-process PID, CPU time and maximum RSS;
- Linux thermal zones when available;
- monotonic duration timing;
- units-per-second throughput calculation.

No network identity, hostname, IP address, cloud account, credential, broker account or
private storage destination is collected by this public module.

## Meme surfaces

The collector data can later feed:

- **PAYLOAD** — progress + throughput;
- **ULT CHARGE** — capacity/resource pressure;
- **OVERTIME** — runtime envelope warnings;
- **KILLFEED** — failures emitted by runtime integration;
- **RESPAWN POINT** — checkpoint duration/state;
- **PLAY OF THE GAME** — downstream evidence-backed highlights only.

These names are presentation semantics. Collector fields remain stable machine data.

## Portability

Collectors are best-effort and dependency-light.

Linux `/proc` and `/sys` metrics are optional. Their absence produces empty or null telemetry
rather than a runtime failure. Cloud-specific metrics belong behind later adapters and must
not enter scientific configuration.
