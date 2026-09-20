# OVERWATCH Runtime Events v1

## Purpose

This layer connects Phase 2 collectors to the frozen OVERWATCH telemetry envelope.

Runtime integration emits evidence. It does not control experiments.

## Initial emitters

- `runtime.snapshot` → **HUD**
- `run.progress` → **PAYLOAD**
- `checkpoint.saved` → **RESPAWN POINT**
- `worker.failed` → **KILLFEED**
- `worker.recovered` → **RESPAWN**

The lore surface is metadata for presentation. The canonical event type remains the
machine contract.

## Runtime snapshot

A runtime snapshot may contain:

- load averages;
- memory totals / available / used;
- disk total / used / free;
- current-process CPU and RSS metrics;
- available thermal zones.

Snapshot collection is best-effort. Missing metrics do not fail the experiment.

## Failure and recovery

A KILLFEED event records an observed runtime failure or interruption.

A RESPAWN event records recovery/resume evidence.

Recovery must not be interpreted as permission to rerun a scientifically completed
observation. Frozen protocol rules remain authoritative.

## RECEIPTS

All emitters write through the append-only JSONL writer, giving OVERWATCH a single
local evidence stream before cloud storage is introduced.
