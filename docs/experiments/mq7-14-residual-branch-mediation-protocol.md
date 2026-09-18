# MQ-7.14 Residual Branch Mediation Protocol

## Research question

Do the highest-ranked residual first-hop branches from neuron 68045 mediate
the remaining perturbation-dependent SC-03 effect after the previously
validated 68045 -> 1273 pathway?

## Background

MQ-7.12 showed that functional removal of:

68045 -> 1273

reduced the DN-C1 plasticity-expression magnitude by approximately 34.3%.

MQ-7.13 then ranked short residual structural routes from neuron 68045 toward
the DN-C1 population.

The three highest-ranked repeated intermediate nodes were:

1. 18444
2. 107
3. 6647

These candidates were selected before causal testing.

## Frozen replay

Market condition:

B

SHOCK target:

56393

SC-03 plasticized edge:

56393 -> 68045

Plasticity multiplier:

0.95

Intervention generation:

32

## Primary branch candidates

Test functional ablation of:

68045 -> 18444

68045 -> 107

68045 -> 6647

Each edge is tested independently.

A cumulative condition also removes all three branches simultaneously.

## Negative-control branch

Choose mechanically from non-zero outgoing edges of neuron 68045:

- exclude 1273;
- exclude 18444, 107, and 6647;
- exclude every intermediate node appearing in the MQ-7.13 top-25 residual
  routes;
- among remaining edges choose greatest absolute baseline weight;
- ties resolve by lowest postsynaptic model index.

The control identity is not selected manually.

## Comparisons

For every lesion condition L:

L0:
- SHOCK 56393
- lesion L
- no SC-03 plasticity

LP:
- identical SHOCK
- identical lesion
- SC-03 multiplier 0.95

The plasticity-expression magnitude is:

abs(DN-C1 score difference between L0 and LP)

## Baseline

The intact-route effect must reproduce approximately:

1.1174368270910759e-08

before lesion effects are interpreted.

## Measurements

For each condition record:

- voltage equality;
- spike equality;
- score equality;
- decision equality;
- DN-C1 score delta;
- absolute DN-C1 effect magnitude;
- attenuation relative to intact;
- structural connectome digest.

## Interpretation

Selective attenuation after removal of a ranked branch supports partial
mediation through that branch.

Greater attenuation under cumulative removal supports distributed residual
routing through multiple branches.

A null branch lesion is a valid result.

No individual branch is assumed causal in advance.

## Claims excluded

This experiment does not establish:

- exclusive pathway usage;
- biological learning in a living organism;
- subjective experience;
- financial utility;
- improved trading performance;
- formal biological network equivalence.
