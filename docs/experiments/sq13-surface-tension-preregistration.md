# SQ-13 — SURFACE TENSION

## Status

**PREREGISTERED / ANALYSIS ONLY / PRE-RESULT**

No new neural execution is authorized.

SQ-13 operates only on already-sealed SQ-11 evidence and the sealed SQ-12
transmission-gate result.

## Antecedent

SQ-12 RESONANCE CASCADE established:

`TRANSMISSION_GATE_CLOSED_192_FRAMES`

The three BODY responders are outside the frozen graded population.

Under the frozen runtime, non-graded neurons transmit through spike state only.

Across all eight BODY masks and all 192 frames:

- BODY source P2 effective activity remained exact;
- BODY responder firing remained exact;
- BODY responder committed spike state remained exact.

The local BODY perturbations therefore did not acquire a transmissible state
during the frozen episode.

## Scientific question

How much decision-boundary margin protected the closed transmission gate?

SQ-13 measures how near the already-observed local BODY responder perturbations
came to changing the frozen binary firing decision.

It does not attempt to open the gate.

## Frozen evidence

Primary evidence:

`artifacts/experiments/sq11-dark-forest/sq11-dark-forest-evidence-v2.npz`

SHA-256:

`cef49b5e581d6c9b2f21aafc701d06e8d53b0abc03f8453c9fe6c5d19ede9c37`

SQ-12 transmission-gate audit:

`artifacts/experiments/sq12-resonance-cascade/sq12-transmission-gate-audit-v1.json`

SHA-256:

`916cb99c1bec589467c6ab6fbff79289d0d0d52c6e2110e95b4d7964f24dd065`

SQ-12 independent verification:

`artifacts/experiments/sq12-resonance-cascade/sq12-transmission-gate-verification-v1.json`

SHA-256:

`8cf58f322a397e6a5bd0798d64c450661655f0e2afa9b49fed000c93c716c353`

SQ-12 result seal:

`artifacts/experiments/sq12-resonance-cascade/sq12-resonance-cascade-result-seal-v1.json`

SHA-256:

`c67db35a6fec7adc5855f9310651caa3bd731c63647696814c59366cf27b0faf`

## Frozen threshold

The authoritative frozen firing threshold is:

`1.0`

The SQ-13 analyzer must independently verify the bound runtime semantics before
interpreting evidence.

No threshold may be estimated, optimized or selected from the result.

## BODY coordinates

BODY order:

- A: source `65084` -> responder `137122`
- B: source `128590` -> responder `317`
- C: source `135589` -> responder `126002`

## Matched contrasts

SQ-13 inherits the 12 single-edge matched contrasts used by SQ-10 and SQ-11.

### BODY A

- `000 -> 100`
- `001 -> 101`
- `010 -> 110`
- `011 -> 111`

### BODY B

- `000 -> 010`
- `001 -> 011`
- `100 -> 110`
- `101 -> 111`

### BODY C

- `000 -> 001`
- `010 -> 011`
- `100 -> 101`
- `110 -> 111`

Mask semantics:

- `0` = BODY edge retained
- `1` = BODY edge structurally omitted

No post-result contrast selection is permitted.

## Authoritative fields

SQ-13 uses only already-preserved SQ-11 fields:

- `responder_voltage_pre_threshold` — P5 float32;
- `responder_fired` — P6 uint8;
- `responder_spikes_post_commit` — P7 uint8.

The analyzer must also verify deterministic r1/r2 equality.

No missing runtime state may be reconstructed.

## P5-divergent frame

For one matched contrast and its tested BODY responder, a P5-divergent frame is:

`retained_P5 != lesioned_P5`

using exact stored float32 equality.

No epsilon or tolerance is used to define divergence.

## Decision-boundary distance

For every P5-divergent frame:

`retained_distance = abs(float64(retained_P5) - 1.0)`

`lesioned_distance = abs(float64(lesioned_P5) - 1.0)`

Define:

`decision_boundary_distance = min(retained_distance, lesioned_distance)`

This is the distance of the nearer observed state to the frozen firing
threshold.

It is descriptive.

It is not a counterfactual intervention magnitude.

## Primary endpoint

The primary endpoint is:

`minimum_decision_boundary_distance`

defined as the minimum decision-boundary distance across every P5-divergent
frame in all 12 matched contrasts.

