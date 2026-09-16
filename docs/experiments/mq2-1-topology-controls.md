# MQ-2.1 Topology Controls

## Status

Completed initial matched-control investigation.

This experiment evaluates whether the intact MaleCNS topology produces
different downstream dynamics from randomized topology after the MQ-2.1 visual
transduction interface has been frozen.

This experiment does not evaluate trading performance, prediction,
profitability, preference, or market understanding.

## Background

MQ-2.1 established a deterministic visual-transduction mechanism that allows
the frozen artificial R1-R6 population to influence biological first-hop
visual relay neurons.

The visual-transduction parameter was calibrated on Neutral only and frozen
before A/B exposure:

`release_gain_v1 = 0.9981738484618123`

Under the frozen model, Condition A produced:

* `40` visual-relay spikes;
* `7` excitatory L2 spikes;
* `280` positive second-hop current events;
* relay-attributed downstream depolarization;
* no wider-connectome spikes.

Condition B produced no relay spikes.

The next question was therefore whether intact biological topology contributed
structure beyond the frozen sensory and visual-transduction interface.

## SHUFFLED MOSCA v2

The original SHUFFLED MOSCA control globally permuted presynaptic identities.

For MQ-2.1 this was insufficient because such a shuffle can disrupt the
R1-R6 visual interface that the new transduction model explicitly represents.

SHUFFLED MOSCA v2 therefore protects all mapped R1-R6 presynaptic identities
while permuting every other presynaptic identity within frozen transmitter
sign.

The control preserves:

* all `3241` mapped R1-R6 identities;
* the complete mapped retinal output interface;
* all `10036` R1-R6 -> L1/L2/L3/Lai relay edges;
* transmitter sign;
* postsynaptic row degree;
* postsynaptic weight sequence;
* incoming absolute normalization;
* total edge count;
* global outdegree distribution.

It randomizes non-retinal biological presynaptic identity and downstream
source-target topology.

### Frozen control artifact

Artifact:

`connectome-shuffled-mosca-v2.npz`

SHA-256:

`2d183a1663531d14fbe58c919568835cbc3fbfbbd60b2959d0fa16c1ba14ac52`

Provenance:

`shuffled-mosca-v2.json`

SHA-256:

`f8d8b11f354f2ba812e0a407a118367a709b01d6bcc88f97b3b5d6814b80b774`

Control construction results:

* protected retinal identities: `3241`;
* protected retinal output edges: `14471`;
* protected R1-R6 -> relay edges: `10036`;
* moved non-retinal identities: `163459`;
* moved protected identities: `0`;
* maximum normalization roundoff:
  `3.5762786865234375e-07`.

Artifact generation was byte-for-byte deterministic across repeated builds.

## Biological vs Single Matched Shuffle

The original Condition A and Condition B synthetic histories were replayed
through both the biological connectome and SHUFFLED MOSCA v2.

A1/A2 exact replay passed independently for both biological and shuffled
topologies.

The normalized market percept and retinal stimulus stream were identical
between biological and shuffled conditions.

### Condition A

| Measure                      | Biological | Shuffled v2 |
| ---------------------------- | ---------: | ----------: |
| Retinal spikes               |       2605 |        2603 |
| Relay spikes                 |         40 |          46 |
| L1 spikes                    |         26 |          31 |
| L2 spikes                    |          7 |           8 |
| L3 spikes                    |          0 |           0 |
| Lai spikes                   |          7 |           7 |
| Wider-connectome spikes      |          0 |           0 |
| First relay frame            |        131 |         131 |
| First excitatory relay frame |        143 |         143 |

The retinal spike counts diverged slightly even though the retinal stimulus
stream was identical.

A subsequent timing probe showed that this difference occurs only after relay
activity has entered the recurrent graph.

### Condition B

Biological and shuffled topology were identical at the measured spike level:

* retinal spikes: `1596`;
* relay spikes: `0`;
* wider-connectome spikes: `0`.

No voltage or spike divergence was observed.

## Topology Divergence Timing

For Condition A:

* first relay activity: frame `131`;
* first whole-network voltage divergence: frame `132`;
* first retinal voltage divergence: frame `132`;
* first relay voltage divergence: frame `132`;
* first wider-network voltage divergence: frame `132`;
* first spike divergence: frame `137`;
* first relay spike divergence: frame `139`;
* wider-connectome spike divergence: none;
* maximum absolute voltage divergence:
  `1.0498813390731812`;
* maximum-divergence frame: `174`.

This ordering is consistent with the intended control design.

The protected visual interface produces the initial relay event, after which
the biological and shuffled downstream topologies immediately produce
different recurrent membrane dynamics.

Those recurrent differences can then feed back into relay and retinal
populations.

For Condition B, where no relay activity occurred:

