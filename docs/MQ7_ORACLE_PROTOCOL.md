**System:** ORACLE-01  
**Codename:** GLaDOS  
**Role:** Behavioral interpretation / adaptation layer  
**Authority:** None
# MQ-7.1 — ORACLE Behavioral-Layer Protocol Freeze

**Status:** FROZEN BEFORE IMPLEMENTATION

> Oracle may change its interpretation of MQ-001. Oracle may not change what MQ-001 was.

## 1. Scientific question

Can a separate adaptive behavioral layer improve the usefulness and consistency of MQ-001 outputs without modifying the frozen connectome, accepted evidence, or authority rules?

Oracle is not part of MQ-001 anatomy. It is a separate behavioral/adaptation layer operating downstream of accepted MQ-001 evidence.

```text
stimulus
   |
   v
 MQ-001
 frozen organism
   |
   v
evidence/readout
   |
   v
 ORACLE
 behavioral interpretation/adaptation
   |
   v
 proposal
   |
   v
WARDEN-01
 independent authority
```

## 2. Core invariant

Oracle may:

* observe accepted MQ-001 outputs;
* maintain its own behavioral state;
* interpret patterns;
* adapt its own internal model;
* apply predefined behavioral or reinforcement perturbations;
* generate proposals;
* abstain;
* record uncertainty.

Oracle must never:

* modify MQ-001 anatomy;
* rewrite the frozen connectome;
* alter accepted historical evidence;
* rewrite telemetry;
* alter scientific stimuli retroactively;
* change scientific pass/fail criteria;
* alter WARDEN-01 policy;
* bypass WARDEN-01;
* execute external actions directly;
* reroll an intervention because the result is inconvenient.

## 3. Allowed inputs

Oracle may receive only frozen or explicitly versioned inputs:

* MQ-001 readout;
* MQ-001 behavioral/internal state;
* stimulus provenance;
* experiment/session ID;
* frame/time information;
* accepted derived features;
* prior Oracle state;
* prior intervention or reinforcement history;
* WARDEN disposition history.

Oracle must not receive privileged WARDEN-01 internals.

Public or externally visible WARDEN dispositions may become historical inputs, but private authority state is not automatically Oracle training material.

## 4. Outputs

Oracle emits proposals, never execution commands.

A proposal must identify at minimum:

* session or experiment ID;
* Oracle version;
* proposal;
* confidence or uncertainty;
* abstention state;
* behavioral state;
* evidence references;
* intervention state when applicable.

WARDEN-01 independently decides whether any downstream action is permissible.

## 5. Allowed adaptation

Oracle may adapt only its own state and parameters, including:

* proposal weighting;
* behavioral preference state;
* response thresholds;
* interpretation weights;
* reinforcement history;
* contextual memory;
* prediction calibration.

The following remain frozen:

* MQ-001 anatomy;
* connectome structure;
* accepted evidence;
* experiment definitions;
* scientific pass/fail criteria.

## 6. Intervention and reinforcement rules

Predefined interventions may be used as Oracle perturbation mechanisms.

Each intervention definition must freeze:

* trigger;
* selection probability;
* intensity;
* duration;
* state variables affected;
* recovery behavior;
* maximum frequency;
* prohibited interactions.

Once an intervention result is selected, it may not be rerolled.

Null, unfavorable, or inconvenient outcomes remain valid experimental outcomes.

## 7. Control conditions

MQ-7 uses at least four comparison conditions.

### O0 — No Oracle

MQ-001 evidence is evaluated without an Oracle behavioral/adaptation layer.

### O1 — Static Oracle

Oracle exists but cannot learn. Initial rules and state are held fixed across runs.

### O2 — Adaptive Oracle

Oracle may adapt according to the frozen adaptation rules in this protocol.

### O3 — Shuffled Oracle

Oracle activity is preserved, but the meaningful association between MQ-001 evidence and Oracle interpretation is disrupted.

