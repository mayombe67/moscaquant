# MQ-5.TS Randomized Ensemble Runner Implementation

## Status

**PRE-RUN IMPLEMENTATION FREEZE REQUIRED**

This runner implements the frozen MQ-5.TS randomized topology-specificity
benchmark. Creating or committing the runner does not execute a randomized
result-bearing seed.

## Entry gate

Randomized execution requires:

- a clean Git working tree;
- all Step 33 harness/metric/runtime/replay/ensemble files tracked by Git;
- the frozen A/D duplicate-replay gate artifact;
- exact gate artifact SHA-256 validation;
- Arm A and Arm D payload hashes reproduced before B/C execution;
- the frozen 20-seed Arm B range;
- the frozen 20-seed Arm C range.

## Randomized arms

Arm B uses the existing SHUFFLED MOSCA v2 interface-preserving,
transmitter-sign-preserving identity permutation.

Arm C uses the frozen native strict matched-topology constructor.

Every precommitted seed is attempted. There is no early stopping and a failed
build is recorded rather than replaced.

## Frozen classification

An Arm C seed counts as an exact response-pattern reproduction only if all
three checks match Arm A:

1. exact responder-set identity;
2. exact first-onset vector over the accepted responder universe, including
   absence;
3. normalized responder-voltage fingerprint L2 distance <= `1e-9`.

The final Arm C classification is:

- 0-1 exact reproductions: `TOPOLOGY-SPECIFIC RESPONSE PATTERN SUPPORTED`
- 2-9 exact reproductions: `MIXED TOPOLOGY SPECIFICITY`
- 10-20 exact reproductions:
  `STRICT NULL FREQUENTLY REPRODUCES RESPONSE`

If fewer than all 20 Arm C seeds complete, classification fails closed as:

`INCOMPLETE_DUE_TO_FAILED_ARM_C_BUILDS`

Mutual information and causal-edge survival remain recorded diagnostics but do
not determine the classification.

## Boundary

No financial semantics, P&L, profitability, trading action, or market
prediction is assigned by MQ-5.TS.
