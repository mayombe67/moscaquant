# MQ-7 Adaptive Activation Replication Protocol

## Purpose

Replicate the validated O1/O2 SC-03 adaptive activation mechanism across a
frozen sequence of sessions without selecting sessions or seeds based on
observed outcomes.

This experiment evaluates reproducibility of protocol-controlled persistent
plasticity mechanics.

It does not test financial utility.

## Frozen schedule

Selector seed:

20260918

Sessions:

mq7-repl-001 through mq7-repl-036

Market replay assignment:

- odd-numbered sessions: condition A
- even-numbered sessions: condition B

The schedule is frozen before D6 outcomes are inspected.

No D6 rerolls are permitted.

## Matched conditions

O1 STATIC:

- identical market replay
- identical selector seed
- identical D6 namespace
- identical connectome
- identical sensory configuration
- identical readout
- SC-03 plasticity disabled

O2 ADAPTIVE:

- same matched inputs
- SC-03 plasticity enabled
- validated credit assignment
- persistent plasticity state
- validated recovery rules

## Credit assignment

Candidate edges remain restricted to the previously supported pathway:

56393 -> 68045 -> 1273

Credit uses the frozen mq7-credit-assignment/v1 protocol.

The most recent 10 effective-activity transitions are used.

Possible classifications:

- ELIGIBLE
- AMBIGUOUS_CREDIT
- NO_ELIGIBLE_PATHWAY

Only one unique ELIGIBLE leader may produce an update.

## Plasticity

Accepted SC-03 updates multiply the selected edge by 0.95.

Persistent multiplier floor:

0.80

Recovery occurs according to sc-03-plasticity-state/v1:

one recovery step after five completed inactive trading sessions.

The structural connectome must never be modified.

## Primary observations

For each session record:

- market replay condition
- D6 selection
- SC-03 applicability
- credit status
- selected credit leader
- plasticity update status
- persistent edge multiplier
- update count
- inactive completed sessions
- O1/O2 voltage-trace equality
- O1/O2 spike-trace equality
- readout-score deltas
- final readout decisions

## Required invariants

Before the first legitimate O2 plasticity update, O1 and O2 neural replay
outputs must be identical.

O1 must never acquire plasticity state.

The D6 selection itself must be identical between O1 and O2.

The baseline structural connectome digest must remain unchanged.

## Interpretation

A voltage-level difference is neural divergence.

A spike difference is spike-level divergence.

A readout decision difference is decision-level divergence.

These outcomes must not be conflated.

## Claims explicitly excluded

This experiment does not establish:

- improved profitability;
- financial utility;
- biological learning in a living organism;
- general intelligence;
- superiority of O2;
- decision-level improvement.

Null results are valid.

No rerolls or post-hoc pathway substitution are permitted.
