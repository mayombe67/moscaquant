# SQ-10 — SOPHON

## Status

HANDOFF / MEASUREMENT CONTRACT DESIGN

No SQ-10 neural execution is authorized by this document.

## Purpose

SQ-07 — THE MAW established that the three RL edges E10/E11/E12 are jointly
required to reproduce the frozen FULL13 endpoint.

SQ-08 — THREE BODY PROBLEM found no irreducible three-way interaction.

SQ-09 — PATTERN SCREAMER showed that, within the preserved SQ-08 evidence:

- all three single-edge main effects are nonzero;
- all pairwise interaction terms are exactly zero after promotion-before-arithmetic;
- the three-way interaction term is exactly zero;
- each main effect is confined to exactly one immediate BODY responder.

The remaining mechanistic question is upstream:

Why does each frozen Tm4 source-to-responder edge produce its corresponding
isolated responder correction?

SQ-10 prospectively measures the previously omitted source-side state.

## Codename

SOPHON

The name reflects three independently instrumented source channels whose
effects appeared downstream as three isolated local corrections.

## Frozen BODY pairs

### A

- source: 65084
- responder: 137122
- inherited edge: E10

### B

- source: 128590
- responder: 317
- inherited edge: E11

### C

- source: 135589
- responder: 126002
- inherited edge: E12

All three sources are frozen Tm4 graded neurons.

## Primary scientific question

For each BODY pair, what source-side state produces the isolated responder
effect observed in SQ-08/SQ-09?

## Specific questions

1. Does the source voltage trajectory change when its outgoing BODY edge is
   lesioned?

2. Does the source spike trajectory change?

3. Does the source effective graded activity change?

4. What exact source activity is presented to the source-to-responder edge at
   the frame where the responder difference first appears?

5. Is the responder difference temporally aligned with removal of that direct
   edge contribution?

6. Do lesions of the other two BODY edges alter that source-to-responder path?

7. Is there evidence of recurrent feedback or cross-coupling that was invisible
   in the SQ-08 DN-only readout?

## Intervention structure

The preferred intervention structure is the same complete 2^3 BODY cube used
by SQ-08:

- 000
- 001
- 010
- 011
- 100
- 101
- 110
- 111

Mask semantics remain:

- 0 = edge retained
- 1 = edge zeroed

No condition ranking is permitted.

All eight conditions are analyzed symmetrically.

## Required prospective measurements

For all three sources, preserve at every frame:

- source voltage;
- source spikes;
- effective graded activity.

For all three immediate responders, preserve at every frame:

- responder voltage;
- responder spikes.

The final frozen contract should additionally preserve or permit exact
deterministic derivation of the direct edge contribution:

    effective_activity[source] * edge_weight

with explicit timing semantics matching the runtime's actual synaptic update.

## Timing requirement

The measurement phase must be specified precisely relative to:

- effective-activity calculation;
- synaptic matrix multiplication;
- voltage decay;
- synaptic/stimulus integration;
- threshold evaluation;
- spike commit;
- voltage reset.

The runtime implementation must be audited before these phase names are frozen.

No ambiguous "source state at frame t" field is acceptable.

## Evidence-schema closure requirement

Every measurement required by the preregistration must map to:

1. a named evidence field; or
2. an explicitly declared deterministic derivation from named evidence fields.

The preregistration, evidence schema, verifier, and execution adapter must agree
before execution authorization.

This requirement follows directly from the SQ-08 source-side readout deviation.

## Initial hypotheses

The hypotheses below are prospective possibilities, not established findings.

### H1 — source-state invariance

The three edge lesions may leave the corresponding presynaptic Tm4 source
trajectory unchanged.

Under this case, the intervention acts primarily by removing transmission of an
otherwise unchanged source signal.

### H2 — direct local transmission

The observed responder effect may be explained by removal of the direct
source-to-responder synaptic contribution.

### H3 — recurrent feedback

Removing a BODY edge may alter later source state through recurrent network
feedback.

If observed, this would reject the simplest feed-forward interpretation.

### H4 — cross-path coupling

Lesioning one BODY edge may alter source-side state associated with another BODY
pair.

If observed, this would reveal coupling that was not visible in SQ-09's
preserved DN endpoint.

## Claim boundary

SQ-10 is a computational source-state experiment.

It does not establish:

- biological necessity;
- biological sufficiency;
- organism-level perception;
- cognition;
- behavior;
- consciousness;
- financial predictive value.

## Authorization boundary

This handoff authorizes:

- code inspection;
- measurement-contract design;
- evidence-schema design;
- verifier design;
- tests;
- preregistration drafting.

It does not authorize neural execution.

## Reserved future codename

`YOU ARE BUGS`

Reserved for a future MoscaQuant experiment.

Do not assign this codename to SQ-10 or consume it for routine follow-up work.

Science first.

Lulz a very close second.
