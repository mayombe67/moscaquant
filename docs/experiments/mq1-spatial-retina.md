# MQ-1 Spatial Retina Validation

## Status

Baseline spatial sensory-mapping experiment.

No neural parameters were tuned based on the result.

## Source

MaleCNS optic-column type assignments v1.0.

SHA-256:

`d4af1cacb751036f7e84bfecc9bec79ca010066ac066559c29b566003ec080d3`

The workbook provides official optic-column coordinates for column-assigned
neurons but does not directly assign coordinates to MQ-001 R1-R6
photoreceptors.

## Mapping method

MQ-001 contains 3,377 retained R1-R6 photoreceptors.

For each R1-R6 neuron, the frozen baseline connectome was searched for
connections to neurons carrying an official optic-column assignment.

The photoreceptor was assigned the `(eye, h1, h2)` coordinate of its
strongest connected officially assigned postsynaptic partner.

Connectome orientation is `post x pre`.

This photoreceptor coordinate is an inferred MQ-001 assignment, not an
official MaleCNS annotation.

Photoreceptors without a defensible assignment remain unplaced. No synthetic
coordinate fallback is used.

## Mapping result

- R1-R6 neurons: 3,377
- Spatially placed: 3,241
- Unplaced: 136
- Coverage: 95.97%
- Unique inferred columns: 800
- Left-eye assignments: 1,085
- Right-eye assignments: 2,156

The left/right asymmetry is preserved as observed and has not been corrected
or artificially balanced.

### Column occupancy

| R1-R6 per column | Columns |
| ---: | ---: |
| 1 | 125 |
| 2 | 99 |
| 3 | 105 |
| 4 | 89 |
| 5 | 108 |
| 6 | 240 |
| 7 | 18 |
| 8 | 6 |
| 9 | 7 |
| 10 | 3 |

## Frozen localized stimuli

The first left and right test columns were selected before examining their
downstream neural responses.

Selection rule:

1. inferred retinal column
2. exactly six R1-R6 neurons
3. geometrically central among six-receptor columns for that eye

Selected columns:

- Left: `L/25/32`
- Right: `R/21/29`

### Left stimulus

R1-R6 body IDs:

- 139004
- 153443
- 172741
- 175990
- 189675
- 212701

Immediate downstream response:

- 6 affected neurons
- 0 positive
- 6 negative
- all 6 `ol_intrinsic`

Cell types:

- T1
- C3
- L3
- L2
- L1
- L4

Four directly annotated downstream neurons independently carry optic-column
coordinate `(25,32)`:

- T1
- C3
- L2
- L1

L3 and L4 lack `assignedOlHex` coordinates in this observation.

### Right stimulus

R1-R6 body IDs:

- 216313
- 221973
- 236789
- 249190
- 264911
- 270341

Immediate downstream response:

- 6 affected neurons
- 0 positive
- 6 negative
- all 6 `ol_intrinsic`

Cell types:

- L2
- L1
- T1
- C3
- L4
- L3

Five directly annotated downstream neurons independently carry optic-column
coordinate `(21,29)`:

- L2
- L1
- T1
- C3
- L3

L4 lacks an `assignedOlHex` coordinate in this observation.

## Spatial specificity

The localized left and right flashes produced:

- Left downstream targets: 6
- Right downstream targets: 6
- Shared downstream targets: 0
- Union: 12
- Jaccard overlap: 0.0

The two retinal locations therefore produced the same immediate cell-type
architecture while propagating through distinct physical neurons.

## Interpretation

The result supports the spatial inference method.

A localized group of six inferred R1-R6 photoreceptors propagates into a
column-specific set of optic-lobe intrinsic neurons.

Independent `assignedOlHex1/2` annotations on downstream neurons agree with
the inferred retinal coordinates for the majority of directly annotated
first-hop targets in both frozen test columns.

This is evidence that the connectivity-derived R1-R6 mapping preserves
columnar spatial organization.

It is not proof that inferred R1-R6 coordinates are biological ground truth,
nor does it establish a complete biological model of Drosophila vision.

The current LIF and transmitter-sign models remain simplified modeled
dynamics.

## Next experiment

Stimulate neighboring inferred retinal columns sequentially and test whether
spatial displacement produces structured, distinguishable propagation through
the frozen MaleCNS connectome.
