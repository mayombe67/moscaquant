# MQ-5.5 — Convergence and Specificity Protocol

Status:

**PRE-REGISTERED / OUTCOMES NOT YET GENERATED**

## Purpose

MQ-5.5 tests convergent-input specificity using the three responder systems
defined in the frozen MQ-5.1 protocol.

The experiment asks whether perturbing both preserved causal inputs produces
a downstream effect that differs from perturbing either input alone.

No assumption of additivity, synergy, redundancy, or equal input strength is
made before outcome generation.

## Frozen convergent systems

### Responder 55

`44274 → 55`

`55925 → 55`

Frozen causal frame:

`F146`

### Responder 51

`55548 → 51`

`87441 → 51`

Frozen causal frame:

`F149`

### Responder 129

`92657 → 129`

`93484 → 129`

Frozen causal frame:

`F148`

These systems were specified in MQ-5.1 before MQ-5 intervention outcomes
were generated.

## Intervention classes

For each convergent system, execute:

1. baseline
2. zero-effect sham
3. input A alone
4. input B alone
5. inputs A and B together

For A-only, B-only, and combined A+B interventions, use:

- 25% attenuation
- 50% attenuation
- 75% attenuation
- 100% attenuation

Combined intervention means both predefined inputs receive the same
attenuation level during their frozen causal frame.

No structural connectome weights are modified.

Interventions remain runtime overlays on presynaptic effective activity.

## Primary measurements

For the predefined responder, record:

- first positive frame
- peak frame
- peak voltage
- integrated positive voltage
- positive-frame count
- target spike count

For the perturbed inputs, record effective activity at the intervention
frame so manipulation magnitude can be verified directly.

## Primary directional comparison

For each attenuation level define:

`E_A`

as the reduction in target integrated positive voltage after perturbing
input A alone.

`E_B`

as the reduction after perturbing input B alone.

`E_AB`

as the reduction after perturbing both inputs together.

Reductions are expressed as positive magnitudes for descriptive comparison:

`E = baseline integrated positive voltage - intervention integrated positive voltage`

The primary combined-input question is:

Does `E_AB` exceed the effect of either individual perturbation?

Descriptive rule:

`E_AB > max(E_A, E_B)`

is reported as:

**combined perturbation exceeds either single-input perturbation**

Failure to satisfy this relationship is reported directly.

It is not reclassified post hoc.

## Additive reference

The descriptive additive reference is:

`E_A + E_B`

The experiment will report the difference:

`E_AB - (E_A + E_B)`

This quantity is descriptive only.

MQ-5.5 does not preregister a statistical null distribution or equivalence
tolerance for additivity.

Therefore this phase must not label outcomes as statistically:

- synergistic
- antagonistic
- subadditive
- superadditive

Those terms require a separately preregistered statistical decision rule.

## Dose-response question

For the combined A+B intervention, increasing attenuation from 25% through
100% is expected to produce downstream change in the predicted direction.

The observed combined dose series must be reported whether monotonic or not.

No success threshold may be introduced after outcome inspection.

## Existing single-node results

MQ-5.3 already contains individual perturbation results for all six causal
inputs.

MQ-5.5 may compare against those immutable results for consistency.

The MQ-5.5 runner will nevertheless execute the required single-input
conditions alongside the combined-input conditions so that all convergence
comparisons are produced under one explicit experiment artifact.

## Controls and validation

Required validation gates:

- baseline execution
- exact baseline/sham identity
- intervention telemetry verification for both input nodes
- deterministic full-silencing replicate
- frozen-artifact hash invariance

A validation failure stops interpretation.

## Temporal interpretation

MQ-5.2 showed that causal effects frequently extend beyond a single frozen
causal frame.

MQ-5.5 does not test single-frame temporal exclusivity.

The frozen causal frames are used as the predefined intervention points for
the convergence experiment.

Any later multi-frame or timing-window convergence experiment must be
separately preregistered.

## Result reporting

Each convergent responder will report:

- A-only effect
- B-only effect
- combined A+B effect
- whether combined exceeds either single input
- descriptive additive reference
- combined minus additive-reference difference
- dose-response behavior
- onset and peak changes
- validation status

All three responder systems must be retained regardless of effect size or
direction.

Negative, null, and inconvenient outcomes are part of the result.

## Scope limits

Successful convergence effects establish behavior within the frozen
MoscaQuant simulation.

They do not establish equivalent biological causality in living Drosophila.

They do not establish financial usefulness.

Financial semantics remain:

**NOT ASSIGNED**
