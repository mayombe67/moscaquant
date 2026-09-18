# MQ-7 Matched Plasticity Mechanics Smoke Test Results

## Purpose

Test whether a previously validated persistent SC-03 synaptic multiplier can
produce measurable neural divergence during the frozen MQ-3.2 market replay
without modifying the structural connectome.

This is a mechanics smoke test only.

It is not the O1/O2 adaptive Oracle experiment.

## Preloaded plasticity

Frozen validation edge:

56393 -> 68045

A single SC-03 plasticity update was preloaded using the validated persistent
plasticity mechanism.

Expected multiplier:

0.95

The baseline connectome was not modified.

## Condition A

Voltage trace identical:

False

Spike trace identical:

True

Baseline decision:

DN-C1

Plasticity decision:

DN-C1

Channel score deltas:

- DN-C0: 0.0
- DN-C1: -1.0445370643920353e-11
- DN-C2: 0.0

Classification:

MEASURABLE NEURAL DIVERGENCE

The preloaded SC-03 multiplier altered the neural voltage trajectory and
produced a small downstream DN-C1 score difference.

No spike-trace divergence or final readout-decision change was observed.

## Condition B

Voltage trace identical:

True

Spike trace identical:

True

Baseline decision:

ABSTAIN

Plasticity decision:

ABSTAIN

Channel score deltas:

- DN-C0: 0.0
- DN-C1: 0.0
- DN-C2: 0.0

Classification:

NO MEASURABLE REPLAY DIVERGENCE

The frozen SC-03 pathway was not measurably recruited by this replay condition.

## Structural integrity

The connectome digest before and after the experiment was identical.

Classification:

STRUCTURAL CONNECTOME UNCHANGED

## Supported conclusions

The validated persistent SC-03 plasticity mechanism can alter neural
propagation during an existing market replay.

The effect is input-dependent.

Plasticity can change voltage-level neural dynamics without necessarily
changing spikes or the final anonymous readout decision.

The structural connectome remains unchanged.

## Not supported

This experiment does not establish:

- improved financial performance;
- degraded financial performance;
- a general decision-level behavioral effect;
- biological learning in a living organism;
- financial utility of SC-03;
- superiority of O2 over O1.

## Status

SC-03 neural-expression mechanics: SUPPORTED

Full O1/O2 adaptive Oracle experiment: NOT YET RUN
