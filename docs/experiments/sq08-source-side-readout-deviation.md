# SQ-08 — Source-Side Readout Protocol Deviation

## Status

CONFIRMED PROTOCOL DEVIATION

This document records a post-result audit finding concerning the frozen
SQ-08 — THREE BODY PROBLEM evidence contract.

It does not alter or recompute the authoritative SQ-08 primary factorial
result.

## Preregistered requirement

The frozen SQ-08 preregistration required, among the mechanistic readouts:

> source-side state for each of BODY A, BODY B, and BODY C

The three frozen BODY edges were:

- BODY A: 65084 -> 137122
- BODY B: 128590 -> 317
- BODY C: 135589 -> 126002

The presynaptic source neurons are therefore:

- 65084
- 128590
- 135589

## Post-result audit

All three source neurons were confirmed to belong to the frozen graded
population:

- 65084: Tm4
- 128590: Tm4
- 135589: Tm4

Their immediate BODY responders were not members of the graded population.

The three source neurons are not present in the frozen DN consensus artifact.

Therefore their state cannot be recovered from the preserved
`primary_positive_voltage` or `primary_spikes` arrays.

## Evidence-schema finding

The frozen SQ-08 evidence schema requires:

- primary_positive_voltage
- primary_spikes
- body_responder_voltage
- body_responder_spikes
- frontier_voltage
- frontier_spikes

and secondary channel spike summaries.

It defines no dedicated BODY-source voltage, spike, or effective-activity
arrays.

The authoritative SQ-08 evidence therefore does not preserve source-side
state for BODY A, BODY B, or BODY C.

## Verification implication

The SQ-08 independent verifier correctly established conformance to the
frozen evidence schema.

However, the evidence schema did not encode every mechanistic measurement
required by the prose preregistration.

Accordingly:

- evidence-schema verification remains valid;
- authoritative artifact integrity remains valid;
- the primary factorial result remains valid;
- BODY-responder and frontier analyses remain valid;
- source-side mechanistic localization is unavailable;
- complete compliance with the preregistered mechanistic-readout set was not
  achieved.

This is a preregistration-to-schema closure failure.

## Primary result boundary

This deviation does not invalidate the preregistered primary SQ-08 test of
the three-way factorial term.

The authoritative primary classification remains:

`THREE_WAY_EXACT_ZERO`

under the frozen numerical-zero contract.

The deviation limits mechanistic localization, not the existence or numerical
classification of the preserved factorial result.

## Prohibited repair

No post-result regeneration or rerun may be represented as having been part
of the original SQ-08 evidence package.

Any future acquisition of BODY-source trajectories occurs after observation
of the SQ-08 result and must therefore be explicitly identified as new,
prospective work.

## Follow-up

SQ-09 — PATTERN SCREAMER may use the existing SQ-08 evidence for:

- static structural-null audit;
- numerical-zero audit;
- lower-order decomposition of already-preserved readouts.

Direct source-side dynamical testing requires a separately frozen prospective
measurement contract before new neural execution.

## Engineering lesson

APOTHEOSIS #26 — PREREGISTRATION-TO-SCHEMA CLOSURE

Every measurement declared required by a frozen scientific protocol must map
to either:

1. an explicitly required machine-verifiable evidence field; or
2. an explicitly declared deterministic derivation from required fields.

A frozen evidence verifier must check this closure before execution
authorization.

Science first.

Gaps get documented, not patched out of history.
