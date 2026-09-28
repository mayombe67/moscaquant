# SQ-11 — DARK FOREST

Status: PREREGISTERED / PRE-EXECUTION

## Antecedent

SQ-10 — SOPHON prospectively tested 12 matched BODY-edge contrasts.

All 12 contrasts were classified:

`DIRECT_EFFECT_BELOW_CALIBRATED_RESOLUTION`

SQ-10 nevertheless observed all of the following:

- every tested source P2 trajectory remained exactly invariant;
- every off-target BODY source remained exactly invariant;
- every off-target BODY responder remained exactly invariant;
- each lesion changed only its paired responder;
- the first responder divergence occurred at:
  - BODY B: frame 124
  - BODY A: frame 125
  - BODY C: frame 127;
- the first-divergence responder delta was extremely close to the
  corresponding algebraic source-activity × edge-weight term.

SQ-10 could not classify those amplitudes as resolved because every predicted
direct effect was below its prospectively frozen absolute numerical tolerance
of:

`3.814697265625e-06`

The sealed SQ-10 evidence SHA-256 is:

`4b2b6ce2b16aae51aa222853786ee1308d51b944913000e8d810cd72930d9360`

The sealed SQ-10 primary-analysis SHA-256 is:

`0797eae1c450a004d9e8e279f036245f129f8319c39b5de83c110ada3affa0c4`

SQ-10 primary analysis was sealed at commit:

`4aa3a6a`

## Scientific question

Can each BODY-edge intervention's first synaptic effect be exactly reconstructed
from the corresponding responder's actual local presynaptic P2 state and the
frozen CSR row arithmetic?

The purpose is to distinguish:

1. the algebraic direct BODY-edge term;
2. float32 accumulation-path effects created after that term changes the row
   accumulator;
3. source-state or recurrent effects;
4. cross-path effects;
5. failure of the proposed local numerical reconstruction.

## Inherited intervention

SQ-11 does not introduce a new neural intervention.

It inherits the SQ-10 / SQ-08 2^3 BODY-edge cube exactly:

- `000`
- `001`
- `010`
- `011`
- `100`
- `101`
- `110`
- `111`

Each mask has deterministic replicates:

- r1
- r2

Total work units:

`16`

Mask semantics remain:

- `0` = BODY edge retained
- `1` = BODY edge removed

BODY identities remain:

- A: 65084 -> 137122
- B: 128590 -> 317
- C: 135589 -> 126002

No new lesion semantics are permitted.

## Frozen stimulus and runtime

Layout:

`RL`

Frame count:

`192`

The existing frozen neural runtime remains unchanged.

SQ-11 instrumentation must be observational only.

It must not:

- change connectome values;
- change stimulus values;
- change update order;
- change runtime precision;
- change thresholding;
- change resetting;
- alter activity;
- alter synaptic current;
- introduce a new neural state.

## Why P3

The BODY intervention first enters the neural update through synaptic matrix
multiplication.

SQ-10 measured source effective activity at P2 and responder voltage at P5.

SQ-11 adds direct observation of the BODY responder aggregate synaptic input at
P3.

P3 is the earliest phase at which the BODY-edge intervention can directly alter
the responder.

This removes later voltage decay, stimulus addition, thresholding and reset
from the primary numerical localization question.

## New local-state measurement

For each frame SQ-11 must preserve:

1. P2 effective activity for the union of all presynaptic neurons appearing in
   the frozen CSR rows of the three BODY responders;
2. the static ordered CSR column indices for each BODY responder row;
3. the static float32 CSR weights for each BODY responder row;
4. the exact BODY-edge CSR position within each row;
5. captured runtime P3 aggregate synaptic input for each BODY responder;
6. the three BODY source P2 trajectories;
7. BODY responder P5/P6/P7 measurements retained for continuity with SQ-10.

The local presynaptic union must be derived from the frozen connectome before
execution and then frozen by evidence schema.

## Local float32 replay

A separate SQ-11 local replay implementation must reconstruct each BODY
responder's P3 synaptic accumulation from:

- the recorded P2 local activity;
- frozen CSR indices;
- frozen CSR float32 weights;
- frozen row ordering.

Replay arithmetic must be frozen before SQ-11 execution.

The replay must not import or call the frozen neural runtime.

The replay must not use SQ-11 result values to select an arithmetic method.

## Numerical qualification before execution

Before neural execution, the proposed local replay implementation must undergo
a fixed synthetic qualification against the frozen sparse-matrix numerical
path.

Qualification inputs and pass/fail rules must be frozen before qualification.

The qualification is not permitted to inspect SQ-11 neural evidence.

The intended primary replay criterion is exact float32 equality.

If exact replay parity cannot be prospectively qualified, SQ-11 execution must
not proceed under this preregistration.

No post-result tolerance may be introduced as a substitute.

## Matched contrasts

SQ-11 uses the same 12 single-bit matched contrasts as SQ-10.

BODY A:

- 000 -> 100
- 001 -> 101
- 010 -> 110
- 011 -> 111

BODY B:

