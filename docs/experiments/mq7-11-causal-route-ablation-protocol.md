# MQ-7.11 Causal Route Ablation Protocol

## Research question

Does perturbation-dependent expression of the persistent SC-03 state require
the validated structural edge:

56393 -> 68045

## Background

MQ-7.8 established perturbation-dependent expression of the persistent
56393 -> 68045 plasticity overlay.

MQ-7.9 showed that 10 of 13 frozen SC-01 targets expose that latent state.

MQ-7.10 showed that all exposing targets were within 0-2 directed hops of
56393, while all three non-exposing targets were three hops from 56393.

Target 56393 produced the largest observed expression magnitude.

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

## Functional ablation

Structural connectome data must not be modified.

An ablation is implemented only as a runtime synaptic correction that removes
the contribution of the selected baseline edge from postsynaptic input.

## Experimental conditions

### SI

SHOCK 56393.

Validated route intact.

No plasticity.

### SPI

SHOCK 56393.

Validated route intact.

SC-03 multiplier 0.95.

### SA

SHOCK 56393.

56393 -> 68045 functionally ablated.

No plasticity.

### SPA

SHOCK 56393.

56393 -> 68045 functionally ablated.

SC-03 state conceptually present, but the ablated edge contributes no signal.

### SC

SHOCK 56393.

Control edge functionally ablated.

No plasticity.

### SPC

SHOCK 56393.

Same control edge functionally ablated.

SC-03 multiplier 0.95.

## Control-edge selection

The control lesion is chosen mechanically from the immutable baseline
connectome:

- postsynaptic neuron must be 68045;
- presynaptic neuron must not be 56393;
- select the non-zero incoming edge with greatest absolute baseline weight;
- ties resolve by lowest presynaptic model index.

This rule is frozen before the edge identity is inspected.

## Primary comparisons

SI vs SPI

Replicates perturbation-dependent plasticity expression with route intact.

SA vs SPA

Tests whether expression survives removal of 56393 -> 68045.

SC vs SPC

Tests whether expression survives a deterministic control lesion into the same
postsynaptic neuron.

## Primary causal pattern

Evidence consistent with mediation through the validated edge requires:

1. SI vs SPI diverges;
2. SA vs SPA becomes identical at the previously affected level(s);
3. SC vs SPC retains measurable divergence.

## Measurements

- voltage trace equality;
- spike trace equality;
- anonymous readout score equality;
- final decision equality;
- DN-C0/C1/C2 score deltas;
- selected control-edge identity and weight;
- structural connectome digest.

## Interpretation limits

Functional ablation of the plasticized edge necessarily removes its direct
contribution.

The experiment therefore tests whether the previously observed replay-level
expression depends on that contribution and whether an anatomically matched
control lesion produces the same collapse.

It does not establish that no alternative biological route could compensate in
a different model or organism.

## Claims excluded

This experiment does not establish:

- biological learning in a living fly;
- subjective memory or pain;
- financial utility;
- improved trading performance;
- universal anatomical necessity;
- consciousness.
