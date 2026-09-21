# MQ-3.PD — Propagation-Depth Diagnostic Results

**Status:** COMPLETE / ACCEPTED DIAGNOSTIC  
**Parent evidence:** MQ-3.2  
**Condition:** A  
**Frozen model modified:** NO  
**Financial semantics used:** NO

## Question

Does the weak downstream response already observed in the accepted MQ-3.2
Condition-A causal route reflect progressive signal loss with increasing
synaptic depth under the frozen MoscaQuant dynamics?

## Frozen path basis

The diagnostic used the previously accepted
`mq3-2-causal-path-decomposition-v1` first-positive activity-supported paths.

Observed source-relative hop sets:

- hop 0: 12 nodes
- hop 1: 9 nodes
- hop 2: 1 node

No new route search was performed.

## Frozen-gain result

Frozen MQ-3.2 release gain:

`0.9981738484618123`

| Hop | Nodes | Integrated positive voltage | Integrated effective activity | Spikes | First positive frame | Voltage survival vs hop 0 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 12 | 14.463509513629074 | 14.463509513629074 | 0 | 144 | 1.0 |
| 1 | 9 | 0.20703680060515714 | 0.008392544254775203 | 0 | 145 | 0.014314423509042865 |
| 2 | 1 | 1.538830129255153e-05 | 0.0 | 0 | 147 | 1.0639396529625828e-06 |

At the frozen gain:

- hop 1 retained approximately 1.431% of hop-0 positive voltage;
- hop 2 retained approximately 0.000106% of hop-0 positive voltage;
- hop 2 retained approximately 0.00743% of hop-1 positive voltage;
- effective activity fell from 14.463509513629074 at hop 0 to
  0.008392544254775203 at hop 1 and 0 at hop 2;
- no hop-set neuron spiked.

The first-positive sequence was temporally ordered:

`144 -> 145 -> 147`

This is consistent with downstream propagation accompanied by severe attenuation.

## Pre-registered diagnostic gain sweep

| Gain multiplier | Release gain | Hop-0 voltage | Hop-1 survival vs hop 0 | Hop-2 survival vs hop 0 | Hop-2 effective activity | Spikes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.50x | 0.49908692423090617 | 0 | n/a | n/a | 0 | 0 |
| 0.75x | 0.7486303863463593 | 0 | n/a | n/a | 0 | 0 |
| 1.00x | 0.9981738484618123 | 14.463509513629074 | 0.014314423509042865 | 1.0639396529625828e-06 | 0 | 0 |
| 1.25x | 1.2477173105772654 | 15.5805084779 | 0.02011403837349412 | 5.260108978841392e-06 | 0 | 0 |
| 1.50x | 1.4972607726927185 | 25.0803850318 | 0.023645708018891282 | 1.6524592575927742e-05 | 0 | 0 |

The two sub-frozen gains produced no positive signal even at hop 0.

Increasing release gain above the frozen value increased transmitted voltage, but
the qualitative depth-collapse pattern remained:

- hop 1 retained only approximately 2.01% of hop-0 voltage at 1.25x;
- hop 1 retained only approximately 2.36% at 1.50x;
- hop 2 retained approximately 0.000526% of hop-0 voltage at 1.25x;
- hop 2 retained approximately 0.00165% at 1.50x;
- hop-2 effective activity remained exactly zero throughout the sweep;
- no hop-set neuron spiked at any tested gain.

## Classification

**THRESHOLDED ONSET WITH SEVERE DEPTH ATTENUATION — SUPPORTED**

The tested frozen model exhibits two related features:

1. a gain threshold between the tested 0.75x and 1.00x conditions for activity to
   enter the frozen causal-path source set; and
2. severe progressive attenuation after that activity appears.

The gain sweep therefore does not rescue effective transmission to hop 2 within
the pre-registered range.

## Interpretation

The weak downstream MQ-3.2 response is compatible with a propagation-depth
limitation in the frozen MoscaQuant dynamics.

This conclusion is model-scoped.

The diagnostic does not establish:

- a universal MaleCNS propagation-depth limit;
- equivalent signal attenuation in a living Drosophila nervous system;
- that the frozen release gain should be changed;
- financial meaning or trading utility;
- biological learning or behavior.

The result does not reopen or retune MQ-3.2.

## Artifact

`${MOSCAQUANT_DATA_ROOT}/experiments/mq3-pd-propagation-depth-v1.json`

SHA-256:

`8c349d926063356d837855c9538de59fbddc20e3a10238c657410a1f1c5b8155`

Negative and null sweep conditions are retained as part of the accepted record.
