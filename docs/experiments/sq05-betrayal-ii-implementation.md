# SQ-05 — TWO BETRAYALS — BETRAYAL II Implementation

**Arm:** `BETRAYAL_II_SHUFFLED`
**Narrative:** THE SECOND BETRAYAL — presentation only
**Status:** IMPLEMENTATION FREEZE CANDIDATE — NO SQ-05 RESULT EXECUTION AUTHORIZED
**Financial semantics:** NOT ASSIGNED

## Purpose

WARTHOG RUN sealed `CURRENT_1X_ADEQUATE_FOR_SQ05`. This gate binds the SQ-05
shuffled arm to that exact `1.0x` strict Arm C topology null without executing
SQ-05 or selecting an outcome-bearing seed.

## Frozen implementation boundary

BETRAYAL II reuses, rather than reimplements:

- `brain.mq5_ts_strict_shuffle_native.build_strict_matched_control_native`
- `brain.mq5_ts_strict_shuffle_verify.verify_strict_matched_control_scalable`

The SQ-05 adapter fixes `1.0x` accepted swaps per eligible edge and
`max_attempt_multiplier = 20`, and it fails closed unless the exact sealed
WARTHOG authority and backend hashes are present.

## Fresh-seed boundary

This gate deliberately does not choose the SQ-05 seed or seed count. A future
SQ-05 preregistration must select fresh seed(s) prospectively.

It forbids reuse of MQ-5.TS Arm C result seeds `20263000..20263019` and WARTHOG
characterization seeds `20264000`, `20264001`, and `20264002`.

## Preserved structural semantics

The authoritative production verifier remains the source of truth for retinal
protection, exact indegree/outdegree, transmitter-sign constraints, incoming
sign counts, row-weight multisets, normalization, edge count, duplicate
exclusion, and baseline-relative `no_new_self_edges`.

## Deliberately unresolved

This gate does not define BETRAYAL I's lesion, SQ-05 stimuli or timing, trial
count, future shuffled seed count, neural endpoints/classification, showcase
trial selection, or any subjective-state claim.

## Execution boundary

`brain/sq05_betrayal_ii.py` intentionally has no CLI and no result writer.
This gate authorizes no topology result construction and no neural execution.

## TWO BETRAYALS

WARTHOG RUN got the Index back to the Control Room.

BETRAYAL II now has a weapon specification: the strict `1.0x` topology null.

The Index is still not inserted.\n