The analyzer must report:

- BODY identity;
- retained mask;
- lesioned mask;
- frame;
- retained P5 value;
- lesioned P5 value;
- retained firing state;
- lesioned firing state;
- absolute P5 difference;
- decision-boundary distance.

Ties are resolved by:

1. frozen contrast order;
2. earliest frame.

## Scale separation

At the primary endpoint, report descriptively:

`scale_separation =
    decision_boundary_distance / abs(retained_P5 - lesioned_P5)`

when the denominator is nonzero.

This value must not be interpreted as:

- a causal multiplier;
- the weight change required to trigger firing;
- a prediction under scaled perturbation;
- evidence for linear extrapolation.

## Consistency gate

For every used stored state, independently verify:

`responder_fired == (responder_voltage_pre_threshold >= 1.0)`

and:

`responder_fired == responder_spikes_post_commit`

Any disagreement refuses interpretation.

## Prospective classifications

Exactly one primary classification must be emitted.

### TRANSMISSION_GATE_CONTRADICTION

Any matched contrast contains a P6 or P7 firing-state difference.

This contradicts the inherited SQ-12 closed-gate result and terminates normal
SQ-13 interpretation.

### NO_P5_PERTURBATION

No tested matched contrast contains a P5-divergent frame.

### GATE_TOUCHES_DECISION_BOUNDARY

P5 divergence exists, all firing decisions remain equal, and:

`minimum_decision_boundary_distance == 0.0`

### GATE_CLOSED_WITH_POSITIVE_DECISION_MARGIN

P5 divergence exists, all firing decisions remain equal, and:

`minimum_decision_boundary_distance > 0.0`

No post-result numerical threshold may be introduced.

## Secondary reporting

For each BODY and each matched contrast report:

- number of P5-divergent frames;
- first divergent frame;
- last divergent frame;
- maximum absolute P5 difference;
- minimum decision-boundary distance;
- frame of minimum decision-boundary distance;
- observed side of threshold at that frame.

Secondary quantities may not redefine the primary classification.

## Deterministic duplication

r1 and r2 must be exactly identical for every SQ-13-used evidence field.

The duplicate runs are integrity controls.

They are not independent statistical samples.

Any mismatch refuses interpretation.

## Numerical boundary

Stored P5 values are authoritative float32 values.

Distance calculations may promote those already-selected values to float64.

No:

- epsilon;
- smoothing;
- interpolation;
- fitted threshold;
- post-result numerical floor

may be introduced.

## Explicit exclusions

SQ-13 does not test:

- larger BODY weights;
- injected responder voltage;
- changed firing thresholds;
- altered graded-population membership;
- longer episodes;
- changed runtime dynamics;
- new plasticity;
- reinforcement;
- downstream execution.

Any attempt to deliberately open the transmission gate is a separate causal
experiment requiring new preregistration.

## Interpretation boundary

SQ-13 describes the robustness of the already-observed computational firing
decision.

It does not establish the magnitude of intervention needed to cross the
threshold.

It does not assume the local effect scales linearly.

## Claim boundary

SQ-13 cannot establish:

- biological robustness;
- organism behavior;
- perception;
- cognition;
- consciousness;
- biological learning;
- market intelligence;
- prediction;
- financial value.

The result applies only to the frozen MoscaQuant computational model and the
stored 192-frame episode.

## Stopping rule

SQ-13 stops after:

1. frozen provenance is verified;
2. deterministic duplicate equality is verified;
3. all 12 matched contrasts are analyzed;
4. the consistency gate passes;
5. exactly one prospective classification is emitted;
6. an independently implemented verifier reproduces the classification and
   primary endpoint;
7. the result is sealed.

No new neural execution is authorized.

## Narrative designation

**SURFACE TENSION**

The name describes the decision-boundary question.

It does not imply that the responder was close to firing.

A very large positive margin is as valid as a near-threshold result.

## Apotheosis watch

APOTHEOSIS #27 remains inherited:

**FUNCTIONAL TRANSMISSIBILITY BEFORE STRUCTURAL REACHABILITY**

SQ-13 does not pre-assign another Apotheosis number.

A new Apotheosis may be promoted only if the completed evidence exposes a
genuinely reusable scientific or engineering rule.

Science first.

Lulz a very close second.
