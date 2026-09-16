# MQ-2.1 Feature Ablation

## Status

Completed first-order feature ablation study.

This experiment evaluates which components of the frozen Market Vision feature
representation contribute to MQ-2.1 visual-relay propagation.

It does not evaluate trading performance, prediction, profitability, market
understanding, preference, or learning.

## Frozen Experimental Context

The experiment used the frozen MQ-2.1 sensory and visual-transduction system.

Visual-transduction gain:

`release_gain_v1 = 0.9981738484618123`

The seven Market Vision features were:

1. return;
2. momentum;
3. volume deviation;
4. realized volatility;
5. spread;
6. order-book imbalance;
7. return-sign entropy.

Ablations were applied after causal normalization by replacing the selected
normalized feature value with `0.0`.

All other experimental components remained unchanged.

## Experimental Design

Fifteen precommitted conditions were evaluated:

* one full-feature baseline;
* seven leave-one-out ablations;
* seven single-feature isolation conditions.

Both synthetic Condition A and Condition B were replayed through every
condition.

The purpose of the leave-one-out experiment was to test feature necessity in
the full-feature context.

The purpose of single-feature isolation was to test whether any one feature was
sufficient to reproduce the observed excitatory relay propagation.

## Result Artifact

Artifact:

`mq2-1-feature-ablation-v1.json`

SHA-256:

`01172427ff57f1b4cc4ad09c729c45136d8cc014f719b74841463516698a26e1`

## Baseline

The intact seven-feature encoder reproduced the frozen MQ-2.1 result:

| Condition | Relay spikes | Excitatory relay spikes |
| --------- | -----------: | ----------------------: |
| A         |           40 |                       7 |
| B         |            0 |                       0 |

Condition A L2/L3-attributed downstream peak:

`0.44255319237709045`

## Leave-One-Out Results

| Removed feature      | A relay | A excitatory |        A L2/L3 peak | B relay |
| -------------------- | ------: | -----------: | ------------------: | ------: |
| return               |      25 |            2 | 0.46330276131629944 |       0 |
| momentum             |      37 |            6 | 0.44255319237709045 |       0 |
| volume deviation     |      23 |            0 |                 0.0 |       0 |
| realized volatility  |      35 |            6 | 0.44255319237709045 |       0 |
| spread               |      21 |            1 |  0.3810741603374481 |       5 |
| order-book imbalance |      32 |            5 | 0.44255319237709045 |       0 |
| return-sign entropy  |      35 |            6 | 0.44255319237709045 |       1 |

## Single-Feature Isolation Results

| Isolated feature     | A relay | A excitatory | A L2/L3 peak | B relay |
| -------------------- | ------: | -----------: | -----------: | ------: |
| return               |       2 |            0 |          0.0 |       0 |
| momentum             |       1 |            0 |          0.0 |       1 |
| volume deviation     |       6 |            0 |          0.0 |       3 |
| realized volatility  |       0 |            0 |          0.0 |       0 |
| spread               |      11 |            0 |          0.0 |       0 |
| order-book imbalance |       1 |            0 |          0.0 |       0 |
| return-sign entropy  |       1 |            0 |          0.0 |       1 |

## Interpretation

No individual Market Vision feature was sufficient to reproduce Condition A's
excitatory L2/L3 relay propagation.

The observed excitatory response therefore depends on interactions among
multiple encoded market dimensions rather than on a single isolated feature.

### Volume deviation

Removing volume deviation reduced Condition A from:

* `40` to `23` total relay spikes;
* `7` to `0` excitatory relay spikes;
* `0.44255319237709045` to `0.0` L2/L3-attributed downstream peak.

Volume deviation is therefore necessary for the observed excitatory relay
propagation in the complete seven-feature context.

This does not establish that volume deviation is globally necessary under
every possible subset of features.

Volume deviation alone was not sufficient:

* Condition A relay spikes: `6`;
* Condition A excitatory relay spikes: `0`.

