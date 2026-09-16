# MQ-5.2 — Generalized Timing-Control Feasibility

Status:

**FROZEN BEFORE GENERALIZED INTERVENTION OUTCOMES**

The frozen 13-edge causal set was scanned prospectively for timing-shift
controls.

## Selection rule

For each causal edge:

1. start at the frozen causal frame
2. search outward up to four frames
3. exclude any frame already belonging to that edge's frozen observed
   causal-frame set
4. require positive effective activity from the same presynaptic neuron
5. select the nearest eligible frame
6. prefer the earlier frame on an equal-distance tie

No intervention outcome was used during selection.

## Result

Timing controls available:

`13 / 13`

All selected controls occur at:

`causal frame + 1`

The frozen assignments are stored in:

`config/controls/mq5-2-generalized-timing-map-v1.json`

## Interpretation constraint

These controls are **temporal controls**, not activity-matched controls.

Source effective activity at the selected timing-control frame may differ
substantially from activity at the causal frame.

Therefore the timing-control comparison tests whether perturbing the same
source at a nearby non-evidence frame produces a different downstream
effect.

It must not be interpreted as comparing equal amounts of removed source
activity.

In several cases the selected F+1 source activity is greater than the
activity at the causal frame. This is retained rather than normalized
post hoc.

If a timing-shift intervention produces an equal or larger effect than the
causal-frame intervention, that result must be reported and must not be
reclassified after outcome inspection.

## Frozen timing map

- `43417 -> 656`: F145 -> F146
- `44274 -> 55`: F146 -> F147
- `55548 -> 51`: F149 -> F150
- `55925 -> 55`: F146 -> F147
- `56393 -> 68045`: F146 -> F147
- `64717 -> 92`: F145 -> F146
- `65084 -> 137122`: F146 -> F147
- `68045 -> 1273`: F147 -> F148
- `87441 -> 51`: F149 -> F150
- `92657 -> 129`: F148 -> F149
- `93484 -> 129`: F148 -> F149
- `128590 -> 317`: F147 -> F148
- `135589 -> 126002`: F147 -> F148

Financial semantics remain:

**NOT ASSIGNED**
