# MQ-3 — Descending Readout and Propagation Bottleneck

## Status

**MQ-3 COMPLETE.**

The descending-neuron output boundary and anonymous anatomical readout populations are frozen. The initial spike-only market readout produced deterministic abstention under both synthetic market conditions because market-conditioned activity did not reach the descending-neuron population.

A subsequent global graded-propagation hypothesis was rejected at its precommitted neutral-contamination gate.

No financial semantics have been assigned to the anonymous output populations.

---

## Frozen descending-neuron boundary

The initial biological output boundary contains all confirmed MaleCNS neurons satisfying the frozen descending-neuron selection rule.

Population:

* confirmed descending neurons: 1,314
* `descending_neuron_tbc` excluded: 2
* financial semantics used during selection: no
* market response used during selection: no

Frozen artifact:

`/home/wil/moscaquant-data/processed/mq3-descending-readout-v1.npz`

SHA-256:

`f74c5b1c28c66c48b9d2ce65a461b112666b1a3e72f8e897c61f17ddddb37102`

Provenance:

`/home/wil/moscaquant-data/processed/mq3-descending-readout-v1.json`

SHA-256:

`1b9321a512148ae786ff47fc1443ad7c27a8aaa40bced324d76ab976ce900fc2`

---

## Anatomy-only structural partition

Direct DN↔DN signed directional connectivity was evaluated independently of market response.

The complete 1,314-neuron DN graph formed one connected component with:

* 75,273 weighted DN→DN edges
* 52,637 positive edges
* 22,636 negative edges
* zero isolated DNs

A deterministic cosine-distance / average-linkage sweep over `k = 2..20` did not identify a strong intrinsic partition.

The highest silhouette within the precommitted range occurred at the upper boundary:

* selected `k`: 20
* silhouette: 0.052902525450789106

The result was retained as a boundary result rather than interpreted as evidence for 20 biological output modes.

Artifact:

`/home/wil/moscaquant-data/processed/mq3-dn-structural-partition-v1.npz`

SHA-256:

`fb4881a7fa6a3958ba8fd9f30eb243b44ed9968eb52ce9c131296ead20a03d72`

Provenance SHA-256:

`a75e1236cd870aae3d612e7ff3fdb24cd531e61dd8cf421107c608f45ac9f441`

---

## Independent cross-view anatomy validation

A second anatomy-only representation was constructed from signed non-DN upstream connectivity into each descending neuron.

The direct DN↔DN representation and non-DN upstream representation were clustered independently.

The strongest cross-view agreement occurred at `k = 3`:

* adjusted Rand index: 0.6832358238805133
* optimally matched neurons: 1,191 / 1,314
* matched fraction: 0.906392694063927

A 10,000-permutation label null produced:

* null median ARI: -0.0002285147398060617
* null maximum ARI: 0.011322629608315553
* null values ≥ observed: 0
* empirical `p(+1)`: 0.00009999000099990002

The `k = 3` result was treated as a coarse anatomical consensus scale, not as evidence for BUY / HOLD / SELL states.

The consensus cores were:

* DN-C0: 6 neurons
* DN-C1: 646 neurons
* DN-C2: 539 neurons
* structurally discordant / unassigned: 123 neurons

DN-C0 is a small but anatomically coherent bilateral population:

* all six neurons subclass `xl`
* four `DNpe029`
* two `DNge153`
* three left / three right

The 123 discordant neurons were deliberately excluded rather than forced into a channel.

Frozen consensus artifact:

`/home/wil/moscaquant-data/processed/mq3-dn-consensus-v1.npz`

SHA-256:

`2e1272b6db6219290af96a828f52764d0f60d937336508251d0a4d6c46fb31f5`

Provenance SHA-256:

`60f16da1bd198f18bd05e2b68112669fb785d25c14eddf2a0aadd1c5c440a0cf`

---

## Neutral readout calibration

The primary MQ-3 readout metric was frozen as mean positive membrane voltage per neuron, preventing the large DN-C1 and DN-C2 populations from dominating merely through population size.

Under the frozen spike-only runtime, neutral input produced exactly zero activity in all three consensus populations across 192 frames:

* DN-C0 mean positive voltage: 0
* DN-C1 mean positive voltage: 0
* DN-C2 mean positive voltage: 0
* DN-C0 spikes: 0
* DN-C1 spikes: 0
* DN-C2 spikes: 0

Independent repeated neutral replay was bitwise deterministic.

The neutral abstention floor was therefore frozen at exact zero.

---

## Initial anonymous market readout

The first MQ-3 market-conditioned test retained anonymous output labels.

No BUY, SELL, HOLD, bullish, bearish, P&L, or profitability information was used.

Decision rule:

* if all three episode scores are exactly zero → `ABSTAIN`
* otherwise the unique maximum anonymous channel wins
* ties → `ABSTAIN`

### Condition A

* DN-C0 score: 0
* DN-C1 score: 0
* DN-C2 score: 0
* DN spikes: 0
* outcome: `ABSTAIN`

### Condition B

* DN-C0 score: 0
* DN-C1 score: 0
* DN-C2 score: 0
* DN spikes: 0
* outcome: `ABSTAIN`

A/A and B/B replay were exact.

Result artifact:

`/home/wil/moscaquant-data/experiments/mq3-anonymous-market-readout-v1.json`

SHA-256:

`15be12fed9f4235893fcbbef7cea82d487e196d80996373312440718200ee0cb`

Interpretation:

The frozen descending decoder did not produce an opinion because no market-conditioned membrane activity reached any assigned descending-neuron population under the spike-only runtime.

This result does not establish that the anatomical decoder is invalid.

---

## Propagation localization

Structural distance from the complete visual relay population showed that all 1,191 assigned descending neurons are within three synapses of the visual relay.

Using only the relay neurons actually active under Condition A:

* relay spike events: 40
* unique active relay neurons: 34
* active types:

  * L1: 23
  * L2: 7
  * Lai: 4

Every assigned DN remained structurally reachable.

Distance from the active relay population:

* one hop: 0 DNs
* two hops: 8 DNs
* three hops: 846 DNs
* four hops: 337 DNs

The active relay population had:

* 518 unique first-hop targets
* 25 first-hop targets that also project directly to assigned DNs

All 25 bridge neurons received signed market-conditioned current.

Bridge dynamics under Condition A:

* bridge neurons receiving any relay current: 25 / 25
* receiving positive current: 20
* receiving negative current: 6
* bridge neurons producing spikes: 0
* maximum bridge membrane voltage: 0.37755101919174194
* minimum bridge membrane voltage: -0.08777699619531631
* bridge neurons reaching `V >= 0.25`: 1
* bridge neurons reaching `V >= 0.50`: 0
* LIF threshold: 1.0

The propagation bottleneck is therefore localized to subthreshold intermediate activity between the active visual relay and descending-neuron output boundary.

---

## MQ-3.1 — global hybrid propagation hypothesis

### Hypothesis

The spike-only point-neuron approximation may discard biologically relevant positive subthreshold state.

A parameter-free experimental runtime was precommitted in which ordinary non-retinal presynaptic activity was:

`max(previous_spike, clip(previous_voltage, 0, threshold) / threshold)`

Controls:

* structural connectome unchanged
* retinal MQ-2.1 transduction unchanged
* R1-R6 remained spike-only
* sensory gain unchanged
* visual release gain unchanged
* DN consensus unchanged
* MQ-3 readout metric unchanged
* no graded gain tuning permitted
* neutral replay required before A/B exposure

### Neutral result

The global hybrid rule failed the neutral-contamination gate.

Neutral input produced substantial deterministic descending-neuron activity:

DN-C0:

* mean positive voltage: 0.3086495144225448
* maximum frame mean: 0.7461612323919932
* mean spike rate per neuron per frame: 0.019965277777777776

DN-C1:

* mean positive voltage: 0.09700511135132954
* maximum frame mean: 0.1785632853386145
* mean spike rate per neuron per frame: 0.006127450980392157

DN-C2:

* mean positive voltage: 0.07665823219823752
* maximum frame mean: 0.13948232858702678
* mean spike rate per neuron per frame: 0.002145176252319109

Repeated neutral replay was exact.

Result artifact:

`/home/wil/moscaquant-data/experiments/mq3-1-hybrid-neutral-calibration-v1.json`

SHA-256:

`ce0e266181b8c710d906d2dc77c4759341a51211d74e72ac5e8cf74185a211c3`

### Verdict

**REJECTED.**

Global positive-subthreshold transmission converts the neutral baseline into descending-neuron activity.

Conditions A and B were not inspected under the MQ-3.1 hybrid runtime after this failure.

The result is retained as a negative result and the global hybrid rule must not be tuned against market-conditioned responses.

---

## Current interpretation

The evidence currently supports the following chain:

`market stimulus`

→ frozen retinal encoding

→ MQ-2.1 visual transduction

→ reproducible biological relay activity under Condition A

→ signed current into identified intermediate bridge neurons

→ subthreshold bridge membrane state

→ no bridge spikes

→ no descending-neuron activity

The anatomical path exists.

The demonstrated failure occurs in the modeled neural dynamics along that path.

This does not justify globally converting every positive membrane potential in the CNS into transmitter release.

---

## Next objective

Before another market-conditioned readout is attempted:

1. identify the biological annotations of the 25 bridge neurons;
2. determine whether graded or nonspiking transmission is biologically defensible for the relevant cell types or pathway;
3. precommit any narrower propagation model independently of A/B behavior;
4. require the replacement model to pass neutral contamination testing;
5. only after neutral passes, repeat anonymous A/B readout.

No financial semantics will be assigned until a reproducible biological output response exists.

---

## Detailed MQ-3.2 experiment records

The final MQ-3.2 experimental line is documented in greater methodological
detail in:

- [`mq3-2-physiology-constrained-propagation.md`](mq3-2-physiology-constrained-propagation.md)
- [`mq3-2-causal-intervention.md`](mq3-2-causal-intervention.md)

This document remains the phase-level MQ-3 record and interpretation summary.

---

## Scientific statement

MQ-3 has not yet demonstrated an autonomous financial opinion.

It has demonstrated that:

* an anatomy-only descending output boundary can be defined without financial semantics;
* two independent structural views recover a reproducible coarse DN organization;
* the spike-only runtime extinguishes the Condition-A signal before the DN boundary;
* the extinction can be localized to identified subthreshold bridge neurons;
* a global graded-propagation solution fails a precommitted neutral control.

The negative MQ-3.1 result constrains the next model rather than being tuned away.
