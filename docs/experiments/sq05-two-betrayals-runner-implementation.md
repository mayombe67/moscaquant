# SQ-05 — TWO BETRAYALS — Authoritative Runner Implementation

**Narrative:** ASSAULT ON THE CONTROL ROOM — presentation only
**Status:** IMPLEMENTATION FREEZE CANDIDATE — RESULT EXECUTION NOT AUTHORIZED
**Execution candidate:** Habitat / local
**RASPUTIN:** not recruited by this implementation

## Purpose

This implementation turns the already-frozen SQ-05 stimulus, BETRAYAL I,
BETRAYAL I sham, BETRAYAL II seed block, endpoint definitions, and
classification rules into one fail-closed authoritative runner.

It does not authorize the result-bearing run.

## Capacity decision

The pre-implementation capacity audit measured the current Habitat host before
this runner was created:

- total RAM: `7.433 GiB`
- available RAM: `3.787 GiB`
- data-root free disk: `413.052 GiB`
- 192-frame neutral full-connectome benchmark: `4.703143 s`
- benchmark process peak RSS: `0.240925 GiB`
- projected 52-episode neural time from that benchmark: `4.08 min`
- historical full-connectome strict-null construction already completed
  successfully on Habitat.

Therefore this implementation selects **local** as the runtime candidate.
RASPUTIN remains available only if a later preflight invalidates the local
capacity assumptions.

These measurements are operational evidence, not scientific endpoints.

## Episode order

The result-bearing execution is exactly 52 neural episodes.

Deterministic gate first:

- `INTACT`: LR x2, RL x2
- `BETRAYAL_I_LESIONED`: LR x2, RL x2
- `BETRAYAL_I_SHAM`: LR x2, RL x2

All six deterministic arm/layout pairs must replay exactly before BETRAYAL II
begins.

Then BETRAYAL II:

- seeds `20265100..20265119`
- each topology is built exactly once
- each built topology is evaluated in LR and RL
- no early stopping
- no failed-seed replacement.

## Runtime semantics

Every neural episode constructs a fresh
`PhysiologyConstrainedVisualTransductionRuntime` using the already-established
frozen relay, graded population, release gain, and connectome semantics.

The runner does not introduce a second neural-dynamics implementation.

SQ-05 stimuli are generated only through the frozen `brain.sq05_stimulus`
module.

BETRAYAL I is built only through the frozen `brain.sq05_betrayal_i` adapter.

BETRAYAL II is built only through the frozen `brain.sq05_betrayal_ii` adapter.

The sham loads the exact 13 edge identities from the frozen sham artifact and
zeros those exact weights. It is not re-derived at execution.

## Result sidecar

Dense traces do not go into JSON.

The binary NPZ sidecar stores all 52 episodes, including:

- the fixed 1,191 DN indices;
- full 192-frame positive-voltage fingerprints;
- full DN spike traces;
- per-frame DN-C0/C1/C2 mean-positive-voltage traces;
- positive-neuron fractions;
- spike counts and rates;
- arm/layout/seed/replicate metadata.

The manifest contains provenance, classifications, strict-null diagnostics,
sidecar SHA-256, and claim boundaries.

## Newly resolved implementation ambiguities

The core preregistration intentionally froze the endpoint mathematics before
outcomes, but two runner-level choices still needed an exact operational
binding. This implementation resolves them before any SQ-05 result:

1. Cue-transition status is evaluated on `INTACT` replicate 1 after duplicate
   equality has passed.
2. BETRAYAL II channel-summary exact reproduction uses the same
   normalized-L2 (`<= 1e-9`) and maximum-absolute (`<= 1e-12`) tolerances as
   the primary fingerprint.

Both LR and RL remain mandatory.

## BETRAYAL I

The primary comparison is unchanged:

for each layout, compare lesion-to-INTACT primary-fingerprint distance with
sham-to-INTACT distance.

The accepted nine historical responders remain secondary diagnostics only.

## BETRAYAL II

A seed is an exact intact-response reproduction only when **both layouts**
pass:

- primary fingerprint normalized L2 `<= 1e-9`;
- primary fingerprint max absolute difference `<= 1e-12`;
- DN-C summary normalized L2 `<= 1e-9`;
- DN-C summary max absolute difference `<= 1e-12`.

If any of the 20 frozen seeds fails or is missing, BETRAYAL II status is
`INCOMPLETE_OR_INVALID`. No replacement seed is permitted.

## No overall winner

The runner reports three separate scientific statuses:

- cue transition;
- BETRAYAL I relative to sham;
- BETRAYAL II strict-null reproduction.

It does not synthesize them into one winner.

## Preflight and authorization

`--preflight-only` verifies frozen identities and output absence. It performs:

- no SQ-05 neural execution;
- no randomized topology construction;
- no preregistered seed execution.

`--run-frozen` remains blocked until a separate tracked authorization artifact
is committed. That artifact must bind:

- implementation commit;
- runner SHA-256;
- runner-config SHA-256;
- core-prereg SHA-256;
- result-schema SHA-256;
- capacity decision;
- execution mode `local`.

The authorization commit must be an ancestor of execution HEAD and the Git tree
must be clean.

## Claim boundary

The runner may report modeled network-response differences only.

It does not establish fruit recognition, hunger, danger, threat perception,
fear, behavior, biological causality, market prediction, or financial value.

## ASSAULT ON THE CONTROL ROOM

The door is open.

The Index is still not in the slot.
