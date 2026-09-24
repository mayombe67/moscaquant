# SQ-05 — TWO BETRAYALS — Stimulus Freeze Candidate

**Status:** STIMULUS FREEZE CANDIDATE — NO NEURAL EXECUTION AUTHORIZED

## Scientific cue names

The scientific protocol uses:

- `CUE_A_LOCALIZED_VISUAL`
- `CUE_B_EXPANDING_VISUAL`

The Panopticon phrases **fruit-associated** and **looming/threat-associated**
remain presentation shorthand only.

No fruit recognition, olfaction, hunger, threat perception, fear, or biological
looming-detector mechanism is claimed.

## Why this design

The frozen retinal artifact supports localized and expanding spatial visual
patterns but the current science repo contains no literal fruit/olfactory
stimulus generator and no pre-existing looming generator.

SQ-05 therefore freezes only what the model can actually instantiate:
a localized retinal cue followed later by an expanding retinal cue.

## Counterbalanced layouts

The retinal map is naturally asymmetric:

- left placed R1-R6: 1,085;
- right placed R1-R6: 2,156.

A single left-versus-right layout would confound cue identity with eye.

Therefore both layouts are mandatory:

- `LR`: Cue A at `L/25/32`; Cue B at `R/21/29`;
- `RL`: Cue A at `R/21/29`; Cue B at `L/25/32`.

Both centers were already frozen six-receptor localized test columns before
SQ-05.

Classification may not use only one layout.

## Timing

The trial uses 192 one-millisecond frames, preserving the project's existing
16-frame temporal cadence:

- frames `0..31`: neutral;
- frames `32..95`: Cue A only;
- frames `96..191`: Cue A remains active while Cue B is added.

Cue B expands one deterministic coordinate radius every 16 frames:

`0, 1, 2, 3, 4, 4`

The final radius-4 footprint is held for one additional block.

This timing is frozen before any SQ-05 neural execution.

## Geometry

Cue A stimulates exactly the six R1-R6 receptors at its frozen center.

Cue B uses nested coordinate windows:

`abs(h1 - center_h1) <= radius`

and

`abs(h2 - center_h2) <= radius`

This is a deterministic operation over the frozen inferred retinal map. It is
not asserted to be an exact biological angular radius.

## Energy rule

Each active cue independently receives total retinal drive equal to the frozen
project sensory gain:

`12.626497881530927`

The drive is divided equally over that cue's active receptors in a frame.

Therefore footprint size changes spatial distribution, not that cue's total
per-frame retinal drive.

When both cues are active, total retinal drive is twice the single-cue value.
That compound-input increase is identical for INTACT, BETRAYAL I, and
BETRAYAL II and is not interpreted as a threat-specific effect.

## Frozen schedule identities

`LR`:

`61e5b3de5ea61947f1053fc513b7a6d8f2fb17af7efca4af038e8c4024d1c3c7`

`RL`:

`e044055d99fe8a19d69b4eee7bd02ba5279641c99b48d0c99cb468a5bd8f20ab`

These digests bind frame number, active neuron indices, active-receptor counts,
and float32 per-receptor drive for both cue components.

## Still unresolved

This stimulus freeze does not choose:

- BETRAYAL II fresh seed(s);
- exact BETRAYAL I sham edges;
- neural endpoints or result classification;
- showcase trial selection;
- result execution mode or authorization.

## TWO BETRAYALS

The Control Room finally has something concrete on the monitors.

First, a small light appears. Later, another visual pattern grows across the
other side of the artificial retina.

Panopticon may call them fruit and danger.

The science record calls them exactly what they are.
