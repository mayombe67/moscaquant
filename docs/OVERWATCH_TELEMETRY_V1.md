# OVERWATCH Telemetry v1

## Purpose

OVERWATCH is MoscaQuant's observability layer.

> OVERWATCH observes, records, and reports. It does not alter frozen experiment behavior.

OVERWATCH has no authority to change scientific parameters, rerun observed experiments, modify Warden policy, place trades, alter Oracle decisions, or publish claims.

## Stable machine contract

Every event uses the `overwatch.telemetry.v1` envelope with stable fields for event identity, UTC timestamp, event type, run/component identity, payload, and optional experiment/provenance references.

Canonical event types are boring on purpose:

- `run.started`
- `run.progress`
- `run.completed`
- `run.failed`
- `run.slow`
- `checkpoint.saved`
- `worker.failed`
- `worker.recovered`
- `capacity.warning`
- `run.highlight_candidate`

## Game-flavored presentation layer

The HUD may translate canonical events into OVERWATCH terminology:

| Canonical event | Surface |
| --- | --- |
| `run.started` | SPAWN |
| `run.progress` | PAYLOAD |
| `checkpoint.saved` | RESPAWN POINT |
| `worker.failed` | KILLFEED |
| `worker.recovered` | RESPAWN |
| `run.slow` | OVERTIME |
| `capacity.warning` | ULT CHARGE |
| `run.completed` | GG |
| `run.highlight_candidate` | PLAY OF THE GAME |

These names are presentation-only. Comedy is downstream of evidence.

## Named surfaces

**HUD** — live operator/spectator view.

**PAYLOAD** — progress, completed work, remaining work, throughput and checkpoint position.

**KILLFEED** — failures, interruptions, dead workers and recovery-related incidents.

**RESPAWN** — recovery/resume history. A respawn is not a scientific rerun unless the frozen protocol permits resumed computation.

**OVERTIME** — work exceeds an expected runtime/resource envelope. It cannot silently change parameters.

**PLAY OF THE GAME** — evidence-backed highlight candidate with no publication authority.

**RECEIPTS** — immutable event/provenance history.

**SAVE STATE / RESPAWN POINT** — checkpoint evidence.

## Boundaries

OVERWATCH MUST NOT change seeds, thresholds, models, samples, protocols, stopping rules, Warden limits, broker authority, or Oracle decisions. It must not hide failures or expose private infrastructure through the public projection.

## Rollout

Phase 1: event envelope, local append-only JSONL, provenance, failure/checkpoint/recovery events and tests.

Phase 2: CPU, memory, load, disk, process state, thermals where available, batch latency, throughput, checkpoint duration and restart state.

Phase 3: interchangeable object-storage backend for cloud persistence.

Panopticon consumes a sanitized projection rather than the raw firehose.

Cloud/runtime configuration stays separate from scientific configuration so moving Habitat to another machine or cloud backend cannot change experimental behavior.

## Public projection boundary

Raw OVERWATCH telemetry is not a Panopticon API.

The reference implementation exposes `overwatch.projection.public_projection()`,
which produces a deliberately lossy public-safe representation. Scientific identity
and provenance fields may pass through, while operational fields such as hostnames,
IP addresses, account identifiers, storage destinations, credentials, private
endpoints and similar infrastructure details are stripped from payloads.

The raw event stream remains authoritative evidence. The public projection is a
presentation product and must never be used to reconstruct missing private runtime
state or to drive scientific decisions.

```text
MoscaQuant / OVERWATCH
        raw telemetry
             |
             +----> private storage / ops
             |
             v
      public projection
             |
             v
        Panopticon HUD
```
