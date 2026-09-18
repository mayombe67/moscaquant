# MQ-7.10 Recruitment Topology Protocol

## Research question

Does the magnitude of perturbation-dependent SC-03 expression observed in
MQ-7.9 relate to structural connectivity between each frozen SC-01 target and
the validated pathway:

56393 -> 68045 -> 1273

## Motivation

MQ-7.9 showed:

- SC-03 plasticity is silent under market condition B without perturbation;
- 10 of 13 frozen SHOCK targets expose the latent plasticized state;
- 3 targets produce no measurable expression;
- target 56393 produces the largest observed DN-C1 difference.

The present analysis tests whether this target-dependent pattern corresponds to
connectome topology.

## Frozen data

Use the MQ-7.9 result artifact without altering or rerunning its outcomes.

Primary effect magnitude per target:

absolute BS(T) vs BPS(T) DN-C1 score delta.

## Structural graph

The baseline immutable connectome is interpreted as directed:

presynaptic neuron -> postsynaptic neuron

No structural weights are modified.

## Targets

Use all 13 frozen SC-01 targets.

No target exclusion is permitted.

## Reference nodes

- 56393: presynaptic node of validated SC-03 edge
- 68045: postsynaptic node of validated SC-03 edge
- 1273: validated downstream node

## Measurements per SHOCK target

Record:

- MQ-7.9 DN-C1 effect magnitude;
- whether MQ-7.9 exposed plasticity;
- direct weight into 56393;
- direct weight into 68045;
- direct weight into 1273;
- shortest directed hop distance to 56393;
- shortest directed hop distance to 68045;
- shortest directed hop distance to 1273.

Unreachable nodes are reported explicitly.

## Interpretation

This analysis is descriptive.

A relationship between graph distance and effect magnitude may motivate a
subsequent preregistered causal lesion experiment.

Topology alone does not establish causal route usage.

No path may be selected for lesion testing until this analysis is frozen.

## Claims excluded

This analysis does not establish:

- that activity actually traversed the shortest structural route;
- causal mediation;
- biological learning;
- financial utility;
- formal network centrality mechanisms;
- anatomical uniqueness.
