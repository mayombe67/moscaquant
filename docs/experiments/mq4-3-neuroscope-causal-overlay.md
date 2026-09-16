# MQ-4.3 — Neuroscope Causal Pathway Overlay

## Status

**COMPLETE**

## Purpose

Visualize the frozen MQ-3.2 first-onset causal pathway set during read-only
Neuroscope replay.

The visualization does not alter simulation state or experimental parameters.

## Source

Replay:

`mq4-neuroscope-replay-A-v1`

Frozen causal artifact:

`mq3-2-first-onset-causal-edges-v1`

Causal edges:

`13`

## Visualization semantics

Gold:

An edge belonging to the frozen MQ-3.2 first-onset causal-path artifact whose
recorded onset frame equals the currently displayed replay frame.

Amber:

A recently activated causal edge retained briefly as a visual afterglow.

Hidden:

Frozen causal edges whose recorded onset has not yet occurred in the replay.

The overlay therefore does not represent all active synapses in the network.

It visualizes only the experimentally frozen first-onset pathway set.

## Rendering

Causal routes are rendered above the neural population field.

Active routes include:

- directional arrowhead
- strong gold glow
- white-hot center line
- moving signal pulse
- model-index edge label

Recently activated routes decay into an amber trail.

## Example

At frame 145, the first frozen onset routes include:

- `64717 -> 92`
- `43417 -> 656`

These correspond to the modeled routes reaching the earliest DN-C1 responders.

Later frames progressively reveal the remaining frozen onset network.

## Boundary

READ ONLY: YES

SIMULATION FEEDBACK: NO

FINANCIAL SEMANTICS USED: NO

The causal overlay visualizes evidence generated during MQ-3.2. It does not
create or modify that evidence.
