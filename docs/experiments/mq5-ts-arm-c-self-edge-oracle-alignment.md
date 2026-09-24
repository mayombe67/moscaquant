# MQ-5.TS Arm C — Reference Self-Edge Oracle Alignment

**Status:** POST-RESULT BACKEND HARDENING — NO SCIENTIFIC RESULT REOPENED

## Why this note exists

The frozen MQ-5.TS Arm C protocol states that no self-edge may be introduced
unless the original graph already contained that exact edge.

The full MaleCNS baseline contains pre-existing structural self-edges.

The native production backend and scalable verifier implement the intended
baseline-relative rule:

- a new `x -> x` is forbidden when baseline `x -> x` was absent;
- baseline `x -> x` remains an allowed exact edge identity;
- duplicate-edge exclusion remains independently enforced.

The bounded Python reference backend was stricter: it rejected every proposed
self-edge, even when the exact `x -> x` edge existed in the original graph.

## Correction

The reference backend now uses the same baseline-relative self-edge eligibility
rule as the native production backend.

A behavioral regression proves that two baseline self-edges may be swapped away
and later recreated as the same exact baseline edges while all strict
invariants remain satisfied.

## Scientific status

This correction does **not**:

- alter the native production backend used by the accepted MQ-5.TS execution;
- regenerate any MQ-5.TS randomized seed;
- modify the accepted MQ-5.TS result artifact;
- change the preregistered Arm C invariant;
- retroactively reinterpret the accepted topology-specificity result.

It aligns the small-graph correctness oracle with the already-frozen invariant
before future reuse of Arm C, including planned SQ-05 / TWO BETRAYALS work.

## Remaining pre-SQ-05 issue

Arm C randomization strength remains frozen at one accepted swap per eligible
edge for MQ-5.TS. A separate prospective mixing-depth characterization is still
required before treating the strict null as the flagship public SQ-05
BETRAYAL II showcase arm.

That future characterization may inform SQ-05 design but may not rewrite the
accepted MQ-5.TS result.
