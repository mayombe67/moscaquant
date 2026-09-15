# MQ-2 Synthetic Market Awareness

## Purpose

Test whether distinct deterministic synthetic market histories produce
reproducibly distinct neural trajectories in MQ-001 through the frozen
Market Vision sensory interface.

This experiment contains no BUY/HOLD/SELL decoder and makes no claim about
trading performance or market understanding.

## Frozen Pipeline

The experiment used:

1. deterministic synthetic market histories;
2. deterministic descriptive market features;
3. six independent causal normalizers;
4. frozen balanced retinal territories;
5. frozen spatial Market Vision encoding;
6. frozen temporal Market Vision encoding;
7. `mq001-market-coupling-v1`;
8. the frozen MQ-001 structural connectome;
9. the minimal deterministic MQ-001 LIF runtime.

The sensory gain was calibrated before this experiment and was not changed
after observing neural responses.

## Conditions

### Condition A

A persistent directional synthetic market regime following a shared baseline
history.

### Condition B

A choppy, directionally disordered synthetic market regime following the same
shared baseline history.

Both conditions use identical normalization warm-up history.

The conditions diverge only after the causal normalizers have accumulated the
same eight-observation baseline.

## Replay Control

Condition A was executed twice from:

- fresh MQ-001 neural state;
- fresh independent causal normalizers;
- identical connectome;
- identical encoder configuration;
- identical sensory gain.

### A1

Normalized feature SHA-256:

`0e813cad7c9fe7af487c0373cfaae81e6f691420686d2794be9766bdee836a46`

Retinal stream SHA-256:

`b9815b338273ed9df2ea558b698e1b4e2f982e343bbc0df5d6ab61643126e77b`

Neural spike trajectory SHA-256:

`822b77fa93e998cf7aa098996933aaa75054ab039eb0bc590be2919d843d2817`

Final voltage SHA-256:

`e3df3fee87c1148917d0139485bfbcb0a86f2e02c8d9ab3d1d4db4d97ed574d6`

Total spikes:

`2603`

Active frames:

`103`

Final maximum voltage:

`0.9837744235992432`

### A2

A2 reproduced every A1 hash exactly.

Total spikes:

`2603`

Active frames:

`103`

Final maximum voltage:

`0.9837744235992432`

Result:

`A1 == A2 EXACT REPLAY PASS`

## Condition B

Normalized feature SHA-256:

`c1ed953df7feb36f6a20eb3ce795ce16c6f740292e9d922b0b586ad43aa51f06`

Retinal stream SHA-256:

`56af598104c6d65e12859a75a9d1596fd2115e055da8fc35598e33aaec162ac9`

Neural spike trajectory SHA-256:

`87f2d1652594d5e36205aa4f8af036e2d011d961e6386ead42aab24460049d09`

Final voltage SHA-256:

`4108f37df5240aa7d16d0c187626bf495bcf2b5d4c8dd28ad3d17f09ad5a9579`

Total spikes:

`1596`

Active frames:

`82`

Final maximum voltage:

`0.9727786779403687`

## A/B Results

Normalized percept differed:

`PASS`

Retinal stimulus stream differed:

`PASS`

Neural spike trajectory differed:

`PASS`

Final neural state differed:

`PASS`

Frames with different total spike counts:

`43`

## Supported Claim

Under the current frozen MQ-2 synthetic experiment, distinct market histories
produce reproducibly distinguishable neural trajectories in MQ-001 through
the artificial Market Vision sensory interface.

## What This Does Not Demonstrate

This experiment does not demonstrate that MQ-001:

- understands markets;
- predicts prices;
- prefers one market regime;
- possesses biological market-processing circuitry;
- has learned anything;
- can make trading decisions;
- can produce profitable behavior.

The market-to-retina mapping is artificial.

The neural substrate uses the frozen biological connectome topology with
modeled LIF dynamics.

## Next Scientific Question

Determine whether the observed neural discrimination survives appropriate
controls, especially:

- repeated synthetic regimes;
- ticker-to-territory permutation;
- matched sensory controls;
- SHUFFLED MOSCA;
- DEAD MOSCA;
- feature ablations.

## Status

`MQ-2 SYNTHETIC MARKET AWARENESS PASS`

## Follow-up: Downstream Propagation Control

Subsequent topology and downstream-propagation controls showed that the
original A/B result measured reproducibly distinct activity at the sensory
photoreceptor layer, but did not demonstrate propagation through the
downstream connectome.

For both synthetic conditions, every observed spike occurred in the mapped
R1-R6 retinal population.

Observed downstream spikes:

`0`

The frozen signed connectome produced exclusively inhibitory first-hop
R1-R6 synaptic drive during the probe:

- downstream positive synaptic events: `0`
- downstream negative synaptic events: `4711`
- strongest positive first-hop drive: `0.0`
- strongest negative first-hop drive: `-0.9777778387069702`
- maximum downstream membrane voltage: `0.0`
- minimum downstream membrane voltage: `-1.8007479906082153`
- LIF firing threshold: `+1.0`

Therefore the original MQ-2 result is retained as a valid sensory
discrimination and deterministic-replay result, but it is not evidence of
whole-connectome market discrimination.

### Revised Supported Claim

Distinct deterministic synthetic market histories produce reproducibly
distinguishable activity in the frozen Market Vision / R1-R6 sensory layer.

Whether that information can propagate into downstream MaleCNS circuitry
requires an additional visual-transduction model.

This limitation motivated MQ-2.1.