The purpose is to distinguish meaningful evidence-dependent adaptation from generic effects of adding another decision layer.

## 8. Determinism and randomness

Where deterministic behavior is expected, identical:

* MQ-001 evidence;
* Oracle version;
* Oracle state;
* scientific configuration;
* runtime-independent seed inputs;

must produce identical output.

Where randomness is intentional, the event must record enough information to audit the stochastic decision, including:

* event ID;
* entropy or PRNG source identifier;
* seed or commitment;
* selected result;
* Oracle version.

## 9. Sealed Oracle policy

Oracle is sealed, not opaque.

### Public

The project publishes:

* scientific protocol;
* input/output contract;
* allowed adaptation;
* forbidden behavior;
* intervention definitions;
* probability distributions;
* control conditions;
* experiment registrations;
* Oracle version;
* implementation or artifact hash;
* intervention events;
* resulting behavioral changes;
* null results;
* WARDEN disposition.

### Private

The project may keep sealed:

* Oracle source implementation;
* internal model weights or state;
* security mechanisms;
* signing keys;
* entropy infrastructure;
* deployment internals;
* anti-tamper mechanisms.

Scientific consequences must remain auditable even when implementation details are sealed.

## 10. Version commitment

Every Oracle build receives an immutable version and artifact identity.

Before an experiment begins, record:

* experiment ID;
* protocol version;
* MQ-001 version;
* Oracle version;
* Oracle artifact hash;
* scientific configuration hash;
* runtime profile;
* control condition;
* seed or entropy commitment;
* timestamp.

An experiment remains permanently associated with the Oracle version used to produce it.

Oracle may not be silently replaced during an active experimental series.

## 11. Audit event chain

Meaningful Oracle actions must generate append-only audit events containing, where applicable:

* event ID;
* timestamp;
* experiment ID;
* session ID;
* MQ-001 evidence references;
* Oracle version;
* Oracle artifact hash;
* pre-state hash;
* input hash;
* proposal or intervention result;
* post-state hash;
* WARDEN disposition;
* previous-event hash;
* current-event hash.

A chained record should make retrospective alteration detectable.

## 12. Claim limitations

Oracle results must not automatically be described as evidence of:

* intelligence;
* consciousness;
* sentience;
* biological emotion;
* biological equivalence;
* understanding;
* profit-generating ability;
* generalization outside tested conditions.

Scientific reporting must describe observable behavior and measured effects.

Narrative or comedic language may exist in Panopticon, but must remain clearly separate from scientific claims.

## 13. Panopticon separation

Scientific records and narrative presentation are separate layers.

Scientific records may include:

* stimulus;
* neural state;
* Oracle state;
* intervention;
* proposal;
* controls;
* statistics;
* provenance.

Panopticon may present the same event through narrative elements such as:

* mood/status visualization;
* achievements;
* Sugar Cube theatrics;
* SCP-style narration;
* social persona;
* other non-scientific presentation.

Narrative presentation must not alter scientific records.

## 14. WARDEN-01 authority boundary

WARDEN-01 remains the independent authority layer.

Oracle may propose.

Oracle may not:

* authorize itself;
* modify WARDEN policy;
* bypass WARDEN;
* directly execute external actions;
* access private authority state unless explicitly exposed through a frozen interface.

## 15. MQ-7.1 pass criteria

MQ-7.1 is complete only when all of the following are frozen:

* scientific question;
* authority boundary;
* input schema;
* output/proposal schema;
* allowed adaptation;
* prohibited adaptation;
* intervention rules;
* no-reroll rule;
* O0 control;
* O1 control;
* O2 adaptive condition;
* O3 shuffled control;
* deterministic/random behavior;
* version/hash scheme;
* public/private boundary;
* audit event schema;
* claim limitations;
* WARDEN-01 supremacy.

No Oracle implementation work should begin before this protocol is reviewed and accepted.
