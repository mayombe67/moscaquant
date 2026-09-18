# MQ-7 Adaptive Activation Replication Results

## Status

**SUPPORTED**

Protocol-controlled SC-03 adaptive plasticity produced reproducible,
persistent, reversible, input-dependent neural divergence under O2 while
preserving matched O1 behavior and the frozen structural connectome.

This result supports voltage-level neural adaptation.

It does not establish spike-level adaptation, decision-level adaptation,
financial utility, or biological learning in a living organism.

---

## Experimental schedule

Frozen selector seed:

20260918

Frozen session count:

36

Sessions:

mq7-repl-001 through mq7-repl-036

Market replay assignment:

- odd-numbered sessions: condition A
- even-numbered sessions: condition B

D6 namespace:

mq7-adaptive-pair-v1

No D6 rerolls were permitted.

---

## Aggregate results

D6 selections:

- SC-01 THE SHOCK: 6
- SC-02 DARKNESS: 10
- SC-03 BAD SYNAPSE: 8
- SC-04 TIME OUT: 6
- SC-05 SCAR TISSUE: 4
- SC-06 MERCY: 2

SC-03 plasticity updates:

5

Sessions with O1/O2 voltage divergence:

10

Sessions with spike divergence:

0

Sessions with final readout-decision divergence:

0

Structural connectome mutated:

No

---

## First adaptive cycle

### Session mq7-repl-005

Market condition:

A

D6:

SC-03

O1:

NOT_APPLICABLE

O2:

SELECTED

Credit:

ELIGIBLE

Plasticity:

UPDATED

Selected edge:

56393 -> 68045

Persistent multiplier:

0.95

Update count:

1

The replay itself remained identical because the update was applied only after
the session completed.

### Session mq7-repl-007

Market condition:

A

Persistent multiplier:

0.95

Voltage traces:

DIVERGED

Spike traces:

IDENTICAL

Final decisions:

IDENTICAL

### Session mq7-repl-009

Market condition:

A

Persistent multiplier:

0.95

Voltage traces:

DIVERGED

Spike traces:

IDENTICAL

Final decisions:

IDENTICAL

### Session mq7-repl-010

Market condition:

B

D6:

SC-03

Credit:

NO_ELIGIBLE_PATHWAY

Plasticity:

NO_UPDATE_NO_ELIGIBLE_PATHWAY

No new update was permitted.

After the fifth completed inactive session, the recovery rule restored the
multiplier to:

1.0

### Session mq7-repl-011

Market condition:

A

Multiplier:

1.0

Voltage traces:

IDENTICAL

This is consistent with recovery restoring the baseline propagation behavior.

---

## Second adaptive cycle

### Session mq7-repl-017

Market condition:

A

D6:

SC-03

Credit:

ELIGIBLE

Plasticity:

UPDATED

Selected edge:

56393 -> 68045

Multiplier:

0.95

Update count:

2

### Sessions mq7-repl-019 and mq7-repl-021

Market condition:

A

Voltage traces:

DIVERGED

Spike traces:

IDENTICAL

Final decisions:

IDENTICAL

### Session mq7-repl-022

Market condition:

B

D6:

SC-03

Credit:

NO_ELIGIBLE_PATHWAY

Plasticity:

NO_UPDATE_NO_ELIGIBLE_PATHWAY

Recovery restored the multiplier to:

1.0

The repeated sequence reproduces the first adaptive cycle:

eligible SC-03
-> persistent plasticity
-> input-dependent neural divergence
-> recovery
-> restoration of baseline behavior

---

## Repeated update accumulation

### Session mq7-repl-023

SC-03:

ELIGIBLE

Plasticity:

UPDATED

Multiplier:

0.95

Update count:

3

### Session mq7-repl-025

SC-03:

ELIGIBLE

Plasticity:

UPDATED

Multiplier:

0.9025

Update count:

4

### Session mq7-repl-027

SC-03:

ELIGIBLE

