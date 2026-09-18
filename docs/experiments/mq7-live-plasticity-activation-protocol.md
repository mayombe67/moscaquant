# MQ-7 — SC-03 Live Plasticity Activation Protocol

Status:

**PRE-REGISTERED / LIVE PLASTICITY DISABLED**

## Purpose

Define the conditions under which SC-03 BAD SYNAPSE may transition from
validated mechanics and observational credit assignment to live adaptive
plasticity.

This protocol governs:

- edge selection;
- ambiguity handling;
- persistence;
- stacking;
- cumulative bounds;
- recovery;
- replay.

Until this protocol is implemented and validated:

`plasticity_active = false`

## Preconditions

SC-03 may be considered for live activation only after:

1. BAD SYNAPSE -5% overlay mechanics are validated;
2. observational credit assignment is validated;
3. the candidate edge belongs to the frozen accepted causal set;
4. a unique eligible leader exists.

All four conditions are required.

## Trigger

A qualifying external loss event may trigger inspection of the recent
neural eligibility trace.

The loss event does not alter:

- edge scores;
- edge ranking;
- plasticity magnitude;
- cumulative bounds.

## Edge selection

If credit assignment returns exactly one unique leader:

`ELIGIBLE`

that edge becomes the sole candidate for SC-03.

If credit assignment returns:

`AMBIGUOUS_CREDIT`

then:

`NO_UPDATE`

If credit assignment returns:

`NO_ELIGIBLE_PATHWAY`

then:

`NO_UPDATE`

No reroll occurs.

## Update magnitude

Each accepted SC-03 update applies:

`multiplier = 0.95`

to the selected edge's current plasticity-adjusted contribution.

The frozen baseline connectome remains unchanged.

## Persistence

SC-03 plasticity is persistent across sessions until recovery rules apply.

Plasticity state must be stored separately from the structural connectome.

Required persisted fields:

- schema version;
- edge identity;
- baseline edge weight reference;
- current cumulative multiplier;
- update count;
- first update session;
- most recent update session;
- evidence reference;
- previous state hash;
- current state hash.

## Stacking

Repeated SC-03 updates may affect the same edge only when that edge is again
the unique eligible leader in a later qualifying event.

Updates stack multiplicatively:

`current_multiplier = current_multiplier × 0.95`

## Cumulative bound

The cumulative multiplier must never fall below:

`0.80`

Therefore the maximum persistent reduction from baseline is:

`20%`

If another -5% multiplicative update would cross the bound, clamp at:

`0.80`

No update may reduce an edge below this bound.

## Recovery

v1 recovery is session-based and deterministic.

If an edge receives no additional SC-03 update for:

`5 completed trading sessions`

its multiplier recovers one step toward baseline:

`multiplier = min(1.0, multiplier / 0.95)`

Recovery may occur once per completed inactive 5-session block.

Recovery continues until:

`multiplier = 1.0`

## No simultaneous multi-edge update

A single SC-03 event may update at most one edge.

This avoids confounding distributed plasticity effects in v1.

## Replay

Given identical:

- frozen baseline artifacts;
- credit-assignment evidence;
- session sequence;
- SC-03 event history;

the resulting plasticity state must replay identically.

## Structural invariance

The following must never be modified:

- `connectome-baseline-v1.npz`;
- CSR `data`;
- CSR `indices`;
- CSR `indptr`.

Plasticity must remain an overlay.

## Authority boundary

SC-03 affects modeled neural plasticity only.

It must not:

- alter WARDEN policy;
- reopen trading;
- disable Sugar Cube Mode;
- modify financial limits;
- rewrite prior D6 history.

## Interpretation limits

Persistent plasticity in MoscaQuant is a modeled adaptive mechanism.

It does not establish equivalent biological synaptic plasticity in living
Drosophila.

It does not prove a synapse caused a financial loss.

It does not establish financial utility.
