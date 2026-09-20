# MQ-002.1 — MATCHED SUBGRAPH QUALIFICATION // LILITH

## THE OTHER FLY

**Status:** FROZEN BEFORE ACQUISITION  
**Class:** Non-result-bearing data acquisition and construction qualification  
**Parent:** MQ-002 // LILITH — provisional comparative biological control

## Identity-check basis

MQ-002.0 found unusually strong traceable overlap between the official
MaleCNS/FlyWire mapping product and the frozen MQ-001 interface:

- retinal territory bodies: `3241 / 3241` mapped;
- visual relay bodies: `2430 / 2430` mapped;
- descending-readout bodies: `1310 / 1314` mapped;
- official mapping entries: `281656`;
- unique cross-matched labels: `8586`.

This justifies proceeding to acquisition of the official aligned-edge table.

It does not yet justify a neural comparison.

## Question

Can we construct a transparent, reproducible, isomorphic-only central-brain
male/female subgraph that preserves enough of MQ-001's frozen visual interface
and downstream readout to support a later preregistered comparison?

## Acquisition

Acquire the official MaleCNS/FlyWire aligned-edge table:

`mcns_fw_edge_comp.feather`

Record:

- source;
- SHA-256;
- byte size;
- row count;
- columns;
- dtypes;
- available isomorphism/dimorphism annotations.

The raw source file is stored outside the public Git repository under the
external data directory. Provenance and derived small metadata may be public.

## Construction rules

Initial candidate family:

`ISOMORPHIC_ONLY`

Rules:

1. central-brain cross-matched data only;
2. VNC connections remain excluded;
3. no edge may be inferred merely because a male edge exists;
4. no missing female edge may be replaced by SHUFFLED MOSCA;
5. no unmatched neuron may be silently relabeled as matched;
6. official cross-match labels and aligned male/female edge data control;
7. excluded MQ-001 interface elements remain listed explicitly;
8. no scientific runtime parameter changes occur in this step.

## Outputs

Produce qualification metadata sufficient to answer:

- how many matched male and female nodes are available;
- how many isomorphic edges are available;
- how much of the frozen retinal interface survives;
- how much of the frozen relay interface survives;
- how much of the frozen descending/readout interface survives;
- which MQ-001 interface identities do not survive;
- whether a later `SQ-03A — THE OTHER FLY` neural experiment is technically
  defensible.

No neural simulation is executed.

## Go / no-go

A later neural protocol may be designed only if:

- the aligned edge file is acquired and provenance-locked;
- the matched node/edge construction is deterministic;
- retained and excluded interface identities are explicit;
- the comparison can use identical model mechanics and simulated time;
- no VNC equivalence is implied.

There is deliberately no numeric pass threshold in MQ-002.1. The construction
statistics are inspected before a result-bearing protocol is frozen.

## Claim boundary

MQ-002.1 qualifies and constructs metadata for a defensible matched male/female
biological subgraph. It performs no neural dynamics and establishes no
behavioral, sex-difference, biological-mechanism, or financial result.
