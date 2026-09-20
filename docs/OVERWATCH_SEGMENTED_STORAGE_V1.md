# OVERWATCH Segmented Object Storage v1

## Purpose

This is the production-shaped object-storage layout for OVERWATCH RECEIPTS.

It replaces the reference read-modify-write JSONL object with immutable event segments
plus a small manifest.

## Layout

Illustrative logical layout:

```text
runs/<run-id>/
  manifest.json
  segments/
    00000001-<digest>.ndjson
    00000002-<digest>.ndjson
    ...
```

Segment objects are immutable evidence.

The manifest is a compact index containing:

- schema version;
- total event count;
- segment count;
- ordered segment keys;
- event count per segment;
- byte count;
- SHA-256 digest.

## Write order

OVERWATCH writes the immutable segment first.

Only after that write succeeds does it update the manifest.

A crash between those operations may leave an orphaned immutable segment, but it does not
create a manifest entry for evidence that was never persisted.

Recovery/reconciliation tooling can later detect orphaned segments.

## Concurrency boundary

Version 1 assumes **one writer per run prefix**.

That ownership rule belongs to deployment/ops.

Multi-writer support will require conditional manifest updates, version tokens, locking,
or another coordination mechanism supplied by the concrete object store.

The public science contract does not silently pretend concurrent appends are safe.

## Batching

`append_many()` writes a batch as one immutable NDJSON segment.

`append()` is valid but creates a single-event segment.

Cloud runtime integrations should batch sensibly to reduce object count and request cost
without changing event semantics.

## Evidence semantics

Segment hashes make corruption or accidental replacement detectable.

Object-storage layout is operational metadata, not a scientific outcome.

Changing segment size, object-store provider, bucket, region, or machine must not change
the experiment protocol or event contents.

## Security

The public repo defines this layout and its integrity rules.

Private ops supplies:

- concrete SDK client;
- credentials;
- production bucket/container;
- IAM/access policy;
- encryption policy;
- retention/lifecycle policy;
- region/endpoints;
- single-writer ownership enforcement.

Panopticon never receives these details. It consumes the sanitized OVERWATCH projection.
