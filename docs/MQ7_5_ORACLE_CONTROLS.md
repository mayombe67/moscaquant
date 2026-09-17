# MQ-7.5 — Oracle Control-Condition Harness

**Status:** DESIGN FREEZE BEFORE IMPLEMENTATION

**System:** ORACLE-01
**Codename:** GLaDOS

## 1. Objective

MQ-7.5 implements explicit experimental control conditions for evaluating Oracle.

Control selection must be declared before a run and preserved in experiment provenance.

The control harness must not itself introduce learning, reinforcement, market strategy, or execution behavior.

## 2. Conditions

### O0 — NO_ORACLE

Oracle interpretation is bypassed.

MQ-001 evidence remains available to the experimental record, but Oracle behavioral state does not influence proposal formation.

Purpose:

Establish the baseline behavior of the system without the Oracle layer.

### O1 — STATIC_ORACLE

Oracle participates using frozen state-transition rules.

Oracle state may advance for bookkeeping and provenance, but adaptive parameters must not change.

Purpose:

Measure effects caused by introducing the Oracle interpretation layer without learning.

### O2 — ADAPTIVE_ORACLE

Oracle participates under rules that permit future adaptive behavior.

During MQ-7.5, no adaptive policy is implemented.

O2 therefore behaves as a capability boundary and provenance condition only.

Purpose:

Provide the experimental condition under which later adaptive behavior will be evaluated.

### O3 — SHUFFLED_ORACLE

Oracle receives valid evidence drawn from the accepted input set, but the meaningful association between evidence and the current experimental frame is deliberately disrupted according to a deterministic shuffle specification.

Purpose:

Test whether observed Oracle effects depend on meaningful MQ-001 evidence rather than the mere presence of an additional interpretation layer.

## 3. Run declaration

Every Oracle experiment must declare exactly one control condition before execution.

Allowed identifiers:

* `O0_NO_ORACLE`
* `O1_STATIC_ORACLE`
* `O2_ADAPTIVE_ORACLE`
* `O3_SHUFFLED_ORACLE`

The selected condition must appear in experiment provenance and audit output.

Control condition may not change during an active run.

## 4. O0 behavior

O0 must not silently instantiate behavioral adaptation.

The harness may emit a provenance record indicating that Oracle was bypassed.

O0 results must remain distinguishable from an Oracle abstention.

`NO_ORACLE` and `ABSTAIN` are different experimental states.

## 5. O1 behavior

O1 may:

* validate Oracle inputs;
* perform deterministic state transitions;
* produce proposals;
* emit audit events;
* persist and replay history.

O1 may not alter adaptive parameters.

Repeated execution from identical state and identical input must produce equivalent scientific output.

## 6. O2 behavior

O2 establishes permission for future Oracle-owned adaptation only.

MQ-7.5 must not implement that adaptation.

Until a later frozen protocol defines adaptive mechanics, O2 must behave equivalently to the non-learning Oracle path while remaining explicitly labeled `O2_ADAPTIVE_ORACLE`.

This prevents future adaptive results from being confused with static-control results.

## 7. O3 behavior

O3 disrupts evidence association while preserving the structure required for comparison.

The shuffle must be:

* deterministic from an explicit seed;
* reproducible;
* auditable;
* restricted to eligible accepted evidence;
* incapable of modifying the underlying scientific evidence.

O3 creates a transformed Oracle input.

It does not rewrite the original MQ-001 evidence record.

## 8. Shuffle provenance

Every shuffled condition must record:

* shuffle algorithm version;
* seed;
* original evidence references;
* shuffled evidence references;
* resulting input hash.

A shuffle must never be rerolled because of an undesirable result.

Initial shuffle algorithm:

`sha256-sort/v1`

For each eligible evidence reference:

`SHA256(seed || NUL || evidence_ref)`

Evidence references are ordered lexicographically by the resulting digest.

This makes O3 deterministic independently of Python PRNG implementation details.
\n\n## 9. Control ownership

The harness controls experimental routing only.

It must not:

* modify MQ-001;
* modify accepted evidence;
* change WARDEN-01 policy;
* authorize actions;
* execute trades;
* modify Oracle history retrospectively.

## 10. Persistence

The selected control condition must survive persistence and replay.

A replay must identify the original condition used for the run.

Replaying an O3 run must not generate a new shuffle.

The originally recorded shuffled input must be used.

## 11. Comparison integrity

The harness should preserve comparability across conditions wherever possible.

Conditions should use the same:

* MQ-001 evidence source;
* scientific configuration;
* experiment definition;
* Oracle version;
* runtime-independent experiment parameters.

Only the control-specific transformation or Oracle participation should differ.

## 12. Failure behavior

Invalid or unknown control identifiers must fail closed.

Missing O3 shuffle provenance must fail closed.

Attempting to change condition during an active run must fail closed.

An O2 request for adaptive behavior before an adaptive protocol exists must fail closed.

## 13. Initial implementation

MQ-7.5 adds:

```text
oracle/
└── controls.py
```

Primary responsibilities:

* define control identifiers;
* validate control selection;
* route O0/O1/O2/O3 execution;
* perform deterministic O3 evidence shuffling;
* preserve control provenance.

## 14. Explicit exclusions

MQ-7.5 does not implement:

* adaptive learning;
* reinforcement;
* D6/Sugar Cube selection;
* reward or punishment;
* market strategy;
* external execution;
* broker connectivity;
* WARDEN authority.

## 15. Pass criteria

MQ-7.5 is complete when:

* all four control conditions are explicit;
* unknown controls are rejected;
* O0 is distinguishable from abstention;
* O1 uses deterministic Oracle behavior;
* O2 is labeled but remains non-adaptive;
* O3 shuffling is deterministic from a seed;
* O3 preserves original evidence;
* O3 shuffle provenance is recorded;
* control selection cannot change mid-run;
* persisted/replayed records retain control identity;
* no adaptive behavior exists yet;
* existing Oracle integrity tests continue to pass.

## 16. Governing invariant

> A control changes how evidence is presented to Oracle, never what the original evidence was.
