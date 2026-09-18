# MQ-7 — SC-03 BAD SYNAPSE Plasticity Mechanics Results

Status:

**COMPLETED / MECHANICS VALIDATED**

## Pre-registration

This experiment was preregistered in:

`docs/experiments/mq7-bad-synapse-plasticity-protocol.md`

before implementation results were generated.

## Frozen pathway

The validated pathway was:

`56393 → 68045 → 1273`

Frozen timing:

- `56393 → 68045` at frame 146
- `68045 → 1273` at frame 147

The pathway had already been supported by MQ-5.4.

## Plasticity mechanism

The tested SC-03 mechanics used a multiplicative synaptic overlay:

`effective_weight = baseline_weight × 0.95`

Properties:

- update magnitude: -5%
- baseline connectome unchanged
- overlay represented separately
- no structural weight mutation
- deterministic behavior
- one eligible edge modified at a time

## Unit validation

Unit tests verified:

- frozen default multiplier of `0.95`;
- exact 5% reduction in selected edge contribution;
- unrelated targets remain unchanged;
- zero presynaptic activity produces zero adjustment;
- source activity is not mutated;
- connectome data are not mutated;
- nonexistent edges are rejected.

## Frozen-connectome integration validation

Both frozen pathway edges were tested independently against:

`connectome-baseline-v1.npz`

### Upstream edge

`56393 → 68045`

The overlay reduced the selected edge contribution to exactly:

`baseline contribution × 0.95`

The resulting postsynaptic change matched:

`baseline edge contribution × -0.05`

within the frozen numerical tolerance.

### Intermediate edge

`68045 → 1273`

The overlay reduced the selected edge contribution to exactly:

`baseline contribution × 0.95`

The resulting downstream change matched:

`baseline edge contribution × -0.05`

within the frozen numerical tolerance.

## Structural invariance

After both interventions:

- `connectome.data` was unchanged;
- `connectome.indices` was unchanged;
- `connectome.indptr` was unchanged.

The SC-03 mechanics therefore operate as an overlay rather than a rewrite of the frozen connectome.

## Test result

Full test suite:

**89 passed**

## Result classification

Bounded -5% synaptic overlay mechanics:

**SUPPORTED**

Selected-edge specificity:

**SUPPORTED**

Real-connectome propagation:

**SUPPORTED**

Frozen-connectome structural invariance:

**SUPPORTED**

Deterministic mechanics:

**SUPPORTED**

Live adaptive plasticity:

**NOT ACTIVATED**

Trading-loss credit assignment:

**NOT DEFINED**

Learning:

**NOT CLAIMED**

Biological synaptic depression in living Drosophila:

**NOT CLAIMED**

Financial utility:

**NOT CLAIMED**

## Live SC-03 status

This result validates only the mechanical implementation of the BAD SYNAPSE plasticity overlay.

It does not establish which pathway should receive negative plasticity after a trading loss.

Until a separate credit-assignment protocol is preregistered and validated:

`plasticity_active = false`

If SC-03 is selected during D6:

`NOT_APPLICABLE`

No reroll occurs.

A financial loss alone remains insufficient evidence that a particular synapse or pathway caused that loss.
