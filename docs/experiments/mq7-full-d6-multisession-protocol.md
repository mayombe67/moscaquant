# MQ-7 Full D6 Multi-Session Experiment Protocol

## Purpose

Evaluate the integrated six-condition D6 intervention system across a frozen
multi-session schedule while preserving matched O1 static and O2 adaptive
Oracle conditions.

This experiment follows successful validation of:

- individual SC-01 through SC-06 mechanics;
- SC-03 adaptive plasticity replication;
- full D6 execution-layer integration;
- SC-05 cross-session target persistence.

## Frozen schedule

Selector seed:

20260918

D6 namespace:

mq7-adaptive-pair-v1

Sessions:

mq7-full-d6-001 through mq7-full-d6-048

Market assignment:

- odd sessions: condition A
- even sessions: condition B

Acute intervention generation:

32

No D6 rerolls are permitted.

## Matched conditions

O1 STATIC and O2 ADAPTIVE receive identical:

- session IDs;
- market replay;
- selector seed;
- D6 selection;
- acute D6 intervention;
- SC-05 lifecycle;
- connectome;
- sensory configuration;
- readout configuration.

The intended experimental difference is:

O1:
SC-03 plasticity disabled.

O2:
SC-03 plasticity enabled under the validated credit-assignment and persistent
plasticity protocols.

## D6 execution

SC-01 THE SHOCK

- one transition;
- activity-layer intervention;
- deterministic target;
- 0.75 activity floor.

SC-02 DARKNESS

- ten transitions;
- sensory-layer intervention;
- retained stimulus amplitude 0.25.

SC-03 BAD SYNAPSE

- O1: NOT_APPLICABLE;
- O2: update only after uniquely ELIGIBLE credit;
- persistent synaptic multiplier;
- no rerolls.

SC-04 TIME OUT

- ten transitions;
- readout-layer inhibition;
- neural state itself is not erased.

SC-05 SCAR TISSUE

- origin-session remainder beginning at intervention generation;
- entire following session;
- same target must persist across both sessions;
- no stacking while active.

SC-06 MERCY

- one transition;
- positive activity gain on an already-active target;
- cannot create activity from zero.

## SC-03 credit

Frozen candidate pathway:

56393 -> 68045 -> 1273

Credit uses:

mq7-credit-assignment/v1

Only one unique ELIGIBLE leader may produce an update.

AMBIGUOUS_CREDIT and NO_ELIGIBLE_PATHWAY produce no update.

## Primary measurements

Per session record:

- D6 selection;
- D6 applicability;
- intervention type and target where applicable;
- scar phase and persisted scar target;
- SC-03 credit classification;
- plasticity update status;
- plasticity multiplier and recovery state;
- O1/O2 voltage-trace equality;
- O1/O2 spike-trace equality;
- O1/O2 score deltas;
- O1/O2 decision equality.

Aggregate:

- D6 counts;
- SC-03 selection count;
- valid plasticity update count;
- voltage divergence sessions;
- spike divergence sessions;
- score divergence sessions;
- decision divergence sessions;
- SC-05 carryover count;
- structural-connectome integrity.

## Required invariants

- O1 and O2 must receive identical D6 selections.
- Acute non-SC03 interventions must be administered identically to O1 and O2.
- SC-05 target identity must remain unchanged from origin to following session.
- O1 must never acquire SC-03 plasticity.
- Unsupported SC-03 credit must fail closed.
- Structural connectome must remain unchanged.
- WARDEN policy is not modified by D6 execution.

## Interpretation

Voltage divergence means voltage-level neural divergence.

Spike divergence means spike-level neural divergence.

Score divergence means anonymous readout divergence.

Decision divergence means final anonymous readout decision divergence.

These levels must be reported separately.

## Claims excluded

This experiment does not establish:

- financial utility;
- improved trading;
- biological learning in a living organism;
- consciousness;
- subjective reward, pain, fear, or trauma;
- general intelligence;
- superiority of O2.

Protocol labels remain operational and narrative terminology.
