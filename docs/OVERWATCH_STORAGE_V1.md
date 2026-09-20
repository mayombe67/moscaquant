# OVERWATCH Storage v1

## Purpose

OVERWATCH storage is an infrastructure boundary beneath the telemetry contract.

Scientific and runtime emitters create canonical events. Storage backends persist those
events without changing their meaning or affecting experiment behavior.

## Backends

### Local JSONL

`LocalJsonlStorage` is the reference implementation.

It writes append-only newline-delimited JSON using the existing OVERWATCH writer.

### S3-compatible object storage

`S3CompatibleJsonlStorage` defines the cloud persistence boundary.

The public science repo intentionally does not:

- import a cloud SDK;
- discover credentials;
- contain account IDs;
- contain production bucket names;
- contain private endpoints;
- contain IAM policy;
- select regions;
- select deployment topology.

Instead, an `ObjectStorageClient` implementation is dependency-injected by deployment/ops
code.

This keeps cloud configuration outside scientific configuration.

## RECEIPTS

The canonical storage object is an append-only NDJSON/JSONL RECEIPTS stream.

A typical logical key may resemble:

`runs/<run-id>/receipts.jsonl`

That convention is illustrative rather than a required production bucket/key layout.

## Current reference implementation limitation

The initial S3-compatible implementation performs a read-modify-write append because generic
object storage does not provide portable byte append semantics.

This is intentionally a correctness/reference adapter, not yet a high-throughput production
writer.

Before production cloud execution, OVERWATCH should move to immutable event objects or
batched segment objects plus a manifest rather than repeatedly rewriting an ever-growing
object.

That optimization must preserve the same canonical event envelope.

## Security boundary

Credentials, cloud SDK configuration, private endpoints, production storage names, IAM
roles and deployment policy belong in private ops configuration.

Panopticon receives only the sanitized public projection, never storage credentials or raw
private runtime telemetry.
