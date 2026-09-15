# MQ-1 Sequential Vision

## Purpose

Test whether MQ-001 can receive a deterministic sequence of localized
visual stimuli through the frozen MaleCNS connectome while preserving
temporal neural state between retinal positions.

This experiment does not claim biological motion perception or
direction selectivity. It establishes the spatial and temporal substrate
required for later motion experiments.

## Retinal map

The MQ-001 R1-R6 retinal map is inferred from the official MaleCNS
optic-column workbook.

Workbook semantics identify:

- `column` as the column ROI name
- `L1` as the L1 bodyId assigned to the column
- `R7` as the R7 bodyId assigned to the column
- `R8` as the R8 bodyId assigned to the column
- `-99` as no identified cell of that type in the column

The frozen mapping contains:

- 3,377 R1-R6 neurons
- 3,241 placed R1-R6 neurons
- 136 unplaced R1-R6 neurons
- 800 inferred optic columns

### Raw-weight audit

The normalized-connectome inference was compared against strongest raw
synaptic-weight inference.

Results:

- normalized placements: 3,241
- raw placements: 3,241
- comparable placements: 3,241
- identical retinal coordinate: 3,239
- different retinal coordinate: 2
- coordinate agreement: 99.94%
- partner agreement: 99.85%
- normalized-only placements: 0
- raw-only placements: 0
- unique columns under either method: 800

The two coordinate disagreements were:

- R1-R6 187441: normalized R/9/20, raw R/9/21
- R1-R6 210647: normalized R/9/20, raw R/9/21

Both disagreements remain recorded rather than manually corrected.

## Frozen retinal artifact

Version:

`retinal-map-v1`

Artifact:

`visual-r1-r6-map-v1.npz`

SHA256:

`c4655220e1aee4eab580a534df009f0a7493f075c42285b430ad1365ae37917f`

Provenance:

`visual-r1-r6-map-v1.json`

SHA256:

`0f2b66efcd5c40afccdc0b72dc2e834e521fb83247fa65872f286e74fe78bbf9`

Repeated builds produced identical artifact and provenance hashes.

## Frozen sequence

The sequence was selected before inspecting its sequential neural
response.

All positions are six-receptor inferred columns on the left eye at
constant h2:

1. L/23/32
2. L/24/32
3. L/25/32

R1-R6 populations:

### L/23/32

- 139947
- 150995
- 153336
- 197095
- 551664
- 552758

### L/24/32

- 85347
- 146475
- 155763
- 162879
- 165962
- 185139

### L/25/32

- 139004
- 153443
- 172741
- 175990
- 189675
- 212701

## Static spatial validation

The independently annotated downstream columnar circuitry followed the
inferred retinal displacement from h1=23 to h1=24 to h1=25.

Immediate first-hop target counts were:

- L/23/32: 7
- L/24/32: 6
- L/25/32: 6

The columns were not forced to have identical downstream topology.

Notable observations included two L4 targets at L/23/32 and an R1-R6
target at L/24/32.

These differences were retained as properties of the frozen graph.

## Sequential LIF result

With one stimulation step per retinal position:

```text
step=000 column=L/23/32 spikes=6 active=6  positive=6 negative=0
step=001 column=L/24/32 spikes=6 active=13 positive=6 negative=7
step=002 column=L/25/32 spikes=6 active=19 positive=6 negative=13
step=003 column=NONE    spikes=0 active=18 positive=0 negative=18
