# MQ-5.TS Arm C Native Backend — Pre-Result Hardening

## Status

**PRE-RESULT IMPLEMENTATION HARDENING**

No MQ-5.TS Arm B or Arm C result-bearing seed had been executed when this change was made.

The semantic Arm C null-model contract remains unchanged. This change affects only native hash-table maintenance.

## Reason

The initial native open-addressed hash table used tombstone deletion. A full Arm C topology performs tens of millions of delete/insert cycles, while the earlier non-result-bearing smoke exercised only a tiny fraction of that churn. Tombstone accumulation could therefore cause progressively longer probe chains or empty-slot exhaustion.

## Change

Deletion now uses backward-shift repair for linear probing, restoring one true empty slot after each erase while preserving lookup correctness.

## Scientific semantics unchanged

- same eligible-edge definition
- same retinal-origin protection
- same transmitter-sign matching
- same no-new-self-edge semantics
- same duplicate-edge rejection
- same accepted-swap target and attempt multiplier
- same SplitMix64 random stream and bounded sampling
- same two-position proposal semantics
- same deterministic weight assignment

## Regression

A long-churn synthetic regression performs twenty accepted swaps per structural edge and requires exact target completion plus all frozen invariants.

## Freeze boundary

`77daf9e` remains the semantic-null checkpoint. The commit containing this hardening becomes the authoritative production-execution freeze if focused tests, the full suite, and a non-result-bearing full-connectome smoke pass before any randomized result seed executes.
