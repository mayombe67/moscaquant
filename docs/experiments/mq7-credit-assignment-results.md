# MQ-7 — SC-03 Observational Credit Assignment Results

Status:

**COMPLETED / OBSERVATIONAL CREDIT ASSIGNMENT VALIDATED**

## Pre-registration

This experiment was preregistered in:

`docs/experiments/mq7-credit-assignment-protocol.md`

before implementation results were generated.

## Purpose

Validate a deterministic neural eligibility trace for SC-03 BAD SYNAPSE
without activating adaptive plasticity.

This phase identifies recently active frozen causal edges that may become
eligible for later negative plasticity.

No synaptic update is performed.

## Frozen candidate pathway

Validation used the previously supported MQ-5.4 pathway:

`56393 → 68045 → 1273`

The two tested causal edges were:

1. `56393 → 68045`
2. `68045 → 1273`

## Eligibility model

For each eligible causal edge:

`contribution = abs(weight × presynaptic_effective_activity)`

A frozen recency weighting was applied over the most recent 10 eligible
transitions:

`recency_weight = 0.5 ** (age / 5)`

The eligibility trace was:

`sum(contribution × recency_weight)`

The newest observation had age 0.

## Validation results

Unit tests verified:

- exact frozen recency function;
- exact 10-transition lookback;
- zero activity produces zero eligibility;
- newer equal activity receives greater credit;
- greater causal contribution receives greater credit when recency is equal;
- no eligible activity produces `NO_ELIGIBLE_PATHWAY`;
- exact ties produce `AMBIGUOUS_CREDIT`;
- a unique highest trace produces `ELIGIBLE`.

## Real-connectome integration

The frozen baseline connectome was used to obtain the real weights for:

`56393 → 68045`

and:

`68045 → 1273`

The resulting eligibility traces were determined only by:

- frozen connectome weight;
- presynaptic effective activity;
- frozen recency weighting.

Ranking was deterministic.

## Financial isolation

The credit-assignment API contains no input for:

- PnL;
- realized loss magnitude;
- trade size;
- WARDEN state;
- portfolio exposure.

A financial loss may define when the recent neural trace is inspected, but
loss magnitude cannot alter the neural eligibility score or ranking.

Equivalent neural evidence therefore produces equivalent credit assignment
regardless of whether the external financial loss is small or large.

## Result classification

Deterministic neural eligibility trace:

**SUPPORTED**

Frozen 10-transition lookback:

**SUPPORTED**

Recency-sensitive credit:

**SUPPORTED**

Contribution-sensitive credit:

**SUPPORTED**

Exact-tie ambiguity preservation:

**SUPPORTED**

Financial-loss isolation:

**SUPPORTED**

Real-connectome operation:

**SUPPORTED**

Synaptic plasticity:

**NOT ACTIVATED**

Financial causation by a neural edge:

**NOT CLAIMED**

Biological learning in living Drosophila:

**NOT CLAIMED**

Financial utility:

**NOT CLAIMED**

## Live SC-03 status

The observational credit-assignment mechanism is validated.

However, live BAD SYNAPSE remains disabled.

Before `plasticity_active = true`, a separate frozen protocol must define:

1. how an eligible edge is selected from the observational trace;
2. when ambiguity blocks an update;
3. persistence and recovery semantics for applied plasticity;
4. whether repeated updates may stack;
5. how accumulated plasticity is bounded;
6. how the already validated -5% overlay is persisted and replayed.

Until that protocol is frozen:

`plasticity_active = false`

If SC-03 is selected:

`NOT_APPLICABLE`

No reroll occurs.
