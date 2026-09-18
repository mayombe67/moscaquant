# MQ-7 — SC-03 Credit Assignment Protocol

Status:

**PRE-REGISTERED / OBSERVATIONAL ONLY**

## Purpose

Define and validate a causal eligibility signal for SC-03 BAD SYNAPSE
without activating adaptive plasticity.

This phase determines which recently active frozen causal edges can be
considered eligible for later negative plasticity.

It does not perform a synaptic update.

## Core principle

A financial loss may trigger evaluation.

A financial loss does not identify a neural cause.

Eligibility must be derived from neural activity and frozen causal
structure independently of PnL.

## Candidate edges

Only edges present in the frozen accepted MQ-3 causal artifact are eligible.

No edge may be added because of later trading performance.

For v1 validation, analysis is restricted to the already supported pathway:

`56393 → 68045 → 1273`

This restriction avoids claiming equivalent causal evidence for every
candidate edge before validation exists.

## Eligibility signal

For an eligible edge:

`presynaptic → postsynaptic`

the instantaneous contribution score is:

`abs(weight × presynaptic_effective_activity)`

This quantity measures the magnitude of the modeled synaptic contribution
at that simulation transition.

It is not interpreted as:

- profit contribution;
- loss contribution;
- biological importance;
- action desirability.

## Recency trace

Eligibility is accumulated over a frozen recent window.

v1 window:

`10 eligible transitions`

For transition age `a`, where the newest transition has age 0:

`recency_weight = 0.5 ** (a / 5)`

The eligibility trace is:

`sum(contribution_score × recency_weight)`

over the frozen 10-transition window.

This produces a deterministic recency-weighted measure of recent causal
engagement.

## Eligibility threshold

An edge is eligible only when:

1. it exists in the frozen causal artifact;
2. it had non-zero presynaptic effective activity during the lookback;
3. its resulting eligibility trace is greater than zero.

No arbitrary minimum effect threshold is introduced in v1.

## Credit-assignment output

The observational system may report:

- edge identity;
- eligibility trace;
- rank among simultaneously eligible validated edges;
- lookback window;
- contributing transitions;
- evidence references.

It must not apply plasticity.

## Financial-event relationship

A realized loss may define the timestamp at which the preceding eligibility
window is inspected.

The loss value itself must not:

- alter the eligibility score;
- select an edge;
- change recency weights;
- increase the plasticity magnitude;
- introduce a previously ineligible edge.

This separates external reinforcement timing from neural credit evidence.

## Ties

Exact ties remain ties.

v1 must not break a scientific tie using:

- PnL;
- trade size;
- random selection;
- narrative preference.

A tie may produce:

`AMBIGUOUS_CREDIT`

and no later plasticity update unless a separately frozen rule resolves it.

## No eligible edge

If no validated causal edge has a positive trace:

`NO_ELIGIBLE_PATHWAY`

SC-03 must not reroll.

## Relationship to SC-03

This protocol validates credit-assignment evidence only.

Live BAD SYNAPSE still requires a later protocol combining:

1. validated eligibility;
2. a frozen selection rule;
3. the already validated -5% overlay;
4. persistence and recovery semantics.

Until that complete protocol is frozen:

`plasticity_active = false`

## Required validation

The observational implementation must verify:

- deterministic scores;
- exact 10-transition lookback;
- frozen recency function;
- zero activity produces zero eligibility;
- more recent equal activity receives greater credit;
- higher causal contribution produces greater credit when recency is equal;
- financial loss magnitude cannot change rankings;
- baseline connectome remains untouched;
- exact ties remain ambiguous.

## Interpretation limits

The eligibility trace represents modeled recent causal engagement.

It does not prove that a synapse caused a financial loss.

It does not establish biological learning in living Drosophila.

It does not establish financial utility.