- 000 -> 010
- 001 -> 011
- 100 -> 110
- 101 -> 111

BODY C:

- 000 -> 001
- 010 -> 011
- 100 -> 101
- 110 -> 111

All 12 contrasts are mandatory.

No post-result contrast selection is permitted.

## First P3 divergence

For each matched contrast, first P3 divergence is the earliest frame where the
tested responder's retained and lesioned captured runtime P3 float32 values are
not exactly equal.

If no P3 divergence occurs during the 192-frame episode, the contrast is
classified `NO_P3_DIVERGENCE`.

## Source-state gate

For a tested BODY edge, its source P2 trajectory must remain exactly identical
between retained and lesioned conditions through and including the first P3
responder divergence.

If the tested source diverges before or at that frame, classify:

`SOURCE_STATE_DIVERGES_BEFORE_OR_AT_P3`

and do not make a direct-local attribution for that contrast.

## Replay gate

At every frame required for the primary comparison, the local replay must
exactly reproduce the captured runtime P3 value for both the retained and
lesioned condition.

Exact means exact float32 equality.

Any mismatch produces:

`LOCAL_REPLAY_MISMATCH`

No tolerance substitution is allowed.

## Primary numerical decomposition

At the first P3 divergence frame:

`runtime_delta =
    float64(retained_P3) - float64(lesioned_P3)`

The algebraic BODY-edge term is:

`direct_term =
    float64(retained_source_P2) * float64(body_edge_weight)`

Because both operands originate as float32 values, float64 multiplication is
used as the high-precision representation of the algebraic edge term.

Define:

`rounding_path_residual =
    runtime_delta - direct_term`

The residual is reported quantitatively.

It is not compared against an empirically selected post-result tolerance.

## Prospective primary classifications

Exactly one primary class must be emitted per contrast.

### DIRECT_TERM_EXACT_FLOAT32

Requirements:

- P3 responder divergence exists;
- tested source P2 is invariant through that divergence;
- retained local replay exactly equals captured retained P3;
- lesioned local replay exactly equals captured lesioned P3;
- `rounding_path_residual == 0.0`.

Interpretation:

Within the frozen computational model, the first P3 effect equals the
algebraic direct BODY-edge term exactly at the stored numerical precision.

### DIRECT_TERM_WITH_FLOAT32_ROUNDING_PATH

Requirements:

- P3 responder divergence exists;
- tested source P2 is invariant through that divergence;
- retained local replay exactly equals captured retained P3;
- lesioned local replay exactly equals captured lesioned P3;
- `rounding_path_residual != 0.0`.

Interpretation:

Within the frozen computational model, the complete first P3 effect is
reconstructed from the local responder row and recorded presynaptic state, but
float32 accumulation causes the runtime effect to differ numerically from the
isolated algebraic BODY-edge term.

The residual must be reported.

### SOURCE_STATE_DIVERGES_BEFORE_OR_AT_P3

The tested source P2 state changes before or at first P3 responder divergence.

Direct-local attribution is refused.

### LOCAL_REPLAY_MISMATCH

The prospectively frozen local replay fails to reproduce captured runtime P3
exactly.

Direct-local attribution is refused.

### NO_P3_DIVERGENCE

No tested responder P3 divergence occurs during the episode.

## Secondary observations

SQ-11 also records:

- first off-target BODY-source P2 divergence;
- first off-target BODY-responder P3 divergence;
- first off-target BODY-responder P5 divergence;
- P5/P6/P7 timing for continuity with SOPHON;
- direct-term magnitude;
- runtime P3 delta magnitude;
- rounding-path residual magnitude.

These are secondary.

They may not redefine the primary classification after results are observed.

## Cross-path interpretation

If off-target BODY sources or responders diverge, that fact must be reported.

Absence of off-target divergence supports spatial isolation only within the
frozen measured BODY system.

It does not establish organism-level independence.

## Deterministic replication

r1 and r2 for every mask must agree exactly on every field declared
deterministic.

The duplicate runs are integrity controls.

They are not independent statistical samples and must not be counted as N=2.

Any deterministic mismatch invalidates primary interpretation.

## Claim boundary

SQ-11 may support claims about the causal and numerical behavior of the frozen
MoscaQuant computational model.

SQ-11 cannot by itself establish:

- biological necessity;
- biological sufficiency;
- organism-level behavior;
- perception;
- intention;
- consciousness;
- fear;
- choice;
- market prediction;
- financial value.

A direct-local computational mechanism must not be promoted into a biological
claim.

## Stopping rule

SQ-11 stops after:

1. replay arithmetic is prospectively frozen;
2. replay qualification passes;
3. the complete 16-work-unit cube executes;
4. all deterministic duplicate pairs pass;
5. evidence closes under the frozen schema;
6. independent evidence verification passes;
7. the preregistered analyzer classifies all 12 contrasts;
8. the result is sealed.

No additional conditions or numerical rules may be introduced after inspecting
SQ-11 results.

Any new hypothesis becomes a new experiment.

## Canonical rule

Science first.

Lulz a very close second.
