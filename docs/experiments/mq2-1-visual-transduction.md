# MQ-2.1 Visual Transduction

## Status

Active experimental detour from MQ-2.

MQ-2.1 was introduced after downstream propagation controls demonstrated
that the current point-neuron LIF runtime cannot transmit the R1-R6 visual
signal beyond the photoreceptor population.

This is a modeled-dynamics change only.

The biological structural connectome remains frozen.

## Motivation

MQ-2 successfully established:

- deterministic market feature generation;
- balanced retinal territories;
- deterministic spatial Market Vision;
- deterministic temporal Market Vision;
- fixed sensory coupling calibrated without market-response tuning;
- exact replay;
- reproducibly different R1-R6 activity for different synthetic market
  histories.

However, downstream propagation analysis found:

- all observed spikes were retinal;
- downstream spikes were zero;
- R1-R6 first-hop current was exclusively negative;
- downstream voltage never rose above zero;
- the existing LIF runtime fires only at a positive threshold.

This means the existing runtime cannot express the first visual handoff
represented by the frozen signed connectome.

## Constraint

MQ-2.1 must make the biological visual pathway computationally expressible.

It must not be tuned to make the market experiment succeed.

The following remain frozen:

- structural connectome;
- neuron population;
- transmitter signs;
- Market Vision feature definitions;
- retinal mapping;
- retinal territory partition;
- spatial encoder;
- temporal encoder;
- sensory gain.

No MQ-2.1 parameter may be selected using A/B market discrimination,
trading behavior, P&L, or a future behavior decoder.

## R1-R6 First-Hop Anatomy

The frozen MaleCNS connectome contains:

- `3241` placed R1-R6 retinal neurons;
- `4236` unique non-mapped first-hop targets;
- `13931` R1-R6 -> target edges.

All `4236` first-hop targets were successfully matched to MaleCNS annotations.

The dominant first-hop populations are:

| Type | Neurons | Edges | Integrated absolute retinal drive |
| --- | ---: | ---: | ---: |
| L1 | 804 | 3268 | 384.676414 |
| L2 | 789 | 3199 | 270.933107 |
| L3 | 762 | 3004 | 146.174277 |
| Lai | 75 | 565 | 47.095046 |
| L4 | 638 | 1410 | 27.976276 |
| T1 | 622 | 1616 | 16.354826 |
| C3 | 308 | 474 | 4.156166 |

L1, L2 and L3 account for approximately 88 percent of measured direct
R1-R6 drive.

Including Lai raises the covered direct retinal drive to approximately
93 percent.

For the initial MQ-2.1 investigation, L1/L2/L3/Lai are therefore treated as
the primary relay population.

This is an experimental boundary, not a claim that all other first-hop
targets are biologically irrelevant.

## Read-Only Relay Probe

Before modifying neural dynamics, a read-only probe measured the direct
R1-R6 inhibitory current received by L1/L2/L3/Lai.

For measurement only, inhibitory current was represented as a positive
inhibition magnitude.

A release-from-inhibition observable was defined as:

`max(previous_inhibition - current_inhibition, 0)`

This quantity was not injected into MQ-001 and did not alter neural state.

## Relay Probe Results

### Integrated release

| Relay | Neutral | A | B |
| --- | ---: | ---: | ---: |
| L1 | 224.176193 | 308.686780 | 177.698715 |
| L2 | 155.831136 | 213.332041 | 123.461871 |
| L3 | 83.987420 | 114.936291 | 66.884632 |
| Lai | 28.257845 | 40.172452 | 21.480249 |

All four relay populations produced distinct deterministic trajectories for:

- Neutral vs A;
- Neutral vs B;
- A vs B.

The ordering of integrated release happened to be:

`A > Neutral > B`

for all four populations.

No behavioral or market meaning is assigned to that ordering.

It does not imply preference, prediction, bullishness, utility, or trading
quality.

## Interpretation

The frozen retinal input already contains temporally structured information
at the biological first-hop relay.

The failure of the original whole-brain replay was therefore not evidence
that the market representation contained no downstream-usable information.

Instead, the existing one-threshold LIF abstraction lacks a mechanism for
expressing the inhibitory/graded visual handoff represented by the frozen
connectome.

## MQ-2.1 Design Direction

The smallest proposed extension is a visual-specific graded relay state for
the identified first-hop visual population.

Conceptually:

R1-R6 activity
-> signed histaminergic inhibition
-> graded relay state
-> reduction/release of inhibition
-> positive contribution to the existing LIF membrane state
-> existing positive firing threshold

MQ-2.1 must not globally introduce negative-threshold spiking.

MQ-2.1 must not flip histaminergic connections to excitatory.

MQ-2.1 must not recalibrate Market Vision sensory gain using market
conditions.

## Calibration Rule

Any new visual-transduction coupling parameter must be calibrated before
examining A/B downstream discrimination.

Calibration must use a condition independent of the experimental A/B result,
preferably the frozen neutral visual sequence and biologically motivated
runtime constraints.

After calibration the parameter is frozen.

A/B is then rerun unchanged.

## Success Criteria

MQ-2.1 succeeds at the transduction level if:

1. the same frozen Market Vision input drives the existing R1-R6 population;
2. the modeled visual relay produces downstream-capable activity;
3. activity propagates beyond the mapped retinal population;
4. replay remains deterministic;
5. parameters were frozen without reference to A/B discrimination;
6. the original connectome remains structurally unchanged.

Whether biological topology provides meaningful structure beyond matched
controls remains a separate experimental question.

## Controls Required After Implementation

After the visual-transduction model is frozen:

- Neutral replay;
- A1/A2 exact replay;
- A/B replay;
- SHUFFLED MOSCA;
- downstream-only response comparison;
- ticker-to-territory permutation;
- feature ablations.

The earlier SHUFFLED MOSCA result is not sufficient for evaluating biological
topology because the pre-MQ-2.1 experiment contained no downstream spikes.

## Scientific Record

The sequence of findings is intentionally preserved:

1. sensory A/B discrimination — PASS
2. deterministic replay — PASS
3. SHUFFLED MOSCA also discriminates A/B — PASS
4. downstream spike analysis — FAIL: zero downstream spikes
5. first-hop polarity probe — exclusively inhibitory R1-R6 drive
6. MaleCNS first-hop classification — L1/L2/L3/Lai dominant
7. read-only release-from-inhibition probe — condition-specific signal present
8. visual-transduction runtime implementation — PENDING

Failure is not removed from the record.

It is the experimental reason MQ-2.1 exists.
