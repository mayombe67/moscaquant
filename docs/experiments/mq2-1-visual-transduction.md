# MQ-2.1 Visual Transduction

## Status

Implemented experimental detour from MQ-2; matched controls remain active.

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
8. visual-transduction runtime implementation — PASS

Failure is not removed from the record.

It is the experimental reason MQ-2.1 exists.
## Implemented Visual Transduction

MQ-2.1 implements a visual-specific transduction adapter without modifying
the frozen structural connectome or transmitter signs.

The frozen primary relay population contains:

| Relay | Neurons |
| --- | ---: |
| L1 | 804 |
| L2 | 789 |
| L3 | 762 |
| Lai | 75 |
| **Total** | **2430** |

The relay population receives `10036` direct R1-R6 edges.

The deterministic relay artifact is:

`visual-relay-map-v1.npz`

SHA-256:

`a3df2746ec69d10a2739a05f3ec55c4bd5f15b10b9a6167aee41c15a647e3478`

The runtime intercepts only the frozen R1-R6 -> relay contribution.

That direct negative histaminergic current is represented as graded inhibition.

A decrease in inhibition produces a positive release-from-inhibition
contribution to the relay neuron's existing LIF membrane state.

The ordinary R1-R6 -> relay current is removed from conventional LIF
processing before this transduction contribution is applied, preventing
double counting.

All other connectome edges retain baseline LIF behavior.

## Neutral-Only Calibration

The visual-transduction gain was calibrated using the frozen Neutral sequence
before examining A/B responses.

The calibration rule was:

> Select the minimum scalar gain such that the strongest passive
> release-integrating relay reaches the existing +1 LIF threshold under
> Neutral.

Calibration results:

- frames: `192`
- release-active frames: `93`
- integrated release: `492.2525965720415`
- passive unscaled peak: `1.0018294924686735`
- peak frame: `148`
- peak neuron index: `64217`
- peak body ID: `84860`
- peak type: `Lai`
- LIF threshold: `1.0`

The resulting frozen parameter is:

`release_gain_v1 = 0.9981738484618123`

No A/B discrimination result, P&L, behavior decoder, or trading outcome was
used to select this value.

The parameter remained unchanged throughout all subsequent experiments
reported below.

## Neutral Runtime Validation

Two exact Neutral replays produced identical neural and final-voltage hashes.

Neutral produced:

- retinal spikes: `2095`
- unique retinal neurons: `479`
- relay spikes: `1`
- unique relay neurons: `1`
- wider-connectome spikes: `0`

The single relay spike occurred:

- frame: `148`
- neuron index: `64217`
- body ID: `84860`
- type: `Lai`

This exactly reproduced the neuron and frame that defined the neutral passive
calibration peak.

Neutral therefore established deterministic R1-R6 -> biological relay
propagation without any A/B exposure.

## Relay Output Polarity

The frozen transmitter-sign model classifies the primary relay populations as:

| Relay | Sign | Wider edges |
| --- | --- | ---: |
| L1 | inhibitory | 11679 negative |
| L2 | excitatory | 30547 positive |
| L3 | excitatory | 48190 positive |
| Lai | inhibitory | 407 negative |

All `789` L2 neurons and all `762` L3 neurons are excitatory in the frozen
transmitter-sign artifact.

All `804` L1 neurons and all `75` Lai neurons are inhibitory.

A total of `1551` relay neurons therefore provide positive routes into the
wider connectome.

The Neutral sequence did not activate those excitatory routes above firing
threshold.

The strongest Neutral passive relay peaks were:

| Relay | Maximum passive voltage |
| --- | ---: |
| L1 | 0.9546374532790125 |
| L2 | 0.774106891241719 |
| L3 | 0.6397256288851253 |
| Lai | 0.9999999606048394 |

## Frozen A/A/B Market Replay

After the visual-transduction runtime and `release_gain_v1` were frozen, the
original deterministic MQ-2 synthetic A/A/B experiment was rerun unchanged.

A1 and A2 reproduced exactly.

Condition A produced:

- retinal spikes: `2605`
- relay spikes: `40`
- unique relay neurons: `34`
- L1 spikes: `26`
- L2 spikes: `7`
- L3 spikes: `0`
- Lai spikes: `7`
- first relay spike frame: `131`
- first excitatory relay spike frame: `143`
- wider-connectome spikes: `0`

Condition B produced:

