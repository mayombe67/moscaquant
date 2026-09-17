# CONF-004A — Sensory-Encoding Robustness:
# Robust Causal Normalization

Status:

**PRE-REGISTERED / OUTCOMES NOT YET GENERATED**

## Purpose

CONF-004A tests whether the principal MQ-5 causal-intervention findings
depend on the original market-feature normalization rule.

The neural substrate remains frozen.

The experiment changes one sensory-encoding assumption while holding the
remaining pipeline fixed.

## Encoder A

The existing frozen pipeline uses:

- the existing seven descriptive market features
- causal rolling normalization
- rolling mean and standard deviation
- bounded transformation using `tanh(z)`
- the frozen retinal territory mapping
- the frozen temporal market encoder
- the frozen sensory gain

Encoder A remains unchanged.

## Encoder B

Encoder B replaces only the causal normalization stage.

It uses a causal robust location and scale estimate derived exclusively
from previous observations:

- location: rolling median
- scale: rolling median absolute deviation
- Gaussian-consistency factor: `1.4826`
- bounded output: `tanh(robust_z)`
- same history window as Encoder A
- same warm-up requirement as Encoder A
- same zero output during insufficient-history warm-up

For feature value `x`:

`robust_z = (x - median(history)) / max(1.4826 * MAD(history), epsilon)`

and:

`normalized = tanh(robust_z)`

The current observation is transformed before it is appended to history.

No future observations may enter the normalization state.

## Held constant

CONF-004A must not alter:

- raw synthetic market observations
- market feature definitions
- asset ordering
- frozen retinal territories
- retinal population
- temporal encoder
- temporal jitter pattern
- motion rule
- volatility timing rule
- entropy timing rule
- sensory gain
- connectome
- physiology runtime
- MQ-5 intervention runtime
- frozen causal source/target identities
- frozen matched-control node identities
- outcome metrics

Therefore this experiment isolates normalization robustness rather than
testing all possible sensory encodings at once.

## Frozen causal set

The same 13 causal source/target relationships from MQ-3/MQ-5 are tested.

No causal edge may be replaced because another edge performs better under
Encoder B.

No causal discovery is performed in CONF-004A.

## Engagement audit

Before interpreting interventions, Encoder B must record whether each frozen
causal source has positive effective activity at its original frozen causal
frame.

Each edge receives one of two engagement states:

- `ENGAGED`
- `NOT_ENGAGED_AT_FROZEN_FRAME`

A source that is not engaged under Encoder B is not automatically counted
as a causal failure.

Instead it is reported as an encoding-dependent lack of circuit engagement.

The original frozen causal frame must not be moved after inspecting Encoder
B merely to recover a desired result.

A later experiment may preregister an alternative temporal-alignment rule,
but CONF-004A will not do so.

## Primary robustness questions

For each engaged causal edge:

1. Does increasing source attenuation produce target change in the
   originally predicted direction?
2. Is the four-level dose series monotonic?
3. Where the already-frozen matched control is also engaged and valid under
   Encoder B, does causal-source full silencing produce a larger effect than
   matched-control full silencing?

The original matched-control model indices remain fixed.

No replacement matched control may be selected after Encoder B is run.

If a frozen matched control is inactive under Encoder B, the matched-control
comparison is reported as unavailable under Encoder B.

## Pathway robustness

The frozen path remains:

`56393 → 68045 → 1273`

CONF-004A will report whether:

- 56393 is engaged at F146
- upstream attenuation changes 68045 in the predicted direction
- 68045 effective activity at F147 changes accordingly
- 1273 changes downstream in the predicted direction

If the pathway is not engaged under Encoder B, that fact is retained.

No replacement pathway is selected.

## Convergence robustness

The frozen systems remain:

`44274 + 55925 → 55`

`55548 + 87441 → 51`

`92657 + 93484 → 129`

For systems whose two inputs are engaged under Encoder B, CONF-004A will
report whether:

- A-only perturbation changes the target
- B-only perturbation changes the target
- combined perturbation exceeds either single perturbation
- combined attenuation remains dose ordered

No statistical synergy classification is assigned.

## Interpretation categories

CONF-004A may produce several scientifically valid outcomes.

### Robust

The relevant frozen finding remains directionally supported under Encoder B.

### Encoding-sensitive magnitude

The qualitative causal finding remains, but effect magnitude changes
substantially.

### Not engaged under Encoder B

The frozen source/path/input is inactive at the predefined frame under the
alternative normalization.

This is evidence of encoding-dependent circuit recruitment and is not
silently converted into either confirmation or causal failure.

### Directional failure under Encoder B

The circuit is engaged, but the predefined intervention does not change the
target in the preregistered direction.

This is retained as evidence against robustness of that finding.

## Aggregate reporting

CONF-004A will report at minimum:

- engaged causal edges / 13
- monotonic dose responses among engaged edges
- directional effects among engaged edges
- usable frozen matched controls under Encoder B
- causal-source versus matched-control comparisons
- pathway engagement and propagation status
- convergence-system engagement and result status

No aggregate success threshold is chosen after results are observed.

## Scope

Passing CONF-004A supports robustness to this specific normalization
alternative.

It does not establish invariance to all possible market-to-sensory
encodings.

A more structurally distinct encoding may be tested later as CONF-004B.

Biological causality:

**NOT CLAIMED**

Financial semantics:

**NOT ASSIGNED**
