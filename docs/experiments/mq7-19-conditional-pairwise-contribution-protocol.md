# MQ-7.19 Conditional Pairwise Contribution Protocol

## Research question

For the three strongest supra-independent pairs identified in MQ-7.18, does
either route account for a larger fraction of the remaining DN-C1 effect when
its partner route is already absent?

## Motivation

MQ-7.18 established that several first-wave pairs produce more attenuation than
predicted by the independent-residual null.

The strongest three frozen pairs were:

1. 62598 + 77298
2. 62598 + 79672
3. 79672 + 77298

MQ-7.19 asks whether the pairwise excess can be described more precisely as
conditional route dependence.

It does not assume biological compensation.

## Frozen parent experiment

MQ-7.19 reuses the MQ-7.18 / MQ-7.17 replay machinery without changing:

- market condition B
- SHOCK target 56393
- intervention generation 32
- plasticized edge 56393 -> 68045
- plasticity multiplier 0.95
- functional lesion implementation
- DN-C1 effect metric
- structural connectome

## Frozen pair set

Only these pairs are tested:

- 62598 + 77298
- 62598 + 79672
- 79672 + 77298

The pair set was frozen directly from the three highest positive interaction
excess values in MQ-7.18.

No replacement or post-hoc pair selection is permitted.

## Conditions per pair

For pair A/B, measure:

- intact
- A alone
- B alone
- A+B

The implementation reruns these conditions under the frozen replay rather than
relying on rounded prose values.

## Conditional residual contribution

Let:

A = attenuation from lesion A alone
B = attenuation from lesion B alone
AB = attenuation from lesion A+B

The fraction of the residual effect removed by B after A is already absent is:

B_given_A =
    (AB - A)
    /
    (1 - A)

Likewise:

A_given_B =
    (AB - B)
    /
    (1 - B)

These values are compared with the corresponding standalone attenuations.

## Conditional gain

For direction B given A:

conditional_gain_B_given_A =
    B_given_A - B

For direction A given B:

conditional_gain_A_given_B =
    A_given_B - A

Positive conditional gain means the route accounts for a larger fraction of the
remaining effect when its partner is absent than it did in the intact context.

Negative conditional gain means the route accounts for a smaller fraction.

## Interpretation

Positive conditional gain is compatible with compensation-like or
supra-independent conditional dependence within the model.

It is not sufficient to claim biological compensation.

Because the pair lesion is symmetric, MQ-7.19 uses directional conditional
normalization only to express each branch relative to the residual left by its
partner. It does not claim temporal adaptation or rewiring.

## Replication requirement

The MQ-7.19 rerun must reproduce the corresponding MQ-7.18 single and pair
attenuations within numerical tolerance before conditional metrics are
interpreted.

## Null control

The validated null edge:

68045 -> 82348

is paired with each unique branch appearing in the frozen MQ-7.19 pair set.

Its conditional gain should remain at numerical zero under the frozen replay.

## Claims excluded

MQ-7.19 does not establish:

- biological compensation
- dynamic rerouting after injury
- synaptic rewiring
- biological learning
- subjective experience
- generalization beyond the frozen replay
- financial utility
- improved trading performance

## Status

COMPLETE — CONDITIONAL COMPENSATION-LIKE DEPENDENCE SUPPORTED