### Spread

Removing spread reduced Condition A from:

* `40` to `21` relay spikes;
* `7` to `1` excitatory relay spike.

The L2/L3-attributed peak fell from:

`0.44255319237709045`

to:

`0.3810741603374481`

Condition B also changed from zero relay activity to:

`5` relay spikes.

Spread therefore appears to contribute both to Condition A propagation and to
maintenance of the original A/B relay-level distinction.

This result does not establish that spread directly suppresses Condition B in
isolation; the effect may depend on interactions with the remaining features.

### Return-sign entropy

Removing return-sign entropy left most Condition A propagation intact:

* `35` relay spikes;
* `6` excitatory relay spikes.

Condition B gained:

`1` relay spike.

This suggests a possible interaction with the A/B distinction, but a single
relay event is insufficient to establish a general suppressive role.

### Return

Removing return reduced Condition A relay activity from `40` to `25` spikes
and excitatory relay activity from `7` to `2`.

However, the maximum L2/L3-attributed downstream peak increased from:

`0.44255319237709045`

to:

`0.46330276131629944`

This demonstrates that relay spike count and maximum downstream depolarization
are distinct observables.

## Supported Claim

Under the frozen MQ-2.1 encoder and visual-transduction model:

* the full seven-feature Condition A stimulus produces excitatory visual-relay
  propagation;
* no individual feature reproduces that excitatory propagation by itself;
* volume deviation is necessary for the observed L2/L3 propagation when all
  other features are present;
* spread strongly modifies both Condition A propagation and the measured A/B
  relay distinction;
* feature interactions are therefore required to explain the observed MQ-2.1
  response.

These results do not establish:

* prediction;
* market understanding;
* learning;
* preference;
* trading performance;
* profitability;
* global feature necessity;
* global feature sufficiency.

## Next Control

The first-order ablations do not identify the minimal feature combination
required for excitatory relay propagation.

The natural next experiment is an exhaustive feature-subset control across the
complete seven-feature power set.

There are:

`2^7 = 128`

possible feature subsets.

Evaluating all subsets removes subset-selection ambiguity and can determine:

* the smallest subsets sufficient for Condition A excitatory relay propagation;
* whether volume deviation appears in every excitatory-producing subset;
* which subsets produce Condition B relay leakage;
* which feature combinations preserve the original A-positive/B-silent relay
  distinction.
## Exhaustive Feature-Subset Control

A second feature-control experiment evaluated the complete power set of the
seven frozen Market Vision features.

With seven features, the complete feature space contains:

`2^7 = 128`

subsets.

Every subset was precommitted and evaluated under both Condition A and
Condition B.

No subset selection or early stopping occurred.

Artifact:

`mq2-1-feature-subsets-v2.json`

SHA-256:

`607ae2227a4edde038aa21bdc055eac32f5fb9deb1ad2568e129f668935dfc34`

## Global Results

Across all 128 feature subsets:

* `48 / 128` produced Condition A excitatory relay activity;
* `40 / 128` produced Condition A excitatory activity while Condition B
  remained relay-silent;
* `40 / 128` produced some Condition B relay activity;
* `0 / 128` produced Condition B excitatory relay activity.

No single feature was sufficient to produce Condition A excitatory relay
propagation.

The minimum sufficient subset size was two features.

Two minimal Condition A excitatory subsets were identified:

1. `return + spread`;
2. `volume_deviation + spread`.

Both also preserved zero Condition B relay activity.

## Minimal Clean Subsets

### Return + spread

Condition A:

* relay spikes: `23`;
* excitatory relay spikes: `1`;
* L2/L3-attributed peak: `0.36942675709724426`.

Condition B:

* relay spikes: `0`.

### Volume deviation + spread

Condition A:

* relay spikes: `25`;
* excitatory relay spikes: `1`;
* L2/L3-attributed peak: `0.46330276131629944`.

Condition B:

* relay spikes: `0`.

