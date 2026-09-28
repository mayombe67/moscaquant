# One True Morty — Persistent Subject State Contract

## Status

**DESIGN SCAFFOLD / NON-EXECUTABLE**

This document defines the future state-boundary model for persistent MQ-001
individual lineages.

It does not:

- activate plasticity;
- alter a checkpoint format;
- authorize a neural experiment;
- change runtime behavior;
- promote any current checkpoint to persistent-individual status.

## Core rule

**Serializable state is not automatically persistent scientific state.**

Every state variable capable of affecting future subject computation across a
defined persistence boundary must be prospectively classified.

No state becomes part of an individual merely because the implementation can
save it.

## State classes

### IMMUTABLE_BASELINE

Shared scientific substrate identifying the model from which a subject lineage
was derived.

Examples:

- MaleCNS structural connectome;
- neuron identity map;
- frozen runtime semantics;
- frozen model parameters;
- frozen experimental configuration where applicable.

This state is referenced by immutable identity and provenance.

A subject does not rewrite it.

### SUBJECT_PERSISTENT

State belonging to one experimental MQ subject and explicitly permitted by a
frozen protocol to affect future computation after the declared persistence
boundary.

Potential examples include:

- subject-specific plasticity overlays;
- persistent scar state;
- persistent modulatory state;
- recovery counters;
- learned subject-specific parameters;
- persistent eligibility state, but only if a protocol explicitly defines
  eligibility as surviving that boundary.

Membership in SUBJECT_PERSISTENT must be prospective.

Implementation convenience is not sufficient.

### EPISODE_LOCAL

Dynamic state explicitly reset at the declared episode or session boundary.

Potential examples include:

- membrane state;
- current spike state;
- refractory state;
- transient activity traces;
- transient modulation;
- transient eligibility.

A future protocol may reclassify a field only prospectively.

Past checkpoints may not be retroactively described as containing persistent
individual state merely because those fields were serialized.

### EXTERNAL_AUTHORITY

State capable of constraining what MQ-001 may do but not belonging to the
subject's neural identity.

Examples:

- WARDEN state;
- broker or account state;
- financial limits;
- containment authorization;
- kill switches;
- external execution state.

External authority must not be smuggled into a neural checkpoint as learned or
subject-persistent state.

### PRESENTATION_ONLY

State used to display, narrate or administratively characterize MQ-001 without
determining scientific neural behavior.

Examples:

- Panopticon cosmetics;
- achievements;
- HR records;
- Employee of the Month status;
- presentation mood;
- lore;
- room decorations.

Presentation state does not become scientific state.

## Persistence-boundary invariant

For every variable capable of changing future subject computation, exactly one
must be true at a declared persistence boundary:

1. it is explicitly SUBJECT_PERSISTENT; or
2. it is explicitly reset.

An unclassified causal variable invalidates the checkpoint as a complete
persistent-individual representation.

## Lineage

Every future persistent-individual checkpoint must identify at least:

- subject ID;
- parent checkpoint or genesis baseline;
- immutable MaleCNS baseline identity;
- runtime semantic version;
- persistent-state schema version;
- hashes of persistent state;
- experiment / experience lineage;
- randomization provenance where applicable;
- deterministic replay provenance where applicable.

## Fork isolation

After two candidate subjects fork experimentally, they must not silently share
SUBJECT_PERSISTENT mutable state.

A shared immutable baseline is permitted.

Shared mutable learned state is not.

Any deliberate synchronization or transfer between lineages requires its own
explicit scientific protocol.

## Qualification boundary

A persistent checkpoint and its qualification experiment are separate
artifacts.

Qualification should normally:

- load a sealed subject checkpoint read-only;
- disable further learning unless specifically preregistered;
- disable new reinforcement unless specifically preregistered;
- preserve frozen qualification inputs;
- emit new immutable evidence.

Training-phase behavior is not automatically qualification evidence.

## One True Morty

**One True Morty** is the canonical designation for a promoted persistent
MQ-001 lineage.

It is a provenance designation, not a scientific conclusion.

Promotion requires a checkpoint complete with respect to every
protocol-defined persistent state variable capable of affecting that subject's
future computation.

Promotion does not imply:

- biological individuality;
- consciousness;
- intelligence;
- agency beyond the defined computational system;
- market skill;
- profitability;
- superiority to scientific controls.

## Relationship to external methodology

External projects may motivate design improvements.

Their learning parameters, biological assumptions, runtimes and scientific
claims are not inherited automatically.

MoscaQuant adapts useful experimental architecture under its own frozen
protocols and provenance.

## Future implementation gate

Before implementing a persistent-individual checkpoint format:

1. freeze the persistence boundary;
2. enumerate every causal runtime state field;
3. classify each field;
4. define reset semantics;
5. define checkpoint schema;
6. implement round-trip tests;
7. implement forbidden-sharing tests across forked subjects;
8. independently verify deterministic continuation where promised.

No One True Morty promotion may precede that gate.

Science first.

Lulz a very close second.
