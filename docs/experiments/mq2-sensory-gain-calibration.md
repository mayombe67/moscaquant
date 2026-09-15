# MQ-2 Sensory Gain Calibration

## Purpose

Define the conversion between normalized Market Vision sensory energy and the
voltage units used by the frozen MQ-001 LIF runtime.

The Market Vision encoder itself is not modified.

## Calibration Rule

Using a neutral 16-frame Market Vision sequence, integrate the sensory stimulus
through the frozen LIF leak equation without:

- connectome recurrence;
- threshold/reset;
- trading behavior;
- P&L;
- downstream-response tuning.

Choose the minimum gain that makes the strongest retinal receptor reach the
LIF threshold under passive integration.

## Frozen Runtime

- dt: 1 ms
- tau: 20 ms
- threshold: 1.0
- reset: 0.0

Calculated decay:

`0.951229453086853`

## Result

Unscaled passive peak voltage:

`0.07919852435588837`

Peak frame:

`15`

Peak neuron index:

`94326`

Derived sensory gain:

`12.626497881530927`

## Neutral MQ-001 Probe

Using the analytically derived gain:

Spikes by frame:

`[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5]`

Total spikes:

`5`

Final maximum subthreshold voltage:

`0.9423753023147583`

No gain adjustment was made after observing this result.

## Status

Accepted as `mq001-market-coupling-v1`.
