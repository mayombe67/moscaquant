# MQ-7.12 Downstream Mediation Protocol

## Research question

Does perturbation-dependent expression of the persistent SC-03 state propagate
through the validated downstream edge:

68045 -> 1273

## Background

The validated pathway is:

56393 -> 68045 -> 1273

SC-03 plasticity modifies only:

56393 -> 68045

MQ-7.11 showed that replay-level expression depends specifically on the
functional contribution of that plasticized edge and survives an unrelated
control lesion into neuron 68045.

MQ-7.12 tests the next causal step.

Unlike MQ-7.11, the edge under primary ablation here is not plasticized.

## Frozen replay

Market condition:

B

SC-01 target:

56393

Intervention generation:

32

Plasticized edge:

56393 -> 68045

Plasticity multiplier:

0.95

Downstream test edge:

68045 -> 1273

## Functional ablation

Structural connectome data must not be modified.

Ablation is implemented as a runtime synaptic correction removing the selected
baseline edge contribution from postsynaptic input.

## Experimental conditions

### DI

SHOCK 56393.

Downstream route intact.

No plasticity.

### DPI

SHOCK 56393.

Downstream route intact.

SC-03 multiplier 0.95.

### DA

SHOCK 56393.

68045 -> 1273 functionally ablated.

No plasticity.

### DPA

SHOCK 56393.

68045 -> 1273 functionally ablated.

SC-03 multiplier 0.95.

### DC

SHOCK 56393.

Deterministic control edge into 1273 functionally ablated.

No plasticity.

### DPC

SHOCK 56393.

Same control edge ablated.

SC-03 multiplier 0.95.

## Control-edge selection

From all non-zero baseline incoming edges to neuron 1273:

- exclude presynaptic neuron 68045;
- choose greatest absolute baseline weight;
- ties resolve by lowest presynaptic model index.

This rule is frozen before control-edge identity is inspected.

## Primary comparisons

DI vs DPI

Replicates the known perturbation-dependent SC-03 expression.

DA vs DPA

Tests whether that expression survives removal of 68045 -> 1273.

DC vs DPC

Tests whether expression survives removal of a deterministic unrelated input
into the same downstream neuron.

## Primary causal pattern

Evidence consistent with downstream mediation through 68045 -> 1273 requires:

1. DI vs DPI diverges at the previously affected voltage/readout level;
2. DA vs DPA loses or materially reduces that divergence;
3. DC vs DPC retains the divergence.

Complete collapse is the strongest result but is not required for evidence of
partial mediation.

## Measurements

- voltage trace equality;
- spike trace equality;
- readout score equality;
- final decision equality;
- DN-C0/C1/C2 score deltas;
- absolute DN-C1 effect magnitude;
- attenuation relative to intact-route expression;
- control-edge identity and weight;
- structural connectome digest.

## Interpretation

If ablation of 68045 -> 1273 selectively removes or attenuates the SC-03
expression while a control lesion does not, this supports causal downstream
mediation through the validated path.

It does not establish that this edge is the only possible downstream route.

## Claims excluded

This experiment does not establish:

- financial utility;
- improved trading;
- biological learning in a living organism;
- subjective memory, pain, or reward;
- exclusive biological pathway usage;
- consciousness.
