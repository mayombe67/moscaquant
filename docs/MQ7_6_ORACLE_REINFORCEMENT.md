# MQ-7.6 — Oracle Reinforcement Interface Freeze

**Status:** DESIGN FREEZE BEFORE IMPLEMENTATION

**System:** ORACLE-01
**Codename:** GLaDOS

> Reinforcement may change GLaDOS. It may not rewrite the fly.

## 1. Objective

MQ-7.6 defines the reinforcement interface used by ORACLE-01 before any reinforcement behavior is implemented.

The reinforcement system exists downstream of accepted MQ-001 evidence and may modify only Oracle-owned state.

It must not modify MQ-001 anatomy, accepted evidence, WARDEN-01 policy, or external execution behavior.

## 2. Reinforcement event

A reinforcement event is a versioned, auditable perturbation applied to Oracle-owned state.

Required fields:

* `reinforcement_id`
* `schema_version`
* `experiment_id`
* `session_id`
* `oracle_version`
* `trigger_id`
* `condition`
* `intensity`
* `duration`
* `selected_at`
* `entropy_commitment`
* `pre_state_hash`
* `post_state_hash`
* `metadata`

The event must be independently identifiable and replayable.

## 3. Six-condition D6 interface

The initial reinforcement selector exposes exactly six frozen condition identifiers.

The symbolic names and scientific semantics must be defined before implementation and must remain stable for the duration of a protocol version.

Each condition definition must specify:

* condition identifier;
* trigger eligibility;
* selection probability;
* intensity semantics;
* duration semantics;
* Oracle state fields allowed to change;
* recovery behavior;
* cooldown;
* maximum frequency;
* prohibited interactions;
* scientific interpretation.

Panopticon display names may differ from scientific identifiers.

## 4. Selection semantics

The initial selector uses a six-outcome uniform selection model unless a later protocol revision explicitly changes the distribution.

Selection must be:

* deterministic from a recorded seed or entropy commitment;
* auditable;
* reproducible;
* independent of presentation-layer theatrics.

Once selected, an outcome may not be rerolled because it is undesirable, inconvenient, or uninteresting.

## 5. No-reroll rule

A selected reinforcement condition is part of the scientific record.

The following are prohibited:

* rerolling;
* replacing an outcome after observing it;
* suppressing an inconvenient result;
* repeating selection until a preferred condition appears;
* silently substituting a different intervention.

A failed or null effect remains valid experimental evidence.

## 6. Trigger boundary

Reinforcement may only occur after a frozen trigger condition is satisfied.

A trigger definition must specify:

* triggering event;
* required control condition;
* prerequisite state;
* cooldown eligibility;
* maximum frequency;
* suppression conditions.

Triggers must not be created retroactively after observing an outcome.

## 7. State ownership

Reinforcement may affect only Oracle-owned fields.

Allowed targets may include:

* `behavioral_state`;
* `adaptation_state`;
* `intervention_state`;
* future explicitly versioned Oracle-owned reinforcement state.

Reinforcement must not modify:

* MQ-001 anatomy;