These results establish that excitatory propagation does not require the full
seven-feature representation.

They also establish that volume deviation is not globally necessary.

## Feature Prevalence

Among all 48 Condition A excitatory subsets:

| Feature              | Presence |
| -------------------- | -------: |
| return               |  33 / 48 |
| momentum             |  23 / 48 |
| volume deviation     |  38 / 48 |
| realized volatility  |  22 / 48 |
| spread               |  41 / 48 |
| order-book imbalance |  26 / 48 |
| return-sign entropy  |  22 / 48 |

Among the 40 Condition A excitatory subsets that also preserved zero Condition
B relay activity:

| Feature              | Presence |
| -------------------- | -------: |
| return               |  25 / 40 |
| momentum             |  19 / 40 |
| volume deviation     |  30 / 40 |
| realized volatility  |  17 / 40 |
| spread               |  40 / 40 |
| order-book imbalance |  19 / 40 |
| return-sign entropy  |  19 / 40 |

Spread was therefore present in every tested feature combination that produced
Condition A excitatory relay propagation while preserving complete Condition B
relay silence.

This does not establish that spread directly suppresses Condition B.
It establishes a complete combinatorial association within the frozen
seven-feature MQ-2.1 stimulus space.

## Non-Spread Excitatory Solutions

Seven feature subsets produced Condition A excitatory activity without spread.

Every one of these subsets also produced Condition B relay activity.

Therefore, within the exhaustive tested feature space:

* spread was not required for Condition A excitatory propagation itself;
* spread was required for the combination of Condition A excitatory
  propagation and zero Condition B relay activity.

## Neutral Empty-Set Control

The empty feature set produced identical results for Conditions A and B:

* retinal spikes: `2095`;
* relay spikes: `1`;
* Lai spikes: `1`;
* excitatory relay spikes: `0`;
* wider-network spikes: `0`.

This is consistent with the previously observed neutral MQ-2.1 relay event and
should not be interpreted as market-conditioned B activity.

## Updated Interpretation

MQ-2.1 feature dependence is combinatorial and non-monotonic.

Features do not behave as independent additive contributors.

Removing one feature from the full encoder can eliminate propagation even
though another smaller subset lacking that same feature can still produce
excitatory activity.

The first-order observation that volume deviation was necessary in the
seven-feature context therefore does not generalize across the full feature
space.

The exhaustive experiment instead identifies spread as the feature most
consistently associated with preservation of the A-excitatory/B-silent
distinction.

No single feature is sufficient.

At least two encoded dimensions are required for Condition A excitatory
propagation under the tested system.

## Final MQ-2.1 Supported Claim

Under the frozen MQ-2.1 sensory encoder, visual-transduction model, and MaleCNS
connectome:

1. structured synthetic market histories produce deterministic retinal
   stimulation;
2. Condition A propagates beyond the artificial retina into biological visual
   relay neurons;
3. Condition A can activate excitatory L2 relay neurons and generate
   second-synapse downstream current;
4. Condition B does not produce excitatory relay activity across any of the
   128 possible feature subsets;
5. the response depends on interactions among multiple Market Vision features;
6. two-feature combinations are sufficient for Condition A excitatory
   propagation;
7. spread is present in every tested subset that simultaneously produces
   Condition A excitatory propagation and preserves zero Condition B relay
   activity;
8. intact biological topology produces reproducibly high, but not unique,
   downstream response magnitude relative to matched interface-preserving
   shuffled controls.

These findings establish reproducible market-conditioned neural dynamics under
the frozen MQ-2.1 model.

They do not establish:

* market understanding;
* prediction;
* preference;
* learning;
* trading skill;
* profitability;
* biological optimality;
* generalization to real market data.

## MQ-2.1 Status

MQ-2.1 experimental controls are complete.

The visual-transduction implementation, topology controls, ticker-territory
controls, and exhaustive feature controls are frozen for this experimental
line.

Further development should proceed without modifying these frozen results.
