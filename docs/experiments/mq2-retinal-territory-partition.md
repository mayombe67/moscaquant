# MQ-2 Retinal Territory Partition

## Purpose

Define six anonymous retinal territories for Market Vision v1 without giving any
ticker a systematic sensory-capacity advantage.

The partition must:

- preserve whole retinal columns;
- use only frozen retinal geometry and mapped R1-R6 receptor counts;
- remain independent of ticker identity;
- remain independent of market data, neural response, P&L, or later behavior;
- preserve the natural asymmetry of the inferred retinal map;
- provide approximately equal bilateral receptor capacity across T1-T6.

## Source

Frozen retinal map:

`visual-r1-r6-map-v1.npz`

Placed R1-R6 receptors:

- Left eye: 1,085
- Right eye: 2,156
- Total: 3,241

Unique retinal columns:

- Left eye: 292
- Right eye: 508
- Total: 800

The left/right asymmetry is retained rather than artificially corrected.

## Rejected Candidate

An earlier geometry-first clustering candidate produced bilateral territory
loads ranging from 437 to 637 receptors.

Maximum difference:

`200 receptors`

This was rejected because territory location would have created a substantial
sensory-capacity advantage for some ticker assignments.

## Accepted Partition

Each eye is partitioned independently using a deterministic 2 x 3 spatial
scheme.

1. Columns are ordered spatially by `h1`.
2. Each eye is divided into two approximately receptor-balanced halves.
3. Each half is ordered by `h2`.
4. Each half is divided into three approximately receptor-balanced bands.
5. Retinal columns remain indivisible.
6. The resulting territories are anonymous T1-T6.

Ticker identity is assigned only after the territory partition is frozen.

## Result

### Left Eye

| Territory | Receptors | Columns | h1 | h2 |
|---|---:|---:|---|---|
| T1 | 180 | 72 | 6-25 | 6-29 |
| T2 | 182 | 37 | 11-24 | 29-32 |
| T3 | 179 | 33 | 15-24 | 32-37 |
| T4 | 183 | 57 | 25-36 | 20-30 |
| T5 | 181 | 47 | 25-36 | 30-34 |
| T6 | 180 | 46 | 25-36 | 34-39 |

Left-eye range:

`179 -> 183`

Maximum difference:

`4 receptors`

### Right Eye

| Territory | Receptors | Columns | h1 | h2 |
|---|---:|---:|---|---|
| T1 | 360 | 91 | 2-18 | 1-13 |
| T2 | 360 | 85 | 3-17 | 13-22 |
| T3 | 361 | 83 | 7-18 | 22-34 |
| T4 | 356 | 103 | 19-36 | 6-30 |
| T5 | 360 | 68 | 19-36 | 30-33 |
| T6 | 359 | 78 | 18-36 | 34-39 |

Right-eye range:

`356 -> 361`

Maximum difference:

`5 receptors`

### Bilateral Sensory Capacity

| Territory | Receptors | Deviation from ideal |
|---|---:|---:|
| T1 | 540 | -0.17 |
| T2 | 542 | +1.83 |
| T3 | 540 | -0.17 |
| T4 | 539 | -1.17 |
| T5 | 541 | +0.83 |
| T6 | 539 | -1.17 |

Ideal target:

`3241 / 6 = 540.1667`

Observed range:

`539 -> 542`

Maximum territory difference:

`3 receptors`

## Invariant Validation

The production partition implementation reproduced the expected bilateral
loads:

`[540, 542, 540, 539, 541, 539]`

The generated territory artifact was rebuilt twice and compared byte-for-byte.

Result:

`TERRITORY ARTIFACT DETERMINISTIC`

The provenance output was also rebuilt and compared byte-for-byte on the
Habitat.

Result:

`TERRITORY PROVENANCE DETERMINISTIC`

## Experimental Interpretation

The accepted partition makes retinal territory approximately neutral with
respect to available mapped R1-R6 receptor capacity.

This does not imply that all territories are biologically equivalent.
Different retinal locations may propagate differently through the biological
connectome.

That distinction is intentional.

Future ticker-to-territory permutation experiments can distinguish behavior
that follows ticker identity from behavior that follows retinal territory.

## Status

Accepted for Market Vision v1.
