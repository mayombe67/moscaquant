# SQ-01 — Temporal Decoupling Protocol v1

**Lore name:** TEMPORAL JETLAG  
**Status:** FROZEN BEFORE EXECUTION once this protocol, config, and runner are committed.

## Purpose

SQ-01 is a science side quest. It does not advance or replace the main MQ phase
gate.

The experiment asks whether accepted MQ-2.1 propagation behavior is narrowly
dependent on the current temporal discretization (`16` frames per observation)
or the current LIF leak step (`dt_ms = 1.0`).

The frozen structural MaleCNS connectome, transmitter signs, market feature
definition, causal normalization, retinal territory mapping, temporal feature
mapping, sensory gain, and MQ-2.1 release gain are not modified.

## Why this is separable

The temporal encoder already preserves mean territory energy across its encoded
window while deterministically changing motion, cadence, and irregularity.

The MQ-2.1 visual runtime applies a membrane decay determined by:

`exp(-dt_ms / tau_ms)`

Therefore frame discretization and runtime leak step are scientifically relevant
model assumptions rather than machine-speed settings.

SQ-01 changes only declared experimental parameters passed into copies of the
existing encoder/runtime interfaces. It does not edit the frozen implementation.

## Frozen matrix

Reference:

- `BASELINE`: 16 frames, 1.0 ms, stimulus scale 1.0

Clock-scale sensitivity at fixed frame representation:

- `CLOCK_FAST`: 16 frames, 0.5 ms, scale 1.0
- `CLOCK_SLOW`: 16 frames, 2.0 ms, scale 1.0

Duration-and-energy-matched resampling:

- `RESAMPLE_8`: 8 frames, 2.0 ms, scale 2.0
- `RESAMPLE_32`: 32 frames, 0.5 ms, scale 0.5

These two resampling variants preserve a nominal 16 ms observation duration and
preserve the baseline summed stimulus multiplier across the observation.

Frame-count confound controls:

- `RAW_8`: 8 frames, 1.0 ms, scale 1.0
- `RAW_32`: 32 frames, 1.0 ms, scale 1.0

The raw controls deliberately do **not** preserve observation duration or total
summed stimulus. They exist to show how much apparent frame-count sensitivity
could be produced by those coupled changes.

## Conditions and determinism

Every variant is run as:

- A1
- A2
- B

A1 and A2 must match exactly on hashes and scalar endpoints. Failure of A/A
determinism invalidates interpretation for that variant.

## Harness parity gate

Before interpreting side-quest variants, the SQ-01 harness must reproduce the
accepted MQ-2.1 baseline runner exactly for both condition A and condition B on:

- normalized hash;
- retinal hash;
- neural hash;
- relay hash;
- wider hash;
- final voltage hash;
- spike totals;
- unique-neuron counts;
- onset frames;
- frame-count trajectories.

Failure of baseline parity invalidates SQ-01.

## Primary endpoints

- relay spikes;
- wider-connectome spikes;
- unique relay neurons;
- unique wider-connectome neurons;
- first relay frame;
- first excitatory relay frame;
- first wider-connectome frame;
- final voltage maximum;
- relay trajectory hash;
- wider-connectome trajectory hash;
- final-voltage hash;
- A/B trajectory discrimination.

For cross-frame-count variants, absolute frame indices are also reported as
nominal simulated milliseconds (`frame_index * dt_ms`) to avoid confusing frame
number with elapsed model time.

## Interpretation

Possible outcomes include:

1. **robust qualitative discrimination** — hashes necessarily change, but A/B
   relay/wider discrimination and propagation remain present;
2. **quantitative timing sensitivity** — propagation remains but counts/onsets
   shift materially;
3. **boundary fragility** — propagation or A/B discrimination disappears under
   one or more reasonable matched variants;
4. **energy/duration confounding** — RAW variants move strongly while matched
   resampling variants remain comparatively stable.

No result may be described as biological temporal robustness without an
independent biologically grounded timing model.

## Claim boundary

SQ-01 is a deterministic sensitivity analysis of the frozen MoscaQuant
computational model. It tests dependence on temporal discretization and runtime
leak-step assumptions.

It does **not** establish biological timing, biological robustness, market
profitability, or live-trading utility.