- retinal spikes: `1596`
- relay spikes: `0`
- L1 spikes: `0`
- L2 spikes: `0`
- L3 spikes: `0`
- Lai spikes: `0`
- wider-connectome spikes: `0`

A and B produced different relay spike trajectories.

The result therefore crosses the experimental boundary that the original
MQ-2 replay did not cross:

market-condition-dependent activity propagated beyond the artificial R1-R6
population into biological visual relay neurons.

Importantly, Condition A included `7` spikes in `7` distinct excitatory L2
neurons.

## Wider-Connectome Synaptic Propagation

Although no wider-connectome neuron crossed firing threshold, the A relay
spikes generated measurable synaptic current outside the frozen
L1/L2/L3/Lai relay population.

For Condition A:

- relay-source frames: `22`
- excitatory relay-source frames: `6`
- positive second-hop current events: `280`
- negative second-hop current events: `375`
- integrated positive current: `14.179275274276733`
- integrated negative absolute current: `33.328545689582825`
- strongest positive current: `0.44255319237709045`
- strongest negative current: `-0.5`
- wider-connectome spikes: `0`

For Condition B:

- relay-source frames: `0`
- positive second-hop current events: `0`
- negative second-hop current events: `0`
- wider-connectome spikes: `0`

Condition-specific activity therefore propagated across a second synaptic
boundary as subthreshold current even though it did not yet produce a
wider-connectome spike.

## Relay-Attributed Membrane Response

A counterfactual accounting trace integrated only current caused by relay
spikes using the same `20 ms` membrane leak as the runtime.

This trace does not introduce another neural model or alter runtime state.

For Condition A:

- relay-only maximum positive downstream voltage:
  `0.4412076535702383`
- L2/L3-only maximum positive downstream voltage:
  `0.44255319237709045`
- strongest L1/Lai-only negative voltage:
  `-0.5`

The downstream neuron that came closest to the +1 firing threshold while
receiving positive relay-attributed voltage reached:

- actual membrane voltage: `0.3980864882469177`
- relay-attributed voltage: `0.42898984808958107`
- gap to threshold: `0.6019135117530823`
- body ID: `515694`

The difference between actual and relay-attributed voltage reflects other
network input acting on the same neuron.

Condition B produced:

- relay-only positive voltage: `0.0`
- L2/L3-only positive voltage: `0.0`

## Supported MQ-2.1 Claim

Under the frozen MQ-2.1 visual-transduction model, distinct deterministic
synthetic market histories produce reproducibly different activity beyond the
artificial retinal population.

Condition A produces biological visual-relay spiking, including excitatory L2
activity, and relay-derived synaptic current measurably depolarizes neurons in
the wider frozen MaleCNS connectome.

Condition B does not produce relay spiking in the same experiment.

This result does not establish:

- market understanding;
- prediction;
- preference;
- learning;
- trading skill;
- profitability;
- biological-topology superiority.

No neuron outside the frozen L1/L2/L3/Lai relay population has yet crossed
firing threshold as a result of this experiment.

## Remaining Experimental Boundary

MQ-2.1 has now demonstrated:

1. deterministic Market Vision input — PASS
2. R1-R6 sensory discrimination — PASS
3. R1-R6 -> biological relay propagation — PASS
4. exact A1/A2 replay — PASS
5. condition-specific relay discrimination — PASS
6. excitatory L2 relay activity — PASS
7. relay -> wider-connectome synaptic current — PASS
8. condition-specific downstream membrane depolarization — PASS
9. wider-connectome spiking — NOT YET OBSERVED

The absence of wider-connectome spikes is retained as an experimental result.

The visual-transduction gain must not be increased in response to this result.

## Next Matched Control

The next major control is a visual-interface-preserving SHUFFLED MOSCA.

The existing pre-MQ-2.1 shuffled control globally permutes presynaptic identity.
That control can also disrupt the R1-R6 -> visual-relay interface that MQ-2.1
was specifically introduced to model.

The MQ-2.1 matched control should therefore preserve the frozen visual input
interface while disrupting biological topology downstream of that boundary.

The matched comparison must preserve:

- Market Vision input;
- retinal mapping;
- R1-R6 -> visual-relay interface;
- transmitter signs;
- sensory gain;
- `release_gain_v1`;
- A/B synthetic histories.

Topology downstream of the visual interface is then shuffled under documented
invariants.

The purpose of this control is to test whether biological topology contributes
structure beyond the already demonstrated sensory and visual-transduction
response.