* voltage divergence: none;
* spike divergence: none;
* maximum absolute voltage divergence: `0.0`.

## Single-Shuffle Downstream Attribution

Condition A was analyzed using the same relay-attribution accounting trace for
the biological and shuffled graphs.

| Metric                          |          Biological |         SHUFFLED v2 |
| ------------------------------- | ------------------: | ------------------: |
| Relay-only max positive voltage |  0.4412076535702383 | 0.07371900975704193 |
| L2/L3-only max positive voltage | 0.44255319237709045 | 0.07371900975704193 |
| Actual wider-network max        |  0.3980864882469177 | 0.07371900975704193 |
| Closest threshold gap           |  0.6019135117530823 |  0.9262809902429581 |

For this particular shuffled realization, the intact biological topology
produced substantially stronger downstream depolarization.

Condition B produced zero relay-attributed downstream voltage in both
topologies.

A single shuffled realization is not sufficient to establish a topology
effect.

## Precommitted Shuffle Ensemble

A null ensemble was therefore defined before inspecting additional shuffle
results.

Configuration:

`config/controls/shuffled-mosca-ensemble-v1.toml`

The precommitted design specified:

* control: `shuffled-mosca-v2`;
* first seed: `20260916`;
* number of seeds: `20`;
* condition: `A`;
* frozen release gain:
  `0.9981738484618123`;
* no seed selection after results.

The four metrics were fixed in advance:

1. relay-only peak;
2. L2/L3-only peak;
3. actual wider-network peak;
4. closest threshold gap.

No shuffled connectome was retained between runs. Each control topology was
constructed in memory, evaluated, and discarded.

### Ensemble result artifact

Artifact:

`mq2-1-shuffled-ensemble-v1.json`

SHA-256:

`321d596763c73b8469b4141d8358f21c5f8231ebc3991e02685620b84c3cc31f`

## Twenty-Seed Ensemble Results

### Relay-only peak

Biological:

`0.4412076535702383`

Shuffled distribution:

* minimum: `0.04447079822421074`;
* median: `0.101720429956913`;
* maximum: `0.5`;
* shuffled controls equal to or greater than biological: `1 / 20`.

Plus-one empirical upper-tail estimate:

`0.09523809523809523`

### L2/L3-only peak

Biological:

`0.44255319237709045`

Shuffled distribution:

* minimum: `0.04447079822421074`;
* median: `0.101720429956913`;
* maximum: `0.5`;
* shuffled controls equal to or greater than biological: `1 / 20`.

Plus-one empirical upper-tail estimate:

`0.09523809523809523`

The biological L2/L3 peak was approximately `4.35x` the shuffled median.

### Actual wider-network peak

Biological:

`0.3980864882469177`

Shuffled distribution:

* minimum: `0.04447079822421074`;
* median: `0.101720429956913`;
* maximum: `0.5`;
* shuffled controls equal to or greater than biological: `1 / 20`.

Plus-one empirical upper-tail estimate:

`0.09523809523809523`

### Closest threshold gap

Biological:

`0.6019135117530823`

Shuffled distribution:

* minimum: `0.5`;
* median: `0.898279570043087`;
* maximum: `0.9555292017757893`;
* shuffled controls equal to or closer to threshold than biological:
  `1 / 20`.

Plus-one empirical lower-tail estimate:

`0.09523809523809523`

## Strongest Shuffled Controls

The strongest shuffled realization was seed:

`20260917`

It produced:

* L2/L3-only peak: `0.5`;
* relay-only peak: `0.5`;
* actual wider peak: `0.5`;
* closest threshold gap: `0.5`.

This control exceeded the biological value and is retained without exclusion.

The next strongest controls were:

| Seed     |    L2/L3-only peak |
| -------- | -----------------: |
| 20260927 | 0.2869565188884735 |
| 20260933 | 0.2584269642829895 |
| 20260923 | 0.2566371560096741 |
| 20260924 |               0.25 |

The biological L2/L3 value therefore exceeded `19 / 20` precommitted matched
shuffles but did not exceed the complete ensemble.

## Initial 20-Seed Interpretation

The initial ensemble provides evidence that the intact MaleCNS topology
produces an unusually strong downstream response relative to this small set of
retinal-interface-preserving randomized controls.

The result is suggestive rather than conclusive.

Specifically:

* biological topology exceeded `19 / 20` shuffled controls on all four
  precommitted metrics;
* one shuffled topology exceeded biology;
* the finite-ensemble plus-one tail estimate is approximately `0.0952`;
* no wider-connectome neuron fired in either the biological graph or the
  initial matched control experiment.

The result therefore does not establish that biological topology is superior
to randomized topology.

It establishes that biological and matched randomized topologies produce
different deterministic recurrent dynamics, and that the biological response
lies near the high-response end of the first precommitted 20-member null
ensemble.

