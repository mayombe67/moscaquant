# MQ-7.4 — Oracle Persistence & Replay

**Status:** DESIGN FREEZE BEFORE IMPLEMENTATION

**System:** ORACLE-01
**Codename:** GLaDOS

> Oracle may resume from history. Oracle may not rewrite history.

## 1. Objective

MQ-7.4 defines how ORACLE-01 persists state and audit history across process or host restarts while preserving the integrity guarantees established in MQ-7.1 through MQ-7.3.

Persistence must not introduce adaptive behavior, authority, execution capability, or silent repair of scientific history.

## 2. Authoritative record

The Oracle event chain is the authoritative historical record.

State snapshots are derived convenience artifacts.

A valid state snapshot must be consistent with the final verified event in the authoritative chain.

If the snapshot and event chain disagree, startup must fail closed.

## 3. Storage layout

Initial logical layout:

```text
<oracle-data-dir>/
├── events.jsonl
├── state.json
└── metadata.json
```

Production cloud placement may use:

```text
/var/lib/moscaquant/oracle/
```

Runtime profiles may change filesystem paths but must not change persistence semantics.

## 4. events.jsonl

`events.jsonl` stores one serialized `OracleEvent` per line.

Rules:

* append-only;
* chronological order;
* no in-place event edits;
* no deletion during normal operation;
* each event must verify its own hash;
* each event after genesis must reference the immediately previous event hash.

A write is not considered committed until the event record is durably written.

## 5. state.json

`state.json` stores the latest materialized Oracle state.

Rules:

* it may be replaced atomically;
* it must never be updated before the corresponding event is durably appended;
* its `state_hash` must match the post-state hash of the final verified event;
* malformed or inconsistent state must fail closed.

A state snapshot is not authoritative evidence by itself.

## 6. metadata.json

`metadata.json` records persistence metadata such as:

* persistence schema version;
* Oracle version;
* Oracle artifact hash;
* last verified event ID;
* last verified event hash;
* state hash;
* event count.

Metadata is an integrity aid, not a replacement for full event-chain verification.

## 7. Commit ordering

A successful transition must persist in this order:

```text
1. construct next state
2. construct proposal
3. construct OracleEvent
4. verify event
5. append event durably
6. atomically replace state snapshot
7. atomically replace metadata
```

A state snapshot must never become visible as committed history before the corresponding event record exists.

## 8. Startup behavior

On startup:

1. load persistence metadata if present;
2. read the complete event log;
3. deserialize every event;
4. verify every event hash;
5. verify every predecessor link;
6. determine the final verified event;
7. load `state.json`;
8. verify the state hash against the final event;
9. verify metadata against the verified chain;
10. only then permit Oracle to resume.

Any integrity failure must prevent normal resume.

## 9. Genesis behavior

An empty persistence directory represents an uninitialized Oracle history.

The first committed event must:

* have no predecessor event hash;
* correspond to a valid initial Oracle state transition;
* establish the first authoritative chain link.

A partially initialized directory must not be treated as an em
