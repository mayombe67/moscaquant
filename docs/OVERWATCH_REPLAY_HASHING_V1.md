# OVERWATCH Deterministic Replay & Hashing v1

## Purpose

SITE-19B should be able to replay historical MoscaQuant state and prove that the reconstructed
state matches the recorded state.

This layer introduces:

- canonical replay serialization;
- stable payload/state hashing;
- replay-frame identity;
- ordered-frame verification;
- explicit divergence reports.

## Why event UUIDs are not replay identity

OVERWATCH event IDs and timestamps are operational metadata.

Two deterministic executions of the same state transition may legitimately receive different
UUIDs and timestamps.

Replay verification therefore hashes the stable event state rather than requiring volatile
identity fields to match.

## Canonical serialization

Replay hashing uses deterministic JSON serialization:

- mapping keys are sorted;
- compact separators are used;
- UTF-8 is used;
- non-finite floats are rejected;
- floating-point values are rounded to a declared precision.

Version 1 defaults to **12 decimal digits**.

This is not a claim that all science should use 12-digit tolerance. It is a replay-contract
default for stable serialization and may be versioned later.

## Event state hash

`event_state_sha256(...)` includes:

- schema version;
- event type;
- run ID;
- component;
- experiment ID;
- subject ID;
- git commit;
- config hash;
- dataset hash;
- artifact reference;
- lore surface;
- payload.

It excludes:

- event UUID;
- event timestamp.

The result is a SHA-256 hash of canonical serialized state.

## Replay frame

A `ReplayFrameV1` records:

- replay schema;
- run ID;
- ordered sample index;
- event type;
- event-state SHA-256;
- original source event ID when available.

The source event ID preserves linkage to RECEIPTS while the state hash provides deterministic
comparison.

## Verification

`verify_replay_frames(...)` detects:

- missing frames;
- unexpected extra frames;
- sample-index mismatches;
- event-type mismatches;
- state-hash divergence.

A successful replay is one where all expected frames match the reconstructed frame sequence.

## Float handling

Small floating-point representation noise can otherwise break deterministic hashes.

Version 1 canonicalization rounds floats before hashing.

This should not hide scientifically meaningful tolerance decisions.

If a future model requires domain-specific numerical tolerances, those should be explicit and
versioned rather than silently widening replay equality.

## Public-safe replay

Panopticon may consume sanitized replay frames rather than raw private events.

The public replay system should preserve:

- ordering;
- event type;
- stable state identity;
- permitted public payload/projection;
- provenance links.

Private fields remain subject to the normal public projection boundary.

## Divergence

Replay divergence is evidence.

It should not be silently repaired.

Examples:

```text
expected physics.pose hash != reconstructed hash
expected sample 214 missing
unexpected motor.state at sample 215
```

Future OVERWATCH integration may emit a dedicated `replay.divergence` event and route it to the
KILLFEED/HUD.

## Relationship to RECEIPTS

RECEIPTS answers:

> Did the stored telemetry remain intact?

Replay verification answers:

> Does reconstruction produce the same ordered state?

Both matter.

A perfectly intact recording can still expose a nondeterministic or incorrect replay engine.

## Next step

With stable replay hashing in place, the next infrastructure layer can define:

- high-frequency sample batches;
- authoritative stream ordering;
- deterministic downsampling;
- public render frames;
- replay divergence events;
- stream/replay handoff for Panopticon.

That is the bridge from stored SITE-19B evidence to a smooth live and historical viewer.
