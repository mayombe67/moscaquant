# MQ-4.1 — Neuroscope Replay Telemetry

## Status

**COMPLETE**

## Purpose

Produce a read-only replay artifact from the frozen MQ-3.2 runtime for
visualization by Neuroscope.

Neuroscope may observe simulation state but may not feed information back into
the model.

## Source

Checkpoint:

`mq-3.2`

Condition:

`A`

Frames:

`192`

Population:

`166700`

## Captured populations

- retinal neurons: 3241
- visual relay neurons: 2430
- graded Tm2/Tm3/Tm4 neurons: 5490
- descending neurons: 1314
- MQ-3 responder neurons: 9

## Sparse telemetry

- effective activity entries: 176615
- spike entries: 2645
- positive voltage entries: 3470474

## Replay artifact

`${MOSCAQUANT_DATA_ROOT}/neuroscope/mq4-neuroscope-replay-A-v1.npz`

SHA-256:

`d670686659a85d2085bb3ad890a5e827fef55276bd48a841b371d51877ffe13c`

## Metadata

`${MOSCAQUANT_DATA_ROOT}/neuroscope/mq4-neuroscope-replay-A-v1.json`

SHA-256:

`afdc77e1086c1d11236078016378aae38d210d552e6a1b78702600040b364e1f`

## Boundary

- READ ONLY: YES
- SIMULATION FEEDBACK: NO
- FINANCIAL SEMANTICS USED: NO

The replay artifact is visualization telemetry only and does not modify the
experimental model.
