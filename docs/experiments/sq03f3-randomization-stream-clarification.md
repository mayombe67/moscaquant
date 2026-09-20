# SQ-03F.3 — Randomization Stream Clarification

**Status:** POST-ANALYSIS IMPLEMENTATION CLARIFICATION  
**Experiment:** SQ-03F.3 — MADE MEN  
**Authoritative result:** `artifacts/sidequests/sq03f3-made-men-result-v1.json`  
**Result SHA256:** `4a6d47be04d8ac31e5994e5ff83f3d8722840e41ebf104e03dc982e7399f0788`

## What the frozen protocol specified

The frozen SQ-03F.3 protocol specified:

- 10,000 randomization iterations;
- base seed `314159`;
- S and C hotspot sets randomized independently;
- identical stratification rules for both hotspot sets;
- no p-values and no post-hoc significance threshold.

The frozen text did **not** explicitly specify how the independent S and C random
streams would be derived from the single configured seed.

## What the implementation executed

The analyzer used deterministic independent streams:

- S seed: `314159`;
- C seed: `314160` (`base_seed + 1`);
- iterations per hotspot set: `10000`.

Both derived seeds were written into the authoritative result artifact.

## Classification

This is a **documentation-specificity gap**, not an unrecorded reroll.

The analyzer did not inspect a result and then choose a favorable seed. The S/C
stream derivation was fixed in code before execution, and the artifact records
the actual seeds used.

The scientific null model, strata, hotspot memberships, iteration count, and
reporting rules were unchanged.

No authoritative artifact is rewritten and no downstream hash is changed by
this clarification.

## Claim boundary

This note does not claim that a different deterministic stream assignment would
produce bit-identical randomization summaries. It records the exact streams that
generated the accepted artifact and prevents future documentation from implying
that both S and C used the identical literal RNG seed.

For any future protocol using multiple independent randomization streams, the
stream-derivation rule must be frozen explicitly before analysis.
