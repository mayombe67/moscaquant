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