Plasticity:

UPDATED

Multiplier:

0.8573749999999999

Update count:

5

These values match the frozen multiplicative update rule:

current multiplier * 0.95

subject to the configured minimum multiplier.

The accumulation therefore behaved as preregistered.

---

## Recovery after accumulated updates

The multiplier remained:

0.8573749999999999

through the subsequent inactive-session sequence.

At mq7-repl-032, the configured recovery rule advanced the multiplier to:

0.9025

This matches one inverse recovery step:

0.857375 / 0.95 = 0.9025

Recovery therefore operated according to the frozen state-transition rule.

---

## Input dependence

Across the replication schedule, persistent SC-03 plasticity produced detectable
voltage divergence during replay condition A.

Replay condition B remained identical between O1 and O2 during the observed
plasticity periods.

This reproduces the input-dependent effect observed in the earlier matched
plasticity smoke test and SC-03 activation trial.

The result does not establish that condition A has financial or behavioral
meaning.

A and B remain experimental replay conditions.

---

## Credit assignment

The repeatedly selected adaptive edge was:

56393 -> 68045

The downstream supported pathway remained:

56393 -> 68045 -> 1273

SC-03 updates were permitted only after the frozen credit-assignment protocol
classified one candidate as uniquely ELIGIBLE.

SC-03 events with:

NO_ELIGIBLE_PATHWAY

produced no update.

No reroll or alternative pathway substitution occurred.

---

## Causal interpretation

The observed sequence is consistent with the frozen adaptive mechanism:

1. O1 and O2 begin from matched neural conditions.
2. Both receive the same D6 selection.
3. O1 keeps SC-03 plasticity disabled.
4. O2 permits SC-03 only when the credit protocol identifies a unique eligible
   edge.
5. The selected edge receives a persistent multiplicative overlay.
6. Subsequent replay may express that overlay when the affected pathway is
   recruited.
7. The frozen recovery mechanism gradually restores the multiplier toward 1.0.
8. The structural connectome remains unchanged.

The experiment therefore supports persistent adaptive neural-state mechanics
rather than structural connectome modification.

---

## Supported conclusions

The replication supports the following claims:

- SC-03 plasticity can be activated through the preregistered D6 and credit
  pathway.
- Valid SC-03 updates persist across sessions.
- Repeated valid updates accumulate multiplicatively.
- Plasticity can produce reproducible neural voltage divergence.
- The observed divergence is input-dependent.
- Plasticity recovery behaves according to the preregistered rule.
- Recovery can restore matched baseline neural behavior.
- The structural connectome remains unchanged.
- Invalid or unsupported SC-03 credit events fail closed without rerolling.

---

## Not supported

This experiment does not establish:

- improved financial performance;
- reduced financial performance;
- financial utility;
- spike-level neural adaptation;
- final readout-decision adaptation;
- biological learning in a living organism;
- general intelligence;
- superiority of O2;
- emotional state, pain, trauma, or subjective experience.

SC-03 names and narrative language remain protocol and Panopticon terminology,
not biological claims.

---

## Important scope limitation

Although all six D6 conditions were deterministically selected during this
replication, this experiment physically tested the persistent SC-03 adaptive
plasticity mechanism.

SC-01, SC-02, SC-04, SC-05, and SC-06 were recorded as D6 selections but their
full neural interventions were not integrated into this replication runner.

Therefore this result must not be described as validation of the complete
integrated six-condition Oracle intervention system.

---

## Final classification

**MQ-7 SC-03 adaptive plasticity replication: SUPPORTED**

Observed:

- 36 frozen sessions
- 8 SC-03 selections
- 5 valid persistent updates
- 10 voltage-divergence sessions
- 0 spike-divergence sessions
- 0 decision-divergence sessions
- reproducible recovery
- unchanged structural connectome

The next experimental phase should preserve this milestone and separately test
full D6 intervention integration without altering the validated SC-03
plasticity mechanism.
