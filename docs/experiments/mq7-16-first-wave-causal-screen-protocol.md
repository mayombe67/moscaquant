# MQ-7.16 First-Wave Causal Screen Protocol

## Research question

Which first-wave activity-divergence nodes observed in MQ-7.15 causally mediate
the perturbation-dependent SC-03 effect on DN-C1?

## Background

MQ-7.15 dynamically traced the SC-03-dependent difference after SHOCK of neuron
56393 under market condition B.

The sequence was:

- generation 32: synaptic divergence begins at 68045;
- generation 33: activity divergence begins at 68045;
- generation 34: the first broader activity-divergence wave appears.

The first-wave candidate nodes are:

- 62598
- 66309
- 69484
- 63192
- 77298
- 65046
- 79672
- 73483
- 62142
- 61694

MQ-7.14 also established that:

68045 -> 82348

produces large early synaptic divergence but zero attenuation of the final
DN-C1 plasticity-expression effect.

That edge is retained as a known null control.

## Frozen replay

Market condition:

B

SHOCK target:

56393

Intervention generation:

32

Plasticized edge:

56393 -> 68045

Plasticity multiplier:

0.95

## Candidate screen

For every first-wave candidate C:

1. verify a non-zero baseline edge 68045 -> C exists;
2. functionally remove that edge contribution;
3. run SHOCK-only control;
4. run identical SHOCK + SC-03 plasticity;
5. measure attenuation of the DN-C1 plasticity-expression effect.

If a listed first-wave candidate has no direct edge from 68045, report it as:

NO_DIRECT_EDGE

and do not substitute another edge or node.

## Null control

Repeat the same procedure for:

68045 -> 82348

## Intact reference

The intact DN-C1 effect must reproduce approximately:

1.1174368270910759e-08

before causal results are interpreted.

## Measurements

Per candidate record:

- direct baseline weight from 68045;
- voltage equality;
- spike equality;
- score equality;
- decision equality;
- DN-C1 score delta;
- absolute DN-C1 effect;
- attenuation relative to intact.

## Interpretation

A candidate with positive attenuation is evidence that the tested direct
68045 -> candidate contribution mediates some fraction of the measured DN-C1
effect.

A candidate with zero attenuation may still participate in network dynamics but
does not measurably mediate this output under the frozen replay.

Candidates must not be ranked causally before this experiment is complete.

## Claims excluded

This experiment does not establish:

- exclusive pathway usage;
- biological learning in a living organism;
- subjective memory or pain;
- financial utility;
- improved trading performance;
- universal biological necessity.