## Initial 20-Seed Supported Claim

Under the frozen MQ-2.1 sensory and visual-transduction model, Condition A
produces deterministic activity that propagates:

1. through the artificial R1-R6 population;
2. into biological L1/L2/L3/Lai visual relay neurons;
3. through excitatory L2 relay neurons;
4. into subthreshold membrane state in the wider MaleCNS connectome.

When the complete retinal output interface is preserved and topology
downstream of that boundary is randomized, recurrent dynamics diverge one
frame after the first relay activity.

Across the first precommitted 20-member randomized ensemble, the intact
MaleCNS topology produced a stronger downstream response than 19 controls on
all four predefined metrics.

This observation does not establish:

* market understanding;
* prediction;
* preference;
* learning;
* trading skill;
* profitability;
* optimality of biological topology;
* statistical significance of a general topology effect.

## Remaining Controls After Ensemble v1

MQ-2.1 still requires additional independent controls before a topology-level
conclusion is justified.

High-priority follow-up:

1. precommitted larger independent shuffle ensemble;
2. ticker-to-territory permutation;
3. feature ablations;
4. downstream response characterization if wider-connectome spikes emerge.

Any larger shuffle ensemble must use new seeds and be committed before its
results are observed.

The 20-seed ensemble must remain in the scientific record regardless of the
outcome of later replication.
## Independent 100-Seed Replication

A larger independent replication was precommitted after completion of the
20-member ensemble.

Configuration:

`config/controls/shuffled-mosca-ensemble-v2.toml`

The replication design specified:

* control: `shuffled-mosca-v2`;
* first seed: `20261000`;
* number of seeds: `100`;
* condition: `A`;
* frozen release gain:
  `0.9981738484618123`;
* no seed selection after results;
* no early stopping;
* all precommitted seeds required to run;
* the same four metrics used in ensemble v1.

The replication used entirely new seeds and did not modify the biological
reference, sensory interface, transduction model, or evaluation metrics.

### Replication result artifact

Artifact:

`mq2-1-shuffled-ensemble-v2.json`

SHA-256:

`05d18a1b616fe32d2f884fc1835d553dcd0185072cf76e5a9b0b1c6871b259ab`

## One-Hundred-Seed Results

The biological reference remained:

| Metric                    |          Biological |
| ------------------------- | ------------------: |
| Relay-only peak           |  0.4412076535702383 |
| L2/L3-only peak           | 0.44255319237709045 |
| Actual wider-network peak |  0.3980864882469177 |
| Closest threshold gap     |  0.6019135117530823 |

### Relay-only peak

Shuffled distribution:

* minimum: `0.02950819581747055`;
* median: `0.12482662126421928`;
* maximum: `1.0`;
* shuffled controls equal to or greater than biological:
  `9 / 100`.

Plus-one empirical upper-tail estimate:

`0.09900990099009901`

### L2/L3-only peak

Shuffled distribution:

* minimum: `0.02950819581747055`;
* median: `0.12482662126421928`;
* maximum: `1.0`;
* shuffled controls equal to or greater than biological:
  `9 / 100`.

Plus-one empirical upper-tail estimate:

`0.09900990099009901`

The biological L2/L3-only peak was approximately `3.55x` the shuffled median.

### Actual wider-network peak

Shuffled distribution:

* minimum: `0.02950819581747055`;
* median: `0.12370959669351578`;
* maximum: `0.5515463948249817`;
* shuffled controls equal to or greater than biological:
  `8 / 100`.

Plus-one empirical upper-tail estimate:

`0.0891089108910891`

### Closest threshold gap

Shuffled distribution:

* minimum: `0.4484536051750183`;
* median: `0.8762904033064842`;
* maximum: `0.9704918041825294`;
* shuffled controls equal to or closer to threshold than biological:
  `8 / 100`.

Plus-one empirical lower-tail estimate:

`0.0891089108910891`

## Replication Interpretation

The independent 100-member replication reproduced the qualitative result of
the initial 20-member ensemble.

In both experiments, the intact MaleCNS topology produced a stronger
downstream response than most, but not all, retinal-interface-preserving
randomized controls.

The replication therefore argues against the 20-member result being solely a
small-sample anomaly.

At the same time, the biological graph was not an extreme outlier.

In the replication:

* `9 / 100` shuffled controls equaled or exceeded the biological relay-only
  peak;
* `9 / 100` equaled or exceeded the biological L2/L3-only peak;
* `8 / 100` equaled or exceeded the biological actual wider-network peak;
* `8 / 100` approached threshold at least as closely as the biological graph.

The corresponding finite-ensemble plus-one tail estimates were approximately
`0.089` to `0.099`.

The supported interpretation is therefore:

> The intact MaleCNS topology reproducibly lies toward the high-response end
> of the tested interface-preserving randomized topology distributions under
> Condition A, approximately within the upper decile for the predefined
> downstream-response metrics.

