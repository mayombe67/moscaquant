# MQ-7.15 Dynamic Differential Trace Protocol

## Research question

Where does the perturbation-dependent SC-03 difference actually propagate
through the model after acute SHOCK of neuron 56393?

## Background

MQ-7.12 established partial mediation through:

68045 -> 1273

with approximately 34.3% attenuation.

MQ-7.13 identified structurally strong residual routes.

MQ-7.14 showed that the three highest-ranked residual first-hop branches:

68045 -> 18444
68045 -> 107
68045 -> 6647

did not measurably mediate the residual effect.

Therefore structural path strength alone is insufficient to identify actual
dynamic propagation.

## Frozen conditions

Market condition:

B

SHOCK target:

56393

SHOCK intervention generation:

32

SC-03 plasticized edge:

56393 -> 68045

SC-03 multiplier:

0.95

## Paired executions

Control:

SHOCK 56393 with no SC-03 plasticity.

Adaptive:

Identical SHOCK 56393 with SC-03 multiplier 0.95.

All other conditions are identical.

## Trace window

Record generations:

32 through 44 inclusive.

This captures the intervention generation and twelve subsequent transitions.

No window extension is permitted after inspecting results.

## Recorded state

At every generation in the frozen window record:

1. effective presynaptic activity entering synaptic propagation;
2. synaptic input after runtime synaptic modifiers.

The structural connectome is not modified.

## Differential measurements

For every model neuron record:

- first generation with non-zero activity divergence above threshold;
- first generation with non-zero synaptic-input divergence above threshold;
- peak absolute activity divergence;
- peak absolute synaptic-input divergence;
- generation of each peak.

Numerical reporting threshold:

1e-15

Differences below this threshold are treated as zero for ranking purposes.

## Ranking

Produce:

- top 50 neurons by peak activity divergence;
- top 50 neurons by peak synaptic-input divergence;
- generation-by-generation count of divergent neurons;
- direct traces for nodes:
  - 56393
  - 68045
  - 1273

Mark whether each ranked neuron belongs directly to the DN-C1 readout
population.

## Interpretation

This experiment maps computational propagation of the SC-03-dependent
difference under the frozen replay.

Early-diverging neurons may become candidates for later causal lesion tests.

Dynamic divergence does not by itself establish causal mediation.

## Claims excluded

This experiment does not establish:

- biological signal propagation in a living fly;
- causal necessity of any newly identified neuron;
- subjective memory or pain;
- financial utility;
- improved trading performance;
- consciousness.
