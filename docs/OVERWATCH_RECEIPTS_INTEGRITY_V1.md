# OVERWATCH RECEIPTS Integrity v1

## Purpose

OVERWATCH must be able to prove that persisted telemetry still matches the evidence that was
originally written.

The integrity verifier is read-only. It never repairs, deletes, rewrites or reorders evidence.

## Verification

For every manifest-referenced segment the verifier checks:

- object exists;
- SHA-256 matches the manifest;
- byte count matches;
- segment decodes as UTF-8 NDJSON;
- every line is valid JSON;
- line/event count matches the manifest record.

It also verifies the manifest's total event count against successfully verified segments.

## Orphan detection

If the concrete object client can list keys, OVERWATCH can detect immutable segment objects
that exist beneath the run's `segments/` prefix but are not referenced by the manifest.

The expected failure mode is an interrupted write:

1. immutable segment succeeds;
2. process dies before manifest update;
3. segment remains as an orphan.

An orphan is evidence requiring reconciliation. It must not be silently deleted or silently
attached to the manifest.

## RECEIPTS verdict

A report is clean only when no integrity issues are present.

Typical issue classes:

- `manifest.missing`
- `manifest.invalid`
- `manifest.schema`
- `segment.missing`
- `segment.sha256`
- `segment.byte_count`
- `segment.ndjson`
- `segment.event_count`
- `manifest.event_total`
- `segment.orphan`

## Authority boundary

Integrity checking is observational.

The verifier has no authority to:

- rerun an experiment;
- regenerate a scientific result;
- modify a frozen manifest;
- delete an orphan;
- choose which conflicting artifact is correct;
- repair corrupted evidence.

Any repair/reconciliation procedure must be explicit, separately logged and preserve the
original failure evidence.

## Cloud boundary

The verifier depends only on the public object-storage client contract.

Concrete listing, SDK credentials, IAM permissions, bucket names, encryption and retention
remain private ops concerns.