This result does not support a claim that the biological topology is uniquely
optimized, overwhelmingly superior, or statistically established as a
general topology effect.

## Combined Ensemble Record

The two precommitted topology ensembles now provide:

| Experiment  | Controls | Controls >= biological L2/L3 peak |
| ----------- | -------: | --------------------------------: |
| Ensemble v1 |       20 |                                 1 |
| Ensemble v2 |      100 |                                 9 |

The direction of the result was preserved across the independent replication:

* biological topology remained above the large majority of shuffled controls;
* randomized topologies capable of matching or exceeding biology remained
  present;
* the biological response therefore appears unusual rather than unique.

The 20-member ensemble and the 100-member replication must both remain in the
scientific record.

The replication does not replace or retroactively reinterpret the initial
ensemble.

## Updated Supported Claim

Under the frozen MQ-2.1 sensory and visual-transduction model, Condition A
produces deterministic activity that propagates:

1. through the artificial R1-R6 population;
2. into biological L1/L2/L3/Lai visual relay neurons;
3. through excitatory L2 relay neurons;
4. into subthreshold membrane state in the wider MaleCNS connectome.

When the retinal output interface is preserved and topology downstream of that
boundary is randomized, recurrent dynamics diverge immediately after visual
relay activation.

Across two independently precommitted randomized-control ensembles totaling
`120` shuffled topologies, the intact MaleCNS response repeatedly fell near the
high-response end of the tested null distributions.

This supports a reproducible topology-associated difference in response
magnitude under the tested Condition A stimulus.

It does not establish:

* market understanding;
* prediction;
* preference;
* learning;
* trading skill;
* profitability;
* optimality of biological topology;
* uniqueness of biological topology;
* a general statistically established topology advantage.

## Remaining Controls After Ensemble v1

The topology-shuffle hypothesis has now received an initial ensemble and an
independent larger replication.

Additional shuffle sampling is not currently the highest-value next step.

Higher-priority MQ-2.1 controls are now:

1. ticker-to-retinal-territory permutation;
2. feature ablations;
3. characterization of downstream propagation if wider-connectome spikes
   emerge.

The existing topology ensembles should remain frozen while these orthogonal
controls are evaluated.
## Ticker-to-Territory Permutation Control

A balanced asset-to-retinal-territory permutation control tested whether the
MQ-2.1 A/B result depended on the original ticker assignment.

The control used twelve precommitted mappings:

* six cyclic rotations;
* six reversed cyclic rotations.

Across the twelve mappings, each of the six assets occupied each retinal
territory exactly twice.

Only asset-to-territory assignment changed.

The following remained frozen:

* synthetic market histories;
* feature calculations;
* per-asset causal normalization;
* retinal territory geometry;
* sensory gain;
* visual-transduction model;
* `release_gain_v1`;
* MaleCNS connectome.

### Input Perturbation Validation

The permutation control produced genuinely different inputs.

For Condition A:

* unique normalized-history hashes: `12 / 12`;
* unique retinal-stimulus hashes: `12 / 12`.

For Condition B:

* unique normalized-history hashes: `12 / 12`;
* unique retinal-stimulus hashes: `12 / 12`.

The control therefore changed what the artificial retinal population received
and was not merely a relabeling of identical inputs.

The first eight observations were identical across assets by construction.

After the synthetic histories diverged, all six normalized asset rows became
distinct.

### Propagation Results

Across all twelve ticker-to-territory mappings:

| Measure                               | Condition A | Condition B |
| ------------------------------------- | ----------: | ----------: |
| Mappings with relay spikes            |     12 / 12 |      0 / 12 |
| Mappings with excitatory relay spikes |     12 / 12 |      0 / 12 |

The L2/L3-attributed downstream peak for Condition A was identical across all
twelve tested mappings:

`0.44255319237709045`

Condition B remained:

`0.0`

The equality of this scalar peak does not imply identical neural trajectories.
The retinal stimulus hashes differed across every mapping.

It establishes only that the maximum L2/L3-attributed downstream response
measured by this experiment was invariant across the tested balanced
asset-to-territory assignments.

## Permutation-Control Interpretation

The original A/B relay-level distinction is not dependent on the original
BTC, ETH, SOL, XRP, HBAR, DOGE ordering across retinal territories.

Condition A continued to produce biological relay activity and excitatory
relay propagation for every tested mapping.

Condition B failed to produce relay activity for every tested mapping.

This strengthens the interpretation that the observed A/B distinction reflects
the structure of the synthetic market conditions rather than one fortunate
ticker-to-retinal-territory assignment.

It does not establish invariance to every possible one of the `6! = 720`
ticker permutations, nor does it establish market understanding,
prediction, preference, learning, or trading performance.
